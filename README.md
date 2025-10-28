# API de Livraison de Pizza

API REST pour gérer les commandes de pizza avec livraison gratuite à partir de 30€.

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

## Lancement de l'API

```bash
uvicorn main:app --reload
```

L'API sera accessible sur `http://localhost:8000`

## Documentation interactive

Une fois l'API lancée, accédez à :
- Swagger UI : `http://localhost:8000/docs`
- ReDoc : `http://localhost:8000/redoc`

## Endpoints disponibles

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
Body :
```json
{
  "pizzas": [
    {
      "name": "Margherita",
      "size": "medium",
      "price": 10.0,
      "toppings": ["tomate", "mozzarella", "basilic"]
    }
  ],
  "customer_name": "Jean Dupont",
  "customer_address": "15 Place du Capitole, 31000 Toulouse"
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
        "price": 10.0,
        "toppings": ["tomate", "mozzarella"]
      }
    ],
    "customer_name": "Jean Dupont",
    "customer_address": "22 Rue Alsace Lorraine, 31000 Toulouse"
  }'
```

Réponse :
```json
{
  "order_id": 1,
  "customer_name": "Jean Dupont",
  "customer_address": "22 Rue Alsace Lorraine, 31000 Toulouse",
  "pizzas": ["Margherita (medium) - 10.0€"],
  "subtotal": 10.0,
  "delivery_fee": 5.0,
  "is_delivery_free": false,
  "total": 15.0
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
        "price": 10.0,
        "toppings": ["tomate", "mozzarella"]
      },
      {
        "name": "Reine",
        "size": "medium",
        "price": 12.0,
        "toppings": ["tomate", "mozzarella", "jambon"]
      },
      {
        "name": "4 Fromages",
        "size": "medium",
        "price": 13.0,
        "toppings": ["mozzarella", "gorgonzola"]
      }
    ],
    "customer_name": "Marie Martin",
    "customer_address": "8 Allée Jean Jaurès, 31000 Toulouse"
  }'
```

Réponse :
```json
{
  "order_id": 2,
  "customer_name": "Marie Martin",
  "customer_address": "8 Allée Jean Jaurès, 31000 Toulouse",
  "pizzas": [
    "Margherita (medium) - 10.0€",
    "Reine (medium) - 12.0€",
    "4 Fromages (medium) - 13.0€"
  ],
  "subtotal": 35.0,
  "delivery_fee": 0.0,
  "is_delivery_free": true,
  "total": 35.0
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
