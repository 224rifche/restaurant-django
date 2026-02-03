from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from datetime import timedelta
import json

from apps.authentication.decorators import role_required
from apps.authentication.models import CustomUser
from apps.payments.models import Caisse, Paiement, SortieCaisse
from apps.orders.models import Commande
from apps.tables.models import TableRestaurant
from apps.menu.models import Plat


@login_required
@role_required(['Radmin', 'Rcomptable', 'Rservent'])
def dashboard_home(request):
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Caisse actuelle
    caisse = Caisse.get_caisse_ouverte()
    
    # Statistiques des commandes
    commandes_en_attente = Commande.objects.filter(statut='en_attente').count()
    commandes_servies = Commande.objects.filter(statut='servie').count()
    commandes_payees_today = Commande.objects.filter(
        statut='payee', 
        date_paiement__date=today
    ).count()
    
    # Chiffre d'affaires
    ca_today = Paiement.objects.filter(
        date_paiement__date=today
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    ca_week = Paiement.objects.filter(
        date_paiement__date__gte=week_ago
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    ca_month = Paiement.objects.filter(
        date_paiement__date__gte=month_ago
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    # Dépenses
    depenses_today = SortieCaisse.objects.filter(
        date_sortie__date=today
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    depenses_month = SortieCaisse.objects.filter(
        date_sortie__date__gte=month_ago
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    # Statistiques des tables
    tables_total = TableRestaurant.objects.count()
    tables_libres = TableRestaurant.objects.filter(current_status='libre').count()
    tables_occupees = tables_total - tables_libres
    
    # Commande moyenne
    commande_moyenne = Commande.objects.filter(
        statut='payee',
        date_paiement__date__gte=month_ago
    ).aggregate(avg=Avg('montant_total'))['avg'] or 0
    
    # Données pour le graphique des ventes (7 derniers jours)
    ventes_par_jour = Paiement.objects.filter(
        date_paiement__date__gte=week_ago
    ).annotate(
        jour=TruncDate('date_paiement')
    ).values('jour').annotate(
        total=Sum('montant'),
        count=Count('id')
    ).order_by('jour')
    
    # Formater les données pour Chart.js
    chart_labels = []
    chart_data = []
    chart_counts = []
    
    for i in range(7):
        date = week_ago + timedelta(days=i)
        chart_labels.append(date.strftime('%d/%m'))
        
        vente = next((v for v in ventes_par_jour if v['jour'] == date), None)
        chart_data.append(float(vente['total']) if vente else 0)
        chart_counts.append(vente['count'] if vente else 0)
    
    # Plats les plus vendus
    plats_populaires = Plat.objects.annotate(
        nb_commandes=Count('commande_items')
    ).order_by('-nb_commandes')[:5]
    
    # Dernières commandes
    dernieres_commandes = Commande.objects.select_related('table').order_by('-date_commande')[:5]
    
    # Derniers paiements
    derniers_paiements = Paiement.objects.select_related(
        'commande', 'utilisateur'
    ).order_by('-date_paiement')[:5]
    
    # Dernières dépenses
    dernieres_depenses = SortieCaisse.objects.select_related(
        'type_depense', 'utilisateur'
    ).order_by('-date_sortie')[:5]
    
    # Statistiques utilisateurs (admin seulement)
    nb_utilisateurs = CustomUser.objects.filter(is_active=True).count()
    
    context = {
        'caisse': caisse,
        'commandes_en_attente': commandes_en_attente,
        'commandes_servies': commandes_servies,
        'commandes_payees_today': commandes_payees_today,
        'ca_today': ca_today,
        'ca_week': ca_week,
        'ca_month': ca_month,
        'depenses_today': depenses_today,
        'depenses_month': depenses_month,
        'tables_total': tables_total,
        'tables_libres': tables_libres,
        'tables_occupees': tables_occupees,
        'commande_moyenne': round(commande_moyenne, 2),
        'chart_labels': json.dumps(chart_labels),
        'chart_data': json.dumps(chart_data),
        'chart_counts': json.dumps(chart_counts),
        'plats_populaires': plats_populaires,
        'dernieres_commandes': dernieres_commandes,
        'derniers_paiements': derniers_paiements,
        'dernieres_depenses': dernieres_depenses,
        'nb_utilisateurs': nb_utilisateurs,
    }
    
    return render(request, 'dashboard/home.html', context)
