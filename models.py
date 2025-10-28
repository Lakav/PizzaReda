from typing import List, Optional, Dict
from pydantic import BaseModel, Field, model_validator, field_validator
import requests
from typing import Tuple


class Price:
    """Classe pour gérer la logique de tarification"""
    DELIVERY_FEE = 5.0
    FREE_DELIVERY_THRESHOLD = 30.0

    # Pizzas valides disponibles au menu
    VALID_PIZZAS = [
        "margherita",
        "reine",
        "4 fromages",
        "calzone",
        "végétarienne",
        "pepperoni",
    ]

    # Alias pour les noms de pizzas
    PIZZA_ALIASES = {
        "vegetarienne": "végétarienne",  # Sans accent
        "reina": "reine",  # Variante
    }

    # Prix de base des pizzas (medium)
    BASE_PRICES = {
        "margherita": 8.0,
        "reine": 10.0,
        "4 fromages": 11.0,
        "calzone": 12.0,
        "végétarienne": 9.0,
        "vegetarienne": 9.0,  # Sans accent
        "pepperoni": 10.5,
        "reina": 10.0,  # Alias pour reine
    }

    # Multiplicateurs selon la taille
    SIZE_MULTIPLIERS = {
        "small": 0.8,
        "medium": 1.0,
        "large": 1.3,
    }

    # Prix adaptés pour chaque topping (supplémentaire)
    TOPPING_PRICES = {
        "tomate": 0.5,
        "mozzarella": 0.8,
        "basilic": 0.3,
        "jambon": 1.2,
        "champignons": 0.7,
        "gorgonzola": 1.5,
        "chèvre": 1.3,
        "emmental": 1.0,
        "pepperoni": 1.5,
        "poivrons": 0.6,
        "oignons": 0.4,
        "olives": 0.9,
        "oeuf": 0.8,
        "bacon": 1.4,
        "poulet": 2.0,
        "ananas": 1.2,
    }

    # Toppings de base inclus par pizza
    BASE_TOPPINGS = {
        "margherita": ["tomate", "mozzarella", "basilic"],
        "reine": ["tomate", "mozzarella", "jambon", "champignons"],
        "reina": ["tomate", "mozzarella", "jambon", "champignons"],
        "4 fromages": ["mozzarella", "gorgonzola", "chèvre", "emmental"],
        "calzone": ["tomate", "mozzarella", "jambon", "oeuf"],
        "végétarienne": ["tomate", "mozzarella", "poivrons", "oignons", "olives"],
        "vegetarienne": ["tomate", "mozzarella", "poivrons", "oignons", "olives"],
        "pepperoni": ["tomate", "mozzarella", "pepperoni"],
    }

    @staticmethod
    def calculate_pizza_price(name: str, size: str, toppings: List[str]) -> float:
        """
        Calcule le prix d'une pizza selon son nom, sa taille et ses toppings
        """
        name_lower = name.lower()

        # Prix de base (pour une pizza inconnue, prix par défaut)
        base_price = Price.BASE_PRICES.get(name_lower, 10.0)

        # Multiplicateur de taille
        size_multiplier = Price.SIZE_MULTIPLIERS.get(size.lower(), 1.0)

        # Calculer le prix avec la taille
        price_with_size = base_price * size_multiplier

        # Toppings de base pour cette pizza
        base_toppings = Price.BASE_TOPPINGS.get(name_lower, [])

        # Calculer le prix des toppings supplémentaires avec prix adaptés
        extra_toppings_price = 0.0
        for topping in toppings:
            topping_lower = topping.lower()
            # Si le topping n'est pas dans les toppings de base, le compter comme supplémentaire
            if topping_lower not in [bt.lower() for bt in base_toppings]:
                # Utiliser le prix du topping s'il existe, sinon 1€ par défaut
                extra_toppings_price += Price.TOPPING_PRICES.get(topping_lower, 1.0)

        # Prix final
        final_price = price_with_size + extra_toppings_price

        return round(final_price, 2)

    @staticmethod
    def calculate_delivery_fee(subtotal: float) -> float:
        """
        Calcule les frais de livraison
        Gratuit à partir de 30€, sinon 5€
        """
        if subtotal >= Price.FREE_DELIVERY_THRESHOLD:
            return 0.0
        return Price.DELIVERY_FEE

    @staticmethod
    def calculate_total(subtotal: float) -> float:
        """Calcule le total avec frais de livraison"""
        delivery_fee = Price.calculate_delivery_fee(subtotal)
        return subtotal + delivery_fee


