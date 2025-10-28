# 📁 Structure du Projet Pizzaiolo

## 🏗️ Arborescence

```
pizzaiolo/
├── src/                          # Code source principal
│   ├── __init__.py
│   ├── main.py                   # Application FastAPI
│   └── models.py                 # Modèles Pydantic et logique métier
│
├── static/                       # Fichiers web (HTML, CSS, JS)
│   ├── index.html               # Page d'accueil
│   ├── client.html              # Interface client
│   ├── admin.html               # Interface admin
│   ├── css/
│   │   └── style.css            # Styles globaux
│   └── js/
│       ├── client.js            # Logique client
│       └── admin.js             # Logique admin
│
├── tests/                        # Tests automatisés
│   ├── __init__.py
│   ├── conftest.py              # Configuration pytest
│   ├── test_endpoints.py        # Tests des endpoints (22 tests)
│   ├── test_inventory.py        # Tests du stock (13 tests)
│   ├── test_workflow.py         # Démonstration workflow complet
│   ├── test_models.py           # Tests des modèles
│   ├── test_api.py              # Tests API généraux
│   ├── test_address_validation.py  # Tests validation d'adresse
│   └── fixtures/                # Données de test
│       ├── __init__.py
│       ├── test_order_valid.json
│       ├── test_order_invalid_city.json
│       ├── test_order_invalid_postal.json
│       └── test_order_nonexistent.json
│
├── docs/                         # Documentation complète
│   ├── README.md                # Guide général du projet
│   ├── INTERFACE_GUIDE.md       # Guide complet des interfaces
│   ├── DEPLOYMENT.md            # Guide de déploiement
│   ├── COMPLETION_SUMMARY.md    # Résumé du projet
│   ├── CHANGEMENTS_PRIX.md      # Changelog tarification
│   ├── PRICING_INFO.md          # Info tarification
│   └── TEST_README.md           # Info sur les tests
│
├── .gitignore                   # Fichiers à ignorer dans Git
├── pytest.ini                   # Configuration pytest
├── requirements.txt             # Dépendances Python
├── app.py                       # Point d'entrée pour uvicorn
├── PROJECT_STRUCTURE.md         # Ce fichier
└── .git/                        # Dépôt Git

```

## 🚀 Comment Utiliser

### Installation

```bash
# Cloner/télécharger le projet
cd pizzaiolo

# Créer et activer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# ou
.venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

### Lancer le Serveur

```bash
# Depuis la racine du projet
uvicorn app:app --reload
```

Ou directement:
```bash
python app.py
```

Accès: http://localhost:8000

### Lancer les Tests

```bash
# Tous les tests
pytest

# Avec verbose
pytest -v

# Test spécifique
pytest tests/test_endpoints.py::TestCreateOrder -v

# Test du workflow complet
python tests/test_workflow.py

# Avec coverage
pytest --cov=src
```

## 📂 Organisation des Fichiers

### `src/` - Code Source
- **main.py**: Serveur FastAPI avec tous les endpoints
- **models.py**: Modèles Pydantic, validation, logique métier

### `static/` - Frontend Web
- **HTML**: Pages web (client, admin, accueil)
- **CSS**: Styling responsive et animations
- **JS**: Logique côté client, API calls, gestion du DOM

### `tests/` - Tests Automatisés
- **test_*.py**: Tests unitaires et d'intégration
- **fixtures/**: Données de test (JSON)
- **conftest.py**: Configuration pytest pour les imports

### `docs/` - Documentation
Guides complets pour utilisation, déploiement, interfaces

## 🔧 Configuration

### pytest.ini
Configure pytest pour chercher les tests dans `tests/`
Permet de lancer `pytest` depuis la racine du projet

### conftest.py
Configure Python path pour les imports automatiques
Permet aux tests d'importer depuis `src/`

### app.py
Lance la application FastAPI avec uvicorn
Permet `uvicorn app:app --reload`

### requirements.txt
Liste toutes les dépendances Python nécessaires

## ✨ Avantages de Cette Structure

✅ **Séparation des préoccupations**
- Code source en `src/`
- Tests en `tests/`
- Documentation en `docs/`
- Frontend en `static/`

✅ **Facilité de maintenance**
- Chaque partie à sa place
- Imports clairs et organisés
- Pas de mélange entre code et tests

✅ **Scalabilité**
- Facile d'ajouter des modules en `src/`
- Facile d'ajouter des tests en `tests/`
- Structure prête pour la croissance

✅ **Bonnes pratiques**
- Suit les conventions Python
- Structure reconnaissable par tous les développeurs
- Compatible avec les outils de CI/CD

## 🔄 Workflows Courants

### Développer une nouvelle fonctionnalité

```bash
# 1. Créer le code dans src/
# 2. Créer les tests dans tests/test_*.py
# 3. Lancer pytest
pytest

# 4. Tester manuellement
uvicorn app:app --reload
# Visiter http://localhost:8000/static/client.html
```

### Ajouter une page frontend

```bash
# 1. Créer le HTML en static/
# 2. Créer le CSS en static/css/
# 3. Créer le JS en static/js/
# 4. Accéder à http://localhost:8000/static/nouvelle_page.html
```

### Ajouter une dépendance

```bash
# 1. pip install nouvelle_lib
# 2. pip freeze > requirements.txt
# 3. Ou: pip install -r requirements.txt pour réinstaller
```

## 📖 Documentation à Consulter

Pour utiliser l'application:
- **`docs/README.md`** - Guide général
- **`docs/INTERFACE_GUIDE.md`** - Guide des interfaces
- **`docs/DEPLOYMENT.md`** - Déploiement en production

## 🎯 Points Clés à Retenir

1. **Code source**: Toujours en `src/`
2. **Tests**: Toujours en `tests/`
3. **Lancer l'app**: `uvicorn app:app --reload`
4. **Lancer les tests**: `pytest`
5. **Ajouter une dépendance**: `pip install X && pip freeze > requirements.txt`

---

**Structure créée le 28/10/2024 - Pizzaiolo v2.0** 🍕
