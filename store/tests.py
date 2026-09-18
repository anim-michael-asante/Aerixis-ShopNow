"""
Tests for the store app.

Covers:
  - Models  (Category, Product, Cart, CartItem, Order, OrderItem)
  - Forms   (CheckoutForm, ProductForm, CategoryForm)
  - Views   (home, product_list, product_detail, cart CRUD, checkout, orders)
  - Context processors (cart_count)
"""

from decimal import Decimal

from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore

from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .forms import CheckoutForm, ProductForm, CategoryForm
from .context_processors import cart_count


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _make_user(username="testuser", password="Str0ng!Pass99", **kw):
    return User.objects.create_user(username=username, password=password, **kw)


def _make_admin(username="admin", password="Str0ng!Pass99"):
    return User.objects.create_user(username=username, password=password, is_staff=True)


def _make_category(name="Electronics", **kw):
    cat, _ = Category.objects.get_or_create(name=name, defaults=kw)
    return cat


def _make_product(category=None, **overrides):
    defaults = {
        "name": "Test Product",
        "description": "A test product.",
        "price": Decimal("99.99"),
        "stock": 10,
        "is_active": True,
    }
    defaults.update(overrides)
    if category is None:
        category = _make_category()
    defaults["category"] = category
    return Product.objects.create(**defaults)


# ═══════════════════════════════════════════════════════════════════════════════
#  MODEL TESTS — Category
# ═══════════════════════════════════════════════════════════════════════════════

class CategoryModelTest(TestCase):

    def test_str(self):
        cat = _make_category(name="Books")
        self.assertEqual(str(cat), "Books")

    def test_slug_auto_generated(self):
        cat = _make_category(name="Smart Phones")
        self.assertEqual(cat.slug, "smart-phones")

    def test_explicit_slug_not_overwritten(self):
        cat = _make_category(name="Gadgets", slug="custom-slug")
        self.assertEqual(cat.slug, "custom-slug")

    def test_product_count(self):
        cat = _make_category()
        _make_product(category=cat)
        _make_product(category=cat, name="Prod2")
        _make_product(category=cat, name="Inactive", is_active=False)
        self.assertEqual(cat.product_count(), 2)

    def test_ordering(self):
        _make_category(name="Zebra")
        _make_category(name="Alpha")
        names = list(Category.objects.values_list("name", flat=True))
        self.assertEqual(names, ["Alpha", "Zebra"])


# ═══════════════════════════════════════════════════════════════════════════════
#  MODEL TESTS — Product
# ═══════════════════════════════════════════════════════════════════════════════

class ProductModelTest(TestCase):

    def test_str(self):
        p = _make_product(name="Widget")
        self.assertEqual(str(p), "Widget")

    def test_slug_auto_generated(self):
        p = _make_product(name="My Great Product")
        self.assertEqual(p.slug, "my-great-product")

    def test_slug_uniqueness(self):
        p1 = _make_product(name="Duplicate")
        p2 = _make_product(name="Duplicate")
        self.assertNotEqual(p1.slug, p2.slug)
        self.assertTrue(p2.slug.startswith("duplicate"))

    def test_get_price_returns_sale_price_if_set(self):
        p = _make_product(price=Decimal("100.00"), sale_price=Decimal("79.99"))
        self.assertEqual(p.get_price(), Decimal("79.99"))

    def test_get_price_returns_regular_price_if_no_sale(self):
        p = _make_product(price=Decimal("100.00"))
        self.assertEqual(p.get_price(), Decimal("100.00"))

    def test_discount_percent(self):
        p = _make_product(price=Decimal("100.00"), sale_price=Decimal("75.00"))
        self.assertEqual(p.discount_percent(), 25)

    def test_discount_percent_zero_when_no_sale(self):
        p = _make_product(price=Decimal("100.00"))
        self.assertEqual(p.discount_percent(), 0)

    def test_discount_percent_zero_when_sale_equals_price(self):
        p = _make_product(price=Decimal("100.00"), sale_price=Decimal("100.00"))
        self.assertEqual(p.discount_percent(), 0)

    def test_in_stock_true(self):
        p = _make_product(stock=5)
        self.assertTrue(p.in_stock())

    def test_in_stock_false(self):
        p = _make_product(stock=0)
        self.assertFalse(p.in_stock())

    def test_ordering_by_newest(self):
        p1 = _make_product(name="First")
        p2 = _make_product(name="Second")
        ids = list(Product.objects.values_list("pk", flat=True))
        self.assertEqual(ids[0], p2.pk)


