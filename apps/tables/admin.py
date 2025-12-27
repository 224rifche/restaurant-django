from django.contrib import admin
from .models import TableRestaurant


@admin.register(TableRestaurant)
class TableRestaurantAdmin(admin.ModelAdmin):
    list_display = ('numero_table', 'nombre_places', 'user', 'current_status', 'created_at')
    list_filter = ('current_status',)
    search_fields = ('numero_table', 'user__login')
    readonly_fields = ('created_at', 'updated_at')
