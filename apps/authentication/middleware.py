from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import logout


class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.exempt_urls = [
            reverse('authentication:login'),
            reverse('authentication:logout'),
            '/admin/',
            '/static/',
            '/media/',
        ]

    def __call__(self, request):
        if not request.user.is_authenticated:
            if not any(request.path.startswith(url) for url in self.exempt_urls):
                return redirect('authentication:login')
        
        elif not request.user.is_active:
            logout(request)
            return redirect('authentication:login')

        response = self.get_response(request)
        return response
