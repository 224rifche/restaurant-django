from django.urls import path
from . import views

app_name = 'tables'

urlpatterns = [
    path('', views.list_tables, name='list_tables'),
    path('create/', views.create_table, name='create_table'),
    path('<int:table_id>/', views.table_detail, name='table_detail'),
    path('<int:table_id>/update/', views.update_table, name='update_table'),
    path('<int:table_id>/delete/', views.delete_table, name='delete_table'),
]
