from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from .models import Almacen, StockAlmacen, Producto, Categoria

@staff_member_required
def admin_dashboard(request):
    """Vista principal del administrador de flores."""
    almacenes = Almacen.objects.using('flores').all()
    context = {
        'almacenes': almacenes,
        'total_productos': Producto.objects.using('flores').count(),
    }
    return render(request, 'flores/admin/dashboard.html', context)

@staff_member_required
def manage_almacenes(request):
    """Gestionar almacenes (Tienda 01, 02, etc)."""
    if request.method == 'POST':
        almacen_id = request.POST.get('almacen_id')
        almacen = get_object_or_404(Almacen.objects.using('flores'), id=almacen_id)
        almacen.activo = not almacen.activo
        almacen.save(using='flores')
        return redirect('flores:admin_almacenes')

    almacenes = Almacen.objects.using('flores').all()
    return render(request, 'flores/admin/almacenes.html', {'almacenes': almacenes})

@staff_member_required
def inventory_management(request, almacen_id):
    """Gestionar inventario de un almacén específico."""
    almacen = get_object_or_404(Almacen.objects.using('flores'), id=almacen_id)
    stocks = StockAlmacen.objects.using('flores').filter(almacen=almacen)
    
    if request.method == 'POST':
        prod_id = request.POST.get('producto_id')
        cantidad = int(request.POST.get('cantidad', 0))
        producto = get_object_or_404(Producto.objects.using('flores'), id=prod_id)
        
        stock, created = StockAlmacen.objects.using('flores').get_or_create(
            almacen=almacen, producto=producto
        )
        stock.cantidad = cantidad
        stock.save(using='flores')
        return redirect('flores:admin_inventario', almacen_id=almacen_id)

    productos = Producto.objects.using('flores').filter(activo=True)
    return render(request, 'flores/admin/inventario.html', {
        'almacen': almacen,
        'stocks': stocks,
        'productos': productos
    })
