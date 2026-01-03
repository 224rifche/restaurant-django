# apps/core/management/commands/seed.py
from django.core.management.base import BaseCommand
from faker import Faker
from django.contrib.auth import get_user_model
from django.db import transaction
import random
from decimal import Decimal

fake = Faker('fr_FR')
User = get_user_model()

class Command(BaseCommand):
    help = 'Génère des données factices pour la base de données'

    def handle(self, *args, **options):
        self.stdout.write('Démarrage de la génération des données factices...')
        
        with transaction.atomic():
            self.create_admin_user()
            self.create_users(10)  # Crée 10 utilisateurs
            self.create_tables(8)  # Crée 8 tables
            self.create_dishes(15)  # Crée 15 plats
            self.create_orders(20)  # Crée 20 commandes
            
        self.stdout.write(self.style.SUCCESS('Données factices générées avec succès !'))

    def create_admin_user(self):
        """Crée un utilisateur administrateur"""
        if not User.objects.filter(login='admin').exists():
            User.objects.create_superuser(
                login='admin',
                password='admin123',
                role='Radmin'
            )
            self.stdout.write(self.style.SUCCESS('Utilisateur admin créé'))

    def create_users(self, count):
        """Crée des utilisateurs factices"""
        from apps.authentication.models import CustomUser
        
        roles = [role[0] for role in CustomUser.ROLE_CHOICES 
                if role[0] not in ['Radmin', 'Rtable']]  # Exclure admin et tables
        
        for _ in range(count):
            User.objects.create_user(
                login=fake.unique.user_name(),
                password='password123',
                role=random.choice(roles)
            )
        self.stdout.write(self.style.SUCCESS(f'Création de {count} utilisateurs'))

    def create_tables(self, count):
        """Crée des tables factices"""
        from apps.tables.models import TableRestaurant
         
        try:
            for i in range(1, count + 1):
                login = f"table{i:02d}"
                user = User.objects.filter(login=login).first()
                if user is None:
                    user = User.objects.create_user(
                        login=login,
                        password='table123',
                        role='Rtable',
                    )

                TableRestaurant.objects.get_or_create(
                    numero_table=f"Table {i}",
                    defaults={
                        'nombre_places': random.choice([2, 2, 4, 4, 6, 8]),
                        'current_status': 'libre',
                        'user': user,
                    },
                )
            self.stdout.write(self.style.SUCCESS(f'Création de {count} tables'))
             
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors de la création des tables : {str(e)}'))

    def create_dishes(self, count):
        """Crée des plats et catégories factices"""
        from apps.menu.models import Plat
         
        try:
            dish_names = [
                'Salade César', 'Burger Classique', 'Pizza Margherita', 'Tiramisu',
                'Poulet rôti', 'Saumon grillé', 'Mousse au chocolat', 'Tarte aux pommes',
                'Soupe à l\'oignon', 'Steak frites', 'Crème brûlée', 'Coca-Cola'
            ]
             
            for _ in range(count):
                dish_name = f"{random.choice(dish_names)} {fake.word().capitalize()}"
                # Prix en GNF (ex: 10 000 à 150 000)
                prix_gnf = Decimal(random.randrange(10_000, 150_001, 500))
                Plat.objects.create(
                    nom=dish_name[:200],
                    prix_unitaire=prix_gnf,
                    image='',
                    disponible=random.choice([True, True, True, False]),
                )
            self.stdout.write(self.style.SUCCESS(f'Création de {count} plats'))
             
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors de la création des plats : {str(e)}'))

    def create_orders(self, count):
        """Crée des commandes factices"""
        from apps.orders.models import Commande, CommandeItem
        from apps.tables.models import TableRestaurant
        from apps.menu.models import Plat
         
        try:
            statuses = ['en_attente', 'servie', 'payee']
            tables = list(TableRestaurant.objects.all())
            plats = list(Plat.objects.filter(disponible=True))

            if not tables:
                self.stdout.write(self.style.WARNING('Aucune table trouvée. Créez d\'abord des tables.'))
                return
                 
            if not plats:
                self.stdout.write(self.style.WARNING('Aucun plat disponible. Créez d\'abord des plats.'))
                return
             
            for _ in range(count):
                table = random.choice(tables)
                selected_plats = random.sample(plats, k=min(len(plats), random.randint(1, 5)))
                items = []
                total = Decimal('0.00')

                for plat in selected_plats:
                    quantite = random.randint(1, 3)
                    prix_unitaire = plat.prix_unitaire
                    total += Decimal(quantite) * prix_unitaire
                    items.append((plat, quantite, prix_unitaire))

                if total < Decimal('0.01'):
                    total = Decimal('0.01')

                commande = Commande.objects.create(
                    table=table,
                    montant_total=total,
                    statut=random.choice(statuses),
                    notes=fake.sentence() if random.random() > 0.7 else '',
                )

                for plat, quantite, prix_unitaire in items:
                    CommandeItem.objects.create(
                        commande=commande,
                        plat=plat,
                        quantite=quantite,
                        prix_unitaire=prix_unitaire,
                        notes=fake.sentence() if random.random() > 0.8 else '',
                    )
                     
            self.stdout.write(self.style.SUCCESS(f'Création de {count} commandes'))
             
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Erreur lors de la création des commandes : {str(e)}'))