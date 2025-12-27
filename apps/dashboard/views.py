from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.authentication.decorators import role_required
from apps.payments.models import Caisse
from apps.orders.models import Commande


@login_required
@role_required(['Radmin', 'Rcomptable', 'Rservent'])
def dashboard_home(request):
    caisse = Caisse.get_caisse_ouverte()
    commandes_en_attente = Commande.objects.filter(statut='en_attente').count()
    commandes_servies = Commande.objects.filter(statut='servie').count()
    commandes_payees = Commande.objects.filter(statut='payee').count()

    return render(request, 'dashboard/home.html', {
        'caisse': caisse,
        'commandes_en_attente': commandes_en_attente,
        'commandes_servies': commandes_servies,
        'commandes_payees': commandes_payees,
    })
