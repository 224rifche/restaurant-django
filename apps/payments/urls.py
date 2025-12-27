from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.dashboard_caisse, name='dashboard_caisse'),

    # Caisse
    path('caisses/', views.CaisseListView.as_view(), name='liste_caisses'),
    path('caisses/ouvrir/', views.CaisseCreateView.as_view(), name='ouvrir_caisse'),
    path('caisses/<int:pk>/', views.CaisseDetailView.as_view(), name='detail_caisse'),
    path('caisses/<int:pk>/fermer/', views.fermer_caisse, name='fermer_caisse'),

    # Paiements
    path('paiements/', views.PaiementListView.as_view(), name='liste_paiements'),
    path('paiements/<int:pk>/', views.PaiementDetailView.as_view(), name='detail_paiement'),
    path('paiements/nouveau/', views.PaiementCreateView.as_view(), name='creer_paiement'),
    path('paiements/commande/<int:commande_id>/nouveau/', views.PaiementCreateView.as_view(), name='creer_paiement_commande'),

    # Types de dépense
    path('types-depense/', views.TypeDepenseListView.as_view(), name='liste_types_depense'),
    path('types-depense/nouveau/', views.TypeDepenseCreateView.as_view(), name='creer_type_depense'),
    path('types-depense/<int:pk>/modifier/', views.TypeDepenseUpdateView.as_view(), name='modifier_type_depense'),
    path('types-depense/<int:pk>/supprimer/', views.TypeDepenseDeleteView.as_view(), name='supprimer_type_depense'),

    # Sorties de caisse
    path('sorties/', views.SortieCaisseListView.as_view(), name='liste_sorties'),
    path('sorties/nouveau/', views.SortieCaisseCreateView.as_view(), name='creer_sortie'),
    path('sorties/<int:pk>/', views.SortieCaisseDetailView.as_view(), name='detail_sortie'),
    path('sorties/<int:pk>/modifier/', views.SortieCaisseUpdateView.as_view(), name='modifier_sortie'),
    path('sorties/<int:pk>/supprimer/', views.SortieCaisseDeleteView.as_view(), name='supprimer_sortie'),

    # API
    path('api/caisse/status/', views.get_caisse_ouverte_status, name='api_caisse_status'),
    path('api/caisse/stats/', views.stats_caisse, name='api_caisse_stats'),
    path('api/caisse/ajouter-fond/', views.ajouter_fond_caisse, name='ajouter_fond_caisse'),
]
