from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from .models import ClienteFidelidad, HistorialMovimientos, StaffPanaderia
from .backends import StaffPanaderiaBackend
from .decorators import login_staff_requerido
import uuid

# --- VISTAS DE AUTENTICACION STAFF ---

def staff_login(request):
    """
    Vista de login para Cajeros y Administradores de Panadería.
    """
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        
        # Validar directamente contra el modelo de staff usando la db aislada
        backend = StaffPanaderiaBackend()
        user = backend.authenticate(request, username=u, password=p)
        
        if user is not None:
            # Login manual custom para aislar la sesión de la master de clienes del ecosistema
            request.session['staff_panaderia_id'] = str(user.id)
            messages.success(request, f"Bienvenido, {user.nombres} ({user.get_rol_display()})")
            return redirect('panaderia:admin_home')
        else:
            messages.error(request, "Credenciales incorrectas o usuario inactivo.")
            
    return render(request, 'panaderia/staff_login.html')

def staff_logout(request):
    if 'staff_panaderia_id' in request.session:
        del request.session['staff_panaderia_id']
    messages.info(request, "Sesión cerrada de forma segura.")
    return redirect('panaderia:staff_login')


# --- VISTAS DEL DASHBOARD (PROTEGIDAS) ---

@login_staff_requerido
def cajero_dashboard(request):
    """
    Dashboard del cajero protegido. Incluye buscador de clientes.
    """
    query = request.GET.get('q', '').strip()
    
    if query:
        # Búsqueda universal por nombre o teléfono
        clientes_recientes = ClienteFidelidad.objects.filter(
            models.Q(nombre__icontains=query) | models.Q(telefono__icontains=query)
        ).order_by('-creado_en')
    else:
        # Modo Default: Últimos 5
        clientes_recientes = ClienteFidelidad.objects.order_by('-creado_en')[:5]
        
    staff = get_object_or_404(StaffPanaderia.objects.using('panaderia'), pk=request.session['staff_panaderia_id'])
    
    return render(request, 'panaderia/dashboard.html', {
        'clientes': clientes_recientes, 
        'staff_activo': staff,
        'search_query': query
    })

