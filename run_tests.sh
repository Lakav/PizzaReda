#!/bin/bash

# Script pour lancer les tests de l'API Pizza

echo "🍕 API de Livraison de Pizza - Tests 🍕"
echo "========================================"
echo ""

# Vérifier que pytest est installé
if ! command -v pytest &> /dev/null
then
    echo "❌ pytest n'est pas installé"
    echo "📦 Installation des dépendances..."
    pip install -r requirements.txt
    echo ""
fi

# Lancer les tests
echo "🧪 Lancement des tests..."
echo ""

pytest -v --tb=short

# Afficher le résultat
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Tous les tests sont passés avec succès!"
else
    echo ""
    echo "❌ Certains tests ont échoué"
    exit 1
fi
