from django.urls import path

from . import views
from .views import agregar_carrito, comprar, pagar, ver_carrito

from .views import (
    agregar_carrito,
    ver_carrito,
    comprar,
    sumar_cantidad,
    restar_cantidad,
    eliminar_producto
)

urlpatterns = [
    path('', ver_carrito, name='ver_carrito'),
    path('agregar/<int:producto_id>/', agregar_carrito, name='agregar_carrito'),
    path('comprar/', comprar, name='comprar'),
    path('sumar/<int:item_id>/', sumar_cantidad, name='sumar_cantidad'),
    path('restar/<int:item_id>/', restar_cantidad, name='restar_cantidad'),
    path('eliminar/<int:item_id>/', eliminar_producto, name='eliminar_producto'),
    path('pagar/', pagar, name='pagar'),
    path('webhook/', views.webhook, name='webhook'),
    path('pago-exitoso/', views.pago_exitoso, name='pago_exitoso'),
    path('vaciar/', views.vaciar_carrito, name='vaciar_carrito'),
    path('comprobante/<int:venta_id>/', views.comprobante, name='comprobante'),
]