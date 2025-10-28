# 🍕 Pizzaiolo - Système Complet de Gestion des Commandes de Pizza

API REST complète avec interfaces web pour clients et vendeurs. Gestion des commandes de pizza avec livraison gratuite à partir de 30€, suivi en temps réel, et gestion du stock.

## Architecture

Le projet utilise les classes suivantes :

- **Pizza** : Représente une pizza avec nom, taille, prix et garnitures
- **Price** : Gère la logique de tarification (frais de livraison, seuil de livraison gratuite)
- **Order** : Représente une commande avec liste de pizzas et informations client

## Règles de tarification

- Frais de livraison : **5€**
- Livraison gratuite à partir de : **30€**

## Installation

1. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## 🚀 Lancement de l'Application

```bash
uvicorn main:app --reload
```

Le serveur sera accessible sur `http://localhost:8000`

### 📱 Accès aux Interfaces

Une fois le serveur lancé, accédez à :

- **Page d'Accueil**: http://localhost:8000/static/index.html
- **Interface Client**: http://localhost:8000/static/client.html
- **Interface Admin**: http://localhost:8000/static/admin.html

### 📚 Documentation API

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🎯 Interfaces Web

### Interface Client
- ✅ Sélection de pizzas avec tailles (Small, Medium, Large)
- ✅ Ajout de toppings supplémentaires
- ✅ Résumé du panier en temps réel
- ✅ Formulaire de livraison avec validation
- ✅ Suivi de commande avec barre de progression
- ✅ Affichage du temps estimé

### Interface Admin/Vendeur
- ✅ Dashboard avec commandes par statut
- ✅ Actualisation automatique toutes les 5 secondes
- ✅ Boutons pour gérer l'état des commandes:
  - Commencer la préparation
  - Marquer prête pour livraison
  - Envoyer en livraison
  - Confirmer la livraison
- ✅ Détails complets des pizzas et adresses

## 🔄 Statuts de Commande

Une commande progresse à travers les statuts suivants:
1. **Pending** (En attente) - Commande créée, en attente de confirmation
2. **Preparing** (Préparation) - Vendeur a commencé la préparation
3. **Ready for Delivery** (Prête) - Pizzas prêtes, en attente du livreur
4. **In Delivery** (En livraison) - Pizzas en route vers le client
5. **Delivered** (Livrée) - Pizzas livrées avec succès

## Endpoints disponibles

### Endpoints Client
```
GET  /pizzas/menu                           # Menu avec prix par taille
GET  /topping/menu                          # Toppings avec prix
POST /orders                                # Créer une commande
GET  /orders/{order_id}                     # Détails d'une commande
GET  /orders/{order_id}/status              # Suivi d'une commande (avec barre de progression)
GET  /orders                                # Toutes les commandes
DELETE /orders/{order_id}                   # Annuler une commande
```

### Endpoints Admin
```
GET    /admin/orders                        # Toutes les commandes par statut
POST   /admin/orders/{id}/start             # Commencer la préparation
POST   /admin/orders/{id}/ready             # Marquer prête pour livraison
POST   /admin/orders/{id}/deliver           # Envoyer en livraison
POST   /admin/orders/{id}/delivered         # Confirmer la livraison
```

### Endpoints Stock
```
GET  /inventory                             # Inventaire complet
POST /inventory/ingredients/{name}/add      # Ajouter du stock
```

### 1. Page d'accueil
```
GET /
```

### 2. Voir le menu
```
GET /pizzas/menu
```
Retourne la liste des pizzas disponibles.

### 3. Informations de tarification
```
GET /pricing/info
```
Retourne les informations sur les frais de livraison.

