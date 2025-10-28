"""
Gestion de la persistance des données avec SQLite
"""
import sqlite3
import os
from typing import Dict
from .models import InventoryManager

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "inventory.db")


class SQLiteInventoryManager(InventoryManager):
    """InventoryManager avec persistance SQLite"""

    def __init__(self):
        """Initialise le gestionnaire d'inventaire avec SQLite"""
        super().__init__()
        self.db_path = DB_PATH
        self._init_db()
        self._load_from_db()

    def _init_db(self):
        """Crée la table SQLite si elle n'existe pas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ingredient TEXT UNIQUE NOT NULL,
                    quantity INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Erreur lors de l'initialisation de la base de données: {e}")

    def _load_from_db(self):
        """Charge l'inventaire depuis la base de données"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT ingredient, quantity FROM inventory")
            rows = cursor.fetchall()

            if rows:
                # Si la DB a des données, les charger
                self.ingredients = {row[0]: row[1] for row in rows}
                print(f"✅ Inventaire chargé de SQLite: {len(self.ingredients)} ingrédients")
            else:
                # Sinon, initialiser avec les valeurs par défaut et les sauvegarder
                self._save_to_db()

            conn.close()
        except sqlite3.Error as e:
            print(f"Erreur lors du chargement de la DB: {e}")
            # En cas d'erreur, utiliser les valeurs par défaut
            self._save_to_db()

    def _save_to_db(self):
        """Sauvegarde l'inventaire actuel dans la base de données"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Supprimer les anciennes données et réinsérer
            cursor.execute("DELETE FROM inventory")

            for ingredient, quantity in self.ingredients.items():
                cursor.execute(
                    """
                    INSERT INTO inventory (ingredient, quantity, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    """,
                    (ingredient, quantity),
                )

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Erreur lors de la sauvegarde en DB: {e}")

    def reduce_inventory(self, pizzas):
        """Réduit l'inventaire et sauvegarde en DB"""
        super().reduce_inventory(pizzas)
        self._save_to_db()

    def restore_inventory(self, pizzas):
        """Restaure l'inventaire et sauvegarde en DB"""
        super().restore_inventory(pizzas)
        self._save_to_db()

    def get_full_inventory(self) -> dict:
        """Retourne l'inventaire complet"""
        return {
            "ingredients": self.ingredients.copy(),
            "total_items": sum(self.ingredients.values()),
            "last_updated": None,  # Peut être amélioré avec la date de la DB
        }

    def reset_to_defaults(self):
        """Réinitialise l'inventaire aux valeurs par défaut"""
        self.ingredients = self.AVAILABLE_INGREDIENTS.copy()
        self._save_to_db()


def get_inventory_manager() -> SQLiteInventoryManager:
    """Retourne une instance du gestionnaire d'inventaire"""
    return SQLiteInventoryManager()
