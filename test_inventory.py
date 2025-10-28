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


def get_ingredients_dict(inventory_response):
    """
    Convertit la réponse d'inventaire en dict simple pour faciliter l'accès aux quantités
    Format: {"pate": 200, "tomate": 100, ...}
    """
    data = inventory_response.json()
    result = {}

    # Ajouter les ingrédients de base
    for item in data.get("base_ingredients", []):
        result[item["name"]] = item["quantity"]

    # Ajouter les toppings
    for item in data.get("toppings", []):
        result[item["name"]] = item["quantity"]

    return result


class TestInventoryEndpoints:
    """Tests pour les endpoints d'inventaire"""

    def test_get_full_inventory(self):
        """Test de récupération de l'inventaire complet"""
        response = client.get("/inventory")
        assert response.status_code == 200
        data = response.json()

        assert "base_ingredients" in data
        assert "toppings" in data
        assert "total_quantity" in data

        # Vérifier la structure des base_ingredients
        for item in data["base_ingredients"]:
            assert "name" in item
            assert "quantity" in item
            assert "is_base_ingredient" in item
            assert item["is_base_ingredient"] is True

        # Vérifier la structure des toppings
        for item in data["toppings"]:
            assert "name" in item
            assert "quantity" in item
            assert "is_base_ingredient" in item
            assert item["is_base_ingredient"] is False

    def test_get_toppings_menu(self):
        """Test de l'endpoint /topping/menu"""
        response = client.get("/topping/menu")
        assert response.status_code == 200
        data = response.json()

        assert isinstance(data, list)
        assert len(data) > 0

        # Vérifier les toppings attendus
        topping_names = [t["name"] for t in data]
        assert "pate" in topping_names
        assert "tomate" in topping_names
        assert "mozzarella" in topping_names
        assert "basilic" in topping_names

        # Vérifier la structure et les prix corrects
        from models import Price
        for topping in data:
            assert "name" in topping
            assert "price" in topping
            # Vérifier que le prix correspond à TOPPING_PRICES ou vaut 1.0 par défaut
            expected_price = Price.TOPPING_PRICES.get(topping["name"].lower(), 1.0)
            assert topping["price"] == expected_price

    def test_add_ingredient_stock_success(self):
        """Test d'ajout de stock pour un ingrédient"""
        ingredient_name = "tomate"
        quantity = 10

        # Récupérer le stock initial
        initial_response = client.get("/inventory")
        ingredients_initial = get_ingredients_dict(initial_response)
        initial_stock = ingredients_initial[ingredient_name]

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
        ingredients_initial = get_ingredients_dict(initial_response)

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
        ingredients_final = get_ingredients_dict(final_response)

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
        ingredients_initial = get_ingredients_dict(initial_response)

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
        ingredients_final = get_ingredients_dict(final_response)

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
        ingredients_initial = get_ingredients_dict(initial_response)
        initial_pate = ingredients_initial["pate"]

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
        ingredients_final = get_ingredients_dict(final_response)
        final_pate = ingredients_final["pate"]
        assert final_pate == initial_pate - 3

    def test_multiple_pizzas_in_one_order(self):
        """Test qu'une commande avec plusieurs pizzas différentes décompte les bons ingrédients"""
        initial_response = client.get("/inventory")
        ingredients_initial = get_ingredients_dict(initial_response)

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
        ingredients_final = get_ingredients_dict(final_response)

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
        ingredients_initial = get_ingredients_dict(initial_response)

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
        ingredients_final = get_ingredients_dict(final_response)

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
