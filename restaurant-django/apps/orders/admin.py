from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Panier, PanierItem, Commande, CommandeItem


class PanierItemInline(admin.TabularInline):
    model = PanierItem
    extra = 0
    readonly_fields = ['plat', 'quantite', 'prix_unitaire', 'total_item']
    fields = ['plat', 'quantite', 'prix_unitaire', 'total_item']
    
    def total_item(self, obj):
        return obj.quantite * obj.prix_unitaire
    total_item.short_description = 'Total'


@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ['id', 'table', 'is_active', 'created_at', 'updated_at', 'total_panier']
    list_filter = ['is_active', 'created_at', 'table']
    search_fields = ['table__numero_table']
    readonly_fields = ['created_at', 'updated_at', 'total_panier']
    inlines = [PanierItemInline]
    
    def total_panier(self, obj):
        return obj.total
    total_panier.short_description = 'Total du panier'
    
    def has_add_permission(self, request):
        return False


class CommandeItemInline(admin.TabularInline):
    model = CommandeItem
    extra = 0
    readonly_fields = ['plat', 'quantite', 'prix_unitaire', 'total_item']
    fields = ['plat', 'quantite', 'prix_unitaire', 'total_item']
    
    def total_item(self, obj):
        return obj.total
    total_item.short_description = 'Total'


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = [
        'numero_commande', 'table', 'get_statut_display', 'montant_total', 
        'date_commande', 'date_service', 'date_paiement', 'view_items_link'
    ]
    list_filter = ['statut', 'date_commande', 'table']
    search_fields = ['numero_commande', 'table__numero_table', 'notes']
    readonly_fields = [
        'numero_commande', 'table', 'montant_total', 'date_commande', 
        'date_service', 'date_paiement', 'total_commande', 'view_items'
    ]
    fieldsets = [
        ('Informations de la commande', {
            'fields': [
                'numero_commande', 'table', 'statut', 'montant_total',
                'date_commande', 'date_service', 'date_paiement', 'notes'
            ]
        }),
        ('Détails', {
            'classes': ('collapse',),
            'fields': ['view_items'],
        }),
    ]
    inlines = [CommandeItemInline]
    actions = ['mark_as_served', 'mark_as_paid']
    
    def view_items_link(self, obj):
        return format_html(
            '<a href="{}" class="button">Voir les articles</a>',
            reverse('admin:orders_commande_change', args=[obj.id])
        )
    view_items_link.short_description = 'Articles'
    
    def view_items(self, obj):
        items = obj.items.select_related('plat').all()
        if not items:
            return "Aucun article dans cette commande."
        
        items_html = "<table class='table'>"
        items_html += "<tr><th>Plat</th><th>Quantité</th><th>Prix unitaire</th><th>Total</th></tr>"
        
        for item in items:
            items_html += f"""
            <tr>
                <td>{item.plat.nom}</td>
                <td>{item.quantite}</td>
                <td>{item.prix_unitaire} €</td>
                <td>{item.total} €</td>
            </tr>
            """
        
        items_html += f"""
        <tr>
            <td colspan="3" style="text-align: right;"><strong>Total:</strong></td>
            <td><strong>{obj.montant_total} €</strong></td>
        </tr>
        """
        items_html += "</table>"
        
        return mark_safe(items_html)
    view_items.short_description = 'Articles de la commande'
    
    def total_commande(self, obj):
        return obj.montant_total
    total_commande.short_description = 'Total de la commande'
    
    @admin.action(description='Marquer comme servie(s)')
    def mark_as_served(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(statut='en_attente').update(
            statut='servie',
            date_service=timezone.now()
        )
        self.message_user(
            request,
            f"{updated} commande(s) marquée(s) comme servie(s)."
        )
    
    @admin.action(description='Marquer comme payée(s)')
    def mark_as_paid(self, request, queryset):
        from django.utils import timezone
        updated = queryset.filter(statut='servie').update(
            statut='payee',
            date_paiement=timezone.now()
        )
        self.message_user(
            request,
            f"{updated} commande(s) marquée(s) comme payée(s)."
        )
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    
    def has_delete_permission(self, request, obj=None):
        # Seul un superutilisateur peut supprimer une commande
        return request.user.is_superuser


@admin.register(PanierItem)
class PanierItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'panier', 'plat', 'quantite', 'prix_unitaire', 'total_item']
    list_filter = ['panier__table']
    search_fields = ['plat__nom', 'panier__id']
    
    def total_item(self, obj):
        return obj.quantite * obj.prix_unitaire
    total_item.short_description = 'Total'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(CommandeItem)
class CommandeItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'commande', 'plat', 'quantite', 'prix_unitaire', 'total_item']
    list_filter = ['commande__statut', 'commande__table']
    search_fields = ['plat__nom', 'commande__numero_commande']
    
    def total_item(self, obj):
        return obj.total
    total_item.short_description = 'Total'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
