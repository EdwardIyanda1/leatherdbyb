from django.urls import path, include
from .views import CustomPasswordResetView
from . import views
from django.contrib.auth import views as auth_views
from core.views import health_check
from core.views import run_migrations

urlpatterns = [
    path("healthz", health_check, name="health_check"),
    path('', views.home, name='home'),
    path("run-migrations/", run_migrations),
    path('subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('checkout/', views.checkout, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),
    path('go/', views.external_redirect_view, name='external_redirect'),
    path('paystack/webhook/', views.paystack_webhook, name='paystack_webhook'),
    path('accounts/password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    # Products & Cart
    path('products/', views.product_list, name='product_list'),
    path('products/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),

    # Account & Auth
    path('accounts/signup/', views.signup_view, name='signup'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('account/', views.account_dashboard, name='account_dashboard'),
    path('account/settings/', views.account_settings, name='account_settings'),

    # Addresses
    path('account/addresses/', views.address_list, name='address_list'),
    path('account/addresses/add/', views.address_add, name='address_add'),
    path('account/addresses/<int:pk>/edit/', views.address_edit, name='address_edit'),
    path('account/addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),

    # Wishlist
    path('account/wishlist/', views.wishlist, name='wishlist'),
    path('account/wishlist/add/<int:product_id>/', views.wishlist_add, name='wishlist_add'),
    path('account/wishlist/remove/<int:product_id>/', views.wishlist_remove, name='wishlist_remove'),

    # Orders
    path('account/orders/', views.order_history, name='order_history'),
    path('account/orders/<int:pk>/', views.order_detail, name='order_detail'),

    # Password Reset
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        html_email_template_name='registration/password_reset_email.html',
    ), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),

    # Static Pages
    path('verify/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('our-craft/', views.our_craft, name='our_craft'),
    path('care-guide/', views.care_guide, name='care_guide'),
    path('shipping-returns/', views.shipping_returns, name='shipping_returns'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('about/', views.about, name='about'),
]

# 404 Error Handler
handler404 = 'core.views.custom_404_view'
