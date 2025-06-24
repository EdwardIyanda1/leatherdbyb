from django.contrib import admin
from .models import (
    Product, Category, ProductImage, 
    UserProfile, Address, Cart, CartItem,
    Order, OrderItem, Wishlist
)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'rating']
    list_filter = ['category', 'rating']
    search_fields = ['name', 'description', 'sku']
    inlines = [ProductImageInline]

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'id']
    inlines = [OrderItemInline]

class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'city', 'state', 'is_default']
    list_filter = ['is_default', 'type']
    search_fields = ['user__username', 'name', 'city']

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(UserProfile)
admin.site.register(Address, AddressAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Wishlist)