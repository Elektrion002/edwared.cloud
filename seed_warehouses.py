import os
import django
import sys

# Setup Django environment
sys.path.append(r'd:\VPS_Plat_Edwared_v01')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edwared_cloud.settings')
django.setup()

from apps.flores.models import Almacen

def seed_warehouses():
    warehouses = [
        {'nombre': 'Almacen tienda flores 01', 'ubicacion': 'Sede Principal'},
        {'nombre': 'Almacen tienda 02', 'ubicacion': 'Sucursal Norte'},
    ]
    for w_data in warehouses:
        almacen, created = Almacen.objects.using('flores').get_or_create(
            nombre=w_data['nombre'],
            defaults={'ubicacion': w_data['ubicacion'], 'activo': True}
        )
        if created:
            print(f"Created warehouse: {w_data['nombre']}")
        else:
            print(f"Warehouse already exists: {w_data['nombre']}")

if __name__ == '__main__':
    seed_warehouses()
