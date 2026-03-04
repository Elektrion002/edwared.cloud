from django.shortcuts import render

def home(request):
    """
    Vista del Dashboard principal para el sistema de Flores.
    """
    return render(request, 'flores/dashboard.html')
