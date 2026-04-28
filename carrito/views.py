from django.shortcuts import render, redirect, get_object_or_404
from .models import Carrito, DetalleVenta
from ventas.models import Venta
from productos.models import Producto
import mercadopago
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib.utils import ImageReader
import os
from django.conf import settings

import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def webhook(request):

    data = json.loads(request.body)

    print(data)

    if data.get("type") == "payment":

        items = Carrito.objects.all()

        for item in items:
            item.producto.stock -= item.cantidad
            item.producto.save()

        items.delete()

    return HttpResponse("OK")
def pagar(request):

    sdk = mercadopago.SDK("APP_USR-4028607881334111-040216-bbcfe153f03df47f3c908c93f54f0875-2371580641")

    items_carrito = Carrito.objects.all()

    items = []

    metodo_entrega = request.GET.get('metodo_entrega', 'local')
    direccion = request.GET.get('direccion', '').lower()

    total_envio = 0
    total = 0

    for item in items_carrito:

        total += item.subtotal

        items.append({
            "title": item.producto.nombre,
            "quantity": item.cantidad,
            "unit_price": float(item.producto.precio)
        })

    if metodo_entrega == 'envio':

        if 'villa carlos paz' in direccion:
            total_envio = 2000
        elif 'mayu sumaj' in direccion:
            total_envio = 1000
        elif 'san antonio' in direccion:
            total_envio = 1500
        elif 'cuesta blanca' in direccion:
            total_envio = 1800
        elif 'icho cruz' in direccion:
            total_envio = 2000

        if total_envio > 0:
            items.append({
                "title": "Costo de envío",
                "quantity": 1,
                "unit_price": float(total_envio)
            })

    total += total_envio

    venta = Venta.objects.create(
        total=total
    )

    preference_data = {
        "items": items,
        "back_urls": {
            "success": "http://127.0.0.1:8000/carrito/pago-exitoso/",
            "failure": "http://127.0.0.1:8000/carrito/",
            "pending": "http://127.0.0.1:8000/carrito/"
        }
    }

    preference_response = sdk.preference().create(preference_data)

    if "response" in preference_response:

        preference = preference_response["response"]

        if "init_point" in preference:
            return redirect(preference["init_point"])

    return HttpResponse("Error al generar pago")
def agregar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)

    session_key = request.session.session_key

    if not session_key:
        request.session.create()
        session_key = request.session.session_key

    item, created = Carrito.objects.get_or_create(
        producto=producto,
        session_key=session_key,
        defaults={'cantidad': 1}
    )

    if not created:
        item.cantidad += 1
        item.save()

    return redirect('ver_carrito')
def ver_carrito(request):
    session_key = request.session.session_key

    items = Carrito.objects.filter(session_key=session_key)

    total_productos = sum(item.subtotal for item in items)

    direccion = request.GET.get('direccion', '')
    metodo_entrega = request.GET.get('metodo_entrega', 'local')

    envio = 0

    direccion_lower = direccion.lower()

    if metodo_entrega == 'envio':
        if 'villa carlos paz' in direccion_lower:
            envio = 2000
        elif 'mayu sumaj' in direccion_lower:
            envio = 1000
        elif 'san antonio' in direccion_lower:
            envio = 1500
        elif 'cuesta blanca' in direccion_lower:
            envio = 1800
        elif 'icho cruz' in direccion_lower:
            envio = 2000

    total = total_productos + envio

    return render(request, 'carrito/ver_carrito.html', {
        'items': items,
        'total': total,
        'total_productos': total_productos,
        'envio': envio,
        'direccion': direccion,
        'metodo_entrega': metodo_entrega
    })
def comprar(request):
    items = Carrito.objects.all()

    for item in items:
        if item.producto.stock < item.cantidad:
            return render(request, 'carrito/error_stock.html', {
                'producto': item.producto
            })

    total = sum(item.subtotal for item in items)
    venta = Venta.objects.create(total=total)

    for item in items:
        producto = item.producto
        producto.stock -= item.cantidad
        producto.save()

    items.delete()

    return render(request, 'carrito/compra_exitosa.html', {'venta': venta})

