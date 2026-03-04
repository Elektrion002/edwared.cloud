import os
import django
import sys

import environ

env = environ.Env()
environ.Env.read_env(os.path.join(os.path.dirname(__file__), '.env'))

# Setup Django Environment (Local pointing to Production via Tunnel)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edwared_cloud.settings')
django.setup()

from django.contrib.auth.models import User
from apps.panaderia.models import StaffPanaderia

def create_staff(username, pin):
    print(f"Buscando o creando usuario base {username}...")
    user, created = User.objects.using('edwared_master').get_or_create(username=username)
    user.set_password(pin)
    user.save(using='edwared_master')
    
    print(f"Sincronizando perfil StaffPanaderia para {username} en db_panaderia...")
    staff, created = StaffPanaderia.objects.using('panaderia').update_or_create(
        user=user,
        defaults={
            'username': username,
            'nombre': 'Eduardo',
            'apellidos': 'Staff' if username == 'edwared001' else 'Admin',
            'pin': pin,
            'activo': True
        }
    )
    print(f"¡Éxito! Cajero {username} listo para produccion VPS.")

create_staff('edwared001', '0686')
create_staff('edwared002', '0686')
