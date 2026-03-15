from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from store.models import Product, Category, Order, OrderItem, Cart
from store.forms import ProductForm, CategoryForm


def admin_required(view_func):
    decorated = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff,
        login_url='/accounts/login/'
    )(view_func)
    return decorated


# ── DASHBOARD HOME ─────────────────────────────────────────────
@admin_required
def dashboard_home(request):
    total_products  = Product.objects.filter(is_active=True).count()
    total_users     = User.objects.filter(is_staff=False).count()
    total_orders    = Order.objects.count()
    total_revenue   = Order.objects.aggregate(r=Sum('total_price'))['r'] or 0
    pending_orders  = Order.objects.filter(status='pending').count()
    low_stock       = Product.objects.filter(stock__lte=5, is_active=True).count()
    recent_orders   = Order.objects.select_related('user').order_by('-created_at')[:8]
    top_products    = Product.objects.filter(is_active=True).order_by('-created_at')[:6]
    recent_users    = User.objects.filter(is_staff=False).order_by('-date_joined')[:5]
    categories      = Category.objects.annotate(cnt=Count('products')).order_by('-cnt')[:6]

    # Orders per status
    status_counts = {s: Order.objects.filter(status=s).count()
                     for s in ['pending','processing','shipped','delivered','cancelled']}

    ctx = {
        'total_products': total_products,
        'total_users': total_users,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'pending_orders': pending_orders,
        'low_stock': low_stock,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'recent_users': recent_users,
        'categories': categories,
        'status_counts': status_counts,
    }
    return render(request, 'dashboard/home.html', ctx)


# ── PRODUCTS ───────────────────────────────────────────────────
@admin_required
def product_list(request):
    q = request.GET.get('q', '')
    cat = request.GET.get('cat', '')
    products = Product.objects.select_related('category').order_by('-created_at')
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    if cat:
        products = products.filter(category__slug=cat)
    categories = Category.objects.all()
    return render(request, 'dashboard/products.html', {
        'products': products, 'categories': categories,
        'q': q, 'active_cat': cat,
    })


@admin_required
def product_create(request):
    form = ProductForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'✓ Product "{form.cleaned_data["name"]}" created!')
        return redirect('dash_products')
    return render(request, 'dashboard/product_form.html', {'form': form, 'action': 'Add'})


@admin_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk)
    form = ProductForm(request.POST or None, request.FILES or None, instance=product)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'✓ Product "{product.name}" updated!')
        return redirect('dash_products')
    return render(request, 'dashboard/product_form.html', {
        'form': form, 'action': 'Edit', 'product': product
    })


@admin_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        name = product.name
        product.delete()
        messages.success(request, f'Product "{name}" deleted.')
        return redirect('dash_products')
    return render(request, 'dashboard/confirm_delete.html', {
        'object': product, 'type': 'Product', 'cancel_url': 'dash_products'
    })


@admin_required
def product_toggle(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save()
    status = 'activated' if product.is_active else 'deactivated'
    messages.success(request, f'Product "{product.name}" {status}.')
    return redirect('dash_products')


# ── CATEGORIES ─────────────────────────────────────────────────
@admin_required
def category_list(request):
    cats = Category.objects.annotate(cnt=Count('products')).order_by('name')
    return render(request, 'dashboard/categories.html', {'categories': cats})


@admin_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Category "{form.cleaned_data["name"]}" created!')
        return redirect('dash_categories')
    return render(request, 'dashboard/category_form.html', {'form': form, 'action': 'Add'})


@admin_required
def category_edit(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    form = CategoryForm(request.POST or None, instance=cat)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'Category "{cat.name}" updated!')
        return redirect('dash_categories')
    return render(request, 'dashboard/category_form.html', {'form': form, 'action': 'Edit', 'category': cat})


@admin_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        name = cat.name
        cat.delete()
        messages.success(request, f'Category "{name}" deleted.')
        return redirect('dash_categories')
    return render(request, 'dashboard/confirm_delete.html', {
        'object': cat, 'type': 'Category', 'cancel_url': 'dash_categories'
    })


# ── ORDERS ─────────────────────────────────────────────────────
@admin_required
def order_list(request):
    status = request.GET.get('status', '')
    orders = Order.objects.select_related('user').order_by('-created_at')
    if status:
        orders = orders.filter(status=status)
    return render(request, 'dashboard/orders.html', {
        'orders': orders,
        'active_status': status,
        'status_choices': Order.STATUS_CHOICES,
    })


@admin_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.pk} status updated to {order.get_status_display()}.')
    return render(request, 'dashboard/order_detail.html', {
        'order': order,
        'status_choices': Order.STATUS_CHOICES,
    })


# ── USERS ──────────────────────────────────────────────────────
@admin_required
def user_list(request):
    q = request.GET.get('q', '')
    users = User.objects.order_by('-date_joined')
    if q:
        users = users.filter(Q(username__icontains=q) | Q(email__icontains=q) |
                             Q(first_name__icontains=q) | Q(last_name__icontains=q))
    return render(request, 'dashboard/users.html', {'users': users, 'q': q})


@admin_required
def user_detail(request, pk):
    u = get_object_or_404(User, pk=pk)
    orders = Order.objects.filter(user=u).order_by('-created_at')
    return render(request, 'dashboard/user_detail.html', {'u': u, 'orders': orders})


@admin_required
def user_toggle(request, pk):
    u = get_object_or_404(User, pk=pk)
    if u != request.user:
        u.is_active = not u.is_active
        u.save()
        status = 'activated' if u.is_active else 'deactivated'
        messages.success(request, f'User "{u.username}" {status}.')
    return redirect('dash_users')


@admin_required
def user_delete(request, pk):
    u = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if u != request.user:
            username = u.username
            u.delete()
            messages.success(request, f'User "{username}" deleted.')
        return redirect('dash_users')
    return render(request, 'dashboard/confirm_delete.html', {
        'object': u, 'type': 'User', 'cancel_url': 'dash_users'
    })
