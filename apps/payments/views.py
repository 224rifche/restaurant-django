from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.db.models import Sum, Q, F, Count
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
from decimal import Decimal

from apps.authentication.decorators import role_required
from apps.orders.models import Commande
from .models import Caisse, Paiement, TypeDepense, SortieCaisse
from .forms import (
    CaisseForm, PaiementForm, TypeDepenseForm, 
    SortieCaisseForm, FilterCaisseForm, FilterPaiementForm, FilterSortieCaisseForm
)


# Vues pour la gestion de la caisse
@login_required
@role_required(['Rservent', 'Radmin', 'Rcomptable', 'Rcaissier'])
def dashboard_caisse(request):
    caisse = Caisse.get_caisse_ouverte()
    dernieres_sorties = SortieCaisse.objects.select_related('type_depense', 'utilisateur').order_by('-date_sortie')[:5]
    derniers_paiements = Paiement.objects.select_related('commande', 'utilisateur').order_by('-date_paiement')[:5]
    
    context = {
        'caisse': caisse,
        'dernieres_sorties': dernieres_sorties,
        'derniers_paiements': derniers_paiements,
    }
    return render(request, 'payments/dashboard_caisse.html', context)


class CaisseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Caisse
    form_class = CaisseForm
    template_name = 'payments/caisse_form.html'
    
    def test_func(self):
        return self.request.user.has_perm('payments.can_open_register')
    
    def handle_no_permission(self):
        messages.error(self.request, "Vous n'avez pas la permission d'ouvrir une caisse.")
        return super().handle_no_permission()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Ouvrir la caisse'
        return context
    
    def form_valid(self, form):
        form.instance.utilisateur_ouverture = self.request.user
        form.instance.est_ouverte = True
        
        # Vérifier qu'aucune caisse n'est déjà ouverte
        if Caisse.objects.filter(est_ouverte=True).exists():
            form.add_error(None, 'Une caisse est déjà ouverte. Veuillez d\'abord la fermer.')
            return self.form_invalid(form)
        
        messages.success(self.request, 'La caisse a été ouverte avec succès.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('payments:dashboard_caisse')

@login_required
def fermer_caisse(request, pk):
    if hasattr(request.user, 'role') and request.user.role == 'Rcomptable':
        messages.error(request, "🚫 Accès refusé : Vous n'êtes pas autorisé à effectuer cette action en tant que comptable.")
        return render(request, 'payments/fermer_caisse.html', {
            'form': CaisseForm(),
            'caisse': None,
            'error': "Action non autorisée pour les comptables"
        })
    
    try:
        caisse = Caisse.objects.get(pk=pk, est_ouverte=True)
    except Caisse.DoesNotExist:
        messages.error(request, "❌ Caisse introuvable ou déjà fermée.")
        return render(request, 'payments/fermer_caisse.html', {
            'form': CaisseForm(),
            'caisse': None,
            'error': "Caisse introuvable ou déjà fermée"
        })
    
    if request.method == 'POST':
        form = CaisseForm(request.POST, instance=caisse)
        if form.is_valid():
            with transaction.atomic():
                caisse = form.save(commit=False)
                caisse.est_ouverte = False
                caisse.date_fermeture = timezone.now()
                caisse.utilisateur_fermeture = request.user
                caisse.save()
                messages.success(request, "✅ Caisse fermée avec succès !")
                return redirect('payments:dashboard_caisse')
        else:
            messages.error(request, "❌ Erreur lors de la fermeture de la caisse. Vérifiez les données saisies.")
    else:
        form = CaisseForm(instance=caisse)
    
    return render(request, 'payments/dashboard_caisse.html', {
        'form': form,
        'caisse': caisse,
        'title': 'Fermer la caisse'
    })

class CaisseDetailView(LoginRequiredMixin, DetailView):
    model = Caisse
    template_name = 'payments/caisse_detail.html'
    context_object_name = 'caisse'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        caisse = self.get_object()
        
        # Statistiques des paiements par mode de paiement
        paiements_par_mode = (
            caisse.paiements.values('mode_paiement')
            .annotate(total=Sum('montant'))
            .order_by('-total')
        )
        
        # Dépenses par type
        depenses_par_type = (
            caisse.sorties.values('type_depense__nom')
            .annotate(total=Sum('montant'))
            .order_by('-total')
        )
        
        context.update({
            'paiements_par_mode': paiements_par_mode,
            'depenses_par_type': depenses_par_type,
            'paiements': caisse.paiements.select_related('commande', 'utilisateur').order_by('-date_paiement'),
            'sorties': caisse.sorties.select_related('type_depense', 'utilisateur').order_by('-date_sortie'),
        })
        return context


class CaisseListView(LoginRequiredMixin, ListView):
    model = Caisse
    template_name = 'payments/caisse_list.html'
    context_object_name = 'caisses'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'utilisateur_ouverture', 'utilisateur_fermeture'
        ).order_by('-date_ouverture')
        
        # Filtrage par date
        date_debut = self.request.GET.get('date_debut')
        date_fin = self.request.GET.get('date_fin')
        
        if date_debut:
            queryset = queryset.filter(date_ouverture__date__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_ouverture__date__lte=date_fin)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = FilterCaisseForm(self.request.GET or None)
        return context


