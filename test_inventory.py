"""
Tests pour la gestion du stock des ingrédients de l'API
"""

import pytest
from fastapi.testclient import TestClient
from main import app, orders_db, inventory


@pytest.fixture(autouse=True)
def reset_database_and_inventory():
    """Reset la base de données et l'inventaire avant chaque test"""
    orders_db.clear()
    # Réinitialiser l'inventaire
    inventory.ingredients = inventory.AVAILABLE_INGREDIENTS.copy()
    yield


client = TestClient(app)


class TestInventoryEndpoints:
    """Tests pour les endpoints d'inventaire"""

    def test_get_inventory_summary(self):
        """Test de récupération du résumé d'inventaire"""
        response = client.get("/inventory")
        assert response.status_code == 200
        data = response.json()

        assert "ingredients" in data
        assert "total_stock" in data
        assert "ingredients_count" in data

    def test_get_ingredients_inventory(self):
        """Test de récupération du stock des ingrédients"""
        response = client.get("/inventory/ingredients")
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0

        # Vérifier que la pâte est présente
        ingredient_names = [ing["name"] for ing in data]
        assert "pate" in ingredient_names

        # Vérifier la structure
        for ingredient in data:
            assert "name" in ingredient
            assert "stock" in ingredient
            assert ingredient["stock"] >= 0

    def test_get_ingredients_menu(self):
        """Test de l'endpoint /ingredients/menu"""
        response = client.get("/ingredients/menu")
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0

        # Vérifier les ingrédients attendus
        ingredient_names = [ing["name"] for ing in data]
        assert "pate" in ingredient_names
        assert "tomate" in ingredient_names
        assert "mozzarella" in ingredient_names
        assert "basilic" in ingredient_names

    def test_add_ingredient_stock_success(self):
        """Test d'ajout de stock pour un ingrédient"""
        ingredient_name = "tomate"
        quantity = 10

        # Récupérer le stock initial
        initial_response = client.get("/inventory/ingredients")
        initial_stock = None
        for ing in initial_response.json():
            if ing["name"].lower() == ingredient_name.lower():
                initial_stock = ing["stock"]
                break

        # Ajouter du stock
        response = client.post(f"/inventory/ingredients/{ingredient_name}/add?quantity={quantity}")
        assert response.status_code == 200
        data = response.json()

        assert "message" in data
        assert data["ingredient_name"] == ingredient_name
        assert data["quantity_added"] == quantity
        assert data["new_stock"] == initial_stock + quantity

    def test_add_ingredient_stock_not_found(self):
        """Test d'ajout de stock pour un ingrédient qui n'existe pas"""
        response = client.post("/inventory/ingredients/IngredientFantome/add?quantity=10")
        assert response.status_code == 404
        assert "non trouvé" in response.json()["detail"]

    def test_add_ingredient_stock_invalid_quantity(self):
        """Test d'ajout avec quantité invalide"""
        response = client.post("/inventory/ingredients/tomate/add?quantity=-5")
        assert response.status_code == 400
        assert "positive" in response.json()["detail"]


