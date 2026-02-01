from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class CategoriePlat(models.Model):
    nom = models.CharField(max_length=100, unique=True, verbose_name='Nom')
    ordre = models.PositiveIntegerField(default=0, verbose_name='Ordre')

    class Meta:
        db_table = 'categories_plats'
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'
        ordering = ['ordre', 'nom']

    def __str__(self):
        return self.nom


class Plat(models.Model):
    nom = models.CharField(max_length=200, verbose_name='Nom du plat')
    categorie = models.ForeignKey(
        CategoriePlat,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Catégorie'
    )
    description = models.TextField(blank=True, verbose_name='Description')
    prix_unitaire = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name='Prix unitaire'
    )
    image = models.ImageField(upload_to='plats/', verbose_name='Image')
    disponible = models.BooleanField(default=True, verbose_name='Disponible')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'plats'
        verbose_name = 'Plat'
        verbose_name_plural = 'Plats'
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} - {self.prix_unitaire} GNF"
