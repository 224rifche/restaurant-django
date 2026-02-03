#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_management.settings')
django.setup()

from apps.menu.models import CategoriePlat
from django.db import connection

print("=== Diagnostic et réparation de la catégorie 6 ===")

try:
    # 1. Examiner la catégorie 6
    print("\n1. Examen de la catégorie 6 :")
    cat6 = CategoriePlat.objects.get(id=6)
    print(f"   ID: {cat6.id}")
    print(f"   Nom: {cat6.nom}")
    print(f"   Ordre: {cat6.ordre}")
    print(f"   Type de ordre: {type(cat6.ordre)}")
    
    # 2. Vérifier les plats associés
    print("\n2. Plats associés à cette catégorie :")
    from apps.menu.models import Plat
    plats_associes = Plat.objects.filter(categorie=cat6)
    for plat in plats_associes:
        print(f"   - Plat {plat.id}: {plat.nom} (ordre: {plat.categorie.ordre if plat.categorie else 'None'})")
    
    # 3. Vérifier directement dans la base de données
    print("\n3. Vérification SQL directe :")
    with connection.cursor() as cursor:
        cursor.execute("SELECT id, nom, ordre FROM categories_plats WHERE id = 6")
        row = cursor.fetchone()
        if row:
            print(f"   SQL: ID={row[0]}, Nom='{row[1]}', Ordre={row[2]} (type: {type(row[2])})")
        
        # Chercher des valeurs anormales
        cursor.execute("SELECT id, nom, ordre FROM categories_plats WHERE ordre REGEXP '[^0-9]'")
        weird_rows = cursor.fetchall()
        if weird_rows:
            print(f"\n   ⚠️  Catégories avec ordre non-numérique :")
            for row in weird_rows:
                print(f"      ID={row[0]}, Nom='{row[1]}', Ordre='{row[2]}'")
    
    # 4. Corriger le problème
    print("\n4. Correction du problème :")
    if isinstance(cat6.ordre, str):
        print(f"   ⚠️  L'ordre est une chaîne: '{cat6.ordre}'")
        try:
            # Essayer de convertir en nombre
            if cat6.ordre.isdigit():
                cat6.ordre = int(cat6.ordre)
                cat6.save()
                print(f"   ✅ Converti en nombre: {cat6.ordre}")
            else:
                # Si ce n'est pas un nombre, mettre une valeur par défaut
                cat6.ordre = 999
                cat6.save()
                print(f"   ✅ Remplacé par défaut: {cat6.ordre}")
        except Exception as e:
            print(f"   ❌ Erreur lors de la correction: {e}")
    else:
        print(f"   ✅ L'ordre est déjà un nombre: {cat6.ordre}")
    
    # 5. Tester la suppression
    print("\n5. Test de suppression :")
    try:
        nom = cat6.nom
        cat6.delete()
        print(f"   ✅ Suppression réussie de: {nom}")
    except Exception as e:
        print(f"   ❌ Erreur suppression: {e}")
        
        # Alternative: marquer comme non supprimable
        print(f"   💡 Alternative: Créer une nouvelle catégorie correcte et migrer")
        
except CategoriePlat.DoesNotExist:
    print("❌ La catégorie 6 n'existe pas")
except Exception as e:
    print(f"❌ Erreur générale: {e}")
    import traceback
    traceback.print_exc()

print("\n=== Recommandations ===")
print("1. Si la suppression échoue, créer une nouvelle catégorie")
print("2. Déplacer les plats vers la nouvelle catégorie")
print("3. Supprimer l'ancienne catégorie depuis la base de données directement")
