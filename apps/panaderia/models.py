import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# --- MANAGER PARA STAFF DE PANADERIA ---
class StaffPanaderiaManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('El usuario debe tener un username')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using='panaderia')
        return user

# --- MODELOS DE SEGURIDAD (CAJEROS Y ADMINS) ---
class StaffPanaderia(AbstractBaseUser):
    ROLES = [
        ('ADMIN', 'Administrador General'),
        ('CAJERO', 'Cajero de Mostrador'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=50, unique=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='CAJERO')
    
    nombres = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=150)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    pin_seguridad = models.CharField(max_length=4, help_text="PIN rápido 4 dígitos")
    
    # Campo para almacenar la ruta de la foto (o usar ImageField si instalamos Pillow)
    foto_perfil = models.CharField(max_length=255, blank=True, null=True, help_text="URL o path de la foto")
    
    activo = models.BooleanField(default=True, help_text="Activado Lógico")
    fecha_ingreso = models.DateField(auto_now_add=True, help_text="Fecha de inicio del trabajo")

    objects = StaffPanaderiaManager()

    USERNAME_FIELD = 'username'
    
    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.get_rol_display()})"


# --- MODELOS DE FIDELIDAD (CLIENTES) ---
from django.core.exceptions import ValidationError

class ClienteFidelidad(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    # Quitamos unique=True porque puede haber varios desactivados con el mismo,
    # la validación estricta solo aplica a los activos.
    telefono = models.CharField(max_length=20, help_text="Para buscar rápido en caja")
    pin_seguridad = models.CharField(max_length=4, help_text="PIN 4 dígitos para portal del cliente")
    puntos_actuales = models.IntegerField(default=0)
    
    # Campo Criptográfico para forzar reseteo si el PIN es vulnerado/olvidado
    requiere_cambio_pin = models.BooleanField(default=False, help_text="Bloquea movimientos hasta que el usuario actualice su contraseña temporal")
    
    activo = models.BooleanField(default=True, help_text="Baja lógica (Soft-Delete)")
    creado_en = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        # Regla estricta: Un teléfono solo puede estar vinculado a UN cliente activo a la vez.
        if self.activo:
            duplicados = ClienteFidelidad.objects.filter(telefono=self.telefono, activo=True)
            if self.pk:
                duplicados = duplicados.exclude(pk=self.pk)
            if duplicados.exists():
                raise ValidationError({'telefono': 'Este número de teléfono ya está registrado en OTRO cliente activo.'})

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        estado = "ACTIVO" if self.activo else "BAJA"
        return f"[{estado}] {self.nombre} - {self.telefono} ({self.puntos_actuales} pts)"

class CatalogoPremios(models.Model):
    nombre_premio = models.CharField(max_length=150)
    costo_puntos = models.IntegerField(help_text="Cuántos puntos cuesta canjear este premio")
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre_premio} ({self.costo_puntos} pts)"

class HistorialMovimientos(models.Model):
    TIPO_MOVIMIENTO = [
        ('SUMA', 'Acumulación de Puntos'),
        ('CANJE', 'Canje de Premio'),
        ('AJUSTE', 'Ajuste Manual'),
    ]

    cliente = models.ForeignKey(ClienteFidelidad, on_delete=models.CASCADE, related_name='movimientos')
    
    # Relacionamos qué Staff (Cajero/Admin) hizo el movimiento para auditoría estricta
    staff_responsable = models.ForeignKey(StaffPanaderia, on_delete=models.SET_NULL, null=True, blank=True, related_name='operaciones_realizadas')
    
    tipo = models.CharField(max_length=20, choices=TIPO_MOVIMIENTO)
    puntos_involucrados = models.IntegerField(help_text="Positivos o negativos")
    nota_cajero = models.CharField(max_length=255, blank=True, null=True, help_text="Ej: Compra Ticket #1024 o Canje Pastel")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.cliente.nombre} | {self.puntos_involucrados} pts"
