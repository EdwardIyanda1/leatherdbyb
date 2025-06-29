from django.contrib import admin
from django import forms
from .models import Order
from django.core.exceptions import ValidationError
from .models import (
    Product, Category, ProductImage, 
    UserProfile, Address, Cart, CartItem,
    Order, OrderItem, Wishlist, Size, ProductSize
)
from .models import NewsletterSubscriber
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

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

class OrderAdminForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'
        widgets = {
            'status': forms.Select(choices=Order.Status.choices),
        }
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total', 'status', 'created_at', 'full_delivery_address', 'ordered_sizes']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'id']
    inlines = [OrderItemInline]

    def save_model(self, request, obj, form, change):
        try:
            obj.clean()
        except ValidationError as e:
            from django.contrib import messages
            messages.error(request, f"❌ Error: {e}")
            return  # prevent save

        if change:
            old_order = Order.objects.get(pk=obj.pk)
            print(f"🟡 OLD: {old_order.status} → NEW: {obj.status}")

            if old_order.status != Order.Status.SHIPPED and obj.status == Order.Status.SHIPPED:
                print("✅ Sending shipped email...")
                self.send_status_email(obj, "shipped")

            elif old_order.status != Order.Status.DELIVERED and obj.status == Order.Status.DELIVERED:
                print("📦 Sending delivered email...")
                self.send_status_email(obj, "delivered")

            elif old_order.status != Order.Status.CANCELLED and obj.status == Order.Status.CANCELLED:
                print("❌ Sending cancelled email...")
                self.send_status_email(obj, "cancelled")

        super().save_model(request, obj, form, change)


    def send_shipped_email(self, order):
        from django.utils import timezone
        from datetime import timedelta

        context = {
            'user': order.user,
            'order': order,
            'shipment': {
                'carrier': "LeatheredbyB Dispatch",
                'tracking_number': f"LB{order.id:06d}",
                'estimated_delivery': timezone.now() + timedelta(days=3),
                'tracking_url': f"https://leatheredbyb.com/track/{order.id}"
            }
        }

        subject = 'Your LeatheredbyB Order Has Shipped!'
        to_email = order.user.email
        print(f"📧 Preparing to send email to: {to_email}")
        
        try:
            html_message = render_to_string('email/order_shipped.html', context)
            plain_message = render_to_string('email/order_shipped.txt', context)
            print("✅ Email templates rendered successfully.")

            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [to_email],
                html_message=html_message,
            )
            print("✅ Email sent successfully via send_mail().")

        except Exception as e:
            print(f"❌ Error sending email: {e}")

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

    def send_status_email(self, order, status_type):
        context = {
            'user': order.user,
            'order': order,
            'shipment': {
                'carrier': "LeatheredbyB Dispatch",
                'tracking_number': f"LB{order.id:06d}",
                'estimated_delivery': timezone.now() + timedelta(days=3),
                'tracking_url': f"https://leatheredbyb.com/track/{order.id}"
            }
        }

        subject_map = {
            'shipped': 'Your LeatheredbyB Order Has Shipped!',
            'delivered': 'Your LeatheredbyB Order Has Been Delivered!',
            'cancelled': 'Your LeatheredbyB Order Was Cancelled',
        }

        subject = subject_map.get(status_type)
        to_email = order.user.email

        try:
            html_template = f"email/order_{status_type}.html"
            plain_template = f"email/order_{status_type}.txt"

            html_message = render_to_string(html_template, context)
            plain_message = render_to_string(plain_template, context)

            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [to_email],
                html_message=html_message,
            )
            print(f"✅ Email sent successfully for status '{status_type}' to {to_email}")
        except Exception as e:
            print(f"❌ Error sending '{status_type}' email: {e}")




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