# ═══════════════════════════════════════════════════════════════════════════════
#  MODEL TESTS — Cart / CartItem
# ═══════════════════════════════════════════════════════════════════════════════

class CartModelTest(TestCase):

    def setUp(self):
        self.user = _make_user()
        self.cart = Cart.objects.create(user=self.user)
        self.product = _make_product(price=Decimal("50.00"))
        self.item = CartItem.objects.create(cart=self.cart, product=self.product, quantity=3)

    def test_str_with_user(self):
        self.assertIn("testuser", str(self.cart))

    def test_str_with_session_key(self):
        cart = Cart.objects.create(session_key="abc123")
        self.assertIn("abc123", str(cart))

    def test_get_total(self):
        self.assertEqual(self.cart.get_total(), Decimal("150.00"))

    def test_get_item_count(self):
        self.assertEqual(self.cart.get_item_count(), 3)

    def test_multiple_items_total(self):
        p2 = _make_product(name="Other", price=Decimal("20.00"))
        CartItem.objects.create(cart=self.cart, product=p2, quantity=2)
        self.assertEqual(self.cart.get_total(), Decimal("190.00"))

    def test_multiple_items_count(self):
        p2 = _make_product(name="Other", price=Decimal("20.00"))
        CartItem.objects.create(cart=self.cart, product=p2, quantity=2)
        self.assertEqual(self.cart.get_item_count(), 5)


class CartItemModelTest(TestCase):

    def test_str(self):
        p = _make_product(name="Keyboard")
        cart = Cart.objects.create(session_key="s1")
        item = CartItem.objects.create(cart=cart, product=p, quantity=2)
        self.assertEqual(str(item), "2x Keyboard")

    def test_get_subtotal(self):
        p = _make_product(price=Decimal("25.00"))
        cart = Cart.objects.create(session_key="s2")
        item = CartItem.objects.create(cart=cart, product=p, quantity=4)
        self.assertEqual(item.get_subtotal(), Decimal("100.00"))

    def test_subtotal_uses_sale_price(self):
        p = _make_product(price=Decimal("100.00"), sale_price=Decimal("60.00"))
        cart = Cart.objects.create(session_key="s3")
        item = CartItem.objects.create(cart=cart, product=p, quantity=2)
        self.assertEqual(item.get_subtotal(), Decimal("120.00"))


# ═══════════════════════════════════════════════════════════════════════════════
#  MODEL TESTS — Order / OrderItem
# ═══════════════════════════════════════════════════════════════════════════════

class OrderModelTest(TestCase):

    def setUp(self):
        self.user = _make_user()
        self.order = Order.objects.create(
            user=self.user,
            first_name="John",
            last_name="Doe",
            email="j@d.com",
            phone="0551111111",
            address="123 Test",
            city="Accra",
            total_price=Decimal("200.00"),
        )

    def test_str(self):
        self.assertIn("testuser", str(self.order))
        self.assertIn(str(self.order.pk), str(self.order))

    def test_default_status_pending(self):
        self.assertEqual(self.order.status, "pending")

    def test_status_color(self):
        self.assertEqual(self.order.status_color(), "#F59E0B")
        self.order.status = "delivered"
        self.assertEqual(self.order.status_color(), "#10B981")

    def test_status_color_unknown(self):
        self.order.status = "unknown"
        self.assertEqual(self.order.status_color(), "#6B7280")

    def test_ordering_by_newest(self):
        o2 = Order.objects.create(
            user=self.user, first_name="A", last_name="B",
            email="a@b.com", phone="0", address="X", city="Y",
            total_price=Decimal("50.00"),
        )
        ids = list(Order.objects.values_list("pk", flat=True))
        self.assertEqual(ids[0], o2.pk)


