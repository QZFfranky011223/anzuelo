import json
from decimal import Decimal

from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Producto
from .models import Cliente, Venta, DetalleVenta
from django.utils import timezone
from django.db.models import Sum, Count
from django.shortcuts import render, redirect
from django.shortcuts import render, redirect
from .models import Producto


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if user.groups.filter(name='admin').exists():
                return redirect('admin_panel')

            elif user.groups.filter(name='cajero').exists():
                return redirect('inicio')

            else:
                return redirect('inicio')

        else:
            return render(request, 'login.html', {
                'error': ' Usuario o contraseña incorrectos'
            })

    return render(request, 'sistema/login.html')


@login_required
def logout_view(request):
    logout(request)
    return redirect('sistema/login')


@login_required
def inicio(request):
    platos = Producto.objects.filter(categoria='plato')
    bebidas = Producto.objects.filter(categoria='bebida')

    sodas = bebidas.filter(bebida_tipo='soda')
    jugos = bebidas.filter(bebida_tipo='jugo')
    otras_bebidas = bebidas.exclude(bebida_tipo__in=['soda', 'jugo'])

    return render(request, 'sistema/index.html', {
        'platos': platos,
        'sodas': sodas,
        'jugos': jugos,
        'otras_bebidas': otras_bebidas,
        'mesas_total': 30,
    })
def _parse_cart(cart_raw):
    """
    Espera cart_raw con formato JSON:
      [{"producto_id": 1, "cantidad": 2}, ...]
    """
    if not cart_raw:
        return []
    try:
        return json.loads(cart_raw)
    except json.JSONDecodeError:
        return []


@login_required
def crear_pedido(request):
    if request.method != 'POST':
        return redirect('inicio')

    mesa = int(request.POST.get('mesa', 1))
    cliente_nombre = (request.POST.get('cliente_nombre') or '').strip()
    cliente_telefono = (request.POST.get('cliente_telefono') or '').strip()
    cart = _parse_cart(request.POST.get('cart'))

    if not cliente_nombre or not cliente_telefono:
        return render(request, 'index.html', {
            'platos': list(Producto.objects.filter(categoria=Producto.Categoria.PLATO)),
            'sodas': list(Producto.objects.filter(categoria=Producto.Categoria.BEBIDA, bebida_tipo=Producto.BebidaTipo.SODA)),
            'jugos': list(Producto.objects.filter(categoria=Producto.Categoria.BEBIDA, bebida_tipo=Producto.BebidaTipo.JUGO_NATURAL)),
            'otras_bebidas': list(Producto.objects.filter(categoria=Producto.Categoria.BEBIDA, bebida_tipo=Producto.BebidaTipo.OTRO)),
            'mesas_total': 30,
            'error': 'Faltan datos del cliente (nombre y teléfono).'
        })

    if not cart:
        return render(request, 'index.html', {
            'platos': list(Producto.objects.filter(categoria=Producto.Categoria.PLATO)),
            'sodas': list(Producto.objects.filter(categoria=Producto.Categoria.BEBIDA, bebida_tipo=Producto.BebidaTipo.SODA)),
            'jugos': list(Producto.objects.filter(categoria=Producto.Categoria.BEBIDA, bebida_tipo=Producto.BebidaTipo.JUGO_NATURAL)),
            'otras_bebidas': list(Producto.objects.filter(categoria=Producto.Categoria.BEBIDA, bebida_tipo=Producto.BebidaTipo.OTRO)),
            'mesas_total': 30,
            'error': 'Tu pedido está vacío.'
        })

    cliente = Cliente.objects.create(nombre=cliente_nombre, telefono=cliente_telefono)
    venta = Venta.objects.create(cliente=cliente, mesa=mesa, total=Decimal('0.00'))

    total = Decimal('0.00')
    for item in cart:
        producto_id = item.get('producto_id')
        cantidad = int(item.get('cantidad', 0))
        if not producto_id or cantidad <= 0:
            continue

        producto = get_object_or_404(Producto, id=producto_id)
        subtotal = (producto.precio or Decimal('0.00')) * cantidad
        DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=cantidad,
            subtotal=subtotal,
        )
        total += subtotal

    venta.total = total
    venta.save()

    return redirect('pedido_detail', venta_id=venta.id)


@login_required
def pedido_detail(request, venta_id):
    venta = get_object_or_404(
        Venta.objects.select_related('cliente').all(),
        id=venta_id
    )

    detalles = DetalleVenta.objects.select_related('producto').filter(venta=venta)
    return render(request, 'sistema/pedido.html', {
        'venta': venta,
        'detalles': detalles,
    })


