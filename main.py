"""
Wrapper pour importer et exposer l'application FastAPI
Permet de lancer: uvicorn main:app --reload
"""
from src.main import app, orders_db, inventory

__all__ = ["app", "orders_db", "inventory"]
