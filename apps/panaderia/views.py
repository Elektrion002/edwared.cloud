from django.shortcuts import render

def home(request):
    """
    Vista del Dashboard principal para el sistema de Panadería.
    """
    return render(request, 'panaderia/dashboard.html')