# Vues pour les paiements
class PaiementCreateView(LoginRequiredMixin, CreateView):
    model = Paiement
    form_class = PaiementForm
    template_name = 'payments/paiement_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        commande_id = self.kwargs.get('commande_id')
        if commande_id:
            commande = get_object_or_404(Commande, pk=commande_id)
            initial.update({
                'commande': commande,
                'montant': commande.montant_total
            })
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        commande_id = self.kwargs.get('commande_id')
        if commande_id:
            context['commande'] = get_object_or_404(Commande, pk=commande_id)
        return context
    
    def form_valid(self, form):
        # Vérifier qu'une caisse est ouverte
        caisse = Caisse.get_caisse_ouverte()
        if not caisse:
            form.add_error(None, 'Aucune caisse n\'est ouverte. Veuillez ouvrir une caisse avant d\'enregistrer un paiement.')
            return self.form_invalid(form)
        
        # Vérifier que la commande n'est pas déjà payée
        commande = form.cleaned_data['commande']
        if hasattr(commande, 'paiement'):
            form.add_error('commande', 'Cette commande a déjà été payée.')
            return self.form_invalid(form)
        
        # S'assurer que le montant correspond à celui de la commande
        if form.cleaned_data['montant'] != commande.montant_total:
            form.add_error('montant', f'Le montant doit être de {commande.montant_total} GNF')
            return self.form_invalid(form)
        
        # Ajouter la caisse et l'utilisateur
        form.instance.caisse = caisse
        form.instance.utilisateur = self.request.user
        
        # Marquer la commande comme payée
        commande.statut = 'payee'
        commande.caissier = self.request.user
        commande.save()
        
        messages.success(self.request, 'Le paiement a été enregistré avec succès.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('payments:detail_paiement', kwargs={'pk': self.object.pk})


class PaiementDetailView(LoginRequiredMixin, DetailView):
    model = Paiement
    template_name = 'payments/paiement_detail.html'
    context_object_name = 'paiement'


class PaiementListView(LoginRequiredMixin, ListView):
    model = Paiement
    template_name = 'payments/paiement_list.html'
    context_object_name = 'paiements'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'commande', 'utilisateur', 'caisse'
        ).order_by('-date_paiement')
        
        # Filtrage par date
        date_debut = self.request.GET.get('date_debut')
        date_fin = self.request.GET.get('date_fin')
        mode_paiement = self.request.GET.get('mode_paiement')
        
        if date_debut:
            queryset = queryset.filter(date_paiement__date__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_paiement__date__lte=date_fin)
        if mode_paiement:
            queryset = queryset.filter(mode_paiement=mode_paiement)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculer le total des paiements
        total_paiements = self.get_queryset().aggregate(
            total=Sum('montant')
        )['total'] or 0
        
        # Statistiques par mode de paiement
        stats_paiements = (
            self.get_queryset().values('mode_paiement')
            .annotate(total=Sum('montant'), count=Count('id'))
            .order_by('-total')
        )
        
        context.update({
            'total_paiements': total_paiements,
            'stats_paiements': stats_paiements,
            'filter_form': FilterPaiementForm(self.request.GET or None),
        })
        return context


# Vues pour les types de dépenses
class TypeDepenseListView(LoginRequiredMixin, ListView):
    model = TypeDepense
    template_name = 'payments/typedepense_list.html'
    context_object_name = 'types_depense'
    
    def get_queryset(self):
        return TypeDepense.objects.annotate(
            total_depenses=Sum('sorties__montant')
        ).order_by('nom')


