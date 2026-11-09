from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Categoria, Refaccion, Carrito, ItemCarrito, Pedido, ItemPedido


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nombre',)}

@admin.register(Refaccion)
class RefaccionAdmin(admin.ModelAdmin):
    list_display = ('sku', 'nombre', 'precio', 'stock', 'compatibilidad', 'activo')
    list_filter = ('activo', 'categoria')
    search_fields = ('nombre', 'sku', 'compatibilidad')
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ('precio', 'stock', 'activo')


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    readonly_fields = ('refaccion', 'precio', 'cantidad')
    extra = 0

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'telefono', 'total', 'estado', 'creado_en')
    list_filter = ('estado', 'creado_en')
    search_fields = ('nombre', 'telefono')
    list_editable = ('estado',)
    inlines = [ItemPedidoInline]

admin.site.register(Carrito)
admin.site.register(ItemCarrito)