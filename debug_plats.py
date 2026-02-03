#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_management.settings')
django.setup()

from apps.menu.models import Plat

print("=== Analyse des plats problématiques ===")

try:
    print("\n--- Plat ID 2 ---")
    plat2 = Plat.objects.get(id=2)
    print(f"Nom: {plat2.nom}")
    print(f"Image: {plat2.image}")
    print(f"Image name: {plat2.image.name if plat2.image else 'None'}")
    print(f"Image size: {plat2.image.size if plat2.image else 'None'}")
    print(f"Catégorie: {plat2.categorie}")
    print(f"Disponible: {plat2.disponible}")
    print(f"Created: {plat2.created_at}")
    print(f"Updated: {plat2.updated_at}")
    
    print("\n--- Plat ID 3 ---")
    plat3 = Plat.objects.get(id=3)
    print(f"Nom: {plat3.nom}")
    print(f"Image: {plat3.image}")
    print(f"Image name: {plat3.image.name if plat3.image else 'None'}")
    print(f"Image size: {plat3.image.size if plat3.image else 'None'}")
    print(f"Catégorie: {plat3.categorie}")
    print(f"Disponible: {plat3.disponible}")
    print(f"Created: {plat3.created_at}")
    print(f"Updated: {plat3.updated_at}")
    
    print("\n=== Test d'accès aux images ===")
    try:
        if plat2.image:
            print(f"Plat 2 - Image URL: {plat2.image.url}")
        else:
            print("Plat 2 - Pas d'image")
    except Exception as e:
        print(f"Plat 2 - Erreur accès image: {e}")
    
    try:
        if plat3.image:
            print(f"Plat 3 - Image URL: {plat3.image.url}")
        else:
            print("Plat 3 - Pas d'image")
    except Exception as e:
        print(f"Plat 3 - Erreur accès image: {e}")

except Exception as e:
    print(f"Erreur générale: {e}")
    import traceback
    traceback.print_exc()
