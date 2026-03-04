from django.urls import path
from . import views

app_name = 'flores'

urlpatterns = [
    path('', views.home, name='home'),
    path('venta/nueva/', views.nueva_venta, name='nueva_venta'),
    path('inventario/cargar/', views.cargar_inventario, name='cargar_inventario'),
]
