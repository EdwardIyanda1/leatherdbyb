from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views
# from django.contrib.auth.views import LogoutView
from .views import checkout
from .views import address_add, address_edit

urlpatterns = [
    path('checkout/', checkout, name='checkout'),
    path('', views.home, name='home'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('our-craft/', views.our_craft, name='our_craft'),
    path('care-guide/', views.care_guide, name='care_guide'),
    path('shipping-returns/', views.shipping_returns, name='shipping_returns'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('account/addresses/add/', address_add, name='address_add'),
    path('account/addresses/<int:pk>/edit/', address_edit, name='address_edit'),
    path('order-success/', views.order_success, name='order_success'),
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
