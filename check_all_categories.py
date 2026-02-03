#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_management.settings')
django.setup()

from apps.menu.models import CategoriePlat
from django.db import connection

print("=== Vérification de TOUTES les catégories ===")

# Vérifier toutes les catégories pour des problèmes similaires
print("\n1. Vérification des données anormales :")
with connection.cursor() as cursor:
    # Chercher toutes les catégories avec ordre non-numérique
    cursor.execute("SELECT id, nom, ordre FROM categories_plats WHERE ordre REGEXP '[^0-9]'")
    weird_rows = cursor.fetchall()
    
    if weird_rows:
        print(f"   ⚠️  Catégories avec ordre non-numérique ({len(weird_rows)}):")
        for row in weird_rows:
            print(f"      ID={row[0]}, Nom='{row[1]}', Ordre='{row[2]}'")
    else:
        print("   ✅ Toutes les catégories ont des ordres numériques")

# Vérifier les plats avec des catégories invalides
print("\n2. Vérification des plats avec catégories problématiques :")
from apps.menu.models import Plat
all_plats = Plat.objects.all()
problem_plats = []

for plat in all_plats:
    if plat.categorie:
        if not isinstance(plat.categorie.ordre, int):
            problem_plats.append(plat)

if problem_plats:
    print(f"   ⚠️  Plats avec catégories problématiques ({len(problem_plats)}):")
    for plat in problem_plats:
        print(f"      Plat {plat.id}: {plat.nom} -> Catégorie {plat.categorie.id} (ordre: {plat.categorie.ordre})")
else:
    print("   ✅ Tous les plats ont des catégories valides")

# Statistiques finales
print(f"\n3. Statistiques :")
print(f"   • Total catégories: {CategoriePlat.objects.count()}")
print(f"   • Total plats: {Plat.objects.count()}")
print(f"   • Plats sans catégorie: {Plat.objects.filter(categorie__isnull=True).count()}")

print("\n=== Recommandations ===")
if weird_rows:
    print("⚠️  CORRIGEZ les catégories avec ordre non-numérique AVANT déploiement!")
else:
    print("✅ Toutes les données semblent correctes - Déploiement sécurisé")
