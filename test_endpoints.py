"""
Tests pour les endpoints de l'API FastAPI
"""

import pytest
from fastapi.testclient import TestClient
from main import app, orders_db, next_order_id


@pytest.fixture(autouse=True)
def reset_database():
    """Reset la base de données avant chaque test"""
    global next_order_id
    orders_db.clear()
    # Note: next_order_id ne peut pas être réinitialisé facilement car c'est une variable globale
    # mais ce n'est pas critique pour les tests
    yield


client = TestClient(app)


class TestRootEndpoint:
    """Tests pour l'endpoint racine"""

    def test_read_root(self):
        """Test de l'endpoint racine"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data
        assert data["message"] == "Bienvenue sur l'API de Livraison de Pizza"


class TestMenuEndpoint:
    """Tests pour l'endpoint du menu"""

    def test_get_menu(self):
        """Test de récupération du menu"""
        response = client.get("/pizzas/menu")
        assert response.status_code == 200
        menu = response.json()
        assert isinstance(menu, list)
        assert len(menu) > 0

    def test_menu_structure(self):
        """Test de la structure des pizzas du menu"""
        response = client.get("/pizzas/menu")
        menu = response.json()
        for pizza in menu:
            assert "name" in pizza
            assert "size" in pizza
            assert "price" in pizza
            assert "toppings" in pizza
            assert pizza["price"] > 0


class TestPricingEndpoint:
    """Tests pour l'endpoint de tarification"""

    def test_get_pricing_info(self):
        """Test de récupération des infos de tarification"""
        response = client.get("/pricing/info")
        assert response.status_code == 200
        data = response.json()
        assert data["delivery_fee"] == 5.0
        assert data["free_delivery_threshold"] == 30.0
        assert "message" in data