@login_required
def pedido_ultimo_mesa(request, mesa):
    venta = (
        Venta.objects
        .select_related('cliente')
        .filter(mesa=mesa)
        .order_by('-fecha')
        .first()
    )
    if not venta:
        return redirect('inicio')
    return redirect('pedido_detail', venta_id=venta.id)


@login_required
def reporte_ventas(request):
    # Fecha seleccionada (YYYY-MM-DD). Por defecto: hoy.
    fecha_str = (request.GET.get('fecha') or '').strip()
    if fecha_str:
        try:
            fecha = timezone.datetime.fromisoformat(fecha_str).date()
        except ValueError:
            fecha = timezone.localdate()
    else:
        fecha = timezone.localdate()

    inicio_dia = timezone.make_aware(timezone.datetime.combine(fecha, timezone.datetime.min.time()))
    fin_dia = timezone.make_aware(timezone.datetime.combine(fecha, timezone.datetime.max.time()))

    ventas_qs = Venta.objects.filter(fecha__range=(inicio_dia, fin_dia))

    resumen = ventas_qs.aggregate(
        total_vendido=Sum('total'),
        cantidad_ventas=Count('id'),
    )

    detalles_qs = (
        DetalleVenta.objects
        .select_related('producto')
        .filter(venta__in=ventas_qs)
        .values('producto__nombre', 'producto__categoria', 'producto__bebida_tipo')
        .annotate(
            unidades=Sum('cantidad'),
            subtotal=Sum('subtotal'),
        )
        .order_by('-subtotal', '-unidades', 'producto__nombre')
    )

    return render(request, 'sistema/reporte.html', {
        'fecha': fecha,
        'resumen': resumen,
        'detalles': list(detalles_qs),
    })


# LISTAR PRODUCTOS
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'sistema/productos.html', {
        'productos': productos
    })

def agregar_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')
        categoria = request.POST.get('tipo')          # 🔥 viene del radio
        bebida_tipo = request.POST.get('subtipo')     # 🔥 viene del hidden
        imagen = request.FILES.get('imagen')

        if not nombre or not precio:
            return render(request, 'sistema/agregar_producto.html', {
                'error': 'Faltan datos'
            })

        Producto.objects.create(
            nombre=nombre,
            precio=float(precio),
            categoria=categoria,
            bebida_tipo=bebida_tipo if categoria == 'bebida' else '',
            imagen=imagen
        )

        return redirect('agregar_producto')   # 🔥 IMPORTANTE

    return render(request, 'sistema/agregar_producto.html')
# VER VENTAS
def lista_ventas(request):
    ventas = Venta.objects.select_related('cliente').all().order_by('-fecha')

    return render(request, 'sistema/ventas.html', {
        'ventas': ventas
    })
@login_required
def admin_panel(request):
    if not request.user.groups.filter(name='admin').exists():
        return redirect('inicio')

    from django.utils import timezone

    # 🔹 Fecha actual
    hoy = timezone.now().date()

    # 🔹 Últimas ventas
    ventas_recientes = Venta.objects.all().order_by('-fecha')[:10]

    # 🔹 Totales
    total_productos = Producto.objects.count()
    total_ventas = Venta.objects.count()

    # 🔹 Ventas del día
    ventas_hoy = Venta.objects.filter(fecha__date=hoy)
    ventas_dia = sum(v.total for v in ventas_hoy)

    # 🔹 Mesas ocupadas (únicas hoy)
    mesas_ocupadas = ventas_hoy.values('mesa').distinct().count()

    return render(request, 'sistema/admin_panel.html', {
        'total_productos': total_productos,
        'total_ventas': total_ventas,
        'ventas': ventas_recientes,          # lista para mostrar
        'ventas_dia': ventas_dia,
        'mesas_ocupadas': mesas_ocupadas,
        'total_mesas': 30,

        #  ahora sí existen
        'ventas_recientes': ventas_recientes,
        'fecha_hoy': hoy,
    })
    
def editar_producto(request, id):
    producto = Producto.objects.get(id=id)

    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.precio = request.POST.get('precio')
        producto.descripcion = request.POST.get('descripcion')

        categoria = request.POST.get('tipo')
        bebida_tipo = request.POST.get('subtipo')

        producto.categoria = categoria
        producto.bebida_tipo = bebida_tipo if categoria == 'bebida' else ''

        if request.FILES.get('imagen'):
            producto.imagen = request.FILES.get('imagen')

        producto.save()

        return redirect('productos')

    return render(request, 'sistema/editar_producto.html', {
        'producto': producto
    })

def eliminar_producto(request, id):
    producto = Producto.objects.get(id=id)
    producto.delete()
    return redirect('productos')