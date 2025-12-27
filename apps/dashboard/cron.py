"""
CronJob pour l'envoi quotidien du rapport de caisse par email
Configuration dans settings.py:
CRONJOBS = [
    ('0 0 * * *', 'apps.dashboard.cron.send_daily_cash_report'),
]

Pour activer les crons:
python manage.py crontab add
"""
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from apps.authentication.models import CustomUser
from apps.payments.models import Caisse, Paiement, SortieCaisse
from apps.orders.models import Commande


def send_daily_cash_report():
    """
    Envoie un rapport quotidien de la caisse à l'administrateur par email.
    Calcule: somme des paiements - somme des dépenses pour la journée.
    """
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    # Récupérer les données du jour précédent
    paiements = Paiement.objects.filter(date_paiement__date=yesterday)
    depenses = SortieCaisse.objects.filter(date_sortie__date=yesterday)
    commandes = Commande.objects.filter(date_commande__date=yesterday)
    
    # Calculer les totaux
    total_paiements = paiements.aggregate(total=Sum('montant'))['total'] or Decimal('0')
    total_depenses = depenses.aggregate(total=Sum('montant'))['total'] or Decimal('0')
    solde_net = total_paiements - total_depenses
    
    nb_commandes = commandes.count()
    nb_paiements = paiements.count()
    nb_depenses = depenses.count()
    
    # Panier moyen
    panier_moyen = total_paiements / nb_paiements if nb_paiements > 0 else Decimal('0')
    
    # Récupérer la caisse actuelle
    caisse = Caisse.get_caisse_ouverte() or Caisse.get_derniere_caisse()
    
    # Préparer le contexte pour l'email
    context = {
        'date': yesterday,
        'total_paiements': total_paiements,
        'total_depenses': total_depenses,
        'solde_net': solde_net,
        'nb_commandes': nb_commandes,
        'nb_paiements': nb_paiements,
        'nb_depenses': nb_depenses,
        'panier_moyen': panier_moyen,
        'caisse': caisse,
        'paiements': paiements.select_related('commande', 'utilisateur')[:10],
        'depenses': depenses.select_related('type_depense', 'utilisateur')[:10],
    }
    
    # Générer le contenu HTML de l'email
    html_content = render_to_string('dashboard/email/daily_report.html', context)
    text_content = strip_tags(html_content)
    
    # Récupérer les emails des administrateurs
    admin_emails = list(
        CustomUser.objects.filter(
            role='Radmin',
            is_active=True
        ).exclude(
            email__isnull=True
        ).exclude(
            email=''
        ).values_list('email', flat=True)
    )
    
    # Si pas d'emails admin, utiliser l'email par défaut
    if not admin_emails:
        admin_emails = [settings.DEFAULT_FROM_EMAIL]
    
    # Envoyer l'email
    try:
        send_mail(
            subject=f'📊 Rapport de caisse du {yesterday.strftime("%d/%m/%Y")} - RestauPro',
            message=text_content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            html_message=html_content,
            fail_silently=False,
        )
        return {
            'success': True,
            'date': yesterday,
            'recipients': admin_emails,
            'solde_net': solde_net
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def update_daily_caisse_balance():
    """
    Met à jour automatiquement le solde de la caisse en calculant:
    somme des paiements - somme des dépenses
    """
    today = timezone.now().date()
    
    caisse = Caisse.get_caisse_ouverte()
    if not caisse:
        return {'success': False, 'error': 'Aucune caisse ouverte'}
    
    # Calculer les totaux pour la caisse actuelle
    total_paiements = caisse.paiements.aggregate(total=Sum('montant'))['total'] or Decimal('0')
    total_depenses = caisse.sorties.aggregate(total=Sum('montant'))['total'] or Decimal('0')
    
    # Calculer le nouveau solde
    nouveau_solde = caisse.solde_initial + total_paiements - total_depenses
    
    # Mettre à jour le solde
    ancien_solde = caisse.solde_actuel
    caisse.solde_actuel = nouveau_solde
    caisse.save()
    
    return {
        'success': True,
        'date': today,
        'ancien_solde': ancien_solde,
        'nouveau_solde': nouveau_solde,
        'difference': nouveau_solde - ancien_solde
    }
