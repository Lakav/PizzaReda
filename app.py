"""
Point d'entrée pour lancer l'application FastAPI
Lance le serveur directement depuis src.main
"""

if __name__ == "__main__":
    import uvicorn
    # Lancer directement depuis src.main
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
