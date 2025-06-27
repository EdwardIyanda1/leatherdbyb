from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
import json
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Product, Category, Cart, CartItem, Size, 
    Order, OrderItem, Wishlist, Address, UserProfile
)
from .forms import AddressForm

def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(featured=True)[:4]
    new_arrivals = Product.objects.order_by('-created_at')[:4]
    
    context = {
        'categories': categories,
        'featured_products': featured_products,
        'new_arrivals': new_arrivals,
    }
    return render(request, 'home.html', context)

@login_required
def account_settings(request):
    user = request.user
    profile = user.userprofile

    if request.method == 'POST':
        # Handle password change
        current_pw = request.POST.get('current_password')
        new_pw = request.POST.get('new_password')
        confirm_pw = request.POST.get('confirm_password')

        if request.user.check_password(current_pw):
            if new_pw == confirm_pw:
                request.user.set_password(new_pw)
                request.user.save()
                update_session_auth_hash(request, request.user)  # Keep user logged in
            else:
                messages.error(request, "New passwords do not match.")
        else:
            messages.error(request, "Current password is incorrect.")

        # Handle email notification setting
        notif_pref = request.POST.get('email_notifications') == "enabled"
        profile = request.user.userprofile
        profile.email_notifications = notif_pref
        profile.save()


        messages.success(request, 'Settings updated.')
        return redirect('account_settings')

    return render(request, 'account/settings.html')

def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.all()
    
    # Filter by category if specified
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(name__icontains=search_query)
    
    context = {
        'categories': categories,
        'products': products,
        'selected_category': category_slug,
        'search_query': search_query,
    }
    return render(request, 'products/list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:4]
    
    # Initialize wishlist as None for anonymous users
    wishlist = None
    if request.user.is_authenticated:
        wishlist, created = Wishlist.objects.get_or_create(user=request.user)

    sizes = product.available_sizes.all()

    return render(request, 'products/detail.html', {
        'product': product,
        'related_products': related_products,
        'wishlist': wishlist,
        'sizes': sizes
    })

@login_required
def address_add(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            
            if address.is_default:
                # Ensure only one default address
                Address.objects.filter(user=request.user).exclude(id=address.id).update(is_default=False)
            
            return redirect('address_list')
    else:
        form = AddressForm()
    
    return render(request, 'account/address_form.html', {
        'form': form,
        'title': 'Add New Address'
    })

@login_required
def address_edit(request, pk):
    address = get_object_or_404(Address, id=pk, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            address = form.save()
            
            if address.is_default:
                # Ensure only one default address
                Address.objects.filter(user=request.user).exclude(id=address.id).update(is_default=False)
            
            return redirect('address_list')
    else:
        form = AddressForm(instance=address)
    
    return render(request, 'account/address_form.html', {
        'form': form,
        'title': 'Edit Address'
    })


def _get_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = get_object_or_404(Cart, id=cart_id)
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    return cart

def cart_detail(request):
    cart = _get_cart(request)
    context = {
        'cart': cart,
    }
    return render(request, 'cart/detail.html', context)

@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_cart(request)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid request data'}, status=400)

    selected_size = data.get('size')
    quantity = data.get('quantity', 1)

    if not selected_size:
        return JsonResponse({'error': 'Please select a size.'}, status=400)

    try:
        size_id = int(selected_size)
        size = Size.objects.get(id=size_id)
    except (ValueError, Size.DoesNotExist):
        return JsonResponse({'error': 'Invalid size selected.'}, status=400)

    try:
        quantity = int(quantity)
        if quantity < 1:
            raise ValueError
    except ValueError:
        return JsonResponse({'error': 'Invalid quantity provided.'}, status=400)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        size=size,
        defaults={'quantity': quantity}
    )

    if not created:
        cart_item.quantity += quantity  # ✅ Use the selected quantity
        cart_item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'quantity': cart_item.quantity,
            'item_total': float(cart_item.total_price),
            'cart_subtotal': float(cart.subtotal),
            'cart_total': float(cart.total),
            'cart_total_items': cart.total_items
        })

    return redirect('cart_detail')


