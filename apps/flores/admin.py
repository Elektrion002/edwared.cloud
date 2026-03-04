from django.contrib import admin
from .models import Categoria, Almacen, StockAlmacen, Producto, CargaViaje, NotaVenta, DetalleVenta, Abono

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Almacen)
class AlmacenAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ubicacion', 'activo')
    list_filter = ('activo',)

@admin.register(StockAlmacen)
class StockAlmacenAdmin(admin.ModelAdmin):
    list_display = ('almacen', 'producto', 'cantidad')
    list_filter = ('almacen', 'producto')

@admin.register(CargaViaje)
class CargaViajeAdmin(admin.ModelAdmin):
    list_display = ('id', 'almacen_origen', 'producto', 'cantidad_actual', 'cantidad_inicial', 'fecha_carga')
    list_filter = ('almacen_origen', 'fecha_carga')

@admin.register(NotaVenta)
class NotaVentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nombre', 'tipo', 'total', 'pagado', 'fecha')
    list_filter = ('tipo', 'pagado', 'fecha')
    inlines = [DetalleVentaInline]

@admin.register(Abono)
class AbonoAdmin(admin.ModelAdmin):
    list_display = ('cliente_nombre', 'monto', 'fecha')
    list_filter = ('fecha',)
