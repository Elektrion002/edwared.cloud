from django.db import models
from django.utils import timezone

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class Producto(models.Model):
    nombre = models.CharField(max_length=200)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    precio_base = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class CargaViaje(models.Model):
    """Stock cargado en el vehículo para un recorrido."""
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad_inicial = models.PositiveIntegerField()
    cantidad_actual = models.PositiveIntegerField()
    fecha_carga = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad_actual}/{self.cantidad_inicial}"

class NotaVenta(models.Model):
    TIPO_VENTA = [('preventa', 'Preventa'), ('directa', 'Venta Directa')]
    cliente_nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=20, choices=TIPO_VENTA)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    pagado = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Nota {self.id} - {self.cliente_nombre}"

class DetalleVenta(models.Model):
    nota = models.ForeignKey(NotaVenta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

class Abono(models.Model):
    cliente_nombre = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    comentario = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Abono {self.cliente_nombre} - ${self.monto}"
