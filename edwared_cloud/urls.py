from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Ruta principal del sistema (Landing edwared.cloud)
    path('', include('apps.core.urls')),
    # Rutas para los módulos de clientes
    path('panaderia/', include('apps.panaderia.urls')),
    path('flores/', include('apps.flores.urls')),
]
