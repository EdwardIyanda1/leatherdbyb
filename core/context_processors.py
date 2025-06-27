from .models import Cart

def cart_context(request):
    cart = None
    total_items = 0

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    elif request.session.session_key:
        cart = Cart.objects.filter(session_key=request.session.session_key).first()

    if cart:
        total_items = cart.total_items

    return {'cart': cart, 'cart_total_items': total_items}
