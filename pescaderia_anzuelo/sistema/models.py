from django.db import models

class Producto(models.Model):

    class Categoria(models.TextChoices):
        PLATO = 'plato', 'Plato'
        BEBIDA = 'bebida', 'Bebida'

    class BebidaTipo(models.TextChoices):
        SODA = 'soda', 'Soda'
        JUGO_NATURAL = 'jugo', 'Jugo Natural'
        OTRA = 'otra', 'Otra'

    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=6, decimal_places=2)

    categoria = models.CharField(max_length=10, choices=Categoria.choices)
    bebida_tipo = models.CharField(max_length=20, choices=BebidaTipo.choices, blank=True)

    imagen = models.ImageField(upload_to='productos/', null=True, blank=True)


class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre


class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    # Número de mesa seleccionada por el cliente/mesero (1..30)
    mesa = models.IntegerField(default=1)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"Venta {self.id}"


class Categoria(models.TextChoices):
    PLATO = 'plato'
    BEBIDA = 'bebida'
    
    
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=8, decimal_places=2)
    
    
