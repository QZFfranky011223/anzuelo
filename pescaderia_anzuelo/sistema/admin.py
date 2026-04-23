from django.contrib import admin
from .models import Producto, Cliente, Venta, DetalleVenta


# ================================
# PRODUCTOS
# ================================
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'categoria', 'bebida_tipo', 'precio')
    list_filter = ('categoria', 'bebida_tipo')
    search_fields = ('nombre', 'descripcion')
    list_editable = ('precio',)  # editar precio rápido
    ordering = ('nombre',)


# ================================
# CLIENTES
# ================================
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'telefono')
    search_fields = ('nombre', 'telefono')
    ordering = ('nombre',)


# ================================
# DETALLE VENTA (INLINE)
# ================================
class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0


# ================================
# VENTAS
# ================================
@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'mesa', 'cliente', 'fecha', 'total')
    list_filter = ('mesa', 'fecha')
    search_fields = ('cliente__nombre', 'cliente__telefono')
    date_hierarchy = 'fecha'  # filtro por fecha bonito
    inlines = [DetalleVentaInline]  # 👈 ver productos dentro de la venta


# ================================
# DETALLE VENTA
# ================================
@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'producto', 'cantidad', 'subtotal')
    list_filter = ('venta', 'producto')