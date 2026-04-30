from django.urls import path
from .views import filtrar_subcategoria, lista_productos
from productos import views
from .views import crear_admin

urlpatterns = [
    path('', lista_productos, name='lista_productos'),
    path('subcategoria/<int:subcategoria_id>/', filtrar_subcategoria, name='filtrar_subcategoria'),
    path('buscar-ajax/', views.buscar_ajax, name='buscar_ajax'),
    path('producto/<int:id>/', views.detalle_producto, name='detalle_producto'),
    path('crear-admin/', crear_admin),

]