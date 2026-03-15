from store.models import Order, Product


def dashboard_context(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}
    try:
        return {
            'pending_orders': Order.objects.filter(status='pending').count(),
            'total_products': Product.objects.filter(is_active=True).count(),
        }
    except Exception:
        return {'pending_orders': 0, 'total_products': 0}
