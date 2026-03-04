from django.urls import path
from . import views_admin, views_public

app_name = 'panaderia'

urlpatterns = [
    # --- Módulo Admin (Cajeros) ---
    path('acceso-staff/', views_admin.staff_login, name='staff_login'),
    path('salir-staff/', views_admin.staff_logout, name='staff_logout'),
    
    path('', views_admin.cajero_dashboard, name='admin_home'),
    path('mi-perfil/', views_admin.mi_perfil, name='mi_perfil'),
    
    path('personal/', views_admin.gestionar_staff, name='gestionar_staff'),
    path('personal/nuevo/', views_admin.registrar_staff, name='registrar_staff'),
    path('personal/eliminar/<str:staff_id>/', views_admin.eliminar_staff, name='eliminar_staff'),
    
    path('cajero/alta/', views_admin.registro_rapido, name='cajero_alta'),
    path('cajero/cliente/<str:cliente_uuid>/', views_admin.cajero_ver_cliente, name='cajero_ver_cliente'),
    path('cajero/cliente/<str:cliente_uuid>/recuperar/', views_admin.generar_pin_temporal, name='generar_pin_temporal'),
    path('cajero/cliente/<str:cliente_uuid>/compartir/', views_admin.enviar_enlace_credencial, name='enviar_enlace_credencial'),
    
    # --- Módulo Directorio CRM y Analítica (Solo Admins) ---
    path('clientes/', views_admin.gestionar_clientes, name='gestionar_clientes'),
    path('clientes/estado/<str:cliente_id>/', views_admin.eliminar_cliente, name='eliminar_cliente'),
    path('estadisticas/', views_admin.dashboard_estadisticas, name='estadisticas'),

    # --- Módulo Cliente (Público) ---
    path('mis-puntos/', views_public.login_cliente, name='login_cliente'),
    path('mis-puntos/seguridad/', views_public.forzar_pin, name='forzar_pin'),
    path('mis-puntos/tarjeta/', views_public.mi_credencial, name='mi_credencial'),
    path('mis-puntos/historial/', views_public.ver_historial, name='ver_historial'),
    path('mis-puntos/cambiar-pin/', views_public.cambiar_pin_cliente, name='cambiar_pin_cliente'),
    path('mis-puntos/salir/', views_public.logout_cliente, name='logout_cliente'),
]
