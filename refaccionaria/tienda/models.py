from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nombre

class Refaccion(models.Model):
    categoria = models.ForeignKey(Categoria, related_name='refacciones', on_delete=models.CASCADE)
    sku = models.CharField(max_length=50, unique=True, help_text="Número de parte o código de barras")
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    compatibilidad = models.CharField(max_length=250, blank=True, help_text="Ej: Ford Fiesta 2005 1.6L, Sedán")
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='refacciones/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sku} - {self.nombre}"

class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carrito {self.id}"

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, related_name='items', on_delete=models.CASCADE)
    refaccion = models.ForeignKey(Refaccion, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def obtener_costo(self):
        return self.refaccion.precio * self.cantidad
class Pedido(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)
    direccion = models.TextField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.nombre}"

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, related_name='items', on_delete=models.CASCADE)
    refaccion = models.ForeignKey(Refaccion, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)