# 🍕 Pizzaiolo - Système de Gestion des Commandes de Pizza

API REST complète avec interfaces web pour clients et vendeurs.

## 🚀 Démarrage rapide

```bash
# Depuis la racine du projet
uvicorn main:app --reload
```

Le serveur démarre sur `http://127.0.0.1:8000`

## 🌐 Accès aux Interfaces

Une fois le serveur en marche:

- **🏠 Accueil**: http://127.0.0.1:8000/static/index.html
- **👤 Client** (Commander & Suivi): http://127.0.0.1:8000/static/client.html
- **👨‍🍳 Admin** (Gestion des commandes): http://127.0.0.1:8000/static/admin.html
- **📚 Documentation API**: http://127.0.0.1:8000/docs

## 📋 Fonctionnalités

✅ **Client**
- Sélection de pizzas avec 3 tailles (S/M/L)
- Ajout de toppings supplémentaires avec affichage en temps réel
- Calcul automatique du prix (base + toppings)
- Livraison gratuite à partir de 30€
- Suivi en temps réel des commandes
- Panier flottant avec mise à jour en direct

✅ **Admin/Vendeur**
- Dashboard avec commandes groupées par statut
- Workflow complet: Attente → Préparation → Prête → Livraison → Livrée
- Gestion du stock des ingrédients
- Auto-refresh toutes les 5 secondes

✅ **API REST**
- Gestion complète des commandes
- Validation des adresses (Nominatim)
- Stock management avec persistance SQLite
- Tarification automatique avec toppings
- Commandes persistantes

## 📂 Structure du Projet

```
.
├── main.py                    # Wrapper pour uvicorn
├── app.py                     # Entry point alternatif
├── src/
│   ├── main.py               # API FastAPI
│   ├── models.py             # Modèles Pydantic
│   └── __init__.py
├── static/                    # Interfaces web
│   ├── index.html
│   ├── client.html
│   ├── admin.html
│   ├── css/style.css
│   └── js/
├── tests/                     # Tests pytest
│   ├── test_endpoints.py
│   ├── test_inventory.py
│   └── ...
└── docs/                      # Documentation
    ├── README.md
    ├── INTERFACE_GUIDE.md
    ├── AUDIT_FIXES.md
    └── ...
```

## ⚙️ Installation des Dépendances

```bash
pip install -r requirements.txt
```

## 🧪 Lancer les Tests

```bash
python -m pytest tests/ -v
```

## 📖 Documentation Complète

Voir le dossier `docs/`:
- **README.md** - Guide général
- **INTERFACE_GUIDE.md** - Guide détaillé des interfaces
- **AUDIT_FIXES.md** - Fixes de sécurité appliquées
- **DEPLOYMENT.md** - Guide de déploiement

## 🔐 Sécurité

⚠️ **Pour développement uniquement**

Fixes de sécurité appliquées:
- ✅ Race condition sur inventaire corrigée
- ✅ CORS restrictif (localhost)
- ✅ Stock restauré à l'annulation
- ✅ Parsing d'adresse sécurisé
- ✅ Livraison déterministe

Pour la production, ajouter:
- [ ] Authentification API key/JWT
- [ ] Rate limiting
- [ ] Persistance en base de données
- [ ] HTTPS/SSL

## 💡 Aide

**Le serveur ne démarre pas?**
```bash
# Vérifiez le port 8000
lsof -i :8000
pkill -f uvicorn  # Tuer les processus existants
```

**Les interfaces ne se chargent pas?**
- Vérifiez que vous accédez à http://127.0.0.1:8000 (pas localhost)
- Vérifiez les logs de la console

**Les tests échouent?**
```bash
python -m pytest tests/ -v --tb=short
```

---

**Version**: 1.0.0
**Dernière mise à jour**: October 28, 2025
**Status**: ✅ Production-ready (dev)
