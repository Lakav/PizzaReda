from typing import List, Optional
from pydantic import BaseModel, Field, model_validator, field_validator
import requests
from typing import Tuple


class Price:
    """Classe pour gérer la logique de tarification"""
    DELIVERY_FEE = 5.0
    FREE_DELIVERY_THRESHOLD = 30.0

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

    # Prix par topping supplémentaire
    TOPPING_PRICE = 1.0

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

        # Compter les toppings supplémentaires
        extra_toppings = len([t for t in toppings if t.lower() not in [bt.lower() for bt in base_toppings]])

        # Prix final
        final_price = price_with_size + (extra_toppings * Price.TOPPING_PRICE)

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


class Pizza(BaseModel):
    """Classe représentant une pizza avec son prix"""
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
        """Retourne un résumé de la commande"""
        subtotal = self.calculate_subtotal()
        delivery_fee = self.calculate_delivery_fee()
        total = self.calculate_total()

        return {
            "order_id": self.order_id,
            "customer_name": self.customer_name,
            "customer_address": str(self.customer_address),
            "pizzas": [str(pizza) for pizza in self.pizzas],
            "subtotal": round(subtotal, 2),
            "delivery_fee": round(delivery_fee, 2),
            "is_delivery_free": delivery_fee == 0,
            "total": round(total, 2)
        }
