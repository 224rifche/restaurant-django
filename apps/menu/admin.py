from django.contrib import admin
from .models import Plat, CategoriePlat


@admin.register(CategoriePlat)
class CategoriePlatAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ordre')
    list_editable = ('ordre',)
    search_fields = ('nom',)
    ordering = ('ordre', 'nom')


@admin.register(Plat)
class PlatAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prix_unitaire', 'disponible', 'created_at')
    list_filter = ('disponible',)
    search_fields = ('nom',)
    readonly_fields = ('created_at', 'updated_at')
