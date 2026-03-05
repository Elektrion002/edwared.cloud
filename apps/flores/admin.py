from django.contrib import admin
from .models import Categoria, Almacen, StockAlmacen, Producto, CargaViaje, NotaVenta, DetalleVenta, Abono

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

# Los modelos de negocio (Almacen, Producto, Venta) se gestionarán 
# internamente en el subsistema de Flores, no aquí.
