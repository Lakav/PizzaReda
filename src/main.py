from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from typing import List, Dict
from models import Pizza, PizzaCreate, Order, OrderCreate, Price, Address, InventoryManager, Topping, Ingredient, PizzaMenuPrice, OrderStatus
from pydantic import ValidationError
import logging
import threading
from datetime import datetime

# Configurer le logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de Livraison de Pizza",
    description="API pour gérer les commandes de pizza avec livraison gratuite à partir de 30€",
    version="1.0.0"
)

# Configurer CORS pour permettre les requêtes du frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permettre toutes les origines (à adapter en production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Monter les fichiers statiques (HTML, CSS, JS)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    logger.info(f"Dossier static créé: {static_dir}")

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Base de données en mémoire pour les commandes
orders_db: Dict[int, Order] = {}
next_order_id = 1
# Lock pour la thread-safety sur next_order_id
order_id_lock = threading.Lock()

# Gestionnaire d'inventaire
inventory = InventoryManager()


@app.get("/")
def read_root():
    """Page d'accueil de l'API"""
    return {
        "message": "Bienvenue sur l'API de Livraison de Pizza",
        "endpoints": {
            "GET /": "Cette page",
            "GET /pizzas/menu": "Voir le menu des pizzas disponibles",
            "GET /topping/menu": "Voir les toppings disponibles avec prix",
            "POST /orders": "Créer une nouvelle commande",
            "GET /orders/{order_id}": "Voir les détails d'une commande",
            "GET /orders": "Voir toutes les commandes",
            "DELETE /orders/{order_id}": "Annuler une commande",
            "GET /inventory": "Voir tout l'inventaire (ingrédients de base et toppings) avec quantités",
            "POST /inventory/ingredients/{ingredient_name}/add": "Ajouter du stock à un ingrédient",
            "GET /pricing/info": "Informations sur la tarification"
        }
    }


@app.get("/pizzas/menu")
def get_menu() -> List[PizzaMenuPrice]:
    """
    Retourne le menu des pizzas disponibles avec les prix pour chaque taille.

    Chaque pizza affiche:
    - Son nom
    - Les toppings inclus de base
    - Les prix pour small, medium et large
    """
    menu_data = [
        ("Margherita", ["tomate", "mozzarella", "basilic"]),
        ("Reine", ["tomate", "mozzarella", "jambon", "champignons"]),
        ("4 Fromages", ["mozzarella", "gorgonzola", "chèvre", "emmental"]),
        ("Calzone", ["tomate", "mozzarella", "jambon", "oeuf"]),
        ("Végétarienne", ["tomate", "mozzarella", "poivrons", "oignons", "olives"]),
        ("Pepperoni", ["tomate", "mozzarella", "pepperoni"]),
    ]

    result = []
    for pizza_name, toppings in menu_data:
        prices = {}
        for size in ["small", "medium", "large"]:
            prices[size] = Price.calculate_pizza_price(pizza_name, size, toppings)

        result.append(PizzaMenuPrice(
            name=pizza_name,
            base_toppings=toppings,
            prices=prices
        ))

    return result


