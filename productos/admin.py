from django.contrib import admin
from .models import Producto, Categoria, SubCategoria

admin.site.register(Producto)
admin.site.register(Categoria)
admin.site.register(SubCategoria)