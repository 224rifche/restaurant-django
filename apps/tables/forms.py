from django import forms
from django.db.models import Q
from .models import TableRestaurant


class TableRestaurantForm(forms.ModelForm):
    class Meta:
        model = TableRestaurant
        fields = ('numero_table', 'nombre_places', 'user')
        widgets = {
            'numero_table': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ex: Table 1',
                'autofocus': True
            }),
            'nombre_places': forms.NumberInput(attrs={
                'class': 'form-input',
                'min': '1',
                'placeholder': 'Nombre de places',
                'value': '4'
            }),
            'user': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        help_texts = {
            'user': 'Optionnel - Sélectionnez un utilisateur de type Table',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.authentication.models import CustomUser
        
        # Rendre le champ user optionnel
        self.fields['user'].required = False
        self.fields['user'].empty_label = "Aucun utilisateur"
        
        # Filtrer les utilisateurs de type Table
        self.fields['user'].queryset = CustomUser.objects.filter(role='Rtable')
        
        # Si on est en mode édition, on inclut l'utilisateur actuel s'il existe
        if self.instance and self.instance.user_id:
            self.fields['user'].queryset = CustomUser.objects.filter(
                Q(role='Rtable') | Q(pk=self.instance.user_id)
            ).distinct()
