# 📱 Guide des Interfaces Pizzaiolo

Ce guide explique comment utiliser les interfaces client et admin de l'application Pizzaiolo.

## 🚀 Démarrage

1. **Lancer le serveur**:
```bash
cd "projet ecole reda"
uvicorn main:app --reload
```

2. **Accéder aux interfaces**:
   - **Accueil**: http://localhost:8000/static/index.html
   - **Client**: http://localhost:8000/static/client.html
   - **Admin**: http://localhost:8000/static/admin.html

---

## 👤 Interface Client

### 1. Page "Commander"

#### Étape 1: Sélectionner les pizzas

1. **Naviguer dans le menu**: Voir les 6 pizzas disponibles
2. **Pour chaque pizza**:
   - Lire la liste des toppings inclus
   - Cliquer sur la taille désirée (S/M/L)
   - La pizza s'ajoute au panier

#### Étape 2: Vérifier le panier

À droite de l'écran:
- **Liste des pizzas**: Voir tous les articles avec prix
- **Sous-total**: Somme des pizzas
- **Frais de livraison**: 5€ ou GRATUIT (si ≥ 30€)
- **Total**: Prix final
- **Bouton ×**: Supprimer une pizza du panier

#### Étape 3: Remplir les informations

- **Nom**: Votre nom complet
- **Numéro de rue**: Ex: "22"
- **Nom de la rue**: Ex: "Rue Alsace-Lorraine"
- **Code postal**: Doit être "31000"
- **Ville**: Doit être "Toulouse"

#### Étape 4: Valider

- Cliquer sur **"Valider la commande"**
- Attendre la confirmation
- Redirection automatique vers le suivi

### 2. Page "Suivi de Commande"

#### Rechercher une commande

1. Entrer le **numéro de commande** (donné à la validation)
2. Cliquer **"Rechercher"** (ou Entrée)

#### Voir le statut

Affichage de:
- **Barre de progression**: Visuelle du statut (0%, 25%, 50%, 75%, 100%)
- **Label de statut**: Texte décrivant le statut actuel
- **Détails**: Adresse, prix, temps estimé
- **Pizzas commandées**: Liste complète
- **Timestamps**: Heure de création, début préparation, fin préparation, livraison

#### Statuts Possibles

| Statut | Couleur | Progression | Description |
|--------|---------|-------------|-------------|
| En attente | Gris | 0% | Commande reçue |
| En préparation | Orange | 25% | Pizzas en cours de préparation |
| Prête | Bleu | 50% | Pizzas prêtes, attente livraison |
| En livraison | Orange | 75% | Pizzas en route |
| Livrée | Vert | 100% | Commande reçue |

---

## 👨‍🍳 Interface Admin/Vendeur

### Dashboard Principal

#### En-tête

- **Nombre total de commandes**: Affichage en gros numéro
- **Bouton Actualiser**: Force le rechargement (auto-rafraîchit aussi tous les 5s)

#### Onglets par Statut

5 onglets pour filtrer les commandes:

1. **En attente** (Pending)
   - Nouvelles commandes attendant confirmation
   - Action: "Commencer la préparation"

2. **Préparation** (Preparing)
   - Commandes actuellement en cours de préparation
   - Action: "Marquer prête"

3. **Prête** (Ready for Delivery)
   - Pizzas terminées, attente du livreur
   - Action: "Envoyer en livraison"

4. **En livraison** (In Delivery)
   - Pizzas actuellement en route
   - Action: "Confirmer livraison"

5. **Livrées** (Delivered)
   - Commandes complétées
   - Actions: Aucune (affichage seul)

#### Carte de Commande

Pour chaque commande affichée:

```
┌─────────────────────────────────────┐
│ Commande #1              ✓ Statut   │
│ 👤 Jean Dupont                      │
├─────────────────────────────────────┤
│ Adresse: 22 Rue Alsace-Lorraine...  │
│ Total: 42.50€                       │
│ Temps estimé: 35 min                │
│ Créée à: 14:30:45                   │
├─────────────────────────────────────┤
│ Pizzas:                             │
│ • Margherita (medium) - 10.50€      │
│   Toppings: tomate, mozzarella...   │
│ • Reine (large) - 15.80€            │
│   Toppings: tomate, mozzarella...   │
├─────────────────────────────────────┤
│ [ ✓ Action suivante ]               │
└─────────────────────────────────────┘
```

### Workflow Admin

#### Étape 1: Nouvelle Commande (En Attente)
- Onglet "En attente" affiche les commandes
- Vérifier les pizzas et adresse
- **Cliquer**: "✓ Commencer la préparation"

#### Étape 2: En Préparation
- Onglet "Préparation" affiche les commandes
- Préparer les pizzas
- **Cliquer**: "✓ Marquer prête" quand terminé

