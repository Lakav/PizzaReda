"""
Configuration pour pytest - ajoute src au chemin Python
"""
import sys
from pathlib import Path

# Ajouter le dossier src ET la racine au chemin Python
project_root = Path(__file__).parent.parent
src_path = project_root / "src"

for path in [str(project_root), str(src_path)]:
    if path not in sys.path:
        sys.path.insert(0, path)
