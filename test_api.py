"""
Script de test pour l'API de livraison de pizza
Exécuter ce script après avoir lancé l'API avec : uvicorn main:app --reload
"""

import requests
import json

BASE_URL = "http://localhost:8000"


def print_response(response, title):
    """Affiche une réponse de manière formatée"""
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"Response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))


def test_api():
    """Teste les différents endpoints de l'API"""

    # 1. Page d'accueil
    print("\n🏠 Test de la page d'accueil")
    response = requests.get(f"{BASE_URL}/")
    print_response(response, "GET /")

    # 2. Voir le menu
    print("\n📋 Test du menu")
    response = requests.get(f"{BASE_URL}/pizzas/menu")
    print_response(response, "GET /pizzas/menu")

    # 3. Informations de tarification
    print("\n💰 Test des informations de tarification")
    response = requests.get(f"{BASE_URL}/pricing/info")
    print_response(response, "GET /pricing/info")

    # 4. Créer une commande avec livraison payante (< 30€)
    print("\n🍕 Test de création de commande (livraison payante)")
    order_data_1 = {
        "pizzas": [
            {
                "name": "Margherita",
                "size": "medium",
                "price": 10.0,
                "toppings": ["tomate", "mozzarella", "basilic"]
            },
            {
                "name": "Reine",
                "size": "medium",
                "price": 12.0,
                "toppings": ["tomate", "mozzarella", "jambon", "champignons"]
            }
        ],
        "customer_name": "Jean Dupont",
        "customer_address": "123 Rue de la Pizza, 75001 Paris"
    }
    response = requests.post(f"{BASE_URL}/orders", json=order_data_1)
    print_response(response, "POST /orders (Commande 22€ - Livraison payante)")
    order_id_1 = response.json()["order_id"]

    # 5. Créer une commande avec livraison gratuite (≥ 30€)
    print("\n🍕🍕🍕 Test de création de commande (livraison gratuite)")
    order_data_2 = {
        "pizzas": [
            {
                "name": "Margherita",
                "size": "medium",
                "price": 10.0,
                "toppings": ["tomate", "mozzarella", "basilic"]
            },
            {
                "name": "Reine",
                "size": "medium",
                "price": 12.0,
                "toppings": ["tomate", "mozzarella", "jambon", "champignons"]
            },
            {
                "name": "4 Fromages",
                "size": "medium",
                "price": 13.0,
                "toppings": ["mozzarella", "gorgonzola", "chèvre", "emmental"]
            }
        ],
        "customer_name": "Marie Martin",
        "customer_address": "456 Avenue des Pizzas, 75002 Paris"
    }
    response = requests.post(f"{BASE_URL}/orders", json=order_data_2)
    print_response(response, "POST /orders (Commande 35€ - Livraison gratuite)")
    order_id_2 = response.json()["order_id"]

    # 6. Voir une commande spécifique
    print(f"\n🔍 Test de récupération de la commande #{order_id_1}")
    response = requests.get(f"{BASE_URL}/orders/{order_id_1}")
    print_response(response, f"GET /orders/{order_id_1}")

    # 7. Voir toutes les commandes
    print("\n📦 Test de récupération de toutes les commandes")
    response = requests.get(f"{BASE_URL}/orders")
    print_response(response, "GET /orders")

    # 8. Annuler une commande
    print(f"\n❌ Test d'annulation de la commande #{order_id_1}")
    response = requests.delete(f"{BASE_URL}/orders/{order_id_1}")
    print_response(response, f"DELETE /orders/{order_id_1}")

    # 9. Vérifier que la commande a bien été annulée
    print(f"\n📦 Vérification des commandes restantes")
    response = requests.get(f"{BASE_URL}/orders")
    print_response(response, "GET /orders (après annulation)")

    print("\n✅ Tests terminés avec succès!")


if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ Erreur : Impossible de se connecter à l'API")
        print("Assurez-vous que l'API est lancée avec : uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