class OrderItemModelTest(TestCase):

    def test_str(self):
        user = _make_user()
        order = Order.objects.create(
            user=user, first_name="A", last_name="B",
            email="a@b.com", phone="0", address="X", city="Y",
            total_price=Decimal("100.00"),
        )
        item = OrderItem.objects.create(
            order=order, product_name="Mouse", quantity=3, price=Decimal("15.00"),
        )
        self.assertEqual(str(item), "3x Mouse")

    def test_get_subtotal(self):
        user = _make_user()
        order = Order.objects.create(
            user=user, first_name="A", last_name="B",
            email="a@b.com", phone="0", address="X", city="Y",
            total_price=Decimal("100.00"),
        )
        item = OrderItem.objects.create(
            order=order, product_name="Mouse", quantity=3, price=Decimal("15.00"),
        )
        self.assertEqual(item.get_subtotal(), Decimal("45.00"))


# ═══════════════════════════════════════════════════════════════════════════════
#  FORM TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class CheckoutFormTest(TestCase):

    def _valid_data(self, **overrides):
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "j@d.com",
            "phone": "0551234567",
            "address": "123 Main St",
            "city": "Accra",
            "notes": "",
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        form = CheckoutForm(data=self._valid_data())
        self.assertTrue(form.is_valid())

    def test_missing_required_field(self):
        form = CheckoutForm(data=self._valid_data(first_name=""))
        self.assertFalse(form.is_valid())
        self.assertIn("first_name", form.errors)

    def test_notes_optional(self):
        form = CheckoutForm(data=self._valid_data(notes=""))
        self.assertTrue(form.is_valid())


class ProductFormTest(TestCase):

    def test_valid_form(self):
        cat = _make_category()
        form = ProductForm(data={
            "name": "New Product",
            "category": cat.pk,
            "description": "Desc",
            "price": "49.99",
            "stock": 10,
            "is_active": True,
            "is_featured": False,
        })
        self.assertTrue(form.is_valid())

    def test_missing_name_rejected(self):
        cat = _make_category()
        form = ProductForm(data={
            "name": "",
            "category": cat.pk,
            "description": "Desc",
            "price": "49.99",
            "stock": 10,
        })
        self.assertFalse(form.is_valid())


class CategoryFormTest(TestCase):

    def test_valid_form(self):
        form = CategoryForm(data={"name": "Books", "description": "All books", "icon": "fa-book"})
        self.assertTrue(form.is_valid())

    def test_missing_name_rejected(self):
        form = CategoryForm(data={"name": ""})
        self.assertFalse(form.is_valid())


# ═══════════════════════════════════════════════════════════════════════════════
#  VIEW TESTS — Home
# ═══════════════════════════════════════════════════════════════════════════════

class HomeViewTest(TestCase):

    def test_renders_successfully(self):
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "home.html")

    def test_context_keys(self):
        resp = self.client.get(reverse("home"))
        for key in ("featured_products", "categories", "new_arrivals", "on_sale"):
            self.assertIn(key, resp.context)


# ═══════════════════════════════════════════════════════════════════════════════
#  VIEW TESTS — Products
# ═══════════════════════════════════════════════════════════════════════════════

class ProductListViewTest(TestCase):

    def setUp(self):
        self.cat = _make_category(name="Tech")
        self.p1 = _make_product(category=self.cat, name="Laptop")
        self.p2 = _make_product(category=self.cat, name="Phone")
        self.url = reverse("product_list")

    def test_renders(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "store/products.html")

    def test_category_filter(self):
        resp = self.client.get(self.url, {"category": "tech"})
        self.assertEqual(resp.context["active_category"], self.cat)

    def test_search_filter(self):
        resp = self.client.get(self.url, {"q": "Laptop"})
        self.assertEqual(resp.context["total_count"], 1)

    def test_price_filter(self):
        resp = self.client.get(self.url, {"min_price": "50", "max_price": "100"})
        self.assertEqual(resp.status_code, 200)

    def test_sort(self):
        resp = self.client.get(self.url, {"sort": "price"})
        self.assertEqual(resp.status_code, 200)

    def test_inactive_products_excluded(self):
        _make_product(name="Hidden", is_active=False)
        resp = self.client.get(self.url)
        names = [p.name for p in resp.context["products"]]
        self.assertNotIn("Hidden", names)


