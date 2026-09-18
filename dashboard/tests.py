"""
Tests for the dashboard app.

Covers:
  - Access control       (admin_required decorator, staff-only access)
  - Dashboard home view  (stats & context)
  - Product CRUD         (list, create, edit, delete, toggle)
  - Category CRUD        (list, create, edit, delete)
  - Order management     (list, detail + status update)
  - User management      (list, detail, toggle, delete)
  - Context processors   (dashboard_context)
"""

from decimal import Decimal

from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User, AnonymousUser

from store.models import Category, Product, Order, OrderItem, Cart, CartItem
from .context_processors import dashboard_context


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _make_user(username="customer", password="Str0ng!Pass99", **kw):
    return User.objects.create_user(username=username, password=password, **kw)


def _make_admin(username="admin", password="Str0ng!Pass99"):
    return User.objects.create_user(username=username, password=password, is_staff=True)


def _make_category(name="Electronics", **kw):
    cat, _ = Category.objects.get_or_create(name=name, defaults=kw)
    return cat


def _make_product(category=None, **overrides):
    defaults = {
        "name": "Test Product",
        "description": "Desc",
        "price": Decimal("99.99"),
        "stock": 10,
        "is_active": True,
    }
    defaults.update(overrides)
    if category is None:
        category = _make_category()
    defaults["category"] = category
    return Product.objects.create(**defaults)


def _make_order(user, **overrides):
    defaults = {
        "user": user,
        "first_name": "John",
        "last_name": "Doe",
        "email": "j@d.com",
        "phone": "0551111111",
        "address": "123 Test St",
        "city": "Accra",
        "total_price": Decimal("150.00"),
    }
    defaults.update(overrides)
    return Order.objects.create(**defaults)


# ═══════════════════════════════════════════════════════════════════════════════
#  ACCESS CONTROL TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class AdminAccessControlTest(TestCase):
    """All dashboard views must be restricted to staff users only."""

    def setUp(self):
        self.admin = _make_admin()
        self.customer = _make_user()
        self.dashboard_urls = [
            reverse("dash_home"),
            reverse("dash_products"),
            reverse("dash_product_create"),
            reverse("dash_categories"),
            reverse("dash_category_create"),
            reverse("dash_orders"),
            reverse("dash_users"),
        ]

    def test_anonymous_redirected_to_login(self):
        for url in self.dashboard_urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 302, f"Anonymous not redirected for {url}")
            self.assertIn("/accounts/login/", resp.url)

    def test_non_staff_redirected_to_login(self):
        self.client.login(username="customer", password="Str0ng!Pass99")
        for url in self.dashboard_urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 302, f"Non-staff not redirected for {url}")

    def test_admin_can_access(self):
        self.client.login(username="admin", password="Str0ng!Pass99")
        for url in self.dashboard_urls:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f"Admin blocked from {url}")


# ═══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD HOME TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardHomeViewTest(TestCase):

    def setUp(self):
        self.admin = _make_admin()
        self.client.login(username="admin", password="Str0ng!Pass99")
        self.url = reverse("dash_home")

    def test_renders(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "dashboard/home.html")

    def test_context_keys(self):
        resp = self.client.get(self.url)
        for key in (
            "total_products", "total_users", "total_orders",
            "total_revenue", "pending_orders", "low_stock",
            "recent_orders", "top_products", "recent_users",
            "categories", "status_counts",
        ):
            self.assertIn(key, resp.context, f"Missing context key: {key}")

    def test_stats_accuracy(self):
        customer = _make_user()
        _make_product()
        _make_order(customer)
        resp = self.client.get(self.url)
        self.assertEqual(resp.context["total_products"], 1)
        self.assertEqual(resp.context["total_users"], 1)  # excludes staff
        self.assertEqual(resp.context["total_orders"], 1)
        self.assertEqual(resp.context["total_revenue"], Decimal("150.00"))

    def test_status_counts(self):
        customer = _make_user()
        _make_order(customer, status="pending")
        _make_order(customer, status="delivered")
        _make_order(customer, status="pending")
        resp = self.client.get(self.url)
        self.assertEqual(resp.context["status_counts"]["pending"], 2)
        self.assertEqual(resp.context["status_counts"]["delivered"], 1)


# ═══════════════════════════════════════════════════════════════════════════════
#  PRODUCT MANAGEMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardProductListTest(TestCase):

    def setUp(self):
        self.admin = _make_admin()
        self.client.login(username="admin", password="Str0ng!Pass99")
        self.url = reverse("dash_products")

    def test_renders(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "dashboard/products.html")

    def test_search_filter(self):
        _make_product(name="Laptop Pro")
        _make_product(name="Mouse Pad")
        resp = self.client.get(self.url, {"q": "Laptop"})
        products = resp.context["products"]
        self.assertEqual(products.count(), 1)
        self.assertEqual(products.first().name, "Laptop Pro")

    def test_category_filter(self):
        cat = _make_category(name="Gaming")
        _make_product(category=cat, name="Controller")
        _make_product(name="Book")
        resp = self.client.get(self.url, {"cat": "gaming"})
        products = resp.context["products"]
        self.assertEqual(products.count(), 1)


