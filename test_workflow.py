"""
Script de démonstration du flux complet de commande
Simule: Client commande → Admin prépare → Admin livre → Client reçoit
"""

import requests
import json
from time import sleep

API_BASE = 'http://localhost:8000/'

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_full_workflow():
    """Teste le flux complet: commande → préparation → livraison"""

    print_section("1️⃣  ÉTAPE 1: CLIENT CRÉE UNE COMMANDE")

    # Client crée une commande
    order_data = {
        "customer_name": "Jean Dupont",
        "pizzas": [
            {
                "name": "Margherita",
                "size": "medium",
                "toppings": ["tomate", "mozzarella", "basilic"]
            },
            {
                "name": "Reine",
                "size": "large",
                "toppings": ["tomate", "mozzarella", "jambon", "champignons"]
            }
        ],
        "customer_address": {
            "street_number": "22",
            "street": "Rue Alsace-Lorraine",
            "city": "Toulouse",
            "postal_code": "31000"
        }
    }

    try:
        response = requests.post(API_BASE + 'orders', json=order_data, timeout=10)
        response.raise_for_status()
        order = response.json()
        order_id = order['order_id']

        print(f"✅ Commande créée avec succès!")
        print(f"   ID: {order_id}")
        print(f"   Client: {order['customer_name']}")
        print(f"   Adresse: {order['customer_address']}")
        print(f"   Pizzas: {len(order['pizzas'])}")
        print(f"   Total: {order['total']}€ (Livraison {'GRATUITE' if order['is_delivery_free'] else order['delivery_fee']+'€'})")
        print(f"   Temps estimé: {order['estimated_delivery_minutes']} minutes")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur lors de la création: {e}")
        return

    # Vérifier le statut initial
    print_section("2️⃣  VÉRIFICATION DU STATUT INITIAL")

    try:
        response = requests.get(f'{API_BASE}orders/{order_id}/status', timeout=10)
        response.raise_for_status()
        status = response.json()

        print(f"✅ Statut actuel: {status['status_label']}")
        print(f"   Progression: {status['progress_percent']}%")
        print(f"   Créée à: {status['created_at']}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}")
        return

    # Admin commence la préparation
    print_section("3️⃣  ADMIN COMMENCE LA PRÉPARATION")

    try:
        response = requests.post(f'{API_BASE}admin/orders/{order_id}/start', timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"✅ Préparation commencée!")
        print(f"   Nouveau statut: {data['order']['status']}")
        print(f"   Heure de début: {data['order']['started_at']}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}")
        return

    # Vérifier la progression
    print_section("4️⃣  VÉRIFICATION DE LA PROGRESSION (CLIENT)")

    try:
        response = requests.get(f'{API_BASE}orders/{order_id}/status', timeout=10)
        response.raise_for_status()
        status = response.json()

        print(f"✅ Statut actuel: {status['status_label']}")
        print(f"   Progression: {status['progress_percent']}%")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}")
        return

    # Admin marque la commande prête
    print_section("5️⃣  ADMIN MARQUE PRÊTE POUR LIVRAISON")

    try:
        response = requests.post(f'{API_BASE}admin/orders/{order_id}/ready', timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"✅ Pizzas prêtes!")
        print(f"   Nouveau statut: {data['order']['status']}")
        print(f"   Heure de fin de préparation: {data['order']['ready_at']}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}")
        return

    # Admin envoie en livraison
    print_section("6️⃣  ADMIN ENVOIE EN LIVRAISON")

    try:
        response = requests.post(f'{API_BASE}admin/orders/{order_id}/deliver', timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"✅ Pizzas en route!")
        print(f"   Nouveau statut: {data['order']['status']}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}")
        return

    # Client suit la livraison
    print_section("7️⃣  CLIENT SUIT LA LIVRAISON")

    try:
        response = requests.get(f'{API_BASE}orders/{order_id}/status', timeout=10)
        response.raise_for_status()
        status = response.json()

        print(f"✅ Statut actuel: {status['status_label']}")
        print(f"   Progression: {status['progress_percent']}%")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}")
        return

    # Admin confirme la livraison
    print_section("8️⃣  ADMIN CONFIRME LA LIVRAISON")

    try:
        response = requests.post(f'{API_BASE}admin/orders/{order_id}/delivered', timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"✅ Commande livrée!")
        print(f"   Nouveau statut: {data['order']['status']}")
        print(f"   Heure de livraison: {data['order']['delivered_at']}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}")
        return

    # Vérification finale
    print_section("9️⃣  VÉRIFICATION FINALE (CLIENT)")

    try:
        response = requests.get(f'{API_BASE}orders/{order_id}/status', timeout=10)
        response.raise_for_status()
        status = response.json()

        print(f"✅ Statut final: {status['status_label']}")
        print(f"   Progression: {status['progress_percent']}%")
        print(f"   Créée à: {status['created_at']}")
        print(f"   Livrée à: {status['delivered_at']}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}")
        return

    # Dashboard admin
    print_section("🔟 DASHBOARD ADMIN FINAL")

    try:
        response = requests.get(f'{API_BASE}admin/orders', timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"✅ Total de commandes: {data['total_orders']}")
        for status_name, orders in data['orders_by_status'].items():
            print(f"   {status_name}: {len(orders)}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Erreur: {e}")
        return

    print_section("✨ FLUX COMPLET TERMINÉ AVEC SUCCÈS ✨")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("  TEST DU FLUX COMPLET DE COMMANDE")
    print("  Assurez-vous que le serveur FastAPI est lancé")
    print("  uvicorn main:app --reload")
    print("="*60)

    try:
        # Vérifier que le serveur est accessible
        response = requests.get(API_BASE, timeout=5)
        if response.status_code == 200:
            test_full_workflow()
        else:
            print(f"\n❌ Erreur: Serveur retourne le code {response.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Erreur: Impossible de se connecter à {API_BASE}")
        print("   Lancez le serveur avec: uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
