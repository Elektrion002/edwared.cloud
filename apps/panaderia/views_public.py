from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ClienteFidelidad, HistorialMovimientos

def login_cliente(request):
    """
    Landing de acceso Frictionless para el portal del cliente.
    """
    if request.method == 'POST':
        telefono = request.POST.get('telefono')
        pin = request.POST.get('pin_seguridad')
        
        try:
            cliente = ClienteFidelidad.objects.get(telefono=telefono, pin_seguridad=pin)
            request.session['cliente_id'] = str(cliente.id)
            
            if cliente.requiere_cambio_pin:
                return redirect('panaderia:forzar_pin')
                
            return redirect('panaderia:mi_credencial')
        except ClienteFidelidad.DoesNotExist:
            messages.error(request, 'Teléfono o PIN incorrectos.')
            
    return render(request, 'panaderia/public/login.html')

def forzar_pin(request):
    """
    Pantalla "Trampa" que obliga al cliente a actualizar su PIN temporal.
    """
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('panaderia:login_cliente')
        
    cliente = get_object_or_404(ClienteFidelidad, id=cliente_id)
    
    # Si ya no requiere cambiarlo, lo mandamos a su credencial
    if not cliente.requiere_cambio_pin:
        return redirect('panaderia:mi_credencial')
        
    if request.method == 'POST':
        nuevo_pin = request.POST.get('nuevo_pin')
        confirmar_pin = request.POST.get('confirmar_pin')
        
        if len(nuevo_pin) == 4 and nuevo_pin.isdigit() and nuevo_pin == confirmar_pin:
            cliente.pin_seguridad = nuevo_pin
            cliente.requiere_cambio_pin = False
            cliente.save()
            messages.success(request, '¡PIN actualizado con éxito! Tu cuenta ha sido desbloqueada.')
            return redirect('panaderia:mi_credencial')
        else:
            messages.error(request, 'Error: Los PINs deben ser exactamente de 4 dígitos y deben coincidir.')
            
    return render(request, 'panaderia/public/forzar_pin.html', {'cliente': cliente})

def mi_credencial(request):
    """
    Vista de la tarjeta digital "Apple Wallet Like" para el cliente, mostrando código QR.
    """
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('panaderia:login_cliente')
        
    cliente = get_object_or_404(ClienteFidelidad, id=cliente_id)
    
    # Redirigir si la cuenta está en modo recuperación
    if cliente.requiere_cambio_pin:
        return redirect('panaderia:forzar_pin')
        
    return render(request, 'panaderia/public/credencial.html', {'cliente': cliente})

def cambiar_pin_cliente(request):
    """
    Permite al cliente cambiar su propio PIN desde su credencial de forma voluntaria.
    """
    cliente_id = request.session.get('cliente_id')
    if not cliente_id or request.method != 'POST':
        return redirect('panaderia:login_cliente')
        
    cliente = get_object_or_404(ClienteFidelidad, id=cliente_id)
    
    pin_actual = request.POST.get('pin_actual')
    nuevo_pin = request.POST.get('nuevo_pin')
    confirmar_pin = request.POST.get('confirmar_pin')
    
    # Validar PIN actual
    if cliente.pin_seguridad != pin_actual:
        messages.error(request, 'El PIN actual es incorrecto.')
        return redirect('panaderia:mi_credencial')
        
    # Validar nuevo PIN
    if len(nuevo_pin) == 4 and nuevo_pin.isdigit() and nuevo_pin == confirmar_pin:
        if nuevo_pin == pin_actual:
            messages.info(request, 'El nuevo PIN es igual al anterior.')
        else:
            cliente.pin_seguridad = nuevo_pin
            cliente.save()
            messages.success(request, '¡Tu PIN de seguridad ha sido actualizado con éxito!')
    else:
        messages.error(request, 'Error: El nuevo PIN debe ser exactamente de 4 dígitos y coincidir con la confirmación.')
        
    return redirect('panaderia:mi_credencial')

def logout_cliente(request):
    if 'cliente_id' in request.session:
        del request.session['cliente_id']
    return redirect('panaderia:login_cliente')

def ver_historial(request):
    """
    Muestra la lista de movimientos (Kardex) del cliente logueado.
    """
    cliente_id = request.session.get('cliente_id')
    if not cliente_id:
        return redirect('panaderia:login_cliente')
        
    cliente = get_object_or_404(ClienteFidelidad, id=cliente_id)
    
    # Redirigir si la cuenta está en modo recuperación
    if cliente.requiere_cambio_pin:
        return redirect('panaderia:forzar_pin')
        
    # Obtener movimientos ordenados por fecha descendente
    movimientos = cliente.movimientos.all().order_by('-fecha')
    
    return render(request, 'panaderia/public/historial.html', {
        'cliente': cliente,
        'movimientos': movimientos
    })
