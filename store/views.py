from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart


# ── HOME ──────────────────────────────────────────────────────────────────────
def home(request):
    featured_products = Product.objects.filter(is_active=True, is_featured=True)[:8]
    categories = Category.objects.all()[:6]
    new_arrivals = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    on_sale = Product.objects.filter(is_active=True, sale_price__isnull=False).exclude(sale_price=None)[:4]
    context = {
        'featured_products': featured_products,
        'categories': categories,
        'new_arrivals': new_arrivals,
        'on_sale': on_sale,
    }
    return render(request, 'home.html', context)


# ── PRODUCTS ──────────────────────────────────────────────────────────────────
def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    category_slug = request.GET.get('category')
    query = request.GET.get('q', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort', '-created_at')

    active_category = None
    if category_slug:
        active_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=active_category)

    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if min_price:
        products = products.filter(price__gte=min_price)
    if max_price:
        products = products.filter(price__lte=max_price)

    sort_options = {
        '-created_at': 'Newest First',
        'created_at': 'Oldest First',
        'price': 'Price: Low to High',
        '-price': 'Price: High to Low',
        'name': 'Name A-Z',
    }
    products = products.order_by(sort)

    context = {
        'products': products,
        'categories': categories,
        'active_category': active_category,
        'query': query,
        'sort': sort,
        'sort_options': sort_options,
        'total_count': products.count(),
    }
    return render(request, 'store/products.html', context)


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    return render(request, 'store/product_detail.html', {'product': product, 'related': related})


# ── CART ──────────────────────────────────────────────────────────────────────
def cart_view(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    return render(request, 'store/cart.html', {'cart': cart, 'items': items})


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    if not product.in_stock():
        messages.error(request, f'Sorry, {product.name} is out of stock.')
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    cart = get_or_create_cart(request)
    quantity = int(request.POST.get('quantity', 1))
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity
    cart_item.save()
    messages.success(request, f'✓ {product.name} added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'home'))


def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id)
    action = request.POST.get('action')
    if action == 'increase':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
            messages.info(request, 'Item removed from cart.')
            return redirect('cart')
    elif action == 'remove':
        cart_item.delete()
        messages.info(request, 'Item removed from cart.')
    return redirect('cart')


def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, pk=item_id)
    cart_item.delete()
    messages.info(request, 'Item removed from cart.')
    return redirect('cart')


# ── CHECKOUT & ORDERS ─────────────────────────────────────────────────────────
@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()

    if not items:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    user = request.user
    initial = {}
    if hasattr(user, 'profile'):
        initial = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'phone': user.profile.phone,
            'address': user.profile.address,
            'city': user.profile.city,
        }

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = user
            order.total_price = cart.get_total()
            order.save()
            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    product_name=item.product.name,
                    quantity=item.quantity,
                    price=item.product.get_price(),
                )
                # Reduce stock
                item.product.stock = max(0, item.product.stock - item.quantity)
                item.product.save()
            cart.items.all().delete()
            messages.success(request, f'🎉 Order #{order.pk} placed successfully!')
            return redirect('order_detail', pk=order.pk)
    else:
        form = CheckoutForm(initial=initial)

    return render(request, 'store/checkout.html', {
        'form': form, 'cart': cart, 'items': items
    })


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'store/orders.html', {'orders': orders})


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    return render(request, 'store/order_detail.html', {'order': order})


@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk, user=request.user)
    if order.status == 'pending':
        order.status = 'cancelled'
        order.save()
        messages.success(request, f'Order #{order.pk} has been cancelled.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    return redirect('order_list')