class DashboardProductCreateTest(TestCase):

    def setUp(self):
        self.admin = _make_admin()
        self.client.login(username="admin", password="Str0ng!Pass99")
        self.cat = _make_category()
        self.url = reverse("dash_product_create")

    def test_get_renders_form(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "dashboard/product_form.html")

    def test_post_creates_product(self):
        resp = self.client.post(self.url, {
            "name": "New Widget",
            "category": self.cat.pk,
            "description": "A widget",
            "price": "29.99",
            "stock": 50,
            "is_active": True,
            "is_featured": False,
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Product.objects.filter(name="New Widget").exists())


class DashboardProductEditTest(TestCase):

    def setUp(self):
        self.admin = _make_admin()
        self.client.login(username="admin", password="Str0ng!Pass99")
        self.product = _make_product(name="Old Name")
        self.url = reverse("dash_product_edit", args=[self.product.pk])

    def test_get_renders_form(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_post_updates_product(self):
        resp = self.client.post(self.url, {
            "name": "Updated Name",
            "category": self.product.category.pk,
            "description": "Updated",
            "price": "59.99",
            "stock": 20,
            "is_active": True,
            "is_featured": False,
        })
        self.assertEqual(resp.status_code, 302)
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, "Updated Name")


class DashboardProductDeleteTest(TestCase):

    def setUp(self):
        self.admin = _make_admin()
        self.client.login(username="admin", password="Str0ng!Pass99")
        self.product = _make_product()
        self.url = reverse("dash_product_delete", args=[self.product.pk])

    def test_get_renders_confirmation(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "dashboard/confirm_delete.html")

    def test_post_deletes_product(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())


class DashboardProductToggleTest(TestCase):

    def setUp(self):
        self.admin = _make_admin()
        self.client.login(username="admin", password="Str0ng!Pass99")
        self.product = _make_product(is_active=True)

    def test_toggle_deactivates(self):
        url = reverse("dash_product_toggle", args=[self.product.pk])
        self.client.get(url)
        self.product.refresh_from_db()
        self.assertFalse(self.product.is_active)

    def test_toggle_activates(self):
        self.product.is_active = False
        self.product.save()
        url = reverse("dash_product_toggle", args=[self.product.pk])
        self.client.get(url)
        self.product.refresh_from_db()
        self.assertTrue(self.product.is_active)


# ═══════════════════════════════════════════════════════════════════════════════
#  CATEGORY MANAGEMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardCategoryListTest(TestCase):

    def setUp(self):
        self.admin = _make_admin()
        self.client.login(username="admin", password="Str0ng!Pass99")

    def test_renders(self):
        resp = self.client.get(reverse("dash_categories"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "dashboard/categories.html")


class DashboardCategoryCreateTest(TestCase):

    def setUp(self):
        self.admin = _make_admin()
        self.client.login(username="admin", password="Str0ng!Pass99")
        self.url = reverse("dash_category_create")

    def test_get_renders_form(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_post_creates_category(self):
        resp = self.client.post(self.url, {
            "name": "Sports",
            "description": "Sports equipment",
            "icon": "fa-football",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(Category.objects.filter(name="Sports").exists())


class DashboardCategoryEditTest(TestCase):

    def setUp(self):
        self.admin = _make_admin()
        self.client.login(username="admin", password="Str0ng!Pass99")
        self.cat = _make_category(name="Old Category")
        self.url = reverse("dash_category_edit", args=[self.cat.pk])

    def test_post_updates_category(self):
        resp = self.client.post(self.url, {
            "name": "Updated Category",
            "description": "Updated",
            "icon": "fa-star",
        })
        self.assertEqual(resp.status_code, 302)
        self.cat.refresh_from_db()
        self.assertEqual(self.cat.name, "Updated Category")


class DashboardCategoryDeleteTest(TestCase):

    def setUp(self):
        self.admin = _make_admin()
        self.client.login(username="admin", password="Str0ng!Pass99")
        self.cat = _make_category()
        self.url = reverse("dash_category_delete", args=[self.cat.pk])

    def test_get_renders_confirmation(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)

    def test_post_deletes_category(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(Category.objects.filter(pk=self.cat.pk).exists())


# ═══════════════════════════════════════════════════════════════════════════════
#  ORDER MANAGEMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardOrderListTest(TestCase):

    def setUp(self):
        self.admin = _make_admin()
        self.customer = _make_user()
        self.client.login(username="admin", password="Str0ng!Pass99")

    def test_renders(self):
        resp = self.client.get(reverse("dash_orders"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "dashboard/orders.html")

    def test_status_filter(self):
        _make_order(self.customer, status="pending")
        _make_order(self.customer, status="shipped")
        resp = self.client.get(reverse("dash_orders"), {"status": "pending"})
        orders = resp.context["orders"]
        self.assertEqual(orders.count(), 1)
        self.assertEqual(orders.first().status, "pending")


class DashboardOrderDetailTest(TestCase):

    def setUp(self):
        self.admin = _make_admin()
        self.customer = _make_user()
        self.order = _make_order(self.customer, status="pending")
        self.client.login(username="admin", password="Str0ng!Pass99")

    def test_renders(self):
        resp = self.client.get(reverse("dash_order_detail", args=[self.order.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "dashboard/order_detail.html")

    def test_post_updates_status(self):
        resp = self.client.post(
            reverse("dash_order_detail", args=[self.order.pk]),
            {"status": "shipped"},
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "shipped")

    def test_invalid_status_ignored(self):
        self.client.post(
            reverse("dash_order_detail", args=[self.order.pk]),
            {"status": "invalid_status"},
        )
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "pending")


# ═══════════════════════════════════════════════════════════════════════════════
#  USER MANAGEMENT TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardUserListTest(TestCase):

    def setUp(self):
        self.admin = _make_admin()
        self.client.login(username="admin", password="Str0ng!Pass99")

    def test_renders(self):
        resp = self.client.get(reverse("dash_users"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "dashboard/users.html")

    def test_search(self):
        _make_user(username="findme", email="findme@test.com")
        _make_user(username="other", email="other@test.com")
        resp = self.client.get(reverse("dash_users"), {"q": "findme"})
        users = resp.context["users"]
        self.assertEqual(users.count(), 1)


class DashboardUserDetailTest(TestCase):

    def setUp(self):
        self.admin = _make_admin()
        self.customer = _make_user()
        self.client.login(username="admin", password="Str0ng!Pass99")

    def test_renders(self):
        resp = self.client.get(reverse("dash_user_detail", args=[self.customer.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "dashboard/user_detail.html")


class DashboardUserToggleTest(TestCase):

    def setUp(self):
        self.admin = _make_admin()
        self.customer = _make_user(is_active=True)
        self.client.login(username="admin", password="Str0ng!Pass99")

    def test_toggle_deactivates_user(self):
        resp = self.client.get(reverse("dash_user_toggle", args=[self.customer.pk]))
        self.customer.refresh_from_db()
        self.assertFalse(self.customer.is_active)

    def test_toggle_activates_user(self):
        self.customer.is_active = False
        self.customer.save()
        self.client.get(reverse("dash_user_toggle", args=[self.customer.pk]))
        self.customer.refresh_from_db()
        self.assertTrue(self.customer.is_active)

    def test_admin_cannot_toggle_self(self):
        self.client.get(reverse("dash_user_toggle", args=[self.admin.pk]))
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)


class DashboardUserDeleteTest(TestCase):

    def setUp(self):
        self.admin = _make_admin()
        self.customer = _make_user()
        self.client.login(username="admin", password="Str0ng!Pass99")

    def test_get_renders_confirmation(self):
        resp = self.client.get(reverse("dash_user_delete", args=[self.customer.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "dashboard/confirm_delete.html")

    def test_post_deletes_user(self):
        pk = self.customer.pk
        resp = self.client.post(reverse("dash_user_delete", args=[pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(User.objects.filter(pk=pk).exists())

    def test_admin_cannot_delete_self(self):
        resp = self.client.post(reverse("dash_user_delete", args=[self.admin.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())


# ═══════════════════════════════════════════════════════════════════════════════
#  CONTEXT PROCESSOR TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class DashboardContextProcessorTest(TestCase):

    def test_returns_empty_for_anonymous(self):
        factory = RequestFactory()
        request = factory.get("/")
        request.user = AnonymousUser()
        result = dashboard_context(request)
        self.assertEqual(result, {})

    def test_returns_empty_for_non_staff(self):
        user = _make_user()
        factory = RequestFactory()
        request = factory.get("/")
        request.user = user
        result = dashboard_context(request)
        self.assertEqual(result, {})

    def test_returns_counts_for_staff(self):
        admin = _make_admin()
        _make_product()
        factory = RequestFactory()
        request = factory.get("/")
        request.user = admin
        result = dashboard_context(request)
        self.assertIn("pending_orders", result)
        self.assertIn("total_products", result)
        self.assertEqual(result["total_products"], 1)
