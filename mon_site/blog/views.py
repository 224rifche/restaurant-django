from django.shortcuts import render

def index(request):
    context = {
        'title': 'Blog',
        'articles': [
            {'title': 'Premier article', 'content': 'Contenu du premier article...'},
            {'title': 'Découverte de Django', 'content': 'Pourquoi j\'ai choisi Django pour mon projet...'},
            {'title': 'Conseils pour les débutants', 'content': 'Quelques conseils pour bien commencer avec Django...'},
        ]
    }
    return render(request, 'blog/index.html', context)
