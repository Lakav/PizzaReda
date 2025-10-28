@echo off
REM Script pour lancer les tests de l'API Pizza (Windows)

echo.
echo 🍕 API de Livraison de Pizza - Tests 🍕
echo ========================================
echo.

REM Vérifier que pytest est installé
python -m pytest --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pytest n'est pas installé
    echo 📦 Installation des dépendances...
    pip install -r requirements.txt
    echo.
)

REM Lancer les tests
echo 🧪 Lancement des tests...
echo.

python -m pytest -v --tb=short

REM Afficher le résultat
if %errorlevel% equ 0 (
    echo.
    echo ✅ Tous les tests sont passés avec succès!
) else (
    echo.
    echo ❌ Certains tests ont échoué
    exit /b 1
)
