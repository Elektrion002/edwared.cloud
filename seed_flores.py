import os
import django
import sys

# Setup Django environment
sys.path.append(r'd:\VPS_Plat_Edwared_v01')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edwared_cloud.settings')
django.setup()

from apps.flores.models import Categoria, Producto
from django.db import connections
from django.db.utils import OperationalError

def seed_data():
    db_conn = connections['flores']
    try:
        db_conn.ensure_connection()
        print("Using 'flores' database (Postgres via Tunnel or SQLite).")
    except OperationalError:
        print("Warning: Could not connect to 'flores' database. Retrying with default if appropriate.")
    
    categories = {
        'Rosas': [
            'Rosa Roja', 'Rosa Blanca', 'Rosa Amarilla', 'Rosa Lila',
            'Rosa Fiusha', 'Rosa Naranja', 'Rosa Safy', 'Rosa Shimer',
            'Rosa Pink Mundial', 'Rosa Caricia', 'Rosa Hermosa', 'Rosa Fashion'
        ],
        'Docenas/Margaritas': [
            'Polares', 'Chenas', 'Godornis', 'Rados', 'Cristal',
            'Argentinas', 'Anat', 'Uvas', 'Holandesa', 'Vikingo',
            'Luneta', 'Pandas', 'Roxanas', 'Chabelas'
        ],
        'Follajes/Especialidades': [
            'Estatis', 'Gypsofilia', 'Solidagos', 'Japones', 'Tulia',
            'Cambray', 'Camedor', 'Hojas', 'Dólar Moneda', 'Dólar',
            'Eucalipto', 'Parbifolia', 'Acacia Dura', 'Mini Dólar',
            'Jani Mirlo', 'Hoja de Plata'
        ],
        'Flores de Corte': [
            'Gerbera', 'Lilis', 'Girasol'
        ]
    }

    for cat_name, products in categories.items():
        category, _ = Categoria.objects.using('flores').get_or_create(nombre=cat_name)
        for prod_name in products:
            Producto.objects.using('flores').get_or_create(
                nombre=prod_name,
                categoria=category
            )
    print("Catalog seeding completed successfully.")

if __name__ == '__main__':
    seed_data()
