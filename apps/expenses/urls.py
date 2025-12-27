from django.urls import path

from . import views

app_name = 'expenses'

urlpatterns = [
    path('nouveau/', views.create_depense, name='create_depense'),
]
