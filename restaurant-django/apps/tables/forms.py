from django import forms
from django.db.models import Q
from .models import TableRestaurant


class TableRestaurantForm(forms.ModelForm):
    class Meta:
        model = TableRestaurant
        fields = ('numero_table', 'nombre_places', 'user')
        widgets = {
            'numero_table': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Ex: Table 1'
            }),
            'nombre_places': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500',
                'min': '1',
                'placeholder': 'Nombre de places'
            }),
            'user': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from apps.authentication.models import CustomUser
        self.fields['user'].empty_label = "Sélectionnez un utilisateur..."

        base_qs = CustomUser.objects.filter(role='Rtable', table__isnull=True)
        if self.instance and getattr(self.instance, 'pk', None) and getattr(self.instance, 'user_id', None):
            self.fields['user'].queryset = CustomUser.objects.filter(
                Q(pk=self.instance.user_id) | Q(role='Rtable', table__isnull=True)
            )
        else:
            self.fields['user'].queryset = base_qs
