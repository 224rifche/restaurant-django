from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'orders'

urlpatterns = [
    # Panier
    path('panier/', login_required(views.view_cart), name='view_cart'),
    path('panier/ajouter/<int:plat_id>/', login_required(views.add_to_cart), name='add_to_cart'),
    path('panier/modifier/<int:item_id>/', login_required(views.update_cart_item), name='update_cart_item'),
    path('panier/supprimer/<int:item_id>/', login_required(views.remove_from_cart), name='remove_from_cart'),
    
    # Commandes
    path('commander/', login_required(views.create_order), name='create_order'),
    path('commande/confirmation/<int:order_id>/', login_required(views.order_confirmation), name='order_confirmation'),
    path('commandes/', login_required(views.list_orders), name='list_orders'),
    path('commande/<int:order_id>/', login_required(views.view_order), name='view_order'),
    path('commande/<int:order_id>/servie/', login_required(views.mark_order_served), name='mark_order_served'),
    path('commande/<int:order_id>/payee/', login_required(views.mark_order_paid), name='mark_order_paid'),
    path('historique/', login_required(views.order_history), name='order_history'),
]