class TypeDepenseCreateView(LoginRequiredMixin, CreateView):
    model = TypeDepense
    form_class = TypeDepenseForm
    template_name = 'payments/typedepense_form.html'
    success_url = reverse_lazy('payments:liste_types_depense')


class TypeDepenseUpdateView(LoginRequiredMixin, UpdateView):
    model = TypeDepense
    form_class = TypeDepenseForm
    template_name = 'payments/typedepense_form.html'
    success_url = reverse_lazy('payments:liste_types_depense')


class TypeDepenseDeleteView(LoginRequiredMixin, DeleteView):
    model = TypeDepense
    template_name = 'payments/typedepense_confirm_delete.html'
    success_url = reverse_lazy('payments:liste_types_depense')
    
    def delete(self, request, *args, **kwargs):
        type_depense = self.get_object()
        if type_depense.sorties.exists():
            messages.error(request, 'Impossible de supprimer ce type de dépense car il est utilisé par des sorties de caisse.')
            return redirect('payments:liste_types_depense')
        return super().delete(request, *args, **kwargs)


# Vues pour les sorties de caisse
class SortieCaisseCreateView(LoginRequiredMixin, CreateView):
    model = SortieCaisse
    form_class = SortieCaisseForm
    template_name = 'payments/sortiecaisse_form.html'
    
    def get_initial(self):
        initial = super().get_initial()
        initial['utilisateur'] = self.request.user
        return initial
    
    def form_valid(self, form):
        # Vérifier qu'une caisse est ouverte
        caisse = Caisse.get_caisse_ouverte()
        if not caisse:
            form.add_error(None, 'Aucune caisse n\'est ouverte. Veuillez ouvrir une caisse avant d\'enregistrer une sortie.')
            return self.form_invalid(form)
        
        form.instance.caisse = caisse
        form.instance.utilisateur = self.request.user
        
        messages.success(self.request, 'La sortie de caisse a été enregistrée avec succès.')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('payments:detail_sortie', kwargs={'pk': self.object.pk})


class SortieCaisseDetailView(LoginRequiredMixin, DetailView):
    model = SortieCaisse
    template_name = 'payments/sortiecaisse_detail.html'
    context_object_name = 'sortie'


class SortieCaisseUpdateView(LoginRequiredMixin, UpdateView):
    model = SortieCaisse
    form_class = SortieCaisseForm
    template_name = 'payments/sortiecaisse_form.html'
    
    def get_success_url(self):
        return reverse('payments:detail_sortie', kwargs={'pk': self.object.pk})


class SortieCaisseDeleteView(LoginRequiredMixin, DeleteView):
    model = SortieCaisse
    template_name = 'payments/sortiecaisse_confirm_delete.html'
    success_url = reverse_lazy('payments:liste_sorties')
    
    def delete(self, request, *args, **kwargs):
        sortie = self.get_object()
        if sortie.caisse.est_ouverte is False:
            messages.error(request, 'Impossible de supprimer une sortie de caisse d\'une caisse déjà fermée.')
            return redirect('payments:detail_sortie', pk=sortie.pk)
        return super().delete(request, *args, **kwargs)


class SortieCaisseListView(LoginRequiredMixin, ListView):
    model = SortieCaisse
    template_name = 'payments/sortiecaisse_list.html'
    context_object_name = 'sorties'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'type_depense', 'utilisateur', 'caisse'
        ).order_by('-date_sortie')
        
        # Filtrage
        type_depense = self.request.GET.get('type_depense')
        date_debut = self.request.GET.get('date_debut')
        date_fin = self.request.GET.get('date_fin')
        
        if type_depense:
            queryset = queryset.filter(type_depense_id=type_depense)
        if date_debut:
            queryset = queryset.filter(date_sortie__date__gte=date_debut)
        if date_fin:
            queryset = queryset.filter(date_sortie__date__lte=date_fin)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculer le total des sorties
        total_sorties = self.get_queryset().aggregate(
            total=Sum('montant')
        )['total'] or 0
        
        # Statistiques par type de dépense
        stats_depenses = (
            self.get_queryset().values('type_depense__nom')
            .annotate(total=Sum('montant'), count=Count('id'))
            .order_by('-total')
        )
        
        context.update({
            'total_sorties': total_sorties,
            'stats_depenses': stats_depenses,
            'types_depense': TypeDepense.objects.all(),
            'filter_form': FilterSortieCaisseForm(self.request.GET or None),
        })
        return context