@app.get("/topping/menu")
def get_toppings_menu() -> List[Topping]:
    """Retourne la liste de tous les toppings disponibles avec leur prix (+1€)"""
    return inventory.get_all_toppings()


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

    GESTION DU STOCK:
    - Vérifie que les pizzas et toppings demandés sont en stock
    - Si rupture de stock, rejette la commande avec un code 409
    - Sinon, décrémente le stock après confirmation

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
        logger.warning(f"Tentative de création de commande sans pizzas par {order_create.customer_name}")
        raise HTTPException(status_code=400, detail="La commande doit contenir au moins une pizza")

    if not order_create.customer_name:
        logger.warning("Tentative de création de commande sans nom de client")
        raise HTTPException(status_code=400, detail="Le nom du client est obligatoire")

    # Vérifier la disponibilité du stock AVANT de créer la commande
    can_fulfill, error_message = inventory.can_fulfill_order(order_create.pizzas)
    if not can_fulfill:
        logger.warning(f"Commande rejetée pour {order_create.customer_name}: {error_message}")
        raise HTTPException(status_code=409, detail=f"Commande impossible: {error_message}")

    # Convertir les PizzaCreate en Pizza avec calcul automatique du prix
    pizzas_with_prices = [Pizza.from_create(pizza_create) for pizza_create in order_create.pizzas]

    # Utiliser le lock pour assurer que next_order_id est thread-safe
    with order_id_lock:
        current_order_id = next_order_id
        next_order_id += 1

    order = Order(
        order_id=current_order_id,
        pizzas=pizzas_with_prices,
        customer_name=order_create.customer_name,
        customer_address=order_create.customer_address
    )

    # Réduire l'inventaire après création de la commande
    inventory.reduce_inventory(pizzas_with_prices)

    orders_db[current_order_id] = order

    logger.info(f"Commande créée: ID={current_order_id}, Client={order_create.customer_name}, Total={order.calculate_total()}€")

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
        logger.warning(f"Tentative d'annulation d'une commande inexistante: ID={order_id}")
        raise HTTPException(status_code=404, detail=f"Commande {order_id} non trouvée")

    order = orders_db.pop(order_id)
    logger.info(f"Commande annulée: ID={order_id}, Client={order.customer_name}")
    return {
        "message": f"Commande {order_id} annulée avec succès",
        "cancelled_order": order.get_summary()
    }


# ====================
# GESTION DU STOCK DES INGRÉDIENTS
# ====================

@app.get("/inventory")
def get_inventory() -> dict:
    """
    Retourne l'inventaire complet avec tous les ingrédients de base et toppings avec leurs quantités.

    Format:
    {
        "base_ingredients": [
            {"name": "pate", "quantity": 200, "is_base_ingredient": true},
            ...
        ],
        "toppings": [
            {"name": "tomate", "quantity": 100, "is_base_ingredient": false},
            {"name": "mozzarella", "quantity": 100, "is_base_ingredient": false},
            ...
        ],
        "total_quantity": 1100
    }
    """
    return inventory.get_full_inventory()


@app.post("/inventory/ingredients/{ingredient_name}/add")
def add_ingredient_stock(ingredient_name: str, quantity: int) -> dict:
    """
    Ajoute du stock à un ingrédient

    Query parameters:
    - quantity: Quantité à ajouter (doit être positif)
    """
    if quantity <= 0:
        logger.warning(f"Tentative d'ajout de stock avec quantité invalide: {ingredient_name}={quantity}")
        raise HTTPException(status_code=400, detail="La quantité doit être positive")

    success = inventory.add_ingredient_stock(ingredient_name, quantity)
    if not success:
        logger.warning(f"Tentative d'ajout de stock pour un ingrédient inexistant: {ingredient_name}")
        raise HTTPException(status_code=404, detail=f"Ingrédient '{ingredient_name}' non trouvé")

    current_stock = inventory.get_ingredient_stock(ingredient_name)
    logger.info(f"Stock augmenté: {ingredient_name} +{quantity} (nouveau stock: {current_stock})")
    return {
        "message": f"Stock de {ingredient_name} augmenté de {quantity}",
        "ingredient_name": ingredient_name,
        "quantity_added": quantity,
        "new_stock": current_stock
    }


# ====================
# ENDPOINTS POUR SUIVI DES COMMANDES (CLIENT)
# ====================

