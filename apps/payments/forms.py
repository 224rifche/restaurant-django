from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models import Q
from django.urls import reverse_lazy
from decimal import Decimal

from apps.orders.models import Commande
from .models import Caisse, Paiement, TypeDepense, SortieCaisse


class CaisseForm(forms.ModelForm):
    class Meta:
        model = Caisse
        fields = ['solde_initial', 'notes']
        widgets = {
            'solde_initial': forms.NumberInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Montant initial de la caisse'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md',
                'rows': 3,
                'placeholder': 'Notes complémentaires (facultatif)'
            }),
        }
    
    def clean_solde_initial(self):
        solde_initial = self.cleaned_data.get('solde_initial')
        if solde_initial < 0:
            raise forms.ValidationError("Le solde initial ne peut pas être négatif.")
        return solde_initial


class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['commande', 'mode_paiement', 'reference', 'notes']
        widgets = {
            'commande': forms.HiddenInput(),
            'mode_paiement': forms.Select(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md',
            }),
            'reference': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md',
                'placeholder': 'Référence (numéro de chèque, etc.)',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md',
                'rows': 2,
                'placeholder': 'Notes complémentaires (facultatif)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ne permettre que les commandes non payées
        self.fields['commande'].queryset = Commande.objects.filter(paiement__isnull=True)
        
        # Si une commande est passée dans les données initiales, limiter à cette commande
        if 'commande' in self.initial:
            self.fields['commande'].widget = forms.HiddenInput()
            self.fields['commande'].disabled = True
    
    def clean_commande(self):
        commande = self.cleaned_data.get('commande')
        if hasattr(commande, 'paiement'):
            raise forms.ValidationError("Cette commande a déjà été payée.")
        return commande


class TypeDepenseForm(forms.ModelForm):
    class Meta:
        model = TypeDepense
        fields = ['nom', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md',
                'placeholder': 'Nom du type de dépense'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md',
                'rows': 3,
                'placeholder': 'Description (facultatif)'
            }),
        }
    
    def clean_nom(self):
        nom = self.cleaned_data.get('nom')
        if TypeDepense.objects.filter(nom__iexact=nom).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Un type de dépense avec ce nom existe déjà.")
        return nom


class SortieCaisseForm(forms.ModelForm):
    class Meta:
        model = SortieCaisse
        fields = ['type_depense', 'montant', 'motif', 'justificatif', 'notes']
        widgets = {
            'type_depense': forms.Select(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md',
            }),
            'montant': forms.NumberInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Montant de la dépense'
            }),
            'motif': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md',
                'placeholder': 'Motif de la dépense',
            }),
            'justificatif': forms.FileInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md',
                'rows': 2,
                'placeholder': 'Notes complémentaires (facultatif)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordonner les types de dépense par nom
        self.fields['type_depense'].queryset = TypeDepense.objects.all().order_by('nom')
    
    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à zéro.")
        return montant


class FilterCaisseForm(forms.Form):
    date_debut = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'p-2 border border-gray-300 rounded-md',
        }),
        label='Du'
    )
    date_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'p-2 border border-gray-300 rounded-md',
        }),
        label='Au'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        
        if date_debut and date_fin and date_debut > date_fin:
            raise forms.ValidationError("La date de début doit être antérieure à la date de fin.")
        
        return cleaned_data


class FilterPaiementForm(FilterCaisseForm):
    MODE_PAIEMENT_CHOICES = [
        ('', 'Tous les modes de paiement'),
        ('especes', 'Espèces'),
        ('carte', 'Carte bancaire'),
        ('cheque', 'Chèque'),
        ('autre', 'Autre'),
    ]
    
    mode_paiement = forms.ChoiceField(
        choices=MODE_PAIEMENT_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'p-2 border border-gray-300 rounded-md',
        }),
        label='Mode de paiement'
    )


class FilterSortieCaisseForm(FilterCaisseForm):
    type_depense = forms.ModelChoiceField(
        queryset=TypeDepense.objects.all().order_by('nom'),
        required=False,
        widget=forms.Select(attrs={
            'class': 'p-2 border border-gray-300 rounded-md',
        }),
        label='Type de dépense'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['type_depense'].empty_label = 'Tous les types'


class FermetureCaisseForm(forms.ModelForm):
    class Meta:
        model = Caisse
        fields = ['solde_actuel', 'notes_fermeture']
        widgets = {
            'solde_actuel': forms.NumberInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Solde réel en caisse'
            }),
            'notes_fermeture': forms.Textarea(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded-md',
                'rows': 3,
                'placeholder': 'Notes de clôture (facultatif)'
            }),
        }
        labels = {
            'solde_actuel': 'Solde réel en caisse',
            'notes_fermeture': 'Notes de clôture'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['solde_actuel'].initial = self.instance.solde_theorique
        self.fields['solde_actuel'].help_text = f"Solde théorique: {self.instance.solde_theorique} GNF"
    
    def clean_solde_actuel(self):
        solde_actuel = self.cleaned_data.get('solde_actuel')
        if solde_actuel < 0:
            raise forms.ValidationError("Le solde ne peut pas être négatif.")
        return solde_actuel


class AjoutFondCaisseForm(forms.Form):
    montant = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        widget=forms.NumberInput(attrs={
            'class': 'w-full p-2 border border-gray-300 rounded-md',
            'step': '0.01',
            'min': '0.01',
            'placeholder': 'Montant à ajouter',
            'hx-post': reverse_lazy('payments:ajouter_fond_caisse'),
            'hx-trigger': 'change',
            'hx-target': '#fond-caisse-result',
        }),
        label='Montant à ajouter',
        help_text='Entrez le montant à ajouter au fond de caisse.'
    )
    
    motif = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full p-2 border border-gray-300 rounded-md',
            'placeholder': 'Motif (facultatif)',
        }),
        label='Motif',
        help_text='Raison de l\'ajout de fonds (ex: Approvisionnement, Remboursement, etc.)'
    )
