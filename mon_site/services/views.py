from django.shortcuts import render

def index(request):
    context = {
        'title': 'Services',
        'services': [
            {'name': 'Développement Web', 'description': 'Création de sites web modernes et réactifs'},
            {'name': 'Conception UI/UX', 'description': 'Design d\'interfaces utilisateur intuitives'},
            {'name': 'Maintenance', 'description': 'Maintenance et mise à jour de sites existants'},
        ]
    }
    return render(request, 'services/index.html', context)
