from django import forms
from .models import Plat, CategoriePlat


class CategoriePlatForm(forms.ModelForm):
    class Meta:
        model = CategoriePlat
        fields = ('nom', 'ordre')
    
    def clean_nom(self):
        nom = self.cleaned_data.get('nom')
        if CategoriePlat.objects.filter(nom__iexact=nom).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Une catégorie avec ce nom existe déjà.")
        return nom


class PlatForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categorie'].widget = forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
        })
        self.fields['categorie'].empty_label = "Choisir une catégorie..."
        self.fields['categorie'].queryset = CategoriePlat.objects.all().order_by('ordre', 'nom')

    def clean_categorie(self):
        categorie = self.cleaned_data.get('categorie')
        if not categorie:
            raise forms.ValidationError('Ce champ est obligatoire.')
        return categorie

    class Meta:
        model = Plat
        fields = ('nom', 'categorie', 'description', 'prix_unitaire', 'image', 'disponible')
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nom du plat'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Description (optionnel)',
                'rows': 3
            }),
            'prix_unitaire': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Prix en GNF'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'accept': 'image/*'
            }),
            'disponible': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            }),
        }
