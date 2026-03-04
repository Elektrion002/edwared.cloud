from django.db import models

class Cliente(models.Model):
    """
    Representa a un dueño de negocio (ej. Juan de la Panadería).
    Se guarda en la Master Database ('default').
    """
    nombre_negocio = models.CharField(max_length=200)
    contacto = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_negocio

class Plataforma(models.Model):
    """
    Representa el sistema contratado por el cliente y su URL/Subdominio de acceso.
    """
    TIPO_PLATAFORMA = [
        ('panaderia', 'Recompensas de Panadería'),
        ('flores', 'Preventa de Flores'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='plataformas')
    tipo = models.CharField(max_length=50, choices=TIPO_PLATAFORMA)
    subdominio = models.CharField(max_length=100, unique=True, help_text="Ej: mipana.edwared.cloud")
    db_name = models.CharField(max_length=50, help_text="Nombre lógico del Database Router (ej. 'panaderia')")
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.cliente.nombre_negocio}"
