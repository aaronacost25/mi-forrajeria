from django.shortcuts import render
from django.db.models import Q

from carrito.models import Carrito
from .models import Producto, Categoria
from django.contrib.auth.models import User
from django.http import HttpResponse

from django.contrib.auth.models import User
from django.http import HttpResponse

def crear_admin(request):
    try:
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@gmail.com', '1234')
            return HttpResponse("Admin creado")
        else:
            return HttpResponse("El admin ya existe")
    except Exception as e:
        return HttpResponse(f"Error: {e}")
def lista_productos(request):
    busqueda = request.GET.get('buscar', '')

    productos = Producto.objects.all()
    categorias = Categoria.objects.all()
    carrito_count = Carrito.objects.count()

    if busqueda:
        productos = productos.filter(
            Q(nombre__icontains=busqueda) |
            Q(descripcion__icontains=busqueda)
        )
        destacados = Producto.objects.none()
    else:
        destacados = Producto.objects.filter(destacado=True)
        productos = Producto.objects.exclude(destacado=True)

    return render(request, 'productos/lista_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'destacados': destacados,
        'busqueda': busqueda , 
        'carrito_count': carrito_count
    })

def filtrar_subcategoria(request, subcategoria_id):
    productos = Producto.objects.filter(subcategoria_id=subcategoria_id)
    categorias = Categoria.objects.all()
    destacados = Producto.objects.none()

    return render(request, 'productos/lista_productos.html', {
        'productos': productos,
        'categorias': categorias,
        'destacados': destacados,
        'busqueda': ''
    })
from django.http import JsonResponse

from django.http import JsonResponse
from django.db.models import Q

def buscar_ajax(request):
    termino = request.GET.get('term', '')

    productos = Producto.objects.filter(
        Q(nombre__icontains=termino) |
        Q(descripcion__icontains=termino)
    )[:5]

    data = []

    for producto in productos:
        data.append({
            'id': producto.id,
            'nombre': producto.nombre,
            'precio': str(producto.precio),
            'imagen': producto.imagen.url,
        })

    return JsonResponse(data, safe=False)

from django.shortcuts import render, get_object_or_404
from .models import Producto
from django.shortcuts import render, get_object_or_404
from .models import Producto

def detalle_producto(request, id):
    producto = get_object_or_404(Producto, id=id)

    relacionados = Producto.objects.filter(
        categoria=producto.categoria
    ).exclude(id=producto.id)[:4]

    return render(request, 'productos/detalle_producto.html', {
        'producto': producto,
        'relacionados': relacionados
    })


