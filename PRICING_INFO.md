# 💰 Système de Tarification Automatique

## Le prix n'est PLUS un choix du client !

Le système calcule automatiquement le prix de chaque pizza selon :
1. **Le type de pizza** (prix de base)
2. **La taille** (multiplicateur)
3. **Les toppings supplémentaires** (+1€ par topping extra)

## 📊 Prix de Base (taille medium)

| Pizza | Prix de base |
|-------|--------------|
| Margherita | 8.00€ |
| Reine | 10.00€ |
| 4 Fromages | 11.00€ |
| Calzone | 12.00€ |
| Végétarienne | 9.00€ |
| Pepperoni | 10.50€ |

## 📏 Multiplicateurs de Taille

| Taille | Multiplicateur | Exemple (Margherita) |
|--------|----------------|----------------------|
| Small | x0.8 | 8€ × 0.8 = **6.40€** |
| Medium | x1.0 | 8€ × 1.0 = **8.00€** |
| Large | x1.3 | 8€ × 1.3 = **10.40€** |

## 🍕 Toppings de Base Inclus

Chaque pizza a ses toppings de base **INCLUS** dans le prix :

- **Margherita** : tomate, mozzarella, basilic
- **Reine** : tomate, mozzarella, jambon, champignons
- **4 Fromages** : mozzarella, gorgonzola, chèvre, emmental
- **Calzone** : tomate, mozzarella, jambon, oeuf
- **Végétarienne** : tomate, mozzarella, poivrons, oignons, olives
- **Pepperoni** : tomate, mozzarella, pepperoni

## ➕ Toppings Supplémentaires

Chaque topping qui n'est **PAS** dans la liste de base coûte **+1.00€**

### Exemples :

```json
{
  "name": "Margherita",
  "size": "medium",
  "toppings": ["tomate", "mozzarella", "basilic"]
}
```
**Prix** : 8.00€ (prix de base, tous les toppings sont inclus)

---

```json
{
  "name": "Margherita",
  "size": "medium",
  "toppings": ["tomate", "mozzarella", "basilic", "olives"]
}
```
**Prix** : 9.00€ (8€ + 1€ pour les olives)

---

```json
{
  "name": "Reine",
  "size": "large",
  "toppings": ["tomate", "mozzarella", "jambon", "champignons", "olives", "poivrons"]
}
```
**Prix** : 15.00€
- Base Reine : 10€
- Taille large : × 1.3 = 13€
- Olives (extra) : +1€
- Poivrons (extra) : +1€
- **Total** : 15€

## 🚚 Frais de Livraison

- **Sous-total < 30€** → Frais : **5.00€**
- **Sous-total ≥ 30€** → Frais : **0.00€** (GRATUIT)

## 📝 Format de Commande

**AVANT (incorrect - ne fonctionne plus)** :
```json
{
  "pizzas": [
    {
      "name": "reina",
      "size": "medium",
      "price": 10,  ❌ NE PLUS METTRE LE PRIX !
      "toppings": ["banana"]
    }
  ],
  "customer_name": "bob",
  "customer_address": "l'enfer sur terre"
}
```

**MAINTENANT (correct)** :
```json
{
  "pizzas": [
    {
      "name": "reina",
      "size": "medium",
      "toppings": ["banana"]
    }
  ],
  "customer_name": "bob",
  "customer_address": "l'enfer sur terre"
}
```

**Résultat** :
```json
{
  "order_id": 1,
  "customer_name": "bob",
  "customer_address": "l'enfer sur terre",
  "pizzas": ["reina (medium) - 11.0€"],
  "subtotal": 11.0,
  "delivery_fee": 5.0,
  "is_delivery_free": false,
  "total": 16.0
}
```

**Calcul** :
- Reine medium = 10€
- Banana (topping extra) = +1€
- Sous-total = 11€
- Frais de livraison = 5€ (< 30€)
- **Total = 16€**

## 🎯 Exemple de Livraison Gratuite

```json
{
  "pizzas": [
    {
      "name": "Calzone",
      "size": "large",
      "toppings": ["tomate", "mozzarella", "jambon", "oeuf"]
    },
    {
      "name": "4 Fromages",
      "size": "large",
      "toppings": ["mozzarella", "gorgonzola", "chèvre", "emmental"]
    },
    {
      "name": "Margherita",
      "size": "small",
      "toppings": ["tomate", "mozzarella", "basilic"]
    }
  ],
  "customer_name": "Bob",
  "customer_address": "456 Avenue Test"
}
```

**Résultat** :
```json
{
  "order_id": 3,
  "customer_name": "Bob",
  "customer_address": "456 Avenue Test",
  "pizzas": [
    "Calzone (large) - 15.6€",
    "4 Fromages (large) - 14.3€",
    "Margherita (small) - 6.4€"
  ],
  "subtotal": 36.3,
  "delivery_fee": 0.0,
  "is_delivery_free": true,
  "total": 36.3
}
```

**Calcul** :
- Calzone large = 12€ × 1.3 = 15.6€
- 4 Fromages large = 11€ × 1.3 = 14.3€
- Margherita small = 8€ × 0.8 = 6.4€
- Sous-total = 36.3€
- Frais de livraison = **0€ (GRATUIT !)** ✅
- **Total = 36.3€**

## ⚙️ Implémentation Technique

Le calcul est géré dans `models.py` :

1. **Classe `Price`** : Contient toute la logique de tarification
   - `BASE_PRICES` : Prix de base des pizzas
   - `SIZE_MULTIPLIERS` : Multiplicateurs par taille
   - `BASE_TOPPINGS` : Toppings inclus par pizza
   - `calculate_pizza_price()` : Méthode de calcul

2. **Classe `Pizza`** :
   - Le champ `price` est **Optional**
   - Un `@model_validator` calcule automatiquement le prix si non fourni

3. **Tests** : 50 tests incluant les nouveaux tests de calcul de prix

## 🚀 Avantages

✅ Le client ne peut pas tricher sur le prix
✅ Prix cohérents et automatiques
✅ Facile d'ajouter de nouvelles pizzas
✅ Facile de changer les prix (un seul endroit)
✅ Logique métier centralisée dans la classe `Price`
