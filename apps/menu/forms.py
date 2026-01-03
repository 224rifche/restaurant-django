from django import forms
from .models import Plat, CategoriePlat


class PlatForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        categories = list(CategoriePlat.objects.order_by('ordre', 'nom').values_list('nom', flat=True))
        if not categories:
            categories = ['Poulet', 'Jus', 'Viande', 'Poisson', 'Chawarma']
        self.fields['categorie'].choices = [(c, c) for c in categories]

    class Meta:
        model = Plat
        fields = ('nom', 'categorie', 'description', 'prix_unitaire', 'image', 'disponible')
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nom du plat'
            }),
            'categorie': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
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
