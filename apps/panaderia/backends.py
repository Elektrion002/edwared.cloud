from django.contrib.auth.backends import BaseBackend
from .models import StaffPanaderia
from django.contrib.auth.hashers import check_password

class StaffPanaderiaBackend(BaseBackend):
    """
    Backend personalizado para autenticar usuarios Staff en la App Panadería
    usando la base de datos `db_panaderia` de forma aislada.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Buscamos al usuario explícitamente en la db de panaderia
            user = StaffPanaderia.objects.using('panaderia').get(username=username, activo=True)
            # Aceptamos tanto la contraseña completa como el PIN rápido de 4 dígitos
            if user.check_password(password) or user.pin_seguridad == password:
                return user
        except StaffPanaderia.DoesNotExist:
            return None
            
    def get_user(self, user_id):
        try:
            return StaffPanaderia.objects.using('panaderia').get(pk=user_id)
        except StaffPanaderia.DoesNotExist:
            return None
