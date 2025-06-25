from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import (
    Product, Category, Cart, CartItem, 
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
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'products/detail.html', context)

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

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    if not created:
        cart_item.quantity += 1
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

@require_POST
def cart_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = _get_cart(request)

    try:
        cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.quantity -= 1
        if cart_item.quantity > 0:
            cart_item.save()
        else:
            cart_item.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'quantity': cart_item.quantity if cart_item.pk else 0,
                'item_total': float(cart_item.total_price) if cart_item.pk else 0,
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

@login_required
def account_dashboard(request):
    user = request.user
    profile = user.userprofile

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

def order_success(request):
    reference = request.GET.get('reference')
    return render(request, 'order_success.html', {'reference': reference})

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
            
            messages.success(request, "Address added successfully!")
            return redirect('address_list')
    else:
        form = AddressForm()
    
    context = {
        'form': form,
        'title': 'Add New Address',
    }
    return render(request, 'account/address_form.html', context)

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
            
            messages.success(request, "Address updated successfully!")
            return redirect('address_list')
    else:
        form = AddressForm(instance=address)
    
    context = {
        'form': form,
        'title': 'Edit Address',
    }
    return render(request, 'account/address_form.html', context)

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