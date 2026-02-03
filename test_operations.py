#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_management.settings')
django.setup()

from apps.menu.models import Plat
from apps.menu.forms import PlatForm
from django.core.files.uploadedfile import SimpleUploadedFile
import io

print("=== Test des opérations CRUD ===")

try:
    # Test modification plat 2
    print("\n--- Test modification Plat 2 ---")
    plat2 = Plat.objects.get(id=2)
    print(f"Plat 2 avant: {plat2.nom}, prix: {plat2.prix_unitaire}")
    
    # Simuler une modification sans image
    data = {
        'nom': 'pizza modifiée',
        'categorie': plat2.categorie.id if plat2.categorie else None,
        'description': 'Test description',
        'prix_unitaire': '12000.00',
        'disponible': True
    }
    
    form = PlatForm(data, instance=plat2)
    if form.is_valid():
        try:
            plat2_modifie = form.save()
            print(f"✓ Modification réussie: {plat2_modifie.nom}")
        except Exception as e:
            print(f"✗ Erreur modification: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"✗ Formulaire invalide: {form.errors}")
    
    # Test modification plat 3
    print("\n--- Test modification Plat 3 ---")
    plat3 = Plat.objects.get(id=3)
    print(f"Plat 3 avant: {plat3.nom}, prix: {plat3.prix_unitaire}")
    
    data = {
        'nom': 'chawarma modifié',
        'categorie': plat3.categorie.id if plat3.categorie else None,
        'description': 'Test description chawarma',
        'prix_unitaire': '15000.00',
        'disponible': True
    }
    
    form = PlatForm(data, instance=plat3)
    if form.is_valid():
        try:
            plat3_modifie = form.save()
            print(f"✓ Modification réussie: {plat3_modifie.nom}")
        except Exception as e:
            print(f"✗ Erreur modification: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"✗ Formulaire invalide: {form.errors}")
    
    # Test suppression plat 2
    print("\n--- Test suppression Plat 2 ---")
    try:
        plat2.delete()
        print("✓ Suppression plat 2 réussie")
    except Exception as e:
        print(f"✗ Erreur suppression plat 2: {e}")
        import traceback
        traceback.print_exc()

except Exception as e:
    print(f"Erreur générale: {e}")
    import traceback
    traceback.print_exc()
