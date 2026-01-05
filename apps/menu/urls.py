from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    path('', views.list_dishes, name='list_dishes'),
    path('manage/', views.manage_dishes, name='manage_dishes'),
    path('categories/', views.manage_categories, name='manage_categories'),
    path('categories/create/', views.create_category, name='create_category'),
    path('categories/<int:category_id>/update/', views.update_category, name='update_category'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('create/', views.create_dish, name='create_dish'),
    path('<int:dish_id>/update/', views.update_dish, name='update_dish'),
    path('<int:dish_id>/toggle/', views.toggle_dish_availability, name='toggle_dish_availability'),
    path('<int:dish_id>/delete/', views.delete_dish, name='delete_dish'),
]
