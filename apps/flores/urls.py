from django.urls import path
from . import views, admin_views

app_name = 'flores'

urlpatterns = [
    path('', views.home, name='home'),
    path('venta/nueva/', views.nueva_venta, name='nueva_venta'),
    path('inventario/cargar/', views.cargar_inventario, name='cargar_inventario'),
    
    # Administración Interna (Sub-sistema)
    path('admin/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/almacenes/', admin_views.manage_almacenes, name='admin_almacenes'),
    path('admin/inventario/<int:almacen_id>/', admin_views.inventory_management, name='admin_inventario'),
]