@app.get("/orders/{order_id}/status")
def get_order_status(order_id: int) -> dict:
    """
    Obtient le statut détaillé d'une commande pour le client
    """
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail=f"Commande {order_id} non trouvée")

    order = orders_db[order_id]
    summary = order.get_summary()

    # Ajouter des informations de progression
    progress = {
        "pending": 0,
        "preparing": 25,
        "ready_for_delivery": 50,
        "in_delivery": 75,
        "delivered": 100,
        "cancelled": 0
    }

    return {
        **summary,
        "progress_percent": progress.get(order.status.value, 0),
        "status_label": {
            "pending": "En attente de confirmation",
            "preparing": "En cours de préparation",
            "ready_for_delivery": "Prête pour livraison",
            "in_delivery": "En cours de livraison",
            "delivered": "Livrée",
            "cancelled": "Annulée"
        }.get(order.status.value, "Inconnu")
    }


# ====================
# ENDPOINTS POUR ADMIN/VENDEUR
# ====================

@app.get("/admin/orders")
def get_admin_orders() -> dict:
    """
    Obtient toutes les commandes groupées par statut (pour le vendeur)
    """
    orders_by_status = {
        "pending": [],
        "preparing": [],
        "ready_for_delivery": [],
        "in_delivery": [],
        "delivered": [],
        "cancelled": []
    }

    for order in orders_db.values():
        status = order.status.value
        if status in orders_by_status:
            orders_by_status[status].append(order.get_summary())

    return {
        "total_orders": len(orders_db),
        "orders_by_status": orders_by_status
    }


@app.post("/admin/orders/{order_id}/start")
def start_order_preparation(order_id: int) -> dict:
    """
    Marque le début de la préparation d'une commande
    """
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail=f"Commande {order_id} non trouvée")

    order = orders_db[order_id]

    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=400, detail=f"Commande ne peut pas être préparée (statut actuel: {order.status.value})")

    order.status = OrderStatus.PREPARING
    order.started_at = datetime.now()

    logger.info(f"Préparation commencée: ID={order_id}, Client={order.customer_name}")

    return {
        "message": f"Préparation de la commande {order_id} commencée",
        "order": order.get_summary()
    }


@app.post("/admin/orders/{order_id}/ready")
def mark_order_ready(order_id: int) -> dict:
    """
    Marque une commande comme prête pour livraison
    """
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail=f"Commande {order_id} non trouvée")

    order = orders_db[order_id]

    if order.status != OrderStatus.PREPARING:
        raise HTTPException(status_code=400, detail=f"Commande doit être en cours de préparation (statut actuel: {order.status.value})")

    order.status = OrderStatus.READY_FOR_DELIVERY
    order.ready_at = datetime.now()

    logger.info(f"Commande prête pour livraison: ID={order_id}, Client={order.customer_name}")

    return {
        "message": f"Commande {order_id} est prête pour livraison",
        "order": order.get_summary()
    }


@app.post("/admin/orders/{order_id}/deliver")
def mark_order_in_delivery(order_id: int) -> dict:
    """
    Marque une commande comme en cours de livraison
    """
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail=f"Commande {order_id} non trouvée")

    order = orders_db[order_id]

    if order.status != OrderStatus.READY_FOR_DELIVERY:
        raise HTTPException(status_code=400, detail=f"Commande doit être prête (statut actuel: {order.status.value})")

    order.status = OrderStatus.IN_DELIVERY

    logger.info(f"Commande en cours de livraison: ID={order_id}, Client={order.customer_name}, Adresse={order.customer_address}")

    return {
        "message": f"Commande {order_id} est en cours de livraison",
        "order": order.get_summary()
    }


@app.post("/admin/orders/{order_id}/delivered")
def mark_order_delivered(order_id: int) -> dict:
    """
    Marque une commande comme livrée
    """
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail=f"Commande {order_id} non trouvée")

    order = orders_db[order_id]

    if order.status != OrderStatus.IN_DELIVERY:
        raise HTTPException(status_code=400, detail=f"Commande doit être en cours de livraison (statut actuel: {order.status.value})")

    order.status = OrderStatus.DELIVERED
    order.delivered_at = datetime.now()

    logger.info(f"Commande livrée: ID={order_id}, Client={order.customer_name}")

    return {
        "message": f"Commande {order_id} a été livrée avec succès",
        "order": order.get_summary()
    }
