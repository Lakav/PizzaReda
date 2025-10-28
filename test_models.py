"""
Tests unitaires pour les classes Pizza, PizzaCreate, Price et Order
"""

import pytest
from models import Pizza, PizzaCreate, Price, Order


class TestPizzaCreate:
    """Tests pour la classe PizzaCreate"""

    def test_create_pizza_without_price(self):
        """Test de création d'une pizza sans prix"""
        pizza_create = PizzaCreate(
            name="Margherita",
            size="medium",
            toppings=["tomate", "mozzarella", "basilic"]
        )
        assert pizza_create.name == "Margherita"
        assert pizza_create.size == "medium"
        assert pizza_create.toppings == ["tomate", "mozzarella", "basilic"]
        # PizzaCreate n'a pas de champ price
        assert not hasattr(pizza_create, 'price')


class TestPizza:
    """Tests pour la classe Pizza"""

    def test_pizza_from_create_basic(self):
        """Test de conversion PizzaCreate vers Pizza avec calcul de prix"""
        pizza_create = PizzaCreate(
            name="Margherita",
            size="medium",
            toppings=["tomate", "mozzarella", "basilic"]
        )
        pizza = Pizza.from_create(pizza_create)

        assert pizza.name == "Margherita"
        assert pizza.size == "medium"
        assert pizza.toppings == ["tomate", "mozzarella", "basilic"]
        assert pizza.price == 8.0  # Prix de base Margherita

    def test_pizza_from_create_with_extra_topping(self):
        """Test du calcul de prix avec topping supplémentaire"""
        pizza_create = PizzaCreate(
            name="Margherita",
            size="medium",
            toppings=["tomate", "mozzarella", "basilic", "olives"]  # olives = extra
        )
        pizza = Pizza.from_create(pizza_create)
        assert pizza.price == 9.0  # 8.0 + 1.0 pour olives

    def test_pizza_from_create_size_small(self):
        """Test du prix selon la taille small"""
        pizza_create = PizzaCreate(
            name="Reine",
            size="small",
            toppings=["tomate", "mozzarella", "jambon", "champignons"]
        )
        pizza = Pizza.from_create(pizza_create)
        assert pizza.price == 8.0  # 10.0 * 0.8

    def test_pizza_from_create_size_large(self):
        """Test du prix selon la taille large"""
        pizza_create = PizzaCreate(
            name="Reine",
            size="large",
            toppings=["tomate", "mozzarella", "jambon", "champignons"]
        )
        pizza = Pizza.from_create(pizza_create)
        assert pizza.price == 13.0  # 10.0 * 1.3

    def test_pizza_str(self):
        """Test de la représentation string d'une pizza"""
        pizza = Pizza(
            name="Reine",
            size="large",
            toppings=["tomate", "mozzarella", "jambon", "champignons"],
            price=13.0
        )
        assert str(pizza) == "Reine (large) - 13.0€"

    def test_pizza_without_toppings(self):
        """Test d'une pizza sans garnitures"""
        pizza_create = PizzaCreate(name="Simple", size="small", toppings=[])
        pizza = Pizza.from_create(pizza_create)
        assert pizza.toppings == []
        assert pizza.price > 0  # Prix calculé automatiquement

    def test_pizza_manual_creation(self):
        """Test de création manuelle d'une Pizza avec prix (pour les tests)"""
        pizza = Pizza(name="Test", size="medium", price=15.0, toppings=[])
        assert pizza.price == 15.0


class TestPrice:
    """Tests pour la classe Price"""

    def test_delivery_fee_constants(self):
        """Test des constantes de tarification"""
        assert Price.DELIVERY_FEE == 5.0
        assert Price.FREE_DELIVERY_THRESHOLD == 30.0

    def test_calculate_pizza_price_base(self):
        """Test du calcul de prix de base"""
        price = Price.calculate_pizza_price("Margherita", "medium", ["tomate", "mozzarella", "basilic"])
        assert price == 8.0

    def test_calculate_pizza_price_with_size_small(self):
        """Test du calcul avec taille small"""
        price = Price.calculate_pizza_price("Reine", "small", ["tomate", "mozzarella", "jambon", "champignons"])
        assert price == 8.0  # 10.0 * 0.8

    def test_calculate_pizza_price_with_size_large(self):
        """Test du calcul avec taille large"""
        price = Price.calculate_pizza_price("Reine", "large", ["tomate", "mozzarella", "jambon", "champignons"])
        assert price == 13.0  # 10.0 * 1.3

    def test_calculate_pizza_price_with_extra_toppings(self):
        """Test du calcul avec toppings supplémentaires"""
        price = Price.calculate_pizza_price("Margherita", "medium", ["tomate", "mozzarella", "basilic", "olives", "jambon"])
        assert price == 10.0  # 8.0 + 2.0 (2 toppings extra)

    def test_calculate_delivery_fee_below_threshold(self):
        """Test des frais de livraison pour une commande < 30€"""
        fee = Price.calculate_delivery_fee(20.0)
        assert fee == 5.0

    def test_calculate_delivery_fee_at_threshold(self):
        """Test des frais de livraison pour une commande = 30€"""
        fee = Price.calculate_delivery_fee(30.0)
        assert fee == 0.0

    def test_calculate_delivery_fee_above_threshold(self):
        """Test des frais de livraison pour une commande > 30€"""
        fee = Price.calculate_delivery_fee(35.0)
        assert fee == 0.0

    def test_calculate_delivery_fee_edge_case(self):
        """Test des frais de livraison juste en dessous du seuil"""
        fee = Price.calculate_delivery_fee(29.99)
        assert fee == 5.0

    def test_calculate_total_with_delivery_fee(self):
        """Test du calcul du total avec frais de livraison"""
        total = Price.calculate_total(20.0)
        assert total == 25.0  # 20 + 5

    def test_calculate_total_free_delivery(self):
        """Test du calcul du total avec livraison gratuite"""
        total = Price.calculate_total(40.0)
        assert total == 40.0  # 40 + 0

    def test_calculate_total_at_threshold(self):
        """Test du calcul du total exactement au seuil"""
        total = Price.calculate_total(30.0)
        assert total == 30.0  # 30 + 0


class TestOrder:
    """Tests pour la classe Order"""

    def test_create_order(self):
        """Test de création d'une commande"""
        pizzas = [
            Pizza(name="Margherita", size="medium", price=10.0, toppings=["tomate"])
        ]
        order = Order(
            order_id=1,
            pizzas=pizzas,
            customer_name="Jean Dupont",
            customer_address="123 Rue de Paris"
        )
        assert order.order_id == 1
        assert len(order.pizzas) == 1
        assert order.customer_name == "Jean Dupont"
        assert order.customer_address == "123 Rue de Paris"

    def test_calculate_subtotal_single_pizza(self):
        """Test du calcul du sous-total avec une pizza"""
        pizzas = [
            Pizza(name="Margherita", size="medium", price=10.0, toppings=[])
        ]
        order = Order(
            order_id=1,
            pizzas=pizzas,
            customer_name="Test",
            customer_address="Test"
        )
        assert order.calculate_subtotal() == 10.0

    def test_calculate_subtotal_multiple_pizzas(self):
        """Test du calcul du sous-total avec plusieurs pizzas"""
        pizzas = [
            Pizza(name="Margherita", size="medium", price=10.0, toppings=[]),
            Pizza(name="Reine", size="medium", price=12.0, toppings=[]),
            Pizza(name="4 Fromages", size="medium", price=13.0, toppings=[])
        ]
        order = Order(
            order_id=1,
            pizzas=pizzas,
            customer_name="Test",
            customer_address="Test"
        )
        assert order.calculate_subtotal() == 35.0

    def test_calculate_delivery_fee_below_threshold(self):
        """Test des frais de livraison pour commande < 30€"""
        pizzas = [
            Pizza(name="Margherita", size="medium", price=10.0, toppings=[])
        ]
        order = Order(
            order_id=1,
            pizzas=pizzas,
            customer_name="Test",
            customer_address="Test"
        )
        assert order.calculate_delivery_fee() == 5.0

    def test_calculate_delivery_fee_above_threshold(self):
        """Test des frais de livraison pour commande >= 30€"""
        pizzas = [
            Pizza(name="Margherita", size="medium", price=10.0, toppings=[]),
            Pizza(name="Reine", size="medium", price=12.0, toppings=[]),
            Pizza(name="4 Fromages", size="medium", price=13.0, toppings=[])
        ]
        order = Order(
            order_id=1,
            pizzas=pizzas,
            customer_name="Test",
            customer_address="Test"
        )
        assert order.calculate_delivery_fee() == 0.0

    def test_calculate_total_with_delivery(self):
        """Test du calcul du total avec frais de livraison"""
        pizzas = [
            Pizza(name="Margherita", size="medium", price=10.0, toppings=[])
        ]
        order = Order(
            order_id=1,
            pizzas=pizzas,
            customer_name="Test",
            customer_address="Test"
        )
        assert order.calculate_total() == 15.0  # 10 + 5

    def test_calculate_total_free_delivery(self):
        """Test du calcul du total avec livraison gratuite"""
        pizzas = [
            Pizza(name="Pizza1", size="medium", price=15.0, toppings=[]),
            Pizza(name="Pizza2", size="medium", price=15.0, toppings=[])
        ]
        order = Order(
            order_id=1,
            pizzas=pizzas,
            customer_name="Test",
            customer_address="Test"
        )
        assert order.calculate_total() == 30.0  # 30 + 0

    def test_get_summary(self):
        """Test de la génération du résumé de commande"""
        pizzas = [
            Pizza(name="Margherita", size="medium", price=10.0, toppings=["tomate"]),
            Pizza(name="Reine", size="large", price=12.0, toppings=["jambon"])
        ]
        order = Order(
            order_id=42,
            pizzas=pizzas,
            customer_name="Jean Dupont",
            customer_address="123 Rue de Paris"
        )
        summary = order.get_summary()

        assert summary["order_id"] == 42
        assert summary["customer_name"] == "Jean Dupont"
        assert summary["customer_address"] == "123 Rue de Paris"
        assert summary["subtotal"] == 22.0
        assert summary["delivery_fee"] == 5.0
        assert summary["is_delivery_free"] == False
        assert summary["total"] == 27.0
        assert len(summary["pizzas"]) == 2

    def test_get_summary_free_delivery(self):
        """Test du résumé avec livraison gratuite"""
        pizzas = [
            Pizza(name="Pizza1", size="medium", price=10.0, toppings=[]),
            Pizza(name="Pizza2", size="medium", price=10.0, toppings=[]),
            Pizza(name="Pizza3", size="medium", price=10.0, toppings=[])
        ]
        order = Order(
            order_id=1,
            pizzas=pizzas,
            customer_name="Test",
            customer_address="Test"
        )
        summary = order.get_summary()

        assert summary["subtotal"] == 30.0
        assert summary["delivery_fee"] == 0.0
        assert summary["is_delivery_free"] == True
        assert summary["total"] == 30.0

    def test_edge_case_29_99_euros(self):
        """Test du cas limite à 29.99€"""
        pizzas = [
            Pizza(name="Test", size="medium", price=29.99, toppings=[])
        ]
        order = Order(
            order_id=1,
            pizzas=pizzas,
            customer_name="Test",
            customer_address="Test"
        )
        assert order.calculate_delivery_fee() == 5.0
        assert order.calculate_total() == pytest.approx(34.99)

    def test_edge_case_30_00_euros(self):
        """Test du cas limite à 30.00€ exactement"""
        pizzas = [
            Pizza(name="Test", size="medium", price=30.0, toppings=[])
        ]
        order = Order(
            order_id=1,
            pizzas=pizzas,
            customer_name="Test",
            customer_address="Test"
        )
        assert order.calculate_delivery_fee() == 0.0
        assert order.calculate_total() == 30.0