class Address(BaseModel):
    """Classe pour représenter et valider une adresse à Toulouse"""
    street_number: str = Field(..., description="Numéro de rue")
    street: str = Field(..., description="Nom de la rue")
    city: str = Field(..., description="Ville (doit être Toulouse)")
    postal_code: str = Field(..., description="Code postal (doit être 31000)")

    @field_validator("city")
    @classmethod
    def validate_city(cls, v: str) -> str:
        """Valide que la ville est Toulouse"""
        if v.lower() != "toulouse":
            raise ValueError("La ville doit être Toulouse")
        return v

    @field_validator("postal_code")
    @classmethod
    def validate_postal_code(cls, v: str) -> str:
        """Valide que le code postal est 31000"""
        if v != "31000":
            raise ValueError("Le code postal doit être 31000 (Toulouse)")
        return v

    @model_validator(mode="after")
    def validate_address_exists(self) -> "Address":
        """Valide que l'adresse existe réellement à Toulouse via Nominatim"""
        # Construire l'adresse pour la requête
        full_address = f"{self.street_number} {self.street}, {self.postal_code} {self.city}, France"

        try:
            # Utiliser l'API Nominatim (OpenStreetMap) pour valider l'adresse
            response = requests.get(
                "https://nominatim.openstreetmap.org/search",
                params={
                    "q": full_address,
                    "format": "json",
                    "limit": 5,  # Chercher les 5 meilleurs résultats
                    "extratags": 1
                },
                headers={"User-Agent": "PizzaOrderingAPI/1.0"},
                timeout=5
            )

            if response.status_code != 200:
                raise ValueError("Impossible de valider l'adresse avec le service de géocodage")

            results = response.json()

            # Vérifier que au moins un résultat existe
            if not results:
                raise ValueError(f"L'adresse '{full_address}' n'existe pas ou n'a pas pu être trouvée à Toulouse")

            # Chercher un résultat qui est une vraie adresse à Toulouse
            valid_result = None
            street_lower = self.street.lower()

            for result in results:
                result_type = result.get("type", "")
                result_class = result.get("class", "")
                display_name = result.get("display_name", "").lower()

                # Vérifier les coordonnées (Toulouse est environ 43.6°N, 1.4°E)
                lat = float(result.get("lat", 0))
                lon = float(result.get("lon", 0))

                # Vérifier que c'est bien à Toulouse (marge de ~20km)
                if not (43.3 < lat < 43.9 and 0.9 < lon < 1.9):
                    continue

                # Rejeter les résultats qui sont juste des limites administratives
                if result_type in ["county", "state", "country"] or result_class == "boundary":
                    continue

                # Vérifier que la rue est dans le résultat
                # (on utilise startswith car Nominatim peut ajouter des caractères comme d'Alsace-Lorraine)
                street_name = self.street.split()[0].lower()  # Premier mot du nom de rue
                if street_name in display_name or street_lower in display_name or \
                   display_name.find(street_name) != -1:
                    # Accepter ce résultat si c'est clairement une adresse
                    if result_type in ["house", "residential", "road", "address"]:
                        valid_result = result
                        break
                    # Sinon, accepter le premier résultat valide à Toulouse avec la rue
                    if not valid_result:
                        valid_result = result

            if not valid_result:
                # Aucun résultat valide trouvé
                raise ValueError(
                    f"L'adresse '{full_address}' n'existe pas à Toulouse. "
                    f"Vérifiez que la rue existe réellement."
                )

            return self

        except requests.RequestException as e:
            raise ValueError(f"Erreur lors de la validation de l'adresse: {str(e)}")

    def __str__(self) -> str:
        """Retourne l'adresse formatée"""
        return f"{self.street_number} {self.street}, {self.postal_code} {self.city}"


