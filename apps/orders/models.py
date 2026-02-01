from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum, F
from decimal import Decimal
from apps.menu.models import Plat
from apps.tables.models import TableRestaurant


class Panier(models.Model):
    table = models.ForeignKey(
        TableRestaurant,
        on_delete=models.CASCADE,
        related_name='paniers',
        verbose_name='Table'
    )
    created_by = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Créé par'
    )
    is_active = models.BooleanField(default=True, verbose_name='Actif')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'paniers'
        verbose_name = 'Panier'
        verbose_name_plural = 'Paniers'
        ordering = ['-created_at']

    def __str__(self):
        return f"Panier {self.id} - Table {self.table.numero_table}"

    @property
    def total(self):
        return self.items.aggregate(
            total=Sum(F('quantite') * F('prix_unitaire'))
        )['total'] or Decimal('0.00')


class PanierItem(models.Model):
    panier = models.ForeignKey(
        Panier,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Panier'
    )
    plat = models.ForeignKey(
        Plat,
        on_delete=models.PROTECT,
        related_name='panier_items',
        verbose_name='Plat'
    )
    quantite = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1, message='La quantité doit être d\'au moins 1'),
            MaxValueValidator(10, message='La quantité ne peut pas dépasser 10')
        ],
        verbose_name='Quantité'
    )
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Prix unitaire'
    )
    notes = models.TextField(blank=True, verbose_name='Notes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'panier_items'
        verbose_name = 'Article du panier'
        verbose_name_plural = 'Articles du panier'
        unique_together = ('panier', 'plat')

    def __str__(self):
        return f"{self.quantite}x {self.plat.nom} (Panier {self.panier_id})"

    @property
    def sous_total(self):
        """Calcule le sous-total pour cet article"""
        return self.prix_unitaire * self.quantite

    def save(self, *args, **kwargs):
        # S'assurer que le prix unitaire est toujours à jour avec le plat
        if not self.pk or not self.prix_unitaire or self.prix_unitaire <= 0:
            self.prix_unitaire = self.plat.prix_unitaire
        super().save(*args, **kwargs)


class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('servie', 'Servie'),
        ('payee', 'Payée'),
    ]

    numero_commande = models.CharField(max_length=50, unique=True, verbose_name='Numéro de commande')
    table = models.ForeignKey(
        TableRestaurant,
        on_delete=models.PROTECT,
        related_name='commandes',
        verbose_name='Table'
    )
    montant_total = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Montant total'
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name='Statut'
    )
    date_commande = models.DateTimeField(auto_now_add=True, verbose_name='Date de commande')
    date_service = models.DateTimeField(null=True, blank=True, verbose_name='Date de service')
    date_paiement = models.DateTimeField(null=True, blank=True, verbose_name='Date de paiement')
    notes = models.TextField(blank=True, verbose_name='Notes')
    serveur = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commandes_serveur',
        verbose_name='Serveur (a commandé)'
    )
    validateur = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commandes_validees',
        verbose_name='Validateur (a servi)'
    )
    caissier = models.ForeignKey(
        'authentication.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commandes_caissier',
        verbose_name='Caissier (a encaissé)'
    )

    class Meta:
        db_table = 'commandes'
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-date_commande']
        permissions = [
            ('can_view_all_orders', 'Peut voir toutes les commandes'),
            ('can_serve_order', 'Peut marquer une commande comme servie'),
            ('can_pay_order', 'Peut enregistrer un paiement'),
        ]

    def __str__(self):
        return f"{self.numero_commande} - Table {self.table.numero_table} - {self.get_statut_display()}"

    def save(self, *args, **kwargs):
        if not self.numero_commande:
            # Format: CMD-YYYYMMDD-XXXX (où XXXX est un numéro séquentiel)
            from django.utils import timezone
            date_str = timezone.now().strftime('%Y%m%d')
            last_cmd = Commande.objects.filter(numero_commande__startswith=f'CMD-{date_str}').order_by('-id').first()
            if last_cmd:
                last_num = int(last_cmd.numero_commande.split('-')[-1])
                new_num = f"{last_num + 1:04d}"
            else:
                new_num = "0001"
            self.numero_commande = f"CMD-{date_str}-{new_num}"
        
        # Mettre à jour les dates en fonction du statut
        if self.statut == 'servie' and not self.date_service:
            from django.utils import timezone
            self.date_service = timezone.now()
        elif self.statut == 'payee' and not self.date_paiement:
            from django.utils import timezone
            self.date_paiement = timezone.now()
            
        super().save(*args, **kwargs)
        
        # Mettre à jour le statut de la table
        self.table.update_status()


class CommandeItem(models.Model):
    commande = models.ForeignKey(
        Commande,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Commande'
    )
    plat = models.ForeignKey(
        Plat,
        on_delete=models.PROTECT,
        related_name='commande_items',
        verbose_name='Plat'
    )
    quantite = models.PositiveIntegerField(verbose_name='Quantité')
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Prix unitaire'
    )
    notes = models.TextField(blank=True, verbose_name='Notes')

    class Meta:
        db_table = 'commande_items'
        verbose_name = 'Article de commande'
        verbose_name_plural = 'Articles de commande'

    def __str__(self):
        return f"{self.quantite}x {self.plat.nom} (Commande {self.commande.numero_commande})"

    @property
    def total(self):
        return self.quantite * self.prix_unitaire