from django.shortcuts import get_object_or_404

from django.http import JsonResponse
def sumar_cantidad(request, item_id):

    item = get_object_or_404(Carrito, id=item_id)

    item.cantidad += 1
    item.save()

    total = sum(i.subtotal for i in Carrito.objects.all())

    return JsonResponse({
        'cantidad': item.cantidad,
        'subtotal': item.subtotal,
        'total': total
    })
def restar_cantidad(request, item_id):

    item = get_object_or_404(Carrito, id=item_id)

    if item.cantidad > 1:
        item.cantidad -= 1
        item.save()

    total = sum(i.subtotal for i in Carrito.objects.all())

    return JsonResponse({
        'cantidad': item.cantidad,
        'subtotal': item.subtotal,
        'total': total
    })
def eliminar_producto(request, item_id):

    item = get_object_or_404(Carrito, id=item_id)
    item.delete()

    total = sum(i.subtotal for i in Carrito.objects.all())

    return JsonResponse({
        'total': total
    })
def pago_exitoso(request):

    items = Carrito.objects.all()

    total = sum(item.subtotal for item in items)

    venta = Venta.objects.create(
        total=total,
        metodo_entrega="Mercado Pago"
    )

    mensaje = "🛒 Nueva compra:%0A"

    for item in items:

        DetalleVenta.objects.create(
            venta=venta,
            producto=item.producto,
            cantidad=item.cantidad,
            subtotal=item.subtotal
        )

        item.producto.stock -= item.cantidad
        item.producto.save()

        mensaje += f"{item.producto.nombre} x{item.cantidad} - ${item.subtotal}%0A"

    items.delete()

    mensaje += f"%0A💰 Total: ${total}"
    

    return redirect(f"https://wa.me/5493541620247?text={mensaje}")
def pago_error(request):
    return render(request,'pago_error.html')


def generar_comprobante(request, venta_id):

    venta = Venta.objects.get(id=venta_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="comprobante.pdf"'

    pdf = canvas.Canvas(response)

    logo_path = os.path.join(settings.MEDIA_ROOT, 'logo.png')

    if os.path.exists(logo_path):
        pdf.drawImage(ImageReader(logo_path), 50, 750, width=100, height=50)

    y = 700

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(180, y, "FORRAJERÍA")

    y -= 40

    pdf.setFont("Helvetica", 11)

    pdf.drawString(50, y, f"Venta N°: {venta.id}")
    y -= 20

    pdf.drawString(50, y, f"Fecha: {venta.fecha.strftime('%d/%m/%Y %H:%M')}")
    y -= 30

    pdf.line(50, y, 500, y)

    y -= 20

    pdf.drawString(50, y, "Producto")
    pdf.drawString(300, y, "Cant.")
    pdf.drawString(400, y, "Subtotal")

    y -= 20

    pdf.line(50, y, 500, y)

    y -= 20

    for detalle in venta.detalleventa_set.all():

        pdf.drawString(50, y, detalle.producto.nombre)
        pdf.drawString(300, y, str(detalle.cantidad))
        pdf.drawString(400, y, f"${detalle.subtotal}")

        y -= 25

    pdf.line(50, y, 500, y)

    y -= 30

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(350, y, f"TOTAL: ${venta.total}")

    pdf.save()

    return response

from .models import Carrito
from django.shortcuts import redirect

def vaciar_carrito(request):

    Carrito.objects.all().delete()

    return redirect('/carrito/')
def comprobante(request, venta_id):

    venta = Venta.objects.get(id=venta_id)
    detalles = venta.detalles.all()

    return render(request, 'comprobante.html', {
        'venta': venta,
        'detalles': detalles
    })