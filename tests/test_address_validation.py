#!/usr/bin/env python3
"""
Script pour tester la validation des adresses
"""

from models import Address
import json

# Test 1: Adresse valide - Rue de Paris, Toulouse
print("=" * 60)
print("TEST 1: Adresse valide à Toulouse")
print("=" * 60)
try:
    address1 = Address(
        street_number="123",
        street="Rue de Paris",
        city="Toulouse",
        postal_code="31000"
    )
    print(f"✓ Adresse valide créée: {address1}")
except ValueError as e:
    print(f"✗ Erreur: {e}")

print()

# Test 2: Mauvaise ville
print("=" * 60)
print("TEST 2: Mauvaise ville (Paris au lieu de Toulouse)")
print("=" * 60)
try:
    address2 = Address(
        street_number="123",
        street="Rue de Paris",
        city="Paris",
        postal_code="31000"
    )
    print(f"✓ Adresse créée: {address2}")
except ValueError as e:
    print(f"✗ Erreur attendue: {e}")

print()

# Test 3: Mauvais code postal
print("=" * 60)
print("TEST 3: Mauvais code postal (75000 au lieu de 31000)")
print("=" * 60)
try:
    address3 = Address(
        street_number="123",
        street="Rue de Paris",
        city="Toulouse",
        postal_code="75000"
    )
    print(f"✓ Adresse créée: {address3}")
except ValueError as e:
    print(f"✗ Erreur attendue: {e}")

print()

# Test 4: Adresse qui n'existe pas
print("=" * 60)
print("TEST 4: Adresse inexistante à Toulouse")
print("=" * 60)
try:
    address4 = Address(
        street_number="99999",
        street="Rue Inexistante ZZZZZ",
        city="Toulouse",
        postal_code="31000"
    )
    print(f"✓ Adresse créée: {address4}")
except ValueError as e:
    print(f"✗ Erreur attendue: {e}")

print()

# Test 5: Une vraie adresse à Toulouse
print("=" * 60)
print("TEST 5: Une vraie adresse - Rue Alsace-Lorraine, Toulouse")
print("=" * 60)
try:
    address5 = Address(
        street_number="22",
        street="Rue Alsace-Lorraine",
        city="Toulouse",
        postal_code="31000"
    )
    print(f"✓ Adresse valide créée: {address5}")
except ValueError as e:
    print(f"✗ Erreur: {e}")

print()

# Test 6: Une autre vraie adresse à Toulouse
print("=" * 60)
print("TEST 6: Une vraie adresse - Allée Jean Jaurès, Toulouse")
print("=" * 60)
try:
    address6 = Address(
        street_number="8",
        street="Allée Jean Jaurès",
        city="Toulouse",
        postal_code="31000"
    )
    print(f"✓ Adresse valide créée: {address6}")
except ValueError as e:
    print(f"✗ Erreur: {e}")
