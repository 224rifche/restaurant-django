from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum
from django.utils import timezone
from decimal import Decimal

from apps.orders.models import Commande
from apps.authentication.models import CustomUser


class Caisse(models.Model):
    """
    Modèle Singleton pour gérer l'état de la caisse du restaurant.
    Une seule instance de ce modèle doit exister.
    """
    solde_initial = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Solde initial de la caisse'
    )
    solde_actuel = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Solde actuel de la caisse'
    )
    notes = models.TextField(blank=True, verbose_name='Notes')
    notes_fermeture = models.TextField(blank=True, verbose_name='Notes de clôture')
    date_ouverture = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'ouverture de la caisse'
    )
    date_fermeture = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date de fermeture de la caisse'
    )
    est_ouverte = models.BooleanField(
        default=True,
        verbose_name='Caisse ouverte ?'
    )
    utilisateur_ouverture = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='caisses_ouvertes',
        verbose_name='Ouverte par'
    )
    utilisateur_fermeture = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='caisses_fermees',
        null=True,
        blank=True,
        verbose_name='Fermée par'
    )

    class Meta:
        db_table = 'caisse'
        verbose_name = 'Caisse'
        verbose_name_plural = 'Caisses'
        permissions = [
            ('can_open_register', 'Peut ouvrir la caisse'),
            ('can_close_register', 'Peut fermer la caisse'),
            ('can_view_register', 'Peut voir les détails de la caisse'),
        ]

    def __str__(self):
        return f'Caisse du {self.date_ouverture.strftime("%d/%m/%Y")} - {self.get_status_display()}'

    def save(self, *args, **kwargs):
        # S'assurer qu'il n'y a qu'une seule instance de Caisse ouverte à la fois
        if self.est_ouverte:
            Caisse.objects.exclude(pk=self.pk).filter(est_ouverte=True).update(
                est_ouverte=False,
                date_fermeture=timezone.now()
            )
        
        # Si c'est une nouvelle caisse, initialiser le solde_actuel
        if not self.pk and not self.solde_actuel:
            self.solde_actuel = self.solde_initial
        
        super().save(*args, **kwargs)
    
    def get_status_display(self):
        return 'Ouverte' if self.est_ouverte else 'Fermée'
    
    @property
    def total_ventes(self):
        """Calcule le total des ventes pour cette caisse"""
        return self.paiements.aggregate(
            total=Sum('montant')
        )['total'] or Decimal('0.00')
    
    @property
    def total_depenses(self):
        """Calcule le total des dépenses pour cette caisse"""
        return self.sorties.aggregate(
            total=Sum('montant')
        )['total'] or Decimal('0.00')
    
    @property
    def solde_theorique(self):
        """Calcule le solde théorique de la caisse"""
        return self.solde_initial + self.total_ventes - self.total_depenses
    
    @property
    def difference(self):
        """Calcule la différence entre le solde théorique et le solde réel"""
        return self.solde_actuel - self.solde_theorique
    
    @classmethod
    def get_caisse_ouverte(cls):
        """Récupère la caisse ouverte ou None si aucune caisse n'est ouverte"""
        try:
            return cls.objects.get(est_ouverte=True)
        except cls.DoesNotExist:
            return None
    
    @classmethod
    def get_derniere_caisse(cls):
        """Récupère la dernière caisse (ouverte ou fermée)"""
        return cls.objects.order_by('-date_ouverture').first()


