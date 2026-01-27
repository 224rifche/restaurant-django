from django.urls import path
from django.views.decorators.http import require_http_methods
from . import views
from .views_qr import (
    QRCodeAdminView, 
    # QRCodeLoginView,  # Commenté car la classe a été supprimée
    generate_qr_code, 
    toggle_table_status, 
    invalidate_all_table_qr_tokens,
    view_qr_code,
)

app_name = 'tables'

urlpatterns = [
    # URLs existantes pour la gestion des tables
    path('', views.list_tables, name='list_tables'),
    path('create/', views.create_table, name='create_table'),
    path('<int:table_id>/', views.table_detail, name='table_detail'),
    path('<int:table_id>/update/', views.update_table, name='update_table'),
    path('<int:table_id>/delete/', views.delete_table, name='delete_table'),
    
    # URLs pour la gestion des QR codes
    path('admin/qr-codes/', QRCodeAdminView.as_view(), name='qr_admin'),
    path('admin/generate-qr/<int:table_id>/', generate_qr_code, name='generate_qr_code'),
    path('admin/view-qr/<int:table_id>/', view_qr_code, name='view_qr_code'),
    path('admin/tables/<int:table_id>/toggle-status/', toggle_table_status, name='toggle_table_status'),
    path('admin/tables/invalidate-all/', invalidate_all_table_qr_tokens, name='invalidate_all_table_qr_tokens'),
    # path('qr/login/<str:token>/', QRCodeLoginView.as_view(), name='qr_login'),  # Désactivé car la vue a été supprimée
    path('<int:table_id>/qr/generate/', generate_qr_code, name='table_generate_qr_code'),
    path('<int:table_id>/qr/view/', view_qr_code, name='table_view_qr_code'),
]
