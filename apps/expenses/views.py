from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from apps.authentication.decorators import role_required
from apps.payments.models import Caisse, SortieCaisse, TypeDepense


@login_required
@role_required(['Rcomptable', 'Radmin'])
def create_depense(request):
    caisse = Caisse.get_caisse_ouverte()
    if not caisse:
        messages.error(request, "Aucune caisse n'est ouverte.")
        return redirect('payments:dashboard_caisse')

    if request.method == 'POST':
        type_depense_id = request.POST.get('type_depense')
        montant = request.POST.get('montant')
        motif = request.POST.get('motif')
        notes = request.POST.get('notes', '')
        justificatif = request.FILES.get('justificatif')

        if not (type_depense_id and montant and motif):
            messages.error(request, "Champs obligatoires manquants.")
            return redirect('expenses:create_depense')

        # Convertir le montant en Decimal pour la comparaison
        from decimal import Decimal, InvalidOperation
        try:
            montant_decimal = Decimal(montant)
        except InvalidOperation:
            messages.error(request, "Montant invalide.")
            return redirect('expenses:create_depense')

        # Vérifier que le solde de la caisse est suffisant (règle du cahier des charges)
        if montant_decimal > caisse.solde_actuel:
            messages.error(
                request, 
                f"Solde insuffisant. Solde actuel: {caisse.solde_actuel}€. "
                f"Montant demandé: {montant_decimal}€"
            )
            return redirect('expenses:create_depense')

        with transaction.atomic():
            # Créer la sortie de caisse
            SortieCaisse.objects.create(
                caisse=caisse,
                type_depense_id=type_depense_id,
                montant=montant_decimal,
                motif=motif,
                justificatif=justificatif,
                utilisateur=request.user,
                notes=notes,
            )
            # Mettre à jour le solde de la caisse
            caisse.solde_actuel -= montant_decimal
            caisse.save()

        messages.success(request, f"Dépense de {montant_decimal}€ enregistrée avec succès.")
        return redirect('payments:dashboard_caisse')

    types_depense = TypeDepense.objects.all().order_by('nom')
    return render(request, 'expenses/create_depense.html', {'caisse': caisse, 'types_depense': types_depense})
