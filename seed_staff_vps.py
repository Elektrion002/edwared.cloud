import os
import django

# Setup Django Environment (Local to the VPS)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edwared_cloud.settings')
django.setup()

from django.contrib.auth.models import User
from apps.panaderia.models import StaffPanaderia

def create_staff(username, pin, role):
    print(f"Buscando o creando usuario base {username}...")
    user, created = User.objects.using('default').get_or_create(username=username)
    user.set_password(pin)
    user.save(using='default')
    
    print(f"Sincronizando perfil StaffPanaderia para {username} en db_panaderia...")
    staff, created = StaffPanaderia.objects.using('panaderia').update_or_create(
        username=username,
        defaults={
            'nombres': 'Eduardo',
            'apellidos': 'Staff VPS',
            'rol': role,
            'pin_seguridad': pin,
            'activo': True
        }
    )
    print(f"¡Éxito! Cajero {username} listo para produccion VPS.")

create_staff('edwared001', '0686', 'ADMIN')
create_staff('edwared002', '0686', 'CAJERO')
