from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.views.static import serve
from restaurant_management import views as project_views

handler404 = 'restaurant_management.views.error_404_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.authentication.urls')),
    path('tables/', include('apps.tables.urls')),
    path('menu/', include('apps.menu.urls')),
    path('orders/', include('apps.orders.urls')),
    path('payments/', include('apps.payments.urls')),
    path('expenses/', include('apps.expenses.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    
    # Diagnostic des médias (uniquement en développement)
    path('diagnostic/media/', project_views.media_diagnostic, name='media_diagnostic'),
    
    # Redirection pour les URLs vides ou racine
    path('', RedirectView.as_view(url='/login/', permanent=False), name='home'),
]

# Servir les fichiers statiques et médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Servir les fichiers médias en production (solution de fallback)
elif not getattr(settings, 'USE_S3', False):
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]

# Gestion des erreurs 404 (uniquement en production)
if not settings.DEBUG:
    urlpatterns += [
        re_path(r'^.*$', project_views.error_404_view, name='error_404'),
    ]