### 4. Créer une commande
```
POST /orders
```
Body (ATTENTION: le "price" est calculé automatiquement, ne pas l'envoyer) :
```json
{
  "pizzas": [
    {
      "name": "Margherita",
      "size": "medium",
      "toppings": ["tomate", "mozzarella", "basilic"]
    }
  ],
  "customer_name": "Jean Dupont",
  "customer_address": {
    "street_number": "15",
    "street": "Place du Capitole",
    "city": "Toulouse",
    "postal_code": "31000"
  }
}
```

### 5. Voir une commande
```
GET /orders/{order_id}
```

### 6. Voir toutes les commandes
```
GET /orders
```

### 7. Annuler une commande
```
DELETE /orders/{order_id}
```

## Exemples d'utilisation

### Exemple 1 : Commande avec livraison payante (< 30€)
```bash
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "pizzas": [
      {
        "name": "Margherita",
        "size": "medium",
        "toppings": ["tomate", "mozzarella"]
      }
    ],
    "customer_name": "Jean Dupont",
    "customer_address": {
      "street_number": "22",
      "street": "Rue Alsace-Lorraine",
      "city": "Toulouse",
      "postal_code": "31000"
    }
  }'
```

Réponse :
```json
{
  "order_id": 1,
  "customer_name": "Jean Dupont",
  "customer_address": "22 Rue Alsace-Lorraine, 31000 Toulouse",
  "pizzas": [
    {
      "name": "Margherita",
      "size": "medium",
      "toppings": ["tomate", "mozzarella"],
      "price": 10.0
    }
  ],
  "subtotal": 10.0,
  "delivery_fee": 5.0,
  "is_delivery_free": false,
  "total": 15.0,
  "status": "pending",
  "created_at": "2025-10-28T14:30:00.000000",
  "started_at": null,
  "ready_at": null,
  "delivered_at": null,
  "estimated_delivery_minutes": 27
}
```

### Exemple 2 : Commande avec livraison gratuite (≥ 30€)
```bash
curl -X POST "http://localhost:8000/orders" \
  -H "Content-Type: application/json" \
  -d '{
    "pizzas": [
      {
        "name": "Margherita",
        "size": "medium",
        "toppings": ["tomate", "mozzarella"]
      },
      {
        "name": "Reine",
        "size": "medium",
        "toppings": ["tomate", "mozzarella", "jambon"]
      },
      {
        "name": "4 Fromages",
        "size": "medium",
        "toppings": ["mozzarella", "gorgonzola"]
      }
    ],
    "customer_name": "Marie Martin",
    "customer_address": {
      "street_number": "8",
      "street": "Allée Jean Jaurès",
      "city": "Toulouse",
      "postal_code": "31000"
    }
  }'
```

Réponse :
```json
{
  "order_id": 2,
  "customer_name": "Marie Martin",
  "customer_address": "8 Allée Jean Jaurès, 31000 Toulouse",
  "pizzas": [
    {
      "name": "Margherita",
      "size": "medium",
      "toppings": ["tomate", "mozzarella"],
      "price": 10.0
    },
    {
      "name": "Reine",
      "size": "medium",
      "toppings": ["tomate", "mozzarella", "jambon"],
      "price": 12.0
    },
    {
      "name": "4 Fromages",
      "size": "medium",
      "toppings": ["mozzarella", "gorgonzola"],
      "price": 13.0
    }
  ],
  "subtotal": 35.0,
  "delivery_fee": 0.0,
  "is_delivery_free": true,
  "total": 35.0,
  "status": "pending",
  "created_at": "2025-10-28T14:35:00.000000",
  "started_at": null,
  "ready_at": null,
  "delivered_at": null,
  "estimated_delivery_minutes": 22
}
```

## Structure du projet

```
projet ecole reda/
├── main.py              # API FastAPI avec les endpoints
├── models.py            # Classes Pizza, Price, Order
├── requirements.txt     # Dépendances Python
└── README.md           # Documentation
```

## Technologies utilisées

- **FastAPI** : Framework web moderne et rapide
- **Pydantic** : Validation des données
- **Uvicorn** : Serveur ASGI
