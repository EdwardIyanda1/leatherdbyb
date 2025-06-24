from django.urls import path, include
from . import views
from .views import checkout

urlpatterns = [
    path('checkout/', checkout, name='checkout'),
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),
    path('account/', views.account_dashboard, name='account_dashboard'),
    path('account/addresses/', views.address_list, name='address_list'),
    path('account/addresses/add/', views.address_add, name='address_add'),
    path('account/addresses/<int:pk>/edit/', views.address_edit, name='address_edit'),
    path('account/addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),
    path('account/wishlist/', views.wishlist, name='wishlist'),
    path('account/wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('account/wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),
    path('account/orders/', views.order_history, name='order_history'),
    path('account/orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('about/', views.about, name='about'),
    path('accounts/', include('django.contrib.auth.urls')),
]
