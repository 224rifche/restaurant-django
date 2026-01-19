import secrets
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from apps.authentication.models import CustomUser


class TableRestaurant(models.Model):
    STATUS_CHOICES = [
        ('libre', 'Libre'),
        ('commande_en_attente', 'Commande en attente'),
        ('commande_servie', 'Commande servie'),
        ('commande_payee', 'Commande payée'),
    ]
    
    QR_STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('blocked', 'Bloquée'),
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
    qr_token = models.CharField(max_length=100, unique=True, blank=True, null=True, verbose_name='Token QR Code')
    qr_status = models.CharField(
        max_length=10, 
        choices=QR_STATUS_CHOICES, 
        default='inactive',
        verbose_name='Statut QR Code'
    )
    last_login_at = models.DateTimeField(null=True, blank=True, verbose_name='Dernière connexion')
    last_login_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='Dernière IP de connexion')

    class Meta:
        db_table = 'tables_restaurant'
        verbose_name = 'Table'
        verbose_name_plural = 'Tables'
        ordering = ['numero_table']

    def __str__(self):
        return f"Table {self.numero_table}"

    def generate_qr_token(self, save=True):
        """Génère un token unique pour le QR code"""
        token = f"table_{self.id}_{secrets.token_urlsafe(16)}"
        self.qr_token = token
        self.qr_status = 'active'
        if save:
            self.save()
        return token
    
    def get_qr_code_url(self, request=None):
        """Retourne l'URL complète pour le QR code"""
        if not self.qr_token:
            self.generate_qr_token()
        
        if request:
            base_url = request.build_absolute_uri('/')
        else:
            base_url = settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'
            
        return f"{base_url}qr/login/{self.qr_token}/"
    
    def block(self):
        """Bloque la table"""
        self.qr_status = 'blocked'
        self.save()
    
    def unblock(self):
        """Débloque la table"""
        self.qr_status = 'active'
        self.save()
    
    def is_blocked(self):
        """Vérifie si la table est bloquée"""
        return self.qr_status == 'blocked'
    
    def record_login(self, ip_address):
        """Enregistre les informations de connexion"""
        self.last_login_at = timezone.now()
        self.last_login_ip = ip_address
        self.save()
    
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
