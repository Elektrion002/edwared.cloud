import os
import django
import sys

# Setup Django environment
sys.path.append(r'd:\VPS_Plat_Edwared_v01')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edwared_cloud.settings')
django.setup()

from apps.flores.models import Categoria, Producto, NotaVenta, CargaViaje

def check_db():
    print("Checking 'flores' database...")
    try:
        cat_count = Categoria.objects.using('flores').count()
        prod_count = Producto.objects.using('flores').count()
        nota_count = NotaVenta.objects.using('flores').count()
        carga_count = CargaViaje.objects.using('flores').count()
        
        print(f"Categories: {cat_count}")
        print(f"Products: {prod_count}")
        print(f"Notes: {nota_count}")
        print(f"Loads: {carga_count}")
        
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == '__main__':
    check_db()
