from django.shortcuts import render
from .models import Plataforma

def portal_landing(request):
    """
    Vista principal de la plataforma maestra (edwared.cloud).
    Muestra los clientes/plataformas activos.
    """
    plataformas_activas = Plataforma.objects.filter(activa=True, cliente__activo=True)
    return render(request, 'core/landing.html', {'plataformas': plataformas_activas})