class TestInventoryManagement:
    """Tests pour la gestion du stock des ingrédients avec les commandes"""

    def test_margherita_consumes_correct_ingredients(self):
        """Test que Margherita consomme: pâte, tomate, mozzarella, basilic"""
        # Récupérer le stock initial
        initial_response = client.get("/inventory")
        initial_data = initial_response.json()
        ingredients_initial = initial_data["ingredients"]

        # Créer une commande de Margherita
        order_data = {
            "pizzas": [
                {
                    "name": "Margherita",
                    "size": "medium",
                    "toppings": ["tomate", "mozzarella", "basilic"]
                }
            ],
            "customer_name": "Test",
            "customer_address": {
                "street_number": "22",
                "street": "Rue Alsace-Lorraine",
                "city": "Toulouse",
                "postal_code": "31000"
            }
        }
        order_response = client.post("/orders", json=order_data)
        assert order_response.status_code == 201

        # Vérifier que le stock a été décrémenté correctement
        final_response = client.get("/inventory")
        final_data = final_response.json()
        ingredients_final = final_data["ingredients"]

        # Pâte doit diminuer de 1
        assert ingredients_final["pate"] == ingredients_initial["pate"] - 1
        # Tomate doit diminuer de 1
        assert ingredients_final["tomate"] == ingredients_initial["tomate"] - 1
        # Mozzarella doit diminuer de 1
        assert ingredients_final["mozzarella"] == ingredients_initial["mozzarella"] - 1
        # Basilic doit diminuer de 1
        assert ingredients_final["basilic"] == ingredients_initial["basilic"] - 1

    def test_reine_consumes_correct_ingredients(self):
        """Test que Reine consomme: pâte, tomate, mozzarella, jambon, champignons"""
        initial_response = client.get("/inventory")
        initial_data = initial_response.json()
        ingredients_initial = initial_data["ingredients"]

        # Créer une commande de Reine
        order_data = {
            "pizzas": [
                {
                    "name": "Reine",
                    "size": "medium",
                    "toppings": ["tomate", "mozzarella", "jambon", "champignons"]
                }
            ],
            "customer_name": "Test",
            "customer_address": {
                "street_number": "22",
                "street": "Rue Alsace-Lorraine",
                "city": "Toulouse",
                "postal_code": "31000"
            }
        }
        client.post("/orders", json=order_data)

        # Vérifier
        final_response = client.get("/inventory")
        final_data = final_response.json()
        ingredients_final = final_data["ingredients"]

        assert ingredients_final["pate"] == ingredients_initial["pate"] - 1
        assert ingredients_final["tomate"] == ingredients_initial["tomate"] - 1
        assert ingredients_final["mozzarella"] == ingredients_initial["mozzarella"] - 1
        assert ingredients_final["jambon"] == ingredients_initial["jambon"] - 1
        assert ingredients_final["champignons"] == ingredients_initial["champignons"] - 1

    def test_order_rejected_insufficient_pate_stock(self):
        """Test qu'une commande est rejetée si la pâte est en rupture de stock"""
        # Vider le stock de pâte
        inventory.ingredients["pate"] = 0

        order_data = {
            "pizzas": [
                {
                    "name": "Margherita",
                    "size": "medium",
                    "toppings": ["tomate", "mozzarella", "basilic"]
                }
            ],
            "customer_name": "Test",
            "customer_address": {
                "street_number": "22",
                "street": "Rue Alsace-Lorraine",
                "city": "Toulouse",
                "postal_code": "31000"
            }
        }

        response = client.post("/orders", json=order_data)
        assert response.status_code == 409
        assert "rupture de stock" in response.json()["detail"]

    def test_order_rejected_insufficient_ingredient_stock(self):
        """Test qu'une commande est rejetée si un ingrédient est en rupture de stock"""
        # Vider le stock de basilic
        inventory.ingredients["basilic"] = 0

        order_data = {
            "pizzas": [
                {
                    "name": "Margherita",
                    "size": "medium",
                    "toppings": ["tomate", "mozzarella", "basilic"]
                }
            ],
            "customer_name": "Test",
            "customer_address": {
                "street_number": "22",
                "street": "Rue Alsace-Lorraine",
                "city": "Toulouse",
                "postal_code": "31000"
            }
        }

        response = client.post("/orders", json=order_data)
        assert response.status_code == 409
        assert "rupture de stock" in response.json()["detail"]

    def test_multiple_orders_reduce_stock_correctly(self):
        """Test que le stock est réduit correctement pour plusieurs commandes"""
        initial_response = client.get("/inventory")
        initial_data = initial_response.json()
        initial_pate = initial_data["ingredients"]["pate"]

        # Créer 3 commandes de Margherita
        for i in range(3):
            order_data = {
                "pizzas": [
                    {
                        "name": "Margherita",
                        "size": "medium",
                        "toppings": ["tomate", "mozzarella", "basilic"]
                    }
                ],
                "customer_name": f"Client{i}",
                "customer_address": {
                    "street_number": "22",
                    "street": "Rue Alsace-Lorraine",
                    "city": "Toulouse",
                    "postal_code": "31000"
                }
            }
            response = client.post("/orders", json=order_data)
            assert response.status_code == 201

        # Vérifier que la pâte a diminué de 3
        final_response = client.get("/inventory")
        final_data = final_response.json()
        final_pate = final_data["ingredients"]["pate"]
        assert final_pate == initial_pate - 3

    def test_multiple_pizzas_in_one_order(self):
        """Test qu'une commande avec plusieurs pizzas différentes décompte les bons ingrédients"""
        initial_response = client.get("/inventory")
        initial_data = initial_response.json()
        ingredients_initial = initial_data["ingredients"]

        # Commande: 1 Margherita + 1 Reine
        order_data = {
            "pizzas": [
                {
                    "name": "Margherita",
                    "size": "medium",
                    "toppings": ["tomate", "mozzarella", "basilic"]
                },
                {
                    "name": "Reine",
                    "size": "medium",
                    "toppings": ["tomate", "mozzarella", "jambon", "champignons"]
                }
            ],
            "customer_name": "Test",
            "customer_address": {
                "street_number": "22",
                "street": "Rue Alsace-Lorraine",
                "city": "Toulouse",
                "postal_code": "31000"
            }
        }
        client.post("/orders", json=order_data)

        # Vérifier
        final_response = client.get("/inventory")
        final_data = final_response.json()
        ingredients_final = final_data["ingredients"]

        # 2 pâtes (une pour chaque pizza)
        assert ingredients_final["pate"] == ingredients_initial["pate"] - 2
        # Tomate: 1 de Margherita + 1 de Reine = 2
        assert ingredients_final["tomate"] == ingredients_initial["tomate"] - 2
        # Mozzarella: 1 de Margherita + 1 de Reine = 2
        assert ingredients_final["mozzarella"] == ingredients_initial["mozzarella"] - 2
        # Basilic: seulement de Margherita = 1
        assert ingredients_final["basilic"] == ingredients_initial["basilic"] - 1
        # Jambon: seulement de Reine = 1
        assert ingredients_final["jambon"] == ingredients_initial["jambon"] - 1
        # Champignons: seulement de Reine = 1
        assert ingredients_final["champignons"] == ingredients_initial["champignons"] - 1

    def test_custom_toppings_deduction(self):
        """Test que les toppings personnalisés (non dans la recette de base) sont aussi déduits"""
        initial_response = client.get("/inventory")
        initial_data = initial_response.json()
        ingredients_initial = initial_data["ingredients"]

        # Margherita + bacon (ingrédient supplémentaire)
        order_data = {
            "pizzas": [
                {
                    "name": "Margherita",
                    "size": "medium",
                    "toppings": ["tomate", "mozzarella", "basilic", "bacon"]
                }
            ],
            "customer_name": "Test",
            "customer_address": {
                "street_number": "22",
                "street": "Rue Alsace-Lorraine",
                "city": "Toulouse",
                "postal_code": "31000"
            }
        }
        client.post("/orders", json=order_data)

        # Vérifier
        final_response = client.get("/inventory")
        final_data = final_response.json()
        ingredients_final = final_data["ingredients"]

        # Bacon doit aussi avoir diminué
        assert ingredients_final["bacon"] == ingredients_initial["bacon"] - 1

    def test_order_rejected_when_multiple_pizzas_insufficient_stock(self):
        """Test qu'une commande multi-pizzas est rejetée si UN ingrédient manque"""
        # Vider la mozzarella
        inventory.ingredients["mozzarella"] = 0

        order_data = {
            "pizzas": [
                {
                    "name": "Margherita",
                    "size": "medium",
                    "toppings": ["tomate", "mozzarella", "basilic"]
                },
                {
                    "name": "Reine",
                    "size": "medium",
                    "toppings": ["tomate", "mozzarella", "jambon", "champignons"]
                }
            ],
            "customer_name": "Test",
            "customer_address": {
                "street_number": "22",
                "street": "Rue Alsace-Lorraine",
                "city": "Toulouse",
                "postal_code": "31000"
            }
        }

        response = client.post("/orders", json=order_data)
        assert response.status_code == 409
        assert "rupture de stock" in response.json()["detail"]