class ProductDetailViewTest(TestCase):

    def test_renders(self):
        p = _make_product(name="Widget")
        resp = self.client.get(reverse("product_detail", args=[p.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "store/product_detail.html")
        self.assertEqual(resp.context["product"], p)

    def test_inactive_product_404(self):
        p = _make_product(name="Ghost", is_active=False)
        resp = self.client.get(reverse("product_detail", args=[p.slug]))
        self.assertEqual(resp.status_code, 404)

    def test_related_products_in_context(self):
        cat = _make_category()
        p1 = _make_product(category=cat, name="Main")
        p2 = _make_product(category=cat, name="Related")
        resp = self.client.get(reverse("product_detail", args=[p1.slug]))
        self.assertIn(p2, resp.context["related"])


# ═══════════════════════════════════════════════════════════════════════════════
#  VIEW TESTS — Cart
# ═══════════════════════════════════════════════════════════════════════════════

class CartViewTest(TestCase):

    def test_renders_empty_cart(self):
        resp = self.client.get(reverse("cart"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "store/cart.html")


class AddToCartViewTest(TestCase):

    def setUp(self):
        self.product = _make_product(stock=10)
        self.url = reverse("add_to_cart", args=[self.product.pk])

    def test_add_item(self):
        resp = self.client.post(self.url, {"quantity": 2}, HTTP_REFERER="/")
        self.assertEqual(resp.status_code, 302)
        # A cart should now exist
        self.assertTrue(Cart.objects.exists())

    def test_add_out_of_stock_shows_error(self):
        self.product.stock = 0
        self.product.save()
        resp = self.client.post(self.url, HTTP_REFERER="/")
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(CartItem.objects.exists())

    def test_add_existing_item_increases_quantity(self):
        self.client.post(self.url, {"quantity": 1}, HTTP_REFERER="/")
        self.client.post(self.url, {"quantity": 3}, HTTP_REFERER="/")
        item = CartItem.objects.first()
        self.assertEqual(item.quantity, 4)


class UpdateCartViewTest(TestCase):

    def setUp(self):
        self.product = _make_product(stock=10, price=Decimal("50.00"))
        cart = Cart.objects.create(session_key="test-session")
        self.item = CartItem.objects.create(cart=cart, product=self.product, quantity=3)
        self.url = reverse("update_cart", args=[self.item.pk])

    def test_increase_quantity(self):
        self.client.post(self.url, {"action": "increase"})
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 4)

    def test_decrease_quantity(self):
        self.client.post(self.url, {"action": "decrease"})
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 2)

    def test_decrease_to_zero_removes_item(self):
        self.item.quantity = 1
        self.item.save()
        self.client.post(self.url, {"action": "decrease"})
        self.assertFalse(CartItem.objects.filter(pk=self.item.pk).exists())

    def test_remove_action(self):
        self.client.post(self.url, {"action": "remove"})
        self.assertFalse(CartItem.objects.filter(pk=self.item.pk).exists())


class RemoveFromCartViewTest(TestCase):

    def test_removes_item(self):
        p = _make_product()
        cart = Cart.objects.create(session_key="test-session")
        item = CartItem.objects.create(cart=cart, product=p, quantity=1)
        resp = self.client.post(reverse("remove_from_cart", args=[item.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(CartItem.objects.filter(pk=item.pk).exists())


# ═══════════════════════════════════════════════════════════════════════════════
#  VIEW TESTS — Checkout & Orders
# ═══════════════════════════════════════════════════════════════════════════════

class CheckoutViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = _make_user()
        self.url = reverse("checkout")
        self.client.login(username="testuser", password="Str0ng!Pass99")
        self.product = _make_product(stock=5, price=Decimal("40.00"))
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

    def test_requires_login(self):
        self.client.logout()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_get_renders_form(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "store/checkout.html")

    def test_post_creates_order(self):
        resp = self.client.post(self.url, {
            "first_name": "John",
            "last_name": "Doe",
            "email": "j@d.com",
            "phone": "0551111111",
            "address": "123 Main St",
            "city": "Accra",
            "notes": "",
        })
        self.assertEqual(resp.status_code, 302)
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.total_price, Decimal("80.00"))
        self.assertEqual(order.items.count(), 1)

    def test_post_reduces_stock(self):
        self.client.post(self.url, {
            "first_name": "John", "last_name": "Doe",
            "email": "j@d.com", "phone": "0", "address": "X",
            "city": "Y", "notes": "",
        })
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

    def test_post_clears_cart(self):
        self.client.post(self.url, {
            "first_name": "John", "last_name": "Doe",
            "email": "j@d.com", "phone": "0", "address": "X",
            "city": "Y", "notes": "",
        })
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.items.count(), 0)

    def test_empty_cart_redirects(self):
        Cart.objects.get(user=self.user).items.all().delete()
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)


class OrderListViewTest(TestCase):

    def setUp(self):
        self.user = _make_user()
        self.client.login(username="testuser", password="Str0ng!Pass99")

    def test_requires_login(self):
        self.client.logout()
        resp = self.client.get(reverse("order_list"))
        self.assertEqual(resp.status_code, 302)

    def test_renders(self):
        resp = self.client.get(reverse("order_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "store/orders.html")


class OrderDetailViewTest(TestCase):

    def setUp(self):
        self.user = _make_user()
        self.order = Order.objects.create(
            user=self.user, first_name="A", last_name="B",
            email="a@b.com", phone="0", address="X", city="Y",
            total_price=Decimal("100.00"),
        )
        self.client.login(username="testuser", password="Str0ng!Pass99")

    def test_renders(self):
        resp = self.client.get(reverse("order_detail", args=[self.order.pk]))
        self.assertEqual(resp.status_code, 200)

    def test_other_user_gets_404(self):
        other = _make_user(username="other")
        self.client.login(username="other", password="Str0ng!Pass99")
        resp = self.client.get(reverse("order_detail", args=[self.order.pk]))
        self.assertEqual(resp.status_code, 404)


class CancelOrderViewTest(TestCase):

    def setUp(self):
        self.user = _make_user()
        self.client.login(username="testuser", password="Str0ng!Pass99")
        self.order = Order.objects.create(
            user=self.user, first_name="A", last_name="B",
            email="a@b.com", phone="0", address="X", city="Y",
            total_price=Decimal("100.00"), status="pending",
        )

    def test_cancel_pending_order(self):
        resp = self.client.post(reverse("cancel_order", args=[self.order.pk]))
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "cancelled")

    def test_cannot_cancel_shipped_order(self):
        self.order.status = "shipped"
        self.order.save()
        self.client.post(reverse("cancel_order", args=[self.order.pk]))
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "shipped")


# ═══════════════════════════════════════════════════════════════════════════════
#  CONTEXT PROCESSOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class CartCountContextProcessorTest(TestCase):

    def test_returns_zero_for_anonymous(self):
        factory = RequestFactory()
        request = factory.get("/")
        request.user = type("AnonymousUser", (), {"is_authenticated": False})()
        request.session = SessionStore()
        result = cart_count(request)
        self.assertEqual(result["cart_count"], 0)

    def test_returns_count_for_authenticated_user(self):
        user = _make_user()
        cart = Cart.objects.create(user=user)
        p = _make_product()
        CartItem.objects.create(cart=cart, product=p, quantity=5)
        factory = RequestFactory()
        request = factory.get("/")
        request.user = user
        result = cart_count(request)
        self.assertEqual(result["cart_count"], 5)


# ═══════════════════════════════════════════════════════════════════════════════
#  STORE SECURITY TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class StoreSecurityTest(TestCase):

    def test_product_form_rejects_ssrf_urls(self):
        cat = _make_category()
        # Test loopback IP
        form = ProductForm(data={
            "name": "SSRF Product",
            "category": cat.pk,
            "description": "Desc",
            "price": "10.00",
            "stock": 5,
            "image_url": "http://127.0.0.1:8000/secret",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("image_url", form.errors)

        # Test localhost
        form = ProductForm(data={
            "name": "SSRF Product 2",
            "category": cat.pk,
            "description": "Desc",
            "price": "10.00",
            "stock": 5,
            "image_url": "http://localhost/admin",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("image_url", form.errors)

    def test_product_form_accepts_valid_public_url(self):
        cat = _make_category()
        form = ProductForm(data={
            "name": "Valid Image Product",
            "category": cat.pk,
            "description": "Desc",
            "price": "10.00",
            "stock": 5,
            "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
        })
        self.assertTrue(form.is_valid(), form.errors)