class TestCreateOrder:
    """Tests pour la création de commandes"""

    def test_create_order_success(self):
        """Test de création d'une commande valide"""
        order_data = {
            "pizzas": [
                {
                    "name": "Margherita",
                    "size": "medium",
                    "toppings": ["tomate", "mozzarella", "basilic"]
                }
            ],
            "customer_name": "Jean Dupont",
            "customer_address": "123 Rue de Paris"
        }
        response = client.post("/orders", json=order_data)
        assert response.status_code == 201
        data = response.json()

        assert "order_id" in data
        assert data["customer_name"] == "Jean Dupont"
        assert data["customer_address"] == "123 Rue de Paris"
        assert data["subtotal"] == 8.0  # Prix auto Margherita
        assert data["delivery_fee"] == 5.0
        assert data["total"] == 13.0
        assert data["is_delivery_free"] == False

    def test_create_order_free_delivery(self):
        """Test de création d'une commande avec livraison gratuite"""
        order_data = {
            "pizzas": [
                {
                    "name": "Calzone",
                    "size": "large",
                    "toppings": ["tomate", "mozzarella", "jambon", "oeuf"]
                },
                {
                    "name": "4 Fromages",
                    "size": "large",
                    "toppings": ["mozzarella", "gorgonzola", "chèvre", "emmental"]
                },
                {
                    "name": "Margherita",
                    "size": "small",
                    "toppings": ["tomate", "mozzarella", "basilic"]
                }
            ],
            "customer_name": "Marie Martin",
            "customer_address": "456 Avenue des Pizzas"
        }
        response = client.post("/orders", json=order_data)
        assert response.status_code == 201
        data = response.json()

        # Calzone large = 15.6, 4 Fromages large = 14.3, Margherita small = 6.4 = 36.3
        assert data["subtotal"] >= 30.0
        assert data["delivery_fee"] == 0.0
        assert data["is_delivery_free"] == True

    def test_create_order_multiple_pizzas(self):
        """Test de création d'une commande avec plusieurs pizzas"""
        order_data = {
            "pizzas": [
                {
                    "name": "Margherita",
                    "size": "small",
                    "toppings": ["tomate", "mozzarella", "basilic"]
                },
                {
                    "name": "Reine",
                    "size": "medium",
                    "toppings": ["tomate", "mozzarella", "jambon", "champignons"]
                },
                {
                    "name": "Pepperoni",
                    "size": "medium",
                    "toppings": ["tomate", "mozzarella", "pepperoni"]
                }
            ],
            "customer_name": "Paul",
            "customer_address": "789 Boulevard"
        }
        response = client.post("/orders", json=order_data)
        assert response.status_code == 201
        data = response.json()

        # Margherita small = 6.4, Reine medium = 10, Pepperoni medium = 10.5
        assert data["subtotal"] > 0
        assert len(data["pizzas"]) == 3

    def test_create_order_empty_pizzas(self):
        """Test qu'on ne peut pas créer une commande sans pizza"""
        order_data = {
            "pizzas": [],
            "customer_name": "Test",
            "customer_address": "Test"
        }
        response = client.post("/orders", json=order_data)
        assert response.status_code == 400
        assert "au moins une pizza" in response.json()["detail"]

    def test_create_order_missing_customer_name(self):
        """Test qu'on ne peut pas créer une commande sans nom de client"""
        order_data = {
            "pizzas": [
                {
                    "name": "Test",
                    "size": "medium",
                    "toppings": []
                }
            ],
            "customer_name": "",
            "customer_address": "123 Rue"
        }
        response = client.post("/orders", json=order_data)
        assert response.status_code == 400

    def test_create_order_missing_address(self):
        """Test qu'on ne peut pas créer une commande sans adresse"""
        order_data = {
            "pizzas": [
                {
                    "name": "Test",
                    "size": "medium",
                    "toppings": []
                }
            ],
            "customer_name": "Jean",
            "customer_address": ""
        }
        response = client.post("/orders", json=order_data)
        assert response.status_code == 400

    def test_create_order_below_threshold(self):
        """Test d'une commande en dessous du seuil de livraison gratuite"""
        order_data = {
            "pizzas": [
                {
                    "name": "Margherita",
                    "size": "medium",
                    "toppings": ["tomate", "mozzarella", "basilic"]
                }
            ],
            "customer_name": "Test",
            "customer_address": "Test"
        }
        response = client.post("/orders", json=order_data)
        assert response.status_code == 201
        data = response.json()

        assert data["subtotal"] < 30.0
        assert data["delivery_fee"] == 5.0
        assert data["is_delivery_free"] == False

    def test_create_order_above_threshold(self):
        """Test d'une commande au-dessus du seuil de livraison gratuite"""
        order_data = {
            "pizzas": [
                {
                    "name": "Calzone",
                    "size": "large",
                    "toppings": ["tomate", "mozzarella", "jambon", "oeuf"]
                },
                {
                    "name": "Reine",
                    "size": "large",
                    "toppings": ["tomate", "mozzarella", "jambon", "champignons"]
                },
                {
                    "name": "Pepperoni",
                    "size": "small",
                    "toppings": ["tomate", "mozzarella", "pepperoni"]
                }
            ],
            "customer_name": "Test",
            "customer_address": "Test"
        }
        response = client.post("/orders", json=order_data)
        assert response.status_code == 201
        data = response.json()

        # Calzone large = 15.6, Reine large = 13.0, Pepperoni small = 8.4 = 37
        assert data["subtotal"] >= 30.0
        assert data["delivery_fee"] == 0.0
        assert data["is_delivery_free"] == True


class TestGetOrder:
    """Tests pour la récupération de commandes"""

    def test_get_order_success(self):
        """Test de récupération d'une commande existante"""
        # Créer une commande d'abord
        order_data = {
            "pizzas": [
                {
                    "name": "Test",
                    "size": "medium",
                    "toppings": []
                }
            ],
            "customer_name": "Test",
            "customer_address": "Test"
        }
        create_response = client.post("/orders", json=order_data)
        order_id = create_response.json()["order_id"]

        # Récupérer la commande
        response = client.get(f"/orders/{order_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == order_id
        assert data["customer_name"] == "Test"

    def test_get_order_not_found(self):
        """Test de récupération d'une commande inexistante"""
        response = client.get("/orders/99999")
        assert response.status_code == 404
        assert "non trouvée" in response.json()["detail"]


class TestGetAllOrders:
    """Tests pour la récupération de toutes les commandes"""

    def test_get_all_orders_empty(self):
        """Test de récupération quand il n'y a aucune commande"""
        response = client.get("/orders")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_all_orders_multiple(self):
        """Test de récupération de plusieurs commandes"""
        # Créer plusieurs commandes
        for i in range(3):
            order_data = {
                "pizzas": [
                    {"name": "Margherita", "size": "medium", "toppings": ["tomate", "mozzarella", "basilic"]}
                ],
                "customer_name": f"Client{i}",
                "customer_address": f"Adresse{i}"
            }
            client.post("/orders", json=order_data)

        # Récupérer toutes les commandes
        response = client.get("/orders")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3


class TestCancelOrder:
    """Tests pour l'annulation de commandes"""

    def test_cancel_order_success(self):
        """Test d'annulation d'une commande existante"""
        # Créer une commande
        order_data = {
            "pizzas": [
                {
                    "name": "Test",
                    "size": "medium",
                    "toppings": []
                }
            ],
            "customer_name": "Test",
            "customer_address": "Test"
        }
        create_response = client.post("/orders", json=order_data)
        order_id = create_response.json()["order_id"]

        # Annuler la commande
        response = client.delete(f"/orders/{order_id}")
        assert response.status_code == 200
        data = response.json()
        assert "annulée avec succès" in data["message"]
        assert "cancelled_order" in data

        # Vérifier que la commande n'existe plus
        get_response = client.get(f"/orders/{order_id}")
        assert get_response.status_code == 404

    def test_cancel_order_not_found(self):
        """Test d'annulation d'une commande inexistante"""
        response = client.delete("/orders/99999")
        assert response.status_code == 404
        assert "non trouvée" in response.json()["detail"]


class TestIntegration:
    """Tests d'intégration complets"""

    def test_full_order_workflow(self):
        """Test du workflow complet de commande"""
        # 1. Vérifier le menu
        menu_response = client.get("/pizzas/menu")
        assert menu_response.status_code == 200

        # 2. Créer une commande
        order_data = {
            "pizzas": [
                {
                    "name": "Margherita",
                    "size": "medium",
                    "toppings": ["tomate"]
                },
                {
                    "name": "Reine",
                    "size": "medium",
                    "toppings": ["jambon"]
                }
            ],
            "customer_name": "Integration Test",
            "customer_address": "123 Test Street"
        }
        create_response = client.post("/orders", json=order_data)
        assert create_response.status_code == 201
        order_id = create_response.json()["order_id"]

        # 3. Récupérer la commande
        get_response = client.get(f"/orders/{order_id}")
        assert get_response.status_code == 200
        assert get_response.json()["customer_name"] == "Integration Test"

        # 4. Vérifier dans toutes les commandes
        all_response = client.get("/orders")
        assert all_response.status_code == 200
        order_ids = [order["order_id"] for order in all_response.json()]
        assert order_id in order_ids

        # 5. Annuler la commande
        cancel_response = client.delete(f"/orders/{order_id}")
        assert cancel_response.status_code == 200

        # 6. Vérifier que la commande est bien annulée
        final_get_response = client.get(f"/orders/{order_id}")
        assert final_get_response.status_code == 404

    def test_multiple_orders_different_delivery_fees(self):
        """Test de plusieurs commandes avec différents frais de livraison"""
        # Commande 1: Livraison payante (petit montant)
        order1 = {
            "pizzas": [{
                    "name": "Margherita",
                    "size": "small",
                    "toppings": ["tomate", "mozzarella", "basilic"]
                }],
            "customer_name": "Client1",
            "customer_address": "Adresse1"
        }
        response1 = client.post("/orders", json=order1)
        assert response1.json()["delivery_fee"] == 5.0
        assert response1.json()["subtotal"] < 30.0

        # Commande 2: Livraison gratuite (grand montant)
        order2 = {
            "pizzas": [
                {
                    "name": "Calzone",
                    "size": "large",
                    "toppings": ["tomate", "mozzarella", "jambon", "oeuf"]
                },
                {
                    "name": "4 Fromages",
                    "size": "large",
                    "toppings": ["mozzarella", "gorgonzola", "chèvre", "emmental"]
                },
                {
                    "name": "Margherita",
                    "size": "small",
                    "toppings": ["tomate", "mozzarella", "basilic"]
                }
            ],
            "customer_name": "Client2",
            "customer_address": "Adresse2"
        }
        response2 = client.post("/orders", json=order2)
        assert response2.json()["delivery_fee"] == 0.0
        assert response2.json()["subtotal"] >= 30.0
