from django.contrib import admin
from .models import (
    Product, Category, ProductImage, 
    UserProfile, Address, Cart, CartItem,
    Order, OrderItem, Wishlist, Size, ProductSize
)
from .models import NewsletterSubscriber

# ----- Product Inlines -----

class ProductSizeInline(admin.TabularInline):
    model = ProductSize
    extra = 1

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)
    
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

# ----- Product Admin -----

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock', 'rating', 'featured']
    list_editable = ['featured']
    list_filter = ['category', 'rating']
    search_fields = ['name', 'description', 'sku']
    inlines = [ProductImageInline, ProductSizeInline]

    def stock_alert(self, obj):
        return "⚠️ Low" if obj.stock < 5 else "OK"
    stock_alert.short_description = "Stock Status"

# ----- Order Admin -----

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    # readonly_fields = ['product', 'size', 'quantity', 'price']
    fields = ['product', 'size', 'quantity', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total', 'status', 'created_at', 'full_delivery_address', 'ordered_sizes']
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

    def ordered_sizes(self, obj):
        items = obj.items.select_related('product', 'size')
        result = []
        for item in items:
            if item.product:
                size_display = f" ({item.size.name})" if item.size else ""
                result.append(f"{item.product.name}{size_display}")
        return ", ".join(result) if result else "—"


    ordered_sizes.short_description = 'Sizes Ordered'

# ----- Address Admin -----

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'city', 'state', 'is_default']
    list_filter = ['is_default', 'type']
    search_fields = ['user__username', 'name', 'city']

# ----- Other Models -----

admin.site.register(Size)
# admin.site.register(ProductSize)
admin.site.register(Category)
admin.site.register(UserProfile)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Wishlist)
