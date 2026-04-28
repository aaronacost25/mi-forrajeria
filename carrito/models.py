from django.db import models
from productos.models import Producto

class Carrito(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    session_key = models.CharField(max_length=100, null=True, blank=True)
    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad
        
class Venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_entrega = models.CharField(max_length=50)
    direccion = models.TextField(blank=True, null=True)

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)