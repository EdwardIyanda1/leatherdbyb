from django.db import models
from decimal import Decimal
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, help_text="Font Awesome icon class")
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(unique=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0)
    sku = models.CharField(max_length=50, unique=True)
    featured = models.BooleanField(default=False)  # ✅ Add this line
    created_at = models.DateTimeField(auto_now_add=True)
    featured = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')
    is_featured = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Image for {self.product.name}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    class Gender(models.TextChoices):
        MALE = 'male', _('Male')
        FEMALE = 'female', _('Female')
        OTHER = 'other', _('Other')
        PREFER_NOT_TO_SAY = 'prefer_not_to_say', _('Prefer not to say')
    
    gender = models.CharField(
        max_length=20,
        choices=Gender.choices,
        blank=True
    )
    profile_image = models.ImageField(upload_to='profiles/', blank=True)
    
    def __str__(self):
        return self.user.username

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class AddressType(models.TextChoices):
        HOME = 'home', _('Home')
        WORK = 'work', _('Work')
        OTHER = 'other', _('Other')

    STATE_CHOICES = [
        ('oyo', 'Oyo'),
        ('lagos', 'Lagos'),
        ('kaduna', 'Kaduna'),
        # Add more states as needed
    ]

    state = models.CharField(max_length=100, choices=STATE_CHOICES)  # ✅ Only this one

    type = models.CharField(
        max_length=10,
        choices=AddressType.choices,
        default=AddressType.HOME
    )
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    line1 = models.CharField(max_length=255)
    line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.name} - {self.line1}, {self.city}"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def subtotal(self):
        return sum(item.total_price for item in self.items.all())

    @property
    def total(self):
        return self.subtotal + Decimal('2000.00') + Decimal('1500.00')  # Shipping + Tax

    @property
    def total_items(self):
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Anonymous Cart ({self.session_key})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    @property
    def total_price(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, default=2000)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=1500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        PROCESSING = 'processing', _('Processing')
        SHIPPED = 'shipped', _('Shipped')
        DELIVERED = 'delivered', _('Delivered')
        CANCELLED = 'cancelled', _('Cancelled')
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def total_price(self):
        return self.price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product.name if self.product else '[deleted]'}"

class Wishlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    
    def __str__(self):
        return f"Wishlist for {self.user.username}"