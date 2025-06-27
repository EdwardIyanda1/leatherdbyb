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
    list_display = ['name', 'category', 'price', 'stock', 'rating', 'featured']
    list_editable = ['featured']
    list_filter = ['category', 'rating']
    search_fields = ['name', 'description', 'sku']
    inlines = [ProductImageInline]

    def stock_alert(self, obj):
        return "⚠️ Low" if obj.stock < 5 else "OK"
    stock_alert.short_description = "Stock Status"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total', 'status', 'created_at', 'full_delivery_address']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'id']
    inlines = [OrderItemInline]

    def full_delivery_address(self, obj):
        if obj.address:
            return (
                f"{obj.address.name}, {obj.address.phone}, "
                f"{obj.address.line1}, {obj.address.line2 if obj.address.line2 else ''}, "
                f"{obj.address.city}, {obj.address.state}, {obj.address.postal_code}"
            )
        return "No Address"
    full_delivery_address.short_description = 'Delivery Address'


class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'city', 'state', 'is_default']
    list_filter = ['is_default', 'type']
    search_fields = ['user__username', 'name', 'city']
search_fields = ['user__username', 'product__name', 'address__city']

admin.site.register(Product, ProductAdmin)
admin.site.register(Category)
admin.site.register(UserProfile)
admin.site.register(Address, AddressAdmin)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Wishlist)