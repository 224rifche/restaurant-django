from django import forms
from .models import Plat, CategoriePlat


class CategoriePlatForm(forms.ModelForm):
    class Meta:
        model = CategoriePlat
        fields = ('nom', 'ordre')


class PlatForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categorie'].widget = forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Catégorie (ex: Poulet, Jus, ...)',
            'list': 'categorie-list',
        })

    def clean_categorie(self):
        value = (self.cleaned_data.get('categorie') or '').strip()
        if not value:
            raise forms.ValidationError('Ce champ est obligatoire.')
        return value

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.categorie:
            CategoriePlat.objects.get_or_create(nom=instance.categorie, defaults={'ordre': 0})
        if commit:
            instance.save()
            self.save_m2m()
        return instance

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
