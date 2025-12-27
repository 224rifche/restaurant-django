from django.contrib import admin
from .models import Plat


@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix_unitaire', 'disponible', 'created_at')
    list_filter = ('disponible',)
    search_fields = ('nom',)
    readonly_fields = ('created_at', 'updated_at')