@login_required
def order_success(request):
    reference = request.GET.get('reference')
    cart = _get_cart(request)

    print("✅ order_success view reached with reference:", reference)
    print("✅ Cart items count:", cart.items.count())

    if not cart.items.exists():
        messages.info(request, "Cart is empty or order already processed.")
        return render(request, 'order_success.html', {'reference': reference})

    address = Address.objects.filter(user=request.user).order_by('-is_default').first()
    if not address:
        messages.error(request, "No shipping address found.")
        return redirect('checkout')

    # Create Order
    order = Order.objects.create(
        user=request.user,
        address=address,
        total=cart.total,
        shipping=Decimal('2000.00'),
        tax=Decimal('1500.00'),
        status='processing'
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    cart.items.all().delete()

    print("✅ Order created successfully:", order.id)
    return render(request, 'order_success.html', {
        'reference': reference,
        'order': order
    })

def some_view(request):
    if not request.session.session_key:
        request.session.save()

@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_cart(request)

    full_delete = request.GET.get('full_delete') == '1'

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        if full_delete:
            cart_item.delete()
        else:
            cart_item.quantity -= 1
            if cart_item.quantity > 0:
                cart_item.save()
            else:
                cart_item.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'quantity': cart_item.quantity if cart_item.pk else 0,
                'cart_subtotal': float(cart.subtotal),
                'cart_total': float(cart.total),
                'cart_total_items': cart.total_items
            })
    except CartItem.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False})

    return redirect('cart_detail')


def our_craft(request):
    return render(request, 'info/our_craft.html')

def care_guide(request):
    return render(request, 'info/care_guide.html')

def shipping_returns(request):
    return render(request, 'info/shipping_returns.html')

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # redirect after successful signup
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

def privacy_policy(request):
    return render(request, 'info/privacy_policy.html')

def cart_update(request, product_id):
    if request.method == 'POST' and request.is_ajax():
        product = get_object_or_404(Product, id=product_id)
        cart = _get_cart(request)
        quantity = int(request.POST.get('quantity', 1))
        
        try:
            cart_item = CartItem.objects.get(cart=cart, product=product)
            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
            else:
                cart_item.delete()
            
            return JsonResponse({
                'success': True,
                'subtotal': cart.subtotal,
                'total_items': cart.total_items,
            })
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False})
    
    return JsonResponse({'success': False})

@login_required
def checkout(request):
    cart = _get_cart(request)
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect('cart_detail')
    
    if request.method == 'POST':
        # Process checkout
        address_id = request.POST.get('address')
        try:
            address = Address.objects.get(id=address_id, user=request.user)
            
            # Create order
            order = Order.objects.create(
                user=request.user,
                address=address,
                total=cart.subtotal + 2000 + 1500,  # subtotal + shipping + tax
            )
            
            # Add items to order
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
            
            # Clear cart
            cart.items.all().delete()
            
            messages.success(request, "Order placed successfully!")
            return redirect('order_detail', pk=order.id)
        
        except Address.DoesNotExist:
            messages.error(request, "Please select a valid address")
    
    # Get user addresses
    addresses = Address.objects.filter(user=request.user)
    
    context = {
        'cart': cart,
        'addresses': addresses,
    }
    return render(request, 'checkout.html', context)

def external_redirect_view(request):
    url = request.GET.get('url')
    if not url or not (url.startswith('http://') or url.startswith('https://')):
        return render(request, '404.html', status=404)

    return render(request, 'redirecting.html', {'redirect_url': url})

@login_required
def account_dashboard(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        profile_image = request.FILES.get('profile_image')

        # Handle full name
        if full_name:
            name_parts = full_name.strip().split()
            user.first_name = name_parts[0]
            user.last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
            user.save()

        # Handle UserProfile fields
        profile.phone = phone
        profile.gender = gender
        profile.date_of_birth = date_of_birth or None

        if profile_image:
            profile.profile_image = profile_image

        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect('account_dashboard')

    return render(request, 'account/profile.html')

@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    context = {
        'addresses': addresses,
    }
    return render(request, 'account/addresses.html', context)

@login_required
def address_delete(request, pk):
    address = get_object_or_404(Address, id=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, "Address deleted successfully!")
        return redirect('address_list')
    
    context = {
        'address': address,
    }
    return render(request, 'account/address_confirm_delete.html', context)

@login_required
def wishlist(request):
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    context = {
        'wishlist': wishlist,
    }
    return render(request, 'account/wishlist.html', context)

@login_required
def wishlist_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist, created = Wishlist.objects.get_or_create(user=request.user)
    
    if product not in wishlist.products.all():
        wishlist.products.add(product)
        messages.success(request, f"{product.name} added to wishlist!")
    else:
        messages.info(request, f"{product.name} is already in your wishlist")
    
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))

@login_required
def wishlist_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist = get_object_or_404(Wishlist, user=request.user)
    
    if product in wishlist.products.all():
        wishlist.products.remove(product)
        messages.success(request, f"{product.name} removed from wishlist!")
    else:
        messages.error(request, "Product not found in wishlist")
    
    return redirect('wishlist')

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'orders/history.html', context)

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, id=pk, user=request.user)
    context = {
        'order': order,
    }
    return render(request, 'orders/detail.html', context)

def about(request):
    return render(request, 'about.html')