class Paiement(models.Model):
    """
    Modèle pour enregistrer les paiements des commandes
    """
    MODE_PAIEMENT_CHOICES = [
        ('especes', 'Espèces'),
        ('carte', 'Carte bancaire'),
        ('cheque', 'Chèque'),
        ('autre', 'Autre'),
    ]
    
    commande = models.OneToOneField(
        Commande,
        on_delete=models.PROTECT,
        related_name='paiement',
        verbose_name='Commande'
    )
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Montant payé'
    )
    mode_paiement = models.CharField(
        max_length=10,
        choices=MODE_PAIEMENT_CHOICES,
        verbose_name='Mode de paiement'
    )
    reference = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Référence (numéro de chèque, etc.)'
    )
    date_paiement = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date du paiement'
    )
    caisse = models.ForeignKey(
        Caisse,
        on_delete=models.PROTECT,
        related_name='paiements',
        verbose_name='Caisse'
    )
    utilisateur = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='paiements_effectues',
        verbose_name='Encaissé par'
    )
    est_valide = models.BooleanField(
        default=False,
        verbose_name='Paiement validé ?',
        help_text='Cocher pour confirmer que le paiement a bien été effectué.'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes complémentaires'
    )

    class Meta:
        db_table = 'paiements'
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date_paiement']
        permissions = [
            ('can_register_payment', 'Peut enregistrer un paiement'),
            ('can_view_payment', 'Peut voir les détails des paiements'),
        ]

    def __str__(self):
        return f'Paiement {self.id} - {self.commande.numero_commande} - {self.montant} GNF'
    
    def save(self, *args, **kwargs):
        from django.core.exceptions import ValidationError
        
        # Vérifier si c'est un nouveau paiement
        if not self.pk:
            # Vérifier qu'un paiement n'existe pas déjà pour cette commande
            if Paiement.objects.filter(commande=self.commande).exists():
                raise ValidationError("Un paiement existe déjà pour cette commande.")
            
            # Vérifier que la caisse est ouverte
            if not self.caisse.est_ouverte:
                raise ValidationError("Impossible d'enregistrer un paiement sur une caisse fermée.")
            
            # Définir l'utilisateur actuel
            if not hasattr(self, 'utilisateur') and hasattr(self, '_request'):
                self.utilisateur = self._request.user
        
        # Si le paiement est marqué comme valide, mettre à jour la commande et la caisse
        if self.est_valide:
            # Mettre à jour le statut de la commande
            self.commande.statut = 'payee'
            self.commande.caissier = self.utilisateur
            self.commande.save()
            
            # Mettre à jour le solde de la caisse
            self.caisse.solde_actuel += self.montant
            self.caisse.save()
        
        # Mettre à jour la date de paiement
        self.date_paiement = timezone.now()
        
        # Appeler la méthode save() de la classe parente
        super().save(*args, **kwargs)


class TypeDepense(models.Model):
    """
    Catégorie pour classer les dépenses
    """
    nom = models.CharField(max_length=100, verbose_name='Nom de la catégorie')
    description = models.TextField(blank=True, verbose_name='Description')
    
    class Meta:
        db_table = 'types_depense'
        verbose_name = 'Type de dépense'
        verbose_name_plural = 'Types de dépense'
        ordering = ['nom']
    
    def __str__(self):
        return self.nom


class SortieCaisse(models.Model):
    """
    Modèle pour enregistrer les sorties de caisse (dépenses, retraits, etc.)
    """
    caisse = models.ForeignKey(
        Caisse,
        on_delete=models.PROTECT,
        related_name='sorties',
        verbose_name='Caisse'
    )
    type_depense = models.ForeignKey(
        TypeDepense,
        on_delete=models.PROTECT,
        related_name='sorties',
        verbose_name='Type de dépense'
    )
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name='Montant'
    )
    date_sortie = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de la sortie'
    )
    motif = models.CharField(
        max_length=255,
        verbose_name='Motif de la sortie'
    )
    justificatif = models.FileField(
        upload_to='justificatifs/depenses/%Y/%m/%d/',
        blank=True,
        null=True,
        verbose_name='Justificatif (facultatif)'
    )
    utilisateur = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='sorties_effectuees',
        verbose_name='Effectuée par'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes complémentaires'
    )

    class Meta:
        db_table = 'sorties_caisse'
        verbose_name = 'Sortie de caisse'
        verbose_name_plural = 'Sorties de caisse'
        ordering = ['-date_sortie']
        permissions = [
            ('can_register_expense', 'Peut enregistrer une dépense'),
            ('can_view_expense', 'Peut voir les détails des dépenses'),
        ]

    def __str__(self):
        return f'Sortie de caisse #{self.id} - {self.motif} - {self.montant} GNF'
    
    def save(self, *args, **kwargs):
        # S'assurer qu'une caisse est ouverte
        if not hasattr(self, 'caisse'):
            caisse = Caisse.get_caisse_ouverte()
            if not caisse:
                raise ValueError('Aucune caisse n\'est ouverte. Veuillez ouvrir une caisse avant d\'enregistrer une sortie.')
            self.caisse = caisse
        
        # Enregistrer l'utilisateur actuel
        if not hasattr(self, 'utilisateur') and hasattr(self, '_request'):
            self.utilisateur = self._request.user
        
        super().save(*args, **kwargs)
