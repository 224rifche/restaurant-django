from django.db import models
from django.core.validators import MinValueValidator
from apps.authentication.models import CustomUser


class TableRestaurant(models.Model):
    STATUS_CHOICES = [
        ('libre', 'Libre'),
        ('commande_en_attente', 'Commande en attente'),
        ('commande_servie', 'Commande servie'),
        ('commande_payee', 'Commande payée'),
    ]

    numero_table = models.CharField(max_length=50, unique=True, verbose_name='Numéro de table')
    nombre_places = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Nombre de places'
    )
    nombre_clients_actuels = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Nombre de clients'
    )
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        related_name='tables',
        verbose_name='Utilisateur associé',
        null=True,
        blank=True
    )
    current_status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='libre',
        verbose_name='Statut actuel'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tables_restaurant'
        verbose_name = 'Table'
        verbose_name_plural = 'Tables'
        ordering = ['numero_table']

    def __str__(self):
        return f"Table {self.numero_table}"

    def get_active_order(self):
        from apps.orders.models import Commande
        return self.commandes.exclude(statut='payee').first()

    def get_last_order(self):
        return self.commandes.first()

    def update_status(self):
        active_order = self.get_active_order()
        if active_order:
            if active_order.statut == 'en_attente':
                self.current_status = 'commande_en_attente'
            elif active_order.statut == 'servie':
                self.current_status = 'commande_servie'
            else:
                self.current_status = 'libre'
        else:
            last_order = self.get_last_order()
            if last_order and last_order.statut == 'payee':
                self.current_status = 'commande_payee'
            else:
                self.current_status = 'libre'

            # Si aucune commande active: la table est considérée libre -> réinitialiser le nombre de clients
            self.nombre_clients_actuels = 0
        self.save()
