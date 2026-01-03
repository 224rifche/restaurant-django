from django.shortcuts import render
 
def error_404_view(request, exception=None):
    return render(request, '404.html', {'requested_path': request.path}, status=404)
