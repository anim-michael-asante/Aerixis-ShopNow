"""
Tests for the accounts app.

Covers:
  - UserProfile model (str, get_full_name, get_avatar_url, signals)
  - Forms  (RegisterForm, UserUpdateForm, ProfileUpdateForm, CustomPasswordChangeForm)
  - Views  (register, login, logout, profile, profile_update, change_password, delete_account)
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

from .models import UserProfile
from .forms import RegisterForm, UserUpdateForm, ProfileUpdateForm, CustomPasswordChangeForm


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _make_user(username="testuser", password="Str0ng!Pass99", **kwargs):
    """Create a User (and its auto-created profile) in one call."""
    return User.objects.create_user(username=username, password=password, **kwargs)


# ═══════════════════════════════════════════════════════════════════════════════
#  MODEL TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class UserProfileModelTest(TestCase):
    """Tests for accounts.models.UserProfile."""

    def setUp(self):
        self.user = _make_user(
            first_name="John",
            last_name="Doe",
            email="john@example.com",
        )
        self.profile = self.user.profile

    # ── __str__ ────────────────────────────────────────────────────────────
    def test_str_representation(self):
        self.assertEqual(str(self.profile), "testuser's Profile")

    # ── get_full_name ──────────────────────────────────────────────────────
    def test_get_full_name_with_names(self):
        self.assertEqual(self.profile.get_full_name(), "John Doe")

    def test_get_full_name_falls_back_to_username(self):
        self.user.first_name = ""
        self.user.last_name = ""
        self.user.save()
        self.assertEqual(self.profile.get_full_name(), "testuser")

    def test_get_full_name_first_only(self):
        self.user.last_name = ""
        self.user.save()
        self.assertEqual(self.profile.get_full_name(), "John")

    # ── get_avatar_url ─────────────────────────────────────────────────────
    def test_get_avatar_url_returns_none_without_avatar(self):
        self.assertIsNone(self.profile.get_avatar_url())

    # ── Signal: profile auto-created ───────────────────────────────────────
    def test_profile_auto_created_on_user_save(self):
        new_user = User.objects.create_user("signaluser", password="P@ss1234!")
        self.assertTrue(hasattr(new_user, "profile"))
        self.assertIsInstance(new_user.profile, UserProfile)

    def test_profile_fields_default_blank(self):
        self.assertEqual(self.profile.phone, "")
        self.assertEqual(self.profile.address, "")
        self.assertEqual(self.profile.city, "")
        self.assertEqual(self.profile.bio, "")

    def test_save_user_profile_signal_creates_missing_profile(self):
        """If the profile was somehow deleted, saving the user re-creates it."""
        self.profile.delete()
        self.user.save()
        self.user.refresh_from_db()
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())


# ═══════════════════════════════════════════════════════════════════════════════
#  FORM TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class RegisterFormTest(TestCase):
    """Tests for accounts.forms.RegisterForm."""

    def _valid_data(self, **overrides):
        data = {
            "username": "newuser",
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
            "password1": "Str0ng!Pass99",
            "password2": "Str0ng!Pass99",
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        form = RegisterForm(data=self._valid_data())
        self.assertTrue(form.is_valid())

    def test_duplicate_email_rejected(self):
        _make_user(email="taken@example.com")
        form = RegisterForm(data=self._valid_data(email="taken@example.com"))
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_password_mismatch_rejected(self):
        form = RegisterForm(data=self._valid_data(password2="DifferentPass1!"))
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_form_fields_have_css_class(self):
        form = RegisterForm()
        for field in form.fields.values():
            self.assertIn("form-control", field.widget.attrs.get("class", ""))

    def test_missing_email_rejected(self):
        data = self._valid_data()
        data["email"] = ""
        form = RegisterForm(data=data)
        self.assertFalse(form.is_valid())


class UserUpdateFormTest(TestCase):
    """Tests for accounts.forms.UserUpdateForm."""

    def test_valid_update(self):
        user = _make_user()
        form = UserUpdateForm(
            data={"first_name": "Updated", "last_name": "Name", "email": "u@e.com"},
            instance=user,
        )
        self.assertTrue(form.is_valid())


class ProfileUpdateFormTest(TestCase):
    """Tests for accounts.forms.ProfileUpdateForm."""

    def test_valid_profile_update(self):
        user = _make_user()
        form = ProfileUpdateForm(
            data={"phone": "0551234567", "address": "123 Main St", "city": "Accra", "bio": "Hi"},
            instance=user.profile,
        )
        self.assertTrue(form.is_valid())

    def test_blank_fields_allowed(self):
        user = _make_user()
        form = ProfileUpdateForm(data={}, instance=user.profile)
        self.assertTrue(form.is_valid())


class CustomPasswordChangeFormTest(TestCase):
    """Tests for accounts.forms.CustomPasswordChangeForm."""

    def test_fields_have_form_control_class(self):
        user = _make_user()
        form = CustomPasswordChangeForm(user)
        for field in form.fields.values():
            self.assertEqual(field.widget.attrs.get("class"), "form-control")


# ═══════════════════════════════════════════════════════════════════════════════
#  VIEW TESTS
# ═══════════════════════════════════════════════════════════════════════════════

class RegisterViewTest(TestCase):
    """Tests for accounts.views.register_view."""

    def setUp(self):
        self.client = Client()
        self.url = reverse("register")

    def test_get_renders_form(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "accounts/register.html")

    def test_post_valid_creates_user_and_redirects(self):
        resp = self.client.post(self.url, {
            "username": "newuser",
            "first_name": "A",
            "last_name": "B",
            "email": "a@b.com",
            "password1": "Str0ng!Pass99",
            "password2": "Str0ng!Pass99",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_post_invalid_shows_form_again(self):
        resp = self.client.post(self.url, {"username": ""})
        self.assertEqual(resp.status_code, 200)

    def test_authenticated_user_redirected_away(self):
        _make_user()
        self.client.login(username="testuser", password="Str0ng!Pass99")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)


class LoginViewTest(TestCase):
    """Tests for accounts.views.login_view."""

    def setUp(self):
        self.client = Client()
        self.url = reverse("login")
        self.user = _make_user()

    def test_get_renders_login_page(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "accounts/login.html")

    def test_post_valid_logs_in_and_redirects(self):
        resp = self.client.post(self.url, {
            "username": "testuser",
            "password": "Str0ng!Pass99",
        })
        self.assertEqual(resp.status_code, 302)

    def test_post_invalid_shows_error(self):
        resp = self.client.post(self.url, {
            "username": "testuser",
            "password": "wrongpass",
        })
        self.assertEqual(resp.status_code, 200)

    def test_next_redirect_honoured(self):
        resp = self.client.post(self.url + "?next=/store/products/", {
            "username": "testuser",
            "password": "Str0ng!Pass99",
        })
        self.assertRedirects(resp, "/store/products/")

    def test_authenticated_user_redirected_away(self):
        self.client.login(username="testuser", password="Str0ng!Pass99")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)


class LogoutViewTest(TestCase):
    """Tests for accounts.views.logout_view."""

    def setUp(self):
        self.client = Client()
        self.user = _make_user()

    def test_post_logs_out_and_redirects(self):
        self.client.login(username="testuser", password="Str0ng!Pass99")
        resp = self.client.post(reverse("logout"))
        self.assertEqual(resp.status_code, 302)

    def test_get_redirects_without_logging_out(self):
        self.client.login(username="testuser", password="Str0ng!Pass99")
        resp = self.client.get(reverse("logout"))
        # GET should still redirect (to home)
        self.assertEqual(resp.status_code, 302)


class ProfileViewTest(TestCase):
    """Tests for accounts.views.profile_view."""

    def setUp(self):
        self.client = Client()
        self.user = _make_user()
        self.url = reverse("profile")

    def test_requires_login(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)

    def test_renders_for_authenticated_user(self):
        self.client.login(username="testuser", password="Str0ng!Pass99")
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "accounts/profile.html")


class ProfileUpdateViewTest(TestCase):
    """Tests for accounts.views.profile_update."""

    def setUp(self):
        self.client = Client()
        self.user = _make_user()
        self.url = reverse("profile_update")
        self.client.login(username="testuser", password="Str0ng!Pass99")

    def test_post_valid_updates_profile(self):
        resp = self.client.post(self.url, {
            "first_name": "Updated",
            "last_name": "User",
            "email": "updated@e.com",
            "phone": "0551234567",
            "address": "456 Elm St",
            "city": "Kumasi",
            "bio": "Hello world",
        })
        self.assertEqual(resp.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.city, "Kumasi")

    def test_requires_login(self):
        self.client.logout()
        resp = self.client.post(self.url, {})
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)


class ChangePasswordViewTest(TestCase):
    """Tests for accounts.views.change_password."""

    def setUp(self):
        self.client = Client()
        self.user = _make_user()
        self.url = reverse("change_password")
        self.client.login(username="testuser", password="Str0ng!Pass99")

    def test_valid_password_change(self):
        resp = self.client.post(self.url, {
            "old_password": "Str0ng!Pass99",
            "new_password1": "NewStr0ng!Pass88",
            "new_password2": "NewStr0ng!Pass88",
        })
        self.assertEqual(resp.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStr0ng!Pass88"))

    def test_wrong_old_password(self):
        resp = self.client.post(self.url, {
            "old_password": "WrongOld!1",
            "new_password1": "NewStr0ng!Pass88",
            "new_password2": "NewStr0ng!Pass88",
        })
        self.assertEqual(resp.status_code, 302)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("Str0ng!Pass99"))


class DeleteAccountViewTest(TestCase):
    """Tests for accounts.views.delete_account."""

    def setUp(self):
        self.client = Client()
        self.user = _make_user()
        self.url = reverse("delete_account")
        self.client.login(username="testuser", password="Str0ng!Pass99")

    def test_correct_password_deletes_account(self):
        resp = self.client.post(self.url, {"password": "Str0ng!Pass99"})
        self.assertEqual(resp.status_code, 302)
        self.assertFalse(User.objects.filter(username="testuser").exists())

    def test_wrong_password_keeps_account(self):
        resp = self.client.post(self.url, {"password": "wrong"})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(User.objects.filter(username="testuser").exists())

    def test_requires_login(self):
        self.client.logout()
        resp = self.client.post(self.url, {"password": "Str0ng!Pass99"})
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/accounts/login/", resp.url)


# ═══════════════════════════════════════════════════════════════════════════════
#  SECURITY HARDENING TESTS (OWASP Top 10)
# ═══════════════════════════════════════════════════════════════════════════════

class SecurityHardeningTest(TestCase):
    """Verifies OWASP Top 10 defenses."""

    def setUp(self):
        self.client = Client()
        self.user = _make_user()

    def test_open_redirect_is_neutralized(self):
        """External domains in next parameter must be rejected and redirected to home."""
        resp = self.client.post(reverse("login") + "?next=https://attacker-phishing.com", {
            "username": "testuser",
            "password": "Str0ng!Pass99",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, "/")

    def test_protocol_relative_open_redirect_is_neutralized(self):
        """Protocol-relative URLs like //evil.com must also be rejected."""
        resp = self.client.post(reverse("login") + "?next=//evil.com/path", {
            "username": "testuser",
            "password": "Str0ng!Pass99",
        })
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, "/")

    def test_security_headers_applied(self):
        """Verify essential security headers like X-Frame-Options and X-Content-Type-Options."""
        resp = self.client.get(reverse("home"))
        self.assertEqual(resp.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(resp.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(resp.headers.get("Referrer-Policy"), "same-origin")

