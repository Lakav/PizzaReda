# Guide des Tests

Ce projet contient deux fichiers de tests complets :

## 📁 Fichiers de tests

1. **test_models.py** - Tests unitaires pour les classes
   - Tests pour la classe `Pizza`
   - Tests pour la classe `Price`
   - Tests pour la classe `Order`

2. **test_endpoints.py** - Tests pour l'API
   - Tests de tous les endpoints
   - Tests d'intégration
   - Tests des cas limites (29.99€ vs 30€)

## 🚀 Installation des dépendances

```bash
pip install -r requirements.txt
```

Ceci installe :
- fastapi, uvicorn, pydantic (pour l'API)
- pytest (pour les tests)
- httpx (pour tester l'API)

## ✅ Lancer tous les tests

```bash
pytest
```

## 📊 Lancer les tests avec plus de détails

```bash
# Verbose mode
pytest -v

# Avec couverture de code
pytest --cov=models --cov=main

# Afficher les print statements
pytest -s

# Arrêter au premier échec
pytest -x
```

## 🎯 Lancer des tests spécifiques

```bash
# Tests des models uniquement
pytest test_models.py

# Tests des endpoints uniquement
pytest test_endpoints.py

# Une classe de tests spécifique
pytest test_models.py::TestPrice

# Un test spécifique
pytest test_models.py::TestPrice::test_calculate_delivery_fee_below_threshold
```

## 📝 Résumé des tests

### test_models.py (41 tests)

#### TestPizza (4 tests)
- ✅ Création d'une pizza
- ✅ Représentation string
- ✅ Pizza sans garnitures
- ✅ Validation prix négatif

#### TestPrice (8 tests)
- ✅ Constantes de tarification
- ✅ Frais de livraison < 30€ → 5€
- ✅ Frais de livraison = 30€ → 0€
- ✅ Frais de livraison > 30€ → 0€
- ✅ Cas limite 29.99€
- ✅ Calcul total avec frais
- ✅ Calcul total livraison gratuite
- ✅ Calcul total au seuil exact

#### TestOrder (14 tests)
- ✅ Création de commande
- ✅ Calcul sous-total (1 pizza)
- ✅ Calcul sous-total (plusieurs pizzas)
- ✅ Frais de livraison < 30€
- ✅ Frais de livraison ≥ 30€
- ✅ Calcul total avec frais
- ✅ Calcul total livraison gratuite
- ✅ Génération du résumé
- ✅ Résumé avec livraison gratuite
- ✅ Cas limite 29.99€
- ✅ Cas limite 30.00€

### test_endpoints.py (27 tests)

#### TestRootEndpoint (1 test)
- ✅ Page d'accueil

#### TestMenuEndpoint (2 tests)
- ✅ Récupération du menu
- ✅ Structure des pizzas

#### TestPricingEndpoint (1 test)
- ✅ Informations de tarification

#### TestCreateOrder (9 tests)
- ✅ Création commande valide
- ✅ Création avec livraison gratuite
- ✅ Création avec plusieurs pizzas
- ✅ Erreur: commande vide
- ✅ Erreur: nom manquant
- ✅ Erreur: adresse manquante
- ✅ Cas limite 29.99€
- ✅ Cas limite 30.00€

#### TestGetOrder (2 tests)
- ✅ Récupération commande existante
- ✅ Erreur 404 commande inexistante

#### TestGetAllOrders (2 tests)
- ✅ Liste vide
- ✅ Plusieurs commandes

#### TestCancelOrder (2 tests)
- ✅ Annulation réussie
- ✅ Erreur 404 commande inexistante

#### TestIntegration (2 tests)
- ✅ Workflow complet de commande
- ✅ Plusieurs commandes avec différents frais

## 🎓 Cas de test importants

### Règle de livraison gratuite
Les tests vérifient particulièrement les cas limites :

```python
# 29.99€ → Frais de livraison: 5€
# 30.00€ → Frais de livraison: 0€ (gratuit)
# 35.00€ → Frais de livraison: 0€ (gratuit)
```

### Validation des données
- ❌ Commande sans pizza
- ❌ Prix négatif
- ❌ Nom client vide
- ❌ Adresse vide

### Tests d'intégration
- Workflow complet : créer → lire → lister → supprimer
- Persistance des données entre les appels

## 📈 Exemple de sortie des tests

```bash
$ pytest -v

test_models.py::TestPizza::test_create_pizza PASSED
test_models.py::TestPizza::test_pizza_str PASSED
test_models.py::TestPrice::test_calculate_delivery_fee_below_threshold PASSED
test_models.py::TestPrice::test_calculate_delivery_fee_at_threshold PASSED
...
test_endpoints.py::TestCreateOrder::test_create_order_success PASSED
test_endpoints.py::TestCreateOrder::test_create_order_free_delivery PASSED
...

======================== 68 tests passed in 0.50s ========================
```

## 🐛 Debugging

Si un test échoue :

```bash
# Mode verbose avec traceback complet
pytest -vv --tb=long

# Arrêter au premier échec pour débugger
pytest -x -vv

# Lancer uniquement le test qui échoue
pytest test_models.py::TestPrice::test_calculate_total -vv
```

## ✨ Tips

- Tous les tests sont indépendants
- La base de données est réinitialisée avant chaque test
- Les tests couvrent les cas normaux ET les cas limites
- Les tests vérifient aussi les erreurs (codes 400, 404)

## 📚 Structure des tests

```
projet ecole reda/
├── models.py              # Code source
├── main.py                # API FastAPI
├── test_models.py         # 41 tests unitaires
├── test_endpoints.py      # 27 tests d'API
└── requirements.txt       # Inclut pytest
```
