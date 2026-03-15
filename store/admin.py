from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Cart, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'product_count', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def product_count(self, obj):
        count = obj.product_count()
        return format_html('<span style="color:#4F46E5;font-weight:bold">{}</span>', count)
    product_count.short_description = 'Products'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'quantity', 'price', 'get_subtotal')

    def get_subtotal(self, obj):
        return f"GH₵{obj.get_subtotal():.2f}"
    get_subtotal.short_description = 'Subtotal'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_thumbnail', 'name', 'category', 'price', 'sale_price', 'stock', 'is_active', 'is_featured')
    list_filter = ('category', 'is_active', 'is_featured')
    list_editable = ('price', 'stock', 'is_active', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at', 'product_thumbnail')
    fieldsets = (
        ('Basic Info', {'fields': ('name', 'slug', 'category', 'description')}),
        ('Pricing', {'fields': ('price', 'sale_price')}),
        ('Media', {'fields': ('image', 'image_url', 'product_thumbnail')}),
        ('Inventory', {'fields': ('stock', 'is_active', 'is_featured')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def product_thumbnail(self, obj):
        url = obj.image.url if obj.image else obj.image_url if obj.image_url else None
        if url:
            return format_html('<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:8px;" />', url)
        return format_html('<div style="width:50px;height:50px;background:#EEF0FF;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#5B4CF5">📦</div>')
    product_thumbnail.short_description = 'Image'


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'item_count', 'cart_total', 'created_at')
    inlines = [CartItemInline]

    def item_count(self, obj):
        return obj.get_item_count()
    item_count.short_description = 'Items'

    def cart_total(self, obj):
        return f"GH₵{obj.get_total():.2f}"
    cart_total.short_description = 'Total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'full_name', 'status_badge', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    list_editable = ('status',) if False else ()  # status editable in detail view
    search_fields = ('user__username', 'first_name', 'last_name', 'email')
    readonly_fields = ('created_at', 'updated_at', 'total_price')
    inlines = [OrderItemInline]

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Customer'

    def status_badge(self, obj):
        color = obj.status_color()
        return format_html(
            '<span style="background:{};color:white;padding:3px 10px;border-radius:20px;font-size:12px;font-weight:bold">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
