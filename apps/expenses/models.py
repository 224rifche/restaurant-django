from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.authentication.models import CustomUser
from apps.payments.models import Caisse, TypeDepense


class Depense(models.Model):
    caisse = models.ForeignKey(Caisse, on_delete=models.PROTECT, related_name='depenses', verbose_name='Caisse')
    type_depense = models.ForeignKey(TypeDepense, on_delete=models.PROTECT, related_name='depenses', verbose_name='Type de dépense')
    montant = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name='Montant')
    motif = models.CharField(max_length=255, verbose_name='Motif')
    date_depense = models.DateTimeField(auto_now_add=True, verbose_name='Date')
    utilisateur = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='depenses', verbose_name='Enregistrée par')
    justificatif = models.FileField(upload_to='justificatifs/depenses/%Y/%m/%d/', blank=True, null=True, verbose_name='Justificatif')
    notes = models.TextField(blank=True, verbose_name='Notes')
    
    class Meta:
        db_table = 'depenses'
        verbose_name = 'Dépense'
        verbose_name_plural = 'Dépenses'
        ordering = ['-date_depense']

    def __str__(self):
        return f"Dépense #{self.id} - {self.motif} ({self.montant} GNF)"
