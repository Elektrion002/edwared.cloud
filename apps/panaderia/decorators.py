from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages

def login_staff_requerido(view_func):
    """
    Decorador que verifica si hay un ID de staff en la sesión.
    Si no lo hay, lo manda al login de staff.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('staff_panaderia_id'):
            messages.error(request, "Acceso denegado. Inicia sesión como administrador o cajero.")
            return redirect('panaderia:staff_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view
