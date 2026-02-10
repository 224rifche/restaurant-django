"""
Commandes à exécuter dans: python manage.py shell
Copiez-collez ces commandes une par une
"""

# 1. Importer les modèles
from apps.menu.models import CategoriePlat, Plat
from apps.tables.models import TableRestaurant
from apps.authentication.models import CustomUser

# 2. Créer les catégories
cat_entrees = CategoriePlat.objects.create(nom="Entrées")
cat_principaux = CategoriePlat.objects.create(nom="Plats principaux")
cat_desserts = CategoriePlat.objects.create(nom="Desserts")
cat_boissons = CategoriePlat.objects.create(nom="Boissons")
cat_poisson = CategoriePlat.objects.create(nom="Poisson")

print("✅ Catégories créées")

# 3. Créer les plats
Plat.objects.create(nom="Salade César", description="Salade fraîche avec poulet", prix_unitaire=8.50, categorie=cat_entrees)
Plat.objects.create(nom="Soupe du jour", description="Soupe maison", prix_unitaire=6.00, categorie=cat_entrees)
Plat.objects.create(nom="Steak frites", description="Steak grillé avec frites", prix_unitaire=15.00, categorie=cat_principaux)
Plat.objects.create(nom="Poulet rôti", description="Poulet rôti avec légumes", prix_unitaire=12.00, categorie=cat_principaux)
Plat.objects.create(nom="Saumon grillé", description="Saumon frais grillé", prix_unitaire=18.00, categorie=cat_poisson)
Plat.objects.create(nom="Tarte aux pommes", description="Tarte maison aux pommes", prix_unitaire=5.50, categorie=cat_desserts)
Plat.objects.create(nom="Crème brûlée", description="Crème brûlée traditionnelle", prix_unitaire=6.00, categorie=cat_desserts)
Plat.objects.create(nom="Coca-Cola", description="Soda classique", prix_unitaire=2.50, categorie=cat_boissons)
Plat.objects.create(nom="Jus d'orange", description="Jus frais", prix_unitaire=3.00, categorie=cat_boissons)

print("✅ Plats créés")

# 4. Créer les tables
for i in range(1, 11):
    TableRestaurant.objects.create(numero_table=str(i), nombre_places=4)

print("✅ Tables créées")

# 5. Créer les utilisateurs
admin = CustomUser.objects.create_user(username="admin", email="admin@restaurant.com", password="admin123", first_name="Admin", last_name="System", role="Radmin", is_staff=True, is_superuser=True)
serveur = CustomUser.objects.create_user(username="serveur", email="serveur@restaurant.com", password="serveur123", first_name="Serveur", last_name="Test", role="Rservent", is_staff=True)
caissier = CustomUser.objects.create_user(username="caissier", email="caissier@restaurant.com", password="caissier123", first_name="Caissier", last_name="Test", role="Rcaissier", is_staff=True)

print("✅ Utilisateurs créés")
print("\n🎉 Données créées avec succès!")
print("\n🔐 Identifiants:")
print("Admin: admin@restaurant.com / admin123")
print("Serveur: serveur@restaurant.com / serveur123") 
print("Caissier: caissier@restaurant.com / caissier123")