# Vues API pour AJAX
@login_required
@require_http_methods(['GET'])
def get_caisse_ouverte_status(request):
    caisse = Caisse.get_caisse_ouverte()
    return JsonResponse({
        'est_ouverte': caisse is not None,
        'solde_actuel': str(caisse.solde_actuel) if caisse else '0.00',
        'date_ouverture': caisse.date_ouverture.isoformat() if caisse else None,
    })


@login_required
@require_http_methods(['POST'])
def ajouter_fond_caisse(request):
    if not request.user.has_perm('payments.can_open_register'):
        return JsonResponse({'success': False, 'error': 'Permission refusée'}, status=403)
    
    try:
        montant = Decimal(request.POST.get('montant', '0'))
        if montant <= 0:
            raise ValueError('Le montant doit être supérieur à zéro')
        
        caisse = Caisse.get_caisse_ouverte()
        if caisse:
            caisse.solde_initial += montant
            caisse.solde_actuel += montant
            caisse.save()
            
            # Enregistrer une sortie de caisse pour le fond de caisse
            type_fond, _ = TypeDepense.objects.get_or_create(
                nom='Fond de caisse',
                defaults={'description': 'Fond de caisse initial et ajouts'}
            )
            
            SortieCaisse.objects.create(
                caisse=caisse,
                type_depense=type_fond,
                montant=montant,
                motif=f'Ajout de fonds par {request.user.get_full_name()}',
                utilisateur=request.user
            )
            
            return JsonResponse({
                'success': True,
                'solde_actuel': str(caisse.solde_actuel),
                'message': f'Fond de caisse augmenté de {montant} GNF avec succès.'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Aucune caisse ouverte. Veuillez d\'abord ouvrir une caisse.'
            }, status=400)
    except (ValueError, TypeError) as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': 'Une erreur est survenue'}, status=500)


@login_required
@require_http_methods(['GET'])
def stats_caisse(request):
    if not request.user.has_perm('payments.can_view_register'):
        return JsonResponse({'error': 'Permission refusée'}, status=403)
    
    caisse = Caisse.get_caisse_ouverte()
    if not caisse:
        return JsonResponse({'error': 'Aucune caisse ouverte'}, status=400)
    
    # Total des paiements par mode
    paiements = (
        caisse.paiements.values('mode_paiement')
        .annotate(total=Sum('montant'))
        .order_by('-total')
    )
    
    # Total des dépenses par type
    depenses = (
        caisse.sorties.values('type_depense__nom')
        .annotate(total=Sum('montant'))
        .order_by('-total')
    )
    
    # Dernières opérations
    dernieres_operations = []
    
    # Ajouter les paiements
    for p in caisse.paiements.order_by('-date_paiement')[:5]:
        dernieres_operations.append({
            'type': 'paiement',
            'date': p.date_paiement,
            'libelle': f'Paiement commande {p.commande.numero_commande}',
            'montant': p.montant,
            'classe': 'text-green-600',
            'icone': 'fa-credit-card'
        })
    
    # Ajouter les sorties
    for s in caisse.sorties.order_by('-date_sortie')[:5]:
        dernieres_operations.append({
            'type': 'sortie',
            'date': s.date_sortie,
            'libelle': f'Sortie: {s.type_depense.nom}',
            'montant': -s.montant,
            'classe': 'text-red-600',
            'icone': 'fa-money-bill-transfer'
        })
    
    # Trier par date
    dernieres_operations.sort(key=lambda x: x['date'], reverse=True)
    
    return JsonResponse({
        'paiements_par_mode': list(paiements),
        'depenses_par_type': list(depenses),
        'dernieres_operations': [{
            'type': op['type'],
            'date': op['date'].strftime('%d/%m/%Y %H:%M'),
            'libelle': op['libelle'],
            'montant': str(op['montant']),
            'classe': op['classe'],
            'icone': op['icone']
        } for op in dernieres_operations],
        'solde_actuel': str(caisse.solde_actuel),
        'solde_theorique': str(caisse.solde_theorique),
        'difference': str(caisse.difference)
    })