class PizzaCreate(BaseModel):
    """Classe pour créer une pizza (sans prix - calculé automatiquement)"""
    model_config = {"extra": "forbid"}  # Interdit les champs supplémentaires comme "price"

    name: str = Field(..., description="Nom de la pizza")
    size: str = Field(..., description="Taille: small, medium, large")
    toppings: List[str] = Field(default_factory=list, description="Liste des garnitures")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Valide que le nom de la pizza est dans le menu"""
        name_lower = v.lower()

        # Vérifier si c'est un alias
        if name_lower in Price.PIZZA_ALIASES:
            name_lower = Price.PIZZA_ALIASES[name_lower]

        # Vérifier si c'est une pizza valide
        if name_lower not in Price.VALID_PIZZAS:
            valid_pizzas_str = ", ".join(Price.VALID_PIZZAS)
            raise ValueError(f"La pizza doit être l'une de: {valid_pizzas_str}")

        return v

    @field_validator("size")
    @classmethod
    def validate_size(cls, v: str) -> str:
        """Valide que la taille est small, medium ou large"""
        valid_sizes = ["small", "medium", "large"]
        if v.lower() not in valid_sizes:
            raise ValueError(f"La taille doit être: {', '.join(valid_sizes)}")
        return v.lower()


class Pizza(BaseModel):
    """Classe représentant une pizza commandée avec son prix et ses toppings"""
    name: str = Field(..., description="Nom de la pizza")
    size: str = Field(..., description="Taille: small, medium, large")
    toppings: List[str] = Field(default_factory=list, description="Liste des garnitures")
    price: float = Field(..., description="Prix calculé automatiquement")

    @staticmethod
    def from_create(pizza_create: PizzaCreate) -> "Pizza":
        """Crée une Pizza à partir d'un PizzaCreate avec calcul automatique du prix"""
        calculated_price = Price.calculate_pizza_price(
            pizza_create.name,
            pizza_create.size,
            pizza_create.toppings
        )
        return Pizza(
            name=pizza_create.name,
            size=pizza_create.size,
            toppings=pizza_create.toppings,
            price=calculated_price
        )

    def __str__(self):
        return f"{self.name} ({self.size}) - {self.price}€"


class PizzaMenuPrice(BaseModel):
    """Classe pour afficher les prix d'une pizza pour chaque taille"""
    name: str = Field(..., description="Nom de la pizza")
    base_toppings: List[str] = Field(..., description="Toppings inclus de base")
    prices: dict = Field(..., description="Prix par taille: {'small': X, 'medium': Y, 'large': Z}")

    def __str__(self):
        return f"{self.name}: small={self.prices['small']}€, medium={self.prices['medium']}€, large={self.prices['large']}€"


class OrderCreate(BaseModel):
    """Classe pour créer une nouvelle commande"""
    pizzas: List[PizzaCreate] = Field(..., description="Liste des pizzas commandées")
    customer_name: str = Field(..., description="Nom du client")
    customer_address: Address = Field(..., description="Adresse de livraison (rue, numéro, ville, code postal)")


class Order(BaseModel):
    """Classe représentant une commande"""
    order_id: int = Field(..., description="Identifiant de la commande")
    pizzas: List[Pizza] = Field(..., description="Liste des pizzas commandées")
    customer_name: str = Field(..., description="Nom du client")
    customer_address: Address = Field(..., description="Adresse de livraison")

    def calculate_subtotal(self) -> float:
        """Calcule le sous-total (prix des pizzas uniquement)"""
        return sum(pizza.price for pizza in self.pizzas)

    def calculate_delivery_fee(self) -> float:
        """Calcule les frais de livraison"""
        subtotal = self.calculate_subtotal()
        return Price.calculate_delivery_fee(subtotal)

    def calculate_total(self) -> float:
        """Calcule le total de la commande"""
        subtotal = self.calculate_subtotal()
        return Price.calculate_total(subtotal)

    def get_summary(self) -> dict:
        """Retourne un résumé de la commande avec détail des pizzas et toppings"""
        subtotal = self.calculate_subtotal()
        delivery_fee = self.calculate_delivery_fee()
        total = self.calculate_total()

        # Formater les pizzas avec détails
        pizzas_detail = []
        for pizza in self.pizzas:
            pizzas_detail.append({
                "name": pizza.name,
                "size": pizza.size,
                "toppings": pizza.toppings,
                "price": round(pizza.price, 2)
            })

        return {
            "order_id": self.order_id,
            "customer_name": self.customer_name,
            "customer_address": str(self.customer_address),
            "pizzas": pizzas_detail,
            "subtotal": round(subtotal, 2),
            "delivery_fee": round(delivery_fee, 2),
            "is_delivery_free": delivery_fee == 0,
            "total": round(total, 2)
        }


# ====================
# GESTION DU STOCK
# ====================

class Topping(BaseModel):
    """Classe représentant un topping disponible avec son prix"""
    name: str = Field(..., description="Nom du topping")
    price: float = Field(1.0, description="Prix du topping supplémentaire")

    def __str__(self) -> str:
        return f"{self.name} (+{self.price}€)"


