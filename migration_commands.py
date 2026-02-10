"""
Migration simple pour PostgreSQL
Exécutez ces commandes une par une dans shell Django
"""

# Commandes à exécuter dans: python manage.py shell
"""
from apps.menu.models import CategoriePlat, Plat
from apps.tables.models import TableRestaurant
from apps.authentication.models import CustomUser

# Créer catégories
categories = [
    CategoriePlat.objects.create(nom="Entrées", description="Plats d'entrée"),
    CategoriePlat.objects.create(nom="Plats principaux", description="Plats principaux"),
    CategoriePlat.objects.create(nom="Desserts", description="Desserts et sucreries"),
    CategoriePlat.objects.create(nom="Boissons", description="Boissons diverses"),
    CategoriePlat.objects.create(nom="Poisson", description="Plats à base de poisson"),
]

# Créer plats
entrees = CategoriePlat.objects.get(nom="Entrées")
principaux = CategoriePlat.objects.get(nom="Plats principaux")
desserts = CategoriePlat.objects.get(nom="Desserts")
boissons = CategoriePlat.objects.get(nom="Boissons")
poisson = CategoriePlat.objects.get(nom="Poisson")

plats = [
    Plat.objects.create(nom="Salade César", description="Salade fraîche avec poulet", prix_unitaire=8.50, categorie=entrees),
    Plat.objects.create(nom="Soupe du jour", description="Soupe maison", prix_unitaire=6.00, categorie=entrees),
    Plat.objects.create(nom="Steak frites", description="Steak grillé avec frites", prix_unitaire=15.00, categorie=principaux),
    Plat.objects.create(nom="Poulet rôti", description="Poulet rôti avec légumes", prix_unitaire=12.00, categorie=principaux),
    Plat.objects.create(nom="Saumon grillé", description="Saumon frais grillé", prix_unitaire=18.00, categorie=poisson),
    Plat.objects.create(nom="Tarte aux pommes", description="Tarte maison aux pommes", prix_unitaire=5.50, categorie=desserts),
    Plat.objects.create(nom="Crème brûlée", description="Crème brûlée traditionnelle", prix_unitaire=6.00, categorie=desserts),
    Plat.objects.create(nom="Coca-Cola", description="Soda classique", prix_unitaire=2.50, categorie=boissons),
    Plat.objects.create(nom="Jus d'orange", description="Jus frais", prix_unitaire=3.00, categorie=boissons),
]

# Créer tables
for i in range(1, 11):
    TableRestaurant.objects.create(numero=i, capacite_max=4, statut="libre")

# Créer utilisateurs
admin = CustomUser.objects.create_user(username="admin", email="admin@restaurant.com", password="admin123", first_name="Admin", last_name="System", role="Radmin", is_staff=True, is_superuser=True)
serveur = CustomUser.objects.create_user(username="serveur", email="serveur@restaurant.com", password="serveur123", first_name="Serveur", last_name="Test", role="Rservent", is_staff=True)
caissier = CustomUser.objects.create_user(username="caissier", email="caissier@restaurant.com", password="caissier123", first_name="Caissier", last_name="Test", role="Rcaissier", is_staff=True)

print("✅ Données créées avec succès!")
"""
