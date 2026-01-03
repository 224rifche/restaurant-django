from django.shortcuts import render
from django.views import View

class Custom404View(View):
    def get(self, request, exception=None):
        return render(
            request,
            '404.html',
            context={
                'title': 'Page non trouvée',
                'message': 'La page que vous recherchez est introuvable.'
            },
            status=404
        )