class Ingredient(BaseModel):
    """Classe représentant un ingrédient en stock"""
    name: str = Field(..., description="Nom de l'ingrédient")
    quantity: int = Field(..., ge=0, description="Quantité en stock")
    is_base_ingredient: bool = Field(False, description="True si c'est un ingrédient de base (pâte, etc.)")

    def __str__(self) -> str:
        ingredient_type = "Base" if self.is_base_ingredient else "Topping"
        return f"{self.name}: {self.quantity} ({ingredient_type})"


class InventoryManager:
    """Classe pour gérer l'inventaire des ingrédients (pas de stock par pizza)"""

    # Liste de tous les ingrédients disponibles avec stock initial
    AVAILABLE_INGREDIENTS = {
        "pate": 200,  # La base de chaque pizza
        "tomate": 100,
        "mozzarella": 100,
        "basilic": 80,
        "jambon": 60,
        "champignons": 50,
        "gorgonzola": 40,
        "chèvre": 45,
        "emmental": 50,
        "pepperoni": 70,
        "poivrons": 60,
        "oignons": 80,
        "olives": 70,
        "oeuf": 50,
        "bacon": 55,
        "poulet": 65,
        "ananas": 40,
    }

    def __init__(self):
        """Initialise l'inventaire des ingrédients"""
        self.ingredients: Dict[str, int] = self.AVAILABLE_INGREDIENTS.copy()

    def get_ingredient_stock(self, ingredient: str) -> int:
        """Retourne le stock d'un ingrédient"""
        return self.ingredients.get(ingredient.lower(), 0)

    def is_ingredient_available(self, ingredient: str, quantity: int = 1) -> bool:
        """Vérifie si un ingrédient est disponible en quantité suffisante"""
        return self.get_ingredient_stock(ingredient) >= quantity

    def can_fulfill_order(self, pizzas: List[PizzaCreate]) -> tuple[bool, Optional[str]]:
        """
        Vérifie si une commande peut être satisfaite en vérifiant les ingrédients
        Retourne (can_fulfill, error_message)
        """
        for pizza in pizzas:
            # Chaque pizza a besoin d'une pâte
            if not self.is_ingredient_available("pate"):
                return False, "La pâte est en rupture de stock"

            # Vérifier les ingrédients de la pizza (tous les toppings = ingrédients)
            for topping in pizza.toppings:
                if not self.is_ingredient_available(topping):
                    return False, f"L'ingrédient '{topping}' est en rupture de stock"

        return True, None

    def reduce_inventory(self, pizzas: List[Pizza]) -> None:
        """
        Réduit l'inventaire des ingrédients après une commande confirmée.
        Chaque pizza consomme sa pâte et ses ingrédients.
        """
        for pizza in pizzas:
            # Réduire la pâte (chaque pizza en consomme une)
            if "pate" in self.ingredients:
                self.ingredients["pate"] -= 1

            # Réduire chaque ingrédient de la pizza
            for ingredient in pizza.toppings:
                ingredient_lower = ingredient.lower()
                if ingredient_lower in self.ingredients:
                    self.ingredients[ingredient_lower] -= 1

    def add_ingredient_stock(self, ingredient_name: str, quantity: int) -> bool:
        """Ajoute du stock à un ingrédient"""
        ingredient_name_lower = ingredient_name.lower()
        if ingredient_name_lower not in self.ingredients:
            return False
        self.ingredients[ingredient_name_lower] += quantity
        return True

    def get_all_toppings(self) -> List[Topping]:
        """Retourne la liste de tous les toppings disponibles avec leur prix (+1€)"""
        # Les toppings ont tous le même prix: 1€ supplémentaire
        return [
            Topping(name=name, price=1.0)
            for name in sorted(self.ingredients.keys())
        ]

    def get_full_inventory(self) -> dict:
        """
        Retourne l'inventaire complet avec tous les ingrédients et toppings
        Format: {
            "base_ingredients": [...],
            "toppings": [...],
            "total_quantity": int
        }
        """
        base_ingredients = ["pate"]  # Ingrédients considérés comme "base"

        base_items = []
        topping_items = []

        for name in sorted(self.ingredients.keys()):
            quantity = self.ingredients[name]
            is_base = name in base_ingredients

            item = Ingredient(
                name=name,
                quantity=quantity,
                is_base_ingredient=is_base
            )

            if is_base:
                base_items.append(item)
            else:
                topping_items.append(item)

        return {
            "base_ingredients": base_items,
            "toppings": topping_items,
            "total_quantity": sum(self.ingredients.values())
        }
