from django.urls import path

from . import views
from . import exports

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    # Exports
    path('export/ventes/excel/', exports.export_ventes_excel, name='export_ventes_excel'),
    path('export/ventes/pdf/', exports.export_ventes_pdf, name='export_ventes_pdf'),
    path('export/commandes/excel/', exports.export_commandes_excel, name='export_commandes_excel'),
]
