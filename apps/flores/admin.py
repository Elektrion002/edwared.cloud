from django.contrib import admin
from .models import Categoria, Producto, CargaViaje, NotaVenta, DetalleVenta, Abono

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 1

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio_base', 'activo')
    list_filter = ('categoria', 'activo')
    search_fields = ('nombre',)

@admin.register(CargaViaje)
class CargaViajeAdmin(admin.ModelAdmin):
    list_display = ('producto', 'cantidad_actual', 'cantidad_inicial', 'fecha_carga')
    list_filter = ('fecha_carga',)

@admin.register(NotaVenta)
class NotaVentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente_nombre', 'tipo', 'total', 'pagado', 'fecha')
    list_filter = ('tipo', 'pagado', 'fecha')
    inlines = [DetalleVentaInline]

@admin.register(Abono)
class AbonoAdmin(admin.ModelAdmin):
    list_display = ('cliente_nombre', 'monto', 'fecha')
    list_filter = ('fecha',)
