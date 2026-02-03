from django.contrib import admin

from .models import Depense


@admin.register(Depense)
class DepenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'date_depense', 'type_depense', 'montant', 'motif', 'caisse', 'utilisateur')
    list_filter = ('type_depense', 'date_depense')
    search_fields = ('motif', 'utilisateur__login')
