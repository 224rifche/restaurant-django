#!/usr/bin/env python
"""
Script pour diagnostiquer et corriger les problèmes de production
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'restaurant_management.settings')
django.setup()

from apps.menu.models import Plat
from apps.orders.models import PanierItem, CommandeItem

print("=== Diagnostic des problèmes de production ===")

# 1. Vérifier les plats avec références
print("\n1. Plats avec des références actives :")
plats_with_refs = []
for plat in Plat.objects.all():
    panier_count = PanierItem.objects.filter(plat=plat).count()
    commande_count = CommandeItem.objects.filter(plat=plat).count()
    if panier_count > 0 or commande_count > 0:
        plats_with_refs.append({
            'id': plat.id,
            'nom': plat.nom,
            'panier_count': panier_count,
            'commande_count': commande_count,
            'total_refs': panier_count + commande_count
        })

for plat_info in sorted(plats_with_refs, key=lambda x: x['total_refs'], reverse=True):
    print(f"  • Plat {plat_info['id']} ({plat_info['nom']}): "
          f"{plat_info['panier_count']} paniers, {plat_info['commande_count']} commandes")

# 2. Vérifier les plats avec des images S3 potentiellement problématiques
print("\n2. Vérification des images S3 :")
plats_with_images = Plat.objects.exclude(image='').exclude(image__isnull=True)
for plat in plats_with_images:
    try:
        if plat.image:
            image_url = plat.image.url
            print(f"  ✓ Plat {plat.id}: {image_url}")
    except Exception as e:
        print(f"  ✗ Plat {plat.id} ({plat.nom}): Erreur image - {e}")

# 3. Simuler les opérations qui échouent en production
print("\n3. Test des opérations problématiques :")

# Test plat 2 (suppression qui échoue en production)
try:
    plat2 = Plat.objects.get(id=2)
    panier_count = PanierItem.objects.filter(plat=plat2).count()
    commande_count = CommandeItem.objects.filter(plat=plat2).count()
    
    print(f"  Plat 2 ({plat2.nom}): {panier_count} paniers, {commande_count} commandes")
    
    if panier_count > 0 or commande_count > 0:
        print(f"  → Doit être marqué comme non disponible (pas supprimable)")
    else:
        print(f"  → Peut être supprimé")
        
except Plat.DoesNotExist:
    print("  Plat 2 n'existe pas")

# Test plat 3 (modification qui échoue en production)
try:
    plat3 = Plat.objects.get(id=3)
    print(f"  Plat 3 ({plat3.nom}): Test de modification...")
    
    # Simuler une modification simple
    original_nom = plat3.nom
    plat3.nom = f"{original_nom} (test)"
    try:
        plat3.save()
        print(f"  ✓ Modification réussie")
        plat3.nom = original_nom
        plat3.save()
    except Exception as e:
        print(f"  ✗ Erreur modification: {e}")
        
except Plat.DoesNotExist:
    print("  Plat 3 n'existe pas")

print("\n=== Recommandations ===")
print("1. Déployer la version mise à jour des vues avec gestion d'erreur")
print("2. Vérifier que USE_S3=True en production avec les bonnes credentials")
print("3. Ajouter le logging configuré pour capturer les erreurs détaillées")
print("4. Redémarrer le serveur de production après déploiement")
