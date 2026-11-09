from django.db.models import Q
import urllib.parse
from django.shortcuts import render, get_object_or_404, redirect
from .models import Categoria, Refaccion, Carrito, ItemCarrito, Pedido,ItemPedido

def _obtener_o_crear_carrito(request):
    if not request.session.session_key:
        request.session.create()
    s_key = request.session.session_key

    if request.user.is_authenticated:
        carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    else:
        carrito, _ = Carrito.objects.get_or_create(session_key=s_key)
    return carrito

def lista_refacciones(request, categoria_slug=None):
    categoria = None
    categorias = Categoria.objects.all()
    refacciones = Refaccion.objects.filter(activo=True)

    # Lógica del buscador
    query = request.GET.get('q')
    if query:
        refacciones = refacciones.filter(
            Q(nombre__icontains=query) | 
            Q(sku__icontains=query) | 
            Q(compatibilidad__icontains=query)
        )

    if categoria_slug:
        categoria = get_object_or_404(Categoria, slug=categoria_slug)
        refacciones = refacciones.filter(categoria=categoria)

    return render(request, 'tienda/lista_refacciones.html', {
        'categoria_actual': categoria,
        'categorias': categorias,
        'refacciones': refacciones,
        'query': query,
    })

def detalle_refaccion(request, id, slug):
    refaccion = get_object_or_404(Refaccion, id=id, slug=slug, activo=True)
    return render(request, 'tienda/detalle_refaccion.html', {
        'refaccion': refaccion
    })

def agregar_al_carrito(request, refaccion_id):
    if request.method == 'POST':
        refaccion = get_object_or_404(Refaccion, id=refaccion_id, activo=True)
        carrito = _obtener_o_crear_carrito(request)
        cantidad = int(request.POST.get('cantidad', 1))

        item, creado = ItemCarrito.objects.get_or_create(carrito=carrito, refaccion=refaccion)
        if not creado:
            item.cantidad += cantidad
        else:
            item.cantidad = cantidad
        item.save()

    return redirect('tienda:ver_carrito')

def eliminar_del_carrito(request, item_id):
    if request.method == 'POST':
        carrito = _obtener_o_crear_carrito(request)
        item = get_object_or_404(ItemCarrito, id=item_id, carrito=carrito)
        item.delete()
    return redirect('tienda:ver_carrito')

def ver_carrito(request):
    carrito = _obtener_o_crear_carrito(request)
    items = carrito.items.select_related('refaccion').all()
    total = sum(item.obtener_costo() for item in items)

    return render(request, 'tienda/carrito.html', {
        'carrito': carrito,
        'items': items,
        'total': total
    })

def checkout(request):
    carrito = _obtener_o_crear_carrito(request)
    items = carrito.items.select_related('refaccion').all()
    
    if not items:
        return redirect('tienda:lista_refacciones')

    total = sum(item.obtener_costo() for item in items)

    if request.method == 'POST':
        nombre = request.POST.get('nombre', 'Cliente')
        direccion = request.POST.get('direccion', 'Recolección en tienda')
        telefono_cliente = request.POST.get('telefono', 'Sin número')

        # 1. Guardar la orden en la base de datos (para el Admin)
        pedido = Pedido.objects.create(
            nombre=nombre,
            telefono=telefono_cliente,
            direccion=direccion,
            total=total
        )

        mensaje = f"🚗 *NUEVO PEDIDO #{pedido.id}*\n\n"
        mensaje += f"*Cliente:* {nombre}\n"
        mensaje += f"*Teléfono:* {telefono_cliente}\n"
        mensaje += f"*Dirección:* {direccion}\n\n"
        mensaje += "*Detalle de las piezas:*\n"

        for item in items:
            # 2. Guardar cada pieza comprada ligada al pedido
            ItemPedido.objects.create(
                pedido=pedido,
                refaccion=item.refaccion,
                precio=item.refaccion.precio,
                cantidad=item.cantidad
            )
            mensaje += f"• {item.cantidad}x {item.refaccion.nombre} (SKU: {item.refaccion.sku}) - ${item.obtener_costo()}\n"

        mensaje += f"\n*Total a pagar:* ${total} MXN"

        mensaje_enc = urllib.parse.quote(mensaje)
        numero_whatsapp = "527445865904" 
        url_whatsapp = f"https://api.whatsapp.com/send?phone={numero_whatsapp}&text={mensaje_enc}"

        items.delete()
        return redirect(url_whatsapp)

    return render(request, 'tienda/checkout.html', {
        'items': items,
        'total': total
    })