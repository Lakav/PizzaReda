"""
Point d'entrée pour lancer l'application FastAPI
Importe le serveur depuis src.main et l'expose pour uvicorn
"""
import sys
from pathlib import Path

# Ajouter src au chemin Python
src_path = str(Path(__file__).parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
