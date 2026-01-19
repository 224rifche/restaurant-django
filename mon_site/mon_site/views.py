from django.shortcuts import render


def index(request):
    return render(request, "mon_site/index.html")