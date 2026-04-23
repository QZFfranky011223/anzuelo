from django.urls import path
from . import views

urlpatterns = [

    # 🔐 AUTH
    path('', views.login_view, name='login'),  # login en raíz
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # 🏠 HOME
    path('inicio/', views.inicio, name='inicio'),

    # 🧾 PEDIDOS
    path('crear-pedido/', views.crear_pedido, name='crear_pedido'),
    path('pedido/<int:venta_id>/', views.pedido_detail, name='pedido_detail'),
    path('pedido-mesa/<int:mesa>/ultimo/', views.pedido_ultimo_mesa, name='pedido_ultimo_mesa'),

    # 📊 REPORTES
    path('reporte/', views.reporte_ventas, name='reporte_ventas'),

    # 🛠️ ADMIN PANEL
    path('admin-panel/', views.admin_panel, name='admin_panel'),

    # PRODUCTOS
    path('admin-panel/productos/', views.lista_productos, name='productos'),
    path('admin-panel/productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('admin-panel/productos/editar/<int:id>/', views.editar_producto, name='editar_producto'),
    path('admin-panel/productos/eliminar/<int:id>/', views.eliminar_producto, name='eliminar_producto'),

    # VENTAS
    path('admin-panel/ventas/', views.lista_ventas, name='ventas'),
]