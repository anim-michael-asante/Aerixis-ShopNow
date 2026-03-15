from .models import Cart


def cart_count(request):
    count = 0
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(user=request.user).first()
        else:
            session_key = request.session.session_key
            if session_key:
                cart = Cart.objects.filter(session_key=session_key).first()
            else:
                cart = None
        if cart:
            count = cart.get_item_count()
    except Exception:
        count = 0
    return {'cart_count': count}
