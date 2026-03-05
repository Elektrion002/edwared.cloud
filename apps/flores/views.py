from django.shortcuts import render, redirect
from django.db import transaction
from .models import NotaVenta, CargaViaje, Producto, Almacen, DetalleVenta

def home(request):
    """
    Vista del Dashboard principal para el sistema de Flores.
    """
    context = {
        'preventas_activas': NotaVenta.objects.using('flores').filter(tipo='preventa', pagado=False).count(),
        'total_productos': Producto.objects.using('flores').filter(activo=True).count(),
        'carga_actual': CargaViaje.objects.using('flores').all().order_by('-fecha_carga')[:5],
    }
    return render(request, 'flores/dashboard.html', context)

def nueva_venta(request):
    """
    Formulario rápido para generar una nota de venta.
    """
    if request.method == 'POST':
        cliente = request.POST.get('cliente')
        prod_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad', 0))
        precio = float(request.POST.get('precio', 0))
        
        with transaction.atomic(using='flores'):
            producto = Producto.objects.using('flores').get(id=prod_id)
            total = cantidad * precio
            nota = NotaVenta.objects.using('flores').create(
                cliente_nombre=cliente,
                tipo='directa',
                total=total,
                pagado=True # Por defecto venta directa es pagada
            )
            DetalleVenta.objects.using('flores').create(
                nota=nota,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio,
                subtotal=total
            )
            # Descontar de la carga del viaje más reciente de ese producto
            carga = CargaViaje.objects.using('flores').filter(producto=producto).order_by('-fecha_carga').first()
            if carga:
                carga.cantidad_actual = max(0, carga.cantidad_actual - cantidad)
                carga.save(using='flores')
                
        return redirect('flores:home')

    productos = Producto.objects.using('flores').filter(activo=True)
    return render(request, 'flores/nueva_venta.html', {'productos': productos})

def cargar_inventario(request):
    """
    Registrar la carga inicial del vehículo para el viaje.
    """
    if request.method == 'POST':
        alm_id = request.POST.get('almacen')
        prod_id = request.POST.get('producto')
        cantidad = int(request.POST.get('cantidad', 0))
        
        almacen = Almacen.objects.using('flores').get(id=alm_id)
        producto = Producto.objects.using('flores').get(id=prod_id)
        
        CargaViaje.objects.using('flores').create(
            almacen_origen=almacen,
            producto=producto,
            cantidad_inicial=cantidad,
            cantidad_actual=cantidad
        )
        return redirect('flores:home')

    productos = Producto.objects.using('flores').filter(activo=True)
    almacenes = Almacen.objects.using('flores').filter(activo=True)
    return render(request, 'flores/cargar_inventario.html', {
        'productos': productos,
        'almacenes': almacenes
    })
