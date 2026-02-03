from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


class AddToCartForm(forms.Form):
    quantite = forms.IntegerField(
        label='Quantité',
        validators=[
            MinValueValidator(1, message=_('La quantité doit être d\'au moins 1')),
            MaxValueValidator(10, message=_('La quantité ne peut pas dépasser 10'))
        ],
        initial=1,
        widget=forms.NumberInput(attrs={
            'class': 'w-16 text-center border border-gray-300 rounded-md',
            'min': '1',
            'max': '10'
        })
    )
    notes = forms.CharField(
        label='Notes supplémentaires',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full mt-2 p-2 border border-gray-300 rounded-md',
            'rows': 2,
            'placeholder': 'Sans oignons, bien cuit, etc.'
        })
    )


class UpdateCartItemForm(forms.ModelForm):
    class Meta:
        from .models import PanierItem
        model = PanierItem
        fields = ['quantite']
        labels = {
            'quantite': _('Quantité')
        }
        widgets = {
            'quantite': forms.NumberInput(attrs={
                'class': 'w-16 text-center border border-gray-300 rounded-md',
                'min': '1',
                'max': '10'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantite'].validators.extend([
            MinValueValidator(1, message=_('La quantité doit être d\'au moins 1')),
            MaxValueValidator(10, message=_('La quantité ne peut pas dépasser 10'))
        ])


class CreateOrderForm(forms.Form):
    notes = forms.CharField(
        label='Notes pour la commande',
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'w-full p-2 border border-gray-300 rounded-md',
            'rows': 3,
            'placeholder': 'Demandes spéciales, allergies, etc.'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].widget.attrs.update({'class': 'w-full p-2 border border-gray-300 rounded-md'})


class FilterOrdersForm(forms.Form):
    STATUT_CHOICES = [
        ('tous', 'Toutes les commandes'),
        ('en_attente', 'En attente'),
        ('servie', 'Servie'),
        ('payee', 'Payée'),
    ]
    
    statut = forms.ChoiceField(
        label='Filtrer par statut',
        choices=STATUT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-md p-2',
            'hx-get': '.',
            'hx-target': '#orders-list',
            'hx-trigger': 'change',
            'hx-push-url': 'true'
        })
    )


class MarkOrderPaidForm(forms.Form):
    montant_paye = forms.DecimalField(
        label='Montant payé',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        widget=forms.NumberInput(attrs={
            'class': 'border border-gray-300 rounded-md p-2',
            'step': '0.01',
            'min': '0.01'
        })
    )
    
    mode_paiement = forms.ChoiceField(
        label='Mode de paiement',
        choices=[
            ('especes', 'Espèces'),
            ('carte', 'Carte bancaire'),
            ('cheque', 'Chèque'),
            ('autre', 'Autre')
        ],
        widget=forms.Select(attrs={
            'class': 'border border-gray-300 rounded-md p-2'
        })
    )
    
    def __init__(self, *args, montant_total=None, **kwargs):
        super().__init__(*args, **kwargs)
        if montant_total is not None:
            self.fields['montant_paye'].initial = montant_total
            self.fields['montant_paye'].widget.attrs['min'] = str(montant_total)
            self.fields['montant_paye'].validators.append(MinValueValidator(montant_total))
