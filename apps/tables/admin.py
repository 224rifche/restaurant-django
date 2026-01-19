from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.safestring import mark_safe
from django.conf import settings

from .models import TableRestaurant


def generate_qr_code(modeladmin, request, queryset):
    if queryset.count() != 1:
        modeladmin.message_user(request, "Veuillez sélectionner une seule table à la fois.", level=messages.ERROR)
        return
    
    table = queryset.first()
    if not table.user:
        modeladmin.message_user(
            request, 
            f"Aucun utilisateur n'est associé à la table {table.numero_table}.", 
            level=messages.ERROR
        )
        return
    
    # Générer le token si nécessaire
    if not table.qr_token:
        table.generate_qr_token()
    
    # Rediriger vers la vue de génération du QR code
    return redirect('tables:generate_qr_code', table_id=table.id)

generate_qr_code.short_description = "Générer le QR code"


def toggle_table_status(modeladmin, request, queryset):
    for table in queryset:
        if table.qr_status == 'blocked':
            table.unblock()
        else:
            table.block()
    
    modeladmin.message_user(
        request, 
        f"Statut de {queryset.count()} table(s) mis à jour avec succès.", 
        level=messages.SUCCESS
    )

toggle_table_status.short_description = "Basculer le statut (actif/bloqué)"


@admin.register(TableRestaurant)
class TableRestaurantAdmin(admin.ModelAdmin):
    list_display = (
        'numero_table', 
        'nombre_places', 
        'user', 
        'current_status', 
        'qr_status_display',
        'last_login_display',
        'created_at',
        'qr_code_actions'
    )
    list_filter = ('current_status', 'qr_status')
    search_fields = ('numero_table', 'user__login')
    readonly_fields = ('created_at', 'updated_at', 'last_login_at', 'last_login_ip', 'qr_token')
    actions = [generate_qr_code, toggle_table_status]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('numero_table', 'nombre_places', 'user', 'current_status')
        }),
        ('Gestion du QR Code', {
            'fields': ('qr_status', 'qr_token', 'last_login_at', 'last_login_ip')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def qr_status_display(self, obj):
        status_map = {
            'active': ('success', 'check-circle'),
            'inactive': ('secondary', 'minus-circle'),
            'blocked': ('danger', 'ban'),
        }
        color, icon = status_map.get(obj.qr_status, ('secondary', 'question-circle'))
        return format_html(
            '<span class="badge bg-{}">{} <i class="fas fa-{}"></i></span>',
            color, obj.get_qr_status_display(), icon
        )
    qr_status_display.short_description = 'Statut QR'
    qr_status_display.admin_order_field = 'qr_status'
    
    def last_login_display(self, obj):
        if obj.last_login_at:
            return format_html(
                '{}<br><small class="text-muted">{}</small>',
                obj.last_login_at.strftime('%d/%m/%Y %H:%M'),
                obj.last_login_ip or ''
            )
        return 'Jamais connecté'
    last_login_display.short_description = 'Dernière connexion'
    last_login_display.admin_order_field = 'last_login_at'
    
    def qr_code_actions(self, obj):
        buttons = []
        
        # Bouton pour générer/télécharger le QR code
        if obj.qr_status == 'active':
            buttons.append(
                f'<a href="{reverse("tables:generate_qr_code", args=[obj.id])}" '
                'class="button" title="Télécharger le QR code">'
                '<i class="fas fa-qrcode"></i> QR Code'
                '</a>'
            )
        else:
            buttons.append(
                f'<a href="{reverse("tables:generate_qr_code", args=[obj.id])}" '
                'class="button" title="Générer un QR code">'
                '<i class="fas fa-plus-circle"></i> Générer QR'
                '</a>'
            )
        
        # Bouton pour gérer le statut
        if obj.qr_status == 'blocked':
            buttons.append(
                f'<a href="#" onclick="return toggleTableStatus({obj.id}, this);" '
                'class="button" title="Débloquer la table">'
                '<i class="fas fa-unlock"></i>'
                '</a>'
            )
        else:
            buttons.append(
                f'<a href="#" onclick="return toggleTableStatus({obj.id}, this);" '
                'class="button" title="Bloquer la table">'
                '<i class="fas fa-lock"></i>'
                '</a>'
            )
        
        return format_html(' '.join(buttons))
    qr_code_actions.short_description = 'Actions'
    qr_code_actions.allow_tags = True
    
    class Media:
        js = [
            'admin/js/jquery.init.js',
            'js/qr_code_admin.js',
        ]
        css = {
            'all': ['css/qr_code_admin.css']
        }