#### Étape 3: Prête
- Onglet "Prête" affiche les commandes
- Attendre le livreur
- **Cliquer**: "✓ Envoyer en livraison" quand parti

#### Étape 4: En Livraison
- Onglet "En livraison" affiche les commandes
- Suivi de la livraison
- **Cliquer**: "✓ Confirmer livraison" à la réception

#### Étape 5: Livrée
- Onglet "Livrées" affiche les commandes complétées
- Archivage automatique

### Indicateurs et Compteurs

Chaque onglet affiche:
- **Nombre de commandes** en petit compteur à côté
- **Nom du vendeur** associé (optionnel)
- **Temps écoulé** depuis la création

### Notifications

- **Alerte succès** (verte): Opération réussie
- **Alerte erreur** (rouge): Problème lors de l'opération
- Les alertes disparaissent après 4 secondes

---

## 🔄 Exemple de Workflow Complet

### Scénario: Jean commande 2 pizzas

#### CÔTÉ CLIENT
1. Va sur **Client**
2. Sélectionne **Margherita (Medium)**
3. Sélectionne **Reine (Large)**
4. Entre ses infos: "Jean Dupont", "22", "Rue Alsace-Lorraine"
5. Clique **"Valider"**
6. Reçoit confirmation: **"Commande #5"**
7. Basculé vers suivi
8. Voit **Barre à 0%** "En attente de confirmation"

#### CÔTÉ ADMIN
1. Va sur **Admin**
2. Voir **"En attente: 1"**
3. Onglet "En attente" montre:
   - Commande #5 - Jean Dupont
   - 2 pizzas (Margherita medium + Reine large)
   - Total: 42.50€
4. Clique **"✓ Commencer la préparation"**
5. Commande passe à **"Préparation: 1"**

#### CÔTÉ CLIENT (Suivi)
- Actualise la page
- Voit **Barre à 25%** "En cours de préparation"
- Voit l'heure de début

#### CÔTÉ ADMIN
1. Prépare les pizzas (15-20 min simul.)
2. Onglet "Préparation" toujours montre Commande #5
3. Clique **"✓ Marquer prête"**
4. Commande passe à **"Prête: 1"**

#### CÔTÉ CLIENT (Suivi)
- Voit **Barre à 50%** "Prête pour livraison"
- Voit l'heure de fin de préparation

#### CÔTÉ ADMIN
1. Livreur arrive
2. Onglet "Prête" montre Commande #5
3. Clique **"✓ Envoyer en livraison"**
4. Commande passe à **"En livraison: 1"**

#### CÔTÉ CLIENT (Suivi)
- Voit **Barre à 75%** "En cours de livraison"

#### CÔTÉ ADMIN
1. Livreur livre (5-15 min simul.)
2. Onglet "En livraison" montre Commande #5
3. Clique **"✓ Confirmer livraison"**
4. Commande passe à **"Livrées: 1"**

#### CÔTÉ CLIENT (Suivi)
- Voit **Barre à 100%** "Livrée" (Vert)
- Voit l'heure de livraison
- Commande archivée

---

## ⚙️ Simulation des Temps

L'application simule automatiquement:

- **Temps de préparation**: 15-20 minutes
  - Basé sur l'ID de commande
  - Incrémenté pour chaque nouvelle commande

- **Temps de livraison**: 5-15 minutes
  - Basé sur le hash de l'adresse
  - Varie selon la rue

- **Temps total estimé**: Somme des deux
  - Affichée au client
  - Mis à jour en temps réel

---

## 🎯 Tips & Tricks

### Pour les Clients

1. **Panier vide?** Sélectionnez d'abord la taille des pizzas
2. **Livraison gratuite?** Commandez pour plus de 30€
3. **Adresse invalide?** Vérifiez que c'est une vraie rue de Toulouse (31000)
4. **Suivi?** Gardez votre numéro de commande!

### Pour les Vendeurs

1. **Auto-refresh** met à jour toutes les 5 secondes
2. **Cliquez le bouton** vert pour avancer la commande
3. **Compteurs** montrent combien en attente
4. **Détails complets** dans chaque carte
5. **Priorisez** les commandes "En attente" d'abord

---

## 🚨 Cas d'Erreur Possibles

| Erreur | Cause | Solution |
|--------|-------|----------|
| "Commande non trouvée" | Mauvais numéro | Vérifiez le numéro |
| "Rupture de stock" | Ingrédients épuisés | Admin ajoute du stock |
| "Adresse invalide" | Pas une vraie rue | Utilisez une rue de Toulouse |
| "Code postal invalide" | Doit être 31000 | Entrez 31000 |
| "Impossible de se connecter" | Serveur arrêté | Lancez `uvicorn main:app --reload` |

---

## 📞 Support

Pour tester l'API directement:
- **Documentation interactive**: http://localhost:8000/docs
- **Tests automatisés**: `python -m pytest test_*.py`
- **Workflow complet**: `python test_workflow.py`
