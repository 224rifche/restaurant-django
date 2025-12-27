from django.contrib import admin

from .models import Caisse, Paiement, TypeDepense, SortieCaisse


@admin.register(Caisse)
class CaisseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'est_ouverte',
        'date_ouverture',
        'date_fermeture',
        'solde_initial',
        'solde_actuel',
        'utilisateur_ouverture',
        'utilisateur_fermeture',
    )
    list_filter = ('est_ouverte', 'date_ouverture')
    search_fields = ('utilisateur_ouverture__login', 'utilisateur_fermeture__login')


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'commande',
        'montant',
        'mode_paiement',
        'date_paiement',
        'caisse',
        'utilisateur',
    )
    list_filter = ('mode_paiement', 'date_paiement')
    search_fields = ('commande__numero_commande', 'utilisateur__login', 'reference')


@admin.register(TypeDepense)
class TypeDepenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'nom')
    search_fields = ('nom',)


@admin.register(SortieCaisse)
class SortieCaisseAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'type_depense',
        'montant',
        'motif',
        'date_sortie',
        'caisse',
        'utilisateur',
    )
    list_filter = ('type_depense', 'date_sortie')
    search_fields = ('motif', 'utilisateur__login')