@login_staff_requerido
def registro_rapido(request):
    """
    Permite al cajero registrar un cliente nuevo desde la terminal.
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        pin = request.POST.get('pin', '1234')  # Pin Default si hay prisas

        if ClienteFidelidad.objects.filter(telefono=telefono).exists():
            messages.error(request, f"El número {telefono} ya está registrado.")
        else:
            nuevo = ClienteFidelidad.objects.create(
                nombre=nombre,
                telefono=telefono,
                pin_seguridad=pin
            )
            messages.success(request, f"¡{nuevo.nombre} registrado exitosamente!")
            return redirect('panaderia:cajero_ver_cliente', cliente_uuid=nuevo.id)
            
    return redirect('panaderia:admin_home')

# --- GESTION DE PERSONAL (SOLO PARA ADMINS) ---

@login_staff_requerido
def gestionar_staff(request):
    """
    Vista exclusiva para Administradores: lista a todos los cajeros activos.
    """
    staff_activo = get_object_or_404(StaffPanaderia.objects.using('panaderia'), pk=request.session['staff_panaderia_id'])
    
    if staff_activo.rol != 'ADMIN':
        messages.error(request, f"Hola {staff_activo.nombres}, no tienes permisos de Administrador para ver el personal.")
        return redirect('panaderia:admin_home')
        
    lista_staff = StaffPanaderia.objects.using('panaderia').all().order_by('-fecha_ingreso')
    return render(request, 'panaderia/lista_staff.html', {'staff_activo': staff_activo, 'lista_staff': lista_staff})

@login_staff_requerido
def registrar_staff(request):
    """
    Permite a un ADMIN dar de alta a un nuevo Cajero, o editar uno existente.
    """
    staff_activo = get_object_or_404(StaffPanaderia.objects.using('panaderia'), pk=request.session['staff_panaderia_id'])
    
    if staff_activo.rol != 'ADMIN':
        return redirect('panaderia:admin_home')
        
    if request.method == 'POST':
        action_type = request.POST.get('action_type', 'create')
        u = request.POST.get('username')
        pwd = request.POST.get('password')
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        pin = request.POST.get('pin')
        
        if action_type == 'create':
            if StaffPanaderia.objects.using('panaderia').filter(username=u).exists():
                messages.error(request, "Ese usuario/ID ya existe.")
            else:
                try:
                    nuevo_cajero = StaffPanaderia.objects.using('panaderia').create(
                        username=u,
                        rol='CAJERO',
                        nombres=nombres,
                        apellidos=apellidos,
                        pin_seguridad=pin
                    )
                    nuevo_cajero.set_password(pwd)
                    nuevo_cajero.save(using='panaderia')
                    messages.success(request, f"Cajero {nombres} dado de alta correctamente.")
                except Exception as e:
                    messages.error(request, f"Error al guardar: {str(e)}")
        
        elif action_type == 'edit':
            staff_id = request.POST.get('staff_id')
            try:
                cajero_edit = get_object_or_404(StaffPanaderia.objects.using('panaderia'), pk=staff_id)
                # Impedir que se cambie a un username que ya existe (y no es el suyo)
                if u != cajero_edit.username and StaffPanaderia.objects.using('panaderia').filter(username=u).exists():
                    messages.error(request, "El nuevo nombre de usuario ya está ocupado.")
                else:
                    cajero_edit.username = u
                    cajero_edit.nombres = nombres
                    cajero_edit.apellidos = apellidos
                    
                    if pin and pin.strip() != "":
                        cajero_edit.pin_seguridad = pin
                    
                    if pwd and pwd.strip() != "":
                        cajero_edit.set_password(pwd)
                        
                    cajero_edit.save(using='panaderia')
                    messages.success(request, f"Datos actualizados para {cajero_edit.nombres}.")
            except Exception as e:
                messages.error(request, f"Error al editar: {str(e)}")
            
    return redirect('panaderia:gestionar_staff')

@login_staff_requerido
def eliminar_staff(request, staff_id):
    """
    Elimina físicamente a un cajero (Solo aplicable si no ha hecho transacciones masivas, por ahora cascada).
    """
    staff_activo = get_object_or_404(StaffPanaderia.objects.using('panaderia'), pk=request.session['staff_panaderia_id'])
    
    if staff_activo.rol != 'ADMIN' or request.method != 'POST':
        return redirect('panaderia:admin_home')
        
    try:
        cajero_delete = get_object_or_404(StaffPanaderia.objects.using('panaderia'), pk=staff_id)
        if cajero_delete.id == staff_activo.id:
            messages.error(request, "No puedes eliminarte a ti mismo.")
        else:
            nombre = cajero_delete.nombres
            cajero_delete.delete(using='panaderia')
            messages.success(request, f"Usuario {nombre} dado de baja definitivamente.")
    except Exception as e:
        messages.error(request, f"Error al eliminar: {str(e)}")
        
    return redirect('panaderia:gestionar_staff')

# --- GESTION MAESTRA DE CLIENTES (SOLO ADMINS) ---

from django.core.exceptions import ValidationError

@login_staff_requerido
def gestionar_clientes(request):
    """
    Vista CRM para Administradores: lista a todos los clientes (activos e inactivos) y permite editar.
    """
    staff_activo = get_object_or_404(StaffPanaderia.objects.using('panaderia'), pk=request.session['staff_panaderia_id'])
    
    if staff_activo.rol != 'ADMIN':
        messages.error(request, "Acceso denegado. Solo administradores pueden ver el padrón de clientes.")
        return redirect('panaderia:admin_home')
        
    if request.method == 'POST':
        action_type = request.POST.get('action_type', 'edit')
        
        if action_type == 'edit':
            cliente_id = request.POST.get('cliente_id')
            nuevo_nombre = request.POST.get('nombre')
            nuevo_telefono = request.POST.get('telefono')
            nuevo_pin = request.POST.get('pin')
            
            try:
                cliente = get_object_or_404(ClienteFidelidad, pk=cliente_id)
                cliente.nombre = nuevo_nombre
                cliente.telefono = nuevo_telefono
                
                if nuevo_pin and nuevo_pin.strip() != "":
                    cliente.pin_seguridad = nuevo_pin.strip()
                    
                # El método clean() del modelo validará la unicidad del teléfono si está activo
                cliente.save()
                messages.success(request, f"Cliente {cliente.nombre} actualizado correctamente.")
            except Exception as e:
                # Capturamos el ValidationError del modelo u otros errores
                if hasattr(e, 'message_dict'):
                    for campo, errores in e.message_dict.items():
                        for error in errores:
                            messages.error(request, f"Error en {campo}: {error}")
                else:
                    messages.error(request, f"Error al guardar: {str(e)}")
                    
        return redirect('panaderia:gestionar_clientes')

    query = request.GET.get('q', '').strip()
    if query:
        lista_clientes = ClienteFidelidad.objects.filter(
            models.Q(nombre__icontains=query) | models.Q(telefono__icontains=query)
        ).order_by('-creado_en')
    else:
        lista_clientes = ClienteFidelidad.objects.all().order_by('-creado_en')
        
    return render(request, 'panaderia/lista_clientes.html', {
        'staff_activo': staff_activo, 
        'lista_clientes': lista_clientes,
        'search_query': query
    })

@login_staff_requerido
def eliminar_cliente(request, cliente_id):
    """
    Activa o desactiva a un cliente (Baja Lógica). No se borra de la DB.
    """
    staff_activo = get_object_or_404(StaffPanaderia.objects.using('panaderia'), pk=request.session['staff_panaderia_id'])
    
    if staff_activo.rol != 'ADMIN' or request.method != 'POST':
        return redirect('panaderia:admin_home')
        
    try:
        cliente = get_object_or_404(ClienteFidelidad, pk=cliente_id)
        if cliente.activo:
            cliente.activo = False
            accion_txt = "dado de baja lógica"
        else:
            cliente.activo = True
            accion_txt = "reactivado"
            
        cliente.save()
        messages.success(request, f"El cliente {cliente.nombre} ha sido {accion_txt}.")
    except Exception as e:
         # Capturamos si falla al reactivar porque choca el teléfono
        if hasattr(e, 'message_dict'):
            messages.error(request, "No se puede reactivar: El número de teléfono ya está siendo usado por otro cliente activo.")
        else:
            messages.error(request, f"Error al cambiar estatus: {str(e)}")
        
    return redirect('panaderia:gestionar_clientes')

# --- MÓDULO DE ANALÍTICA Y ESTADÍSTICAS (DASHBOARD DIRECTIVO) ---

from django.db.models import Sum, Count, Q
from django.utils import timezone
import datetime

@login_staff_requerido
def dashboard_estadisticas(request):
    """
    Vista global del Director (Admin) para ver métricas, top clientes y la macro-auditoría.
    """
    staff_activo = get_object_or_404(StaffPanaderia.objects.using('panaderia'), pk=request.session['staff_panaderia_id'])
    
    # Solo los administradores pueden ver datos financieros de la sucursal
    if staff_activo.rol != 'ADMIN':
        messages.error(request, "Acceso Denegado. Solo nivel Dirección puede visualizar métricas.")
        return redirect('panaderia:admin_home')

    # 1. KPIs Globales Historicos
    total_clientes_activos = ClienteFidelidad.objects.filter(activo=True).count()
    
    puntos_otorgados_raw = HistorialMovimientos.objects.filter(tipo='SUMA').aggregate(total=Sum('puntos_involucrados'))['total']
    total_puntos_otorgados = puntos_otorgados_raw if puntos_otorgados_raw else 0
    
    puntos_canjeados_raw = HistorialMovimientos.objects.filter(tipo='CANJE').aggregate(total=Sum('puntos_involucrados'))['total']
    total_puntos_canjeados = abs(puntos_canjeados_raw) if puntos_canjeados_raw else 0 # abs() porque se guardan como negativos en canje

    puntos_circulando = total_puntos_otorgados - total_puntos_canjeados

    # 2. Ranking Top 10 Clientes (Con más puntos guardados actualmente)
    top_clientes = ClienteFidelidad.objects.filter(activo=True).order_by('-puntos_actuales')[:10]

    # 3. Auditoría de Cajeros (Top Staff otorgando puntos)
    # Sumamos cuantos puntos ha 'SUMADO' cada cajero
    top_cajeros = StaffPanaderia.objects.using('panaderia').annotate(
        total_puntos_dados=Sum('operaciones_realizadas__puntos_involucrados', filter=Q(operaciones_realizadas__tipo='SUMA')),
        total_movimientos=Count('operaciones_realizadas')
    ).order_by('-total_puntos_dados')[:5]

    # 4. Kardex Maestro (Filtro por fecha)
    filtro_fecha = request.GET.get('rango', 'hoy')
    
    hoy = timezone.localdate()
    movimientos_qs = HistorialMovimientos.objects.all().order_by('-fecha')
    
    RANGO_TXT = "Hoy"
    if filtro_fecha == 'hoy':
        movimientos_filtrados = movimientos_qs.filter(fecha__date=hoy)
    elif filtro_fecha == 'ayer':
        RANGO_TXT = "Ayer"
        movimientos_filtrados = movimientos_qs.filter(fecha__date=hoy - datetime.timedelta(days=1))
    elif filtro_fecha == 'semana':
        RANGO_TXT = "Últimos 7 días"
        movimientos_filtrados = movimientos_qs.filter(fecha__date__gte=hoy - datetime.timedelta(days=7))
    elif filtro_fecha == 'mes':
        RANGO_TXT = "Este Mes"
        movimientos_filtrados = movimientos_qs.filter(fecha__year=hoy.year, fecha__month=hoy.month)
    else: # Historico (Todo)
        RANGO_TXT = "Histórico Completo"
        movimientos_filtrados = movimientos_qs 

    # Extraer resumen solo de ese filtro de fecha
    otorgados_periodo = movimientos_filtrados.filter(tipo='SUMA').aggregate(total=Sum('puntos_involucrados'))['total'] or 0
    canjeados_periodo = abs(movimientos_filtrados.filter(tipo='CANJE').aggregate(total=Sum('puntos_involucrados'))['total'] or 0)
    
    # LIMITAR filas renderizadas en frontend para no colapsar la memoria del navegador
    movimientos_render = movimientos_filtrados[:100]

    context = {
        'staff_activo': staff_activo,
        'kpi_total_clientes': total_clientes_activos,
        'kpi_circulando': puntos_circulando,
        'kpi_otorgados': total_puntos_otorgados,
        'kpi_canjeados': total_puntos_canjeados,
        
        'top_clientes': top_clientes,
        'top_cajeros': top_cajeros,
        
        'kardex': movimientos_render,
        'rango_activo': filtro_fecha,
        'rango_txt': RANGO_TXT,
        'resumen_rango': {
            'otorgados': otorgados_periodo,
            'canjeados': canjeados_periodo
        }
    }
    
    return render(request, 'panaderia/estadisticas.html', context)

@login_staff_requerido
def mi_perfil(request):
    """
    Permite a CUALQUIER MIEMBRO del staff (Cajero o Admin) cambiar su propio PIN y contraseña.
    """
    staff_activo = get_object_or_404(StaffPanaderia.objects.using('panaderia'), pk=request.session['staff_panaderia_id'])
    
    if request.method == 'POST':
        nuevo_pin = request.POST.get('nuevo_pin')
        nueva_pwd = request.POST.get('nueva_password')
        actualizado = False
        
        try:
            if nuevo_pin and nuevo_pin.strip() != "":
                staff_activo.pin_seguridad = nuevo_pin.strip()
                actualizado = True
                
            if nueva_pwd and nueva_pwd.strip() != "":
                staff_activo.set_password(nueva_pwd)
                actualizado = True
                
            if actualizado:
                staff_activo.save(using='panaderia')
                messages.success(request, "¡Tus credenciales han sido actualizadas con éxito! 🔒")
            else:
                messages.info(request, "No se realizaron cambios.")
                
        except Exception as e:
            messages.error(request, f"Ocurrió un error al actualizar: {str(e)}")
            
        return redirect('panaderia:mi_perfil')

    return render(request, 'panaderia/mi_perfil.html', {'staff_activo': staff_activo})

import random

@login_staff_requerido
def generar_pin_temporal(request, cliente_uuid):
    """
    Bloquea la cuenta del cliente y le genera un PIN temporal que se envía por WhatsApp.
    """
    staff_activo = get_object_or_404(StaffPanaderia.objects.using('panaderia'), pk=request.session['staff_panaderia_id'])
    
    try:
        uuid_obj = uuid.UUID(cliente_uuid)
        cliente = get_object_or_404(ClienteFidelidad, id=uuid_obj)
    except ValueError:
        return redirect('panaderia:admin_home')
        
    if request.method == 'POST':
        # Generar PIN temporal random de 4 digitos
        pin_temp = str(random.randint(1000, 9999))
        
        # Bloquear la cuenta para forzar cambio
        cliente.pin_seguridad = pin_temp
        cliente.requiere_cambio_pin = True
        cliente.save()
        
        # Auditar la acción (Importante para seguridad)
        HistorialMovimientos.objects.create(
            cliente=cliente, 
            tipo='AJUSTE', 
            puntos_involucrados=0, 
            nota_cajero="Solicitó Reseteo de PIN/Credencial", 
            staff_responsable=staff_activo
        )
        
        # Aquí construiríamos el Link de WhatsApp (puedes ajustar el texto a tu gusto)
        # Usando build_absolute_uri para generar el dominio dinámicamente
        link_portal = request.build_absolute_uri('/panaderia/mis-puntos/')
        mensaje = f"Hola {cliente.nombre}, somos de tu Panadería EDWARED 🥐. Tu nuevo PIN temporal de seguridad es: *{pin_temp}*. Entra a {link_portal} para actualizarlo inmediatamente."
        
        from urllib.parse import quote
        wa_link = f"https://wa.me/{cliente.telefono}?text={quote(mensaje)}"
        
        # Redirigir al cajero a WhatsApp (se abre en nueva pestaña usualmente si se maneja desde el front, 
        # pero aquí en Django daremos el link listo para clickear en la UI).
        messages.success(request, f"Se generó el PIN temporal: {pin_temp}.")
        # Lo pasamos de vuelta por URL o Mensaje para que el cajero de el clic
        request.session['wa_link_temporal'] = wa_link
        
    return redirect('panaderia:cajero_ver_cliente', cliente_uuid=cliente.id)

@login_staff_requerido
def enviar_enlace_credencial(request, cliente_uuid):
    """
    Envía el enlace del portal de cliente por WhatsApp SIN resetear el PIN.
    """
    try:
        uuid_obj = uuid.UUID(cliente_uuid)
        cliente = get_object_or_404(ClienteFidelidad, id=uuid_obj)
    except ValueError:
        return redirect('panaderia:admin_home')
        
    if request.method == 'POST':
        # Usando build_absolute_uri para generar el dominio dinámicamente
        link_portal = request.build_absolute_uri('/panaderia/mis-puntos/')
        mensaje = f"Hola {cliente.nombre}, somos de tu Panadería EDWARED 🥐. Aquí tienes el enlace directo para entrar a tu cuenta y ver tus recompensas: {link_portal}"
        
        from urllib.parse import quote
        wa_link = f"https://wa.me/{cliente.telefono}?text={quote(mensaje)}"
        
        messages.success(request, "Enlace de WhatsApp generado con éxito.")
        request.session['wa_link_temporal'] = wa_link
        
    return redirect('panaderia:cajero_ver_cliente', cliente_uuid=cliente.id)


@login_staff_requerido
def cajero_ver_cliente(request, cliente_uuid):
    """
    Abre la "Terminal de Cobro" protegido. El cajero en sesión quedará ligado permanentemente a la auditoría.
    """
    staff = get_object_or_404(StaffPanaderia.objects.using('panaderia'), pk=request.session['staff_panaderia_id'])
    
    try:
        uuid_obj = uuid.UUID(cliente_uuid)
        cliente = get_object_or_404(ClienteFidelidad, id=uuid_obj)
    except ValueError:
        messages.error(request, "Código QR Inválido. UUID corrupto.")
        return redirect('panaderia:admin_home')
        
    historial = cliente.movimientos.all().order_by('-fecha')[:10]
    
    # Recuperar el link de WhatsApp si acaba de pedir reset
    wa_link = request.session.pop('wa_link_temporal', None)
    
    if request.method == 'POST':
        if cliente.requiere_cambio_pin:
            messages.error(request, "CRÍTICO: La cuenta está bloqueada por seguridad. El cliente debe iniciar sesión en su celular y cambiar su PIN temporal antes de poder usar puntos.")
            return redirect('panaderia:cajero_ver_cliente', cliente_uuid=cliente.id)
            
        accion = request.POST.get('accion')
        try:
            puntos = int(request.POST.get('puntos', 0))
            if puntos > 0:
                if accion == 'substract' and cliente.puntos_actuales >= puntos:
                    cliente.puntos_actuales -= puntos
                    HistorialMovimientos.objects.create(cliente=cliente, tipo='CANJE', puntos_involucrados=-puntos, nota_cajero="Canje Mostrador", staff_responsable=staff)
                    messages.success(request, f"¡Se rebajaron {puntos} puntos correctamente!")
                elif accion == 'add':
                    cliente.puntos_actuales += puntos
                    HistorialMovimientos.objects.create(cliente=cliente, tipo='SUMA', puntos_involucrados=puntos, nota_cajero="Compra Mostrador", staff_responsable=staff)
                    messages.success(request, f"¡Se abonaron {puntos} puntos correctamente!")
                else:
                    messages.error(request, "Puntos insuficientes para canje.")
                    
                cliente.save()
            return redirect('panaderia:cajero_ver_cliente', cliente_uuid=cliente.id)
        except ValueError:
            messages.error(request, "Valor de puntos inválido.")

    return render(request, 'panaderia/terminal_caja.html', {
        'cliente': cliente, 
        'historial': historial, 
        'staff_activo': staff,
        'wa_link': wa_link
    })
