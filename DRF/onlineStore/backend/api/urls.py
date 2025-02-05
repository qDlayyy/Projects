from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()

router.register(r'products', views.PublicProductViewSet, basename='product')
router.register(r'admin/products', views.AdminProductsViewSet, basename='admin-products')
router.register(r'cart', views.CartItemViewSet, basename='cart')


urlpatterns =  [
    path('', include(router.urls)),
    path('products/<int:pk>/', views.detail_product_public_view, name='detail-product'),
    path('products/<int:pk>/add/', views.add_to_cart, name='add-to-cart'),
    path('admin/promocodes/', views.admin_promocodes_create, name='admin-promocodes-create'),
    path('admin/promocodes/<int:pk>/', views.admin_single_promocode_view, name='admin-promocode'),
    path('admin/settings/', views.admin_store_base_view, name='admin-store-settings'),
    path('admin/settings/<int:pk>', views.admin_store_base_view_single, name='admin-detail-store-settings'),
    path('registration/', views.user_register_view, name='regisrtation'),
    path('registration/<str:token>/', views.user_register_token_confirmation, name='confirmation'),
    path('order/', views.order_view, name='order'),
    path('cabinet/', views.cabinet_view, name='cabinet')
]