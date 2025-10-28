from fastapi import FastAPI, HTTPException
from typing import List, Dict
from models import Pizza, PizzaCreate, Order, OrderCreate, Price, Address
from pydantic import ValidationError

app = FastAPI(
    title="API de Livraison de Pizza",
    description="API pour gérer les commandes de pizza avec livraison gratuite à partir de 30€",
    version="1.0.0"
)

# Base de données en mémoire pour les commandes
orders_db: Dict[int, Order] = {}
next_order_id = 1


@app.get("/")
def read_root():
    """Page d'accueil de l'API"""
    return {
        "message": "Bienvenue sur l'API de Livraison de Pizza",
        "endpoints": {
            "GET /": "Cette page",
            "GET /pizzas/menu": "Voir le menu des pizzas disponibles",
            "POST /orders": "Créer une nouvelle commande",
            "GET /orders/{order_id}": "Voir les détails d'une commande",
            "GET /orders": "Voir toutes les commandes",
            "GET /pricing/info": "Informations sur la tarification"
        }
    }


@app.get("/pizzas/menu")
def get_menu() -> List[Pizza]:
    """Retourne le menu des pizzas disponibles avec prix calculés automatiquement"""
    menu_data = [
        PizzaCreate(name="Margherita", size="medium", toppings=["tomate", "mozzarella", "basilic"]),
        PizzaCreate(name="Reine", size="medium", toppings=["tomate", "mozzarella", "jambon", "champignons"]),
        PizzaCreate(name="4 Fromages", size="medium", toppings=["mozzarella", "gorgonzola", "chèvre", "emmental"]),
        PizzaCreate(name="Calzone", size="large", toppings=["tomate", "mozzarella", "jambon", "oeuf"]),
        PizzaCreate(name="Végétarienne", size="medium", toppings=["tomate", "mozzarella", "poivrons", "oignons", "olives"]),
        PizzaCreate(name="Pepperoni", size="medium", toppings=["tomate", "mozzarella", "pepperoni"]),
    ]
    # Convertir en Pizza avec prix calculés
    return [Pizza.from_create(pizza) for pizza in menu_data]


@app.get("/pricing/info")
def get_pricing_info():
    """Retourne les informations sur la tarification"""
    return {
        "delivery_fee": Price.DELIVERY_FEE,
        "free_delivery_threshold": Price.FREE_DELIVERY_THRESHOLD,
        "message": f"Livraison gratuite à partir de {Price.FREE_DELIVERY_THRESHOLD}€"
    }


@app.post("/orders", status_code=201)
def create_order(order_create: OrderCreate) -> dict:
    """
    Crée une nouvelle commande de pizza

    Le prix de chaque pizza est calculé AUTOMATIQUEMENT selon :
    - Le type de pizza (prix de base)
    - La taille (multiplicateur : small=0.8, medium=1.0, large=1.3)
    - Les toppings supplémentaires (+1€ par topping extra)

    L'adresse est VALIDÉE pour être une vraie adresse à Toulouse (code postal 31000).

    Corps de la requête:
    - pizzas: Liste des pizzas à commander (SANS PRIX)
    - customer_name: Nom du client
    - customer_address: Objet adresse avec les champs:
        - street_number: Numéro de rue (ex: "123")
        - street: Nom de la rue (ex: "Rue de Paris")
        - city: Ville (doit être "Toulouse")
        - postal_code: Code postal (doit être "31000")

        L'adresse est validée via géocodage pour s'assurer qu'elle existe réellement à Toulouse.
    """
    global next_order_id

    if not order_create.pizzas:
        raise HTTPException(status_code=400, detail="La commande doit contenir au moins une pizza")

    if not order_create.customer_name:
        raise HTTPException(status_code=400, detail="Le nom du client est obligatoire")

    # Convertir les PizzaCreate en Pizza avec calcul automatique du prix
    pizzas_with_prices = [Pizza.from_create(pizza_create) for pizza_create in order_create.pizzas]

    order = Order(
        order_id=next_order_id,
        pizzas=pizzas_with_prices,
        customer_name=order_create.customer_name,
        customer_address=order_create.customer_address
    )

    orders_db[next_order_id] = order
    next_order_id += 1

    return order.get_summary()


@app.get("/orders/{order_id}")
def get_order(order_id: int) -> dict:
    """Récupère les détails d'une commande spécifique"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail=f"Commande {order_id} non trouvée")

    order = orders_db[order_id]
    return order.get_summary()


@app.get("/orders")
def get_all_orders() -> List[dict]:
    """Récupère toutes les commandes"""
    return [order.get_summary() for order in orders_db.values()]


@app.delete("/orders/{order_id}")
def cancel_order(order_id: int) -> dict:
    """Annule une commande"""
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail=f"Commande {order_id} non trouvée")

    order = orders_db.pop(order_id)
    return {
        "message": f"Commande {order_id} annulée avec succès",
        "cancelled_order": order.get_summary()
    }
