from django import forms
from .models import Plat


class PlatForm(forms.ModelForm):
    class Meta:
        model = Plat
        fields = ('nom', 'prix_unitaire', 'image', 'disponible')
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nom du plat'
            }),
            'prix_unitaire': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Prix en euros'
            }),
            'image': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'accept': 'image/*'
            }),
            'disponible': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500'
            }),
        }
