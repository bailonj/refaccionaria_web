from django.urls import path
from . import views

app_name = 'tienda'

urlpatterns = [
    path('', views.lista_refacciones, name='lista_refacciones'),
    path('categoria/<slug:categoria_slug>/', views.lista_refacciones, name='lista_por_categoria'),
    path('refaccion/<int:id>/<slug:slug>/', views.detalle_refaccion, name='detalle_refaccion'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:refaccion_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_del_carrito'),
    path('checkout/', views.checkout, name='checkout'),
]