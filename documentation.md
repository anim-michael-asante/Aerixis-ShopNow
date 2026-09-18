# Project Documentation — Aerixis ShopNow

## Table of Contents
- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [User Flow](#user-flow)
  - [1. Customer Journey](#1-customer-journey)
  - [2. Admin & Staff Journey](#2-admin--staff-journey)
- [Component Map](#component-map)
- [API Routes](#api-routes)
- [Security Notes (OWASP Top 10 Protections Applied)](#security-notes-owasp-top-10-protections-applied)
  - [A01 — Broken Access Control](#a01--broken-access-control)
  - [A02 — Cryptographic Failures](#a02--cryptographic-failures)
  - [A03 — Injection](#a03--injection)
  - [A04 — Insecure Design](#a04--insecure-design)
  - [A05 — Security Misconfiguration](#a05--security-misconfiguration)
  - [A06 — Vulnerable and Outdated Components](#a06--vulnerable-and-outdated-components)
  - [A07 — Identification & Authentication Failures](#a07--identification--authentication-failures)
  - [A08 — Software and Data Integrity](#a08--software-and-data-integrity)
  - [A09 — Security Logging and Monitoring](#a09--security-logging-and-monitoring)
  - [A10 — Server-Side Request Forgery (SSRF)](#a10--server-side-request-forgery-ssrf)
- [Design Decisions](#design-decisions)
- [Responsive Breakpoints](#responsive-breakpoints)
- [Test Suite & Verification](#test-suite--verification)
- [Known Limitations](#known-limitations)

---

## Overview
**Aerixis ShopNow** is a full-stack e-commerce web platform built with Django. It provides a secure, streamlined shopping and store management experience. The platform supports browsing and filtering products, persistent cart management for both guests and authenticated users, secure checkout with atomic transactions, user profile administration, and a staff-only management dashboard for product, category, order, and customer operations.

---

## Tech Stack
- **Backend Framework**: Django (v4.2+)
- **Database**: SQLite3 (development) / PostgreSQL-ready
- **Image Processing**: Pillow (v10.0+)
- **Frontend Architecture**: Django Templates, Semantic HTML5, Vanilla CSS custom properties design system
- **Typography & Icons**: Google Fonts (Inter), Font Awesome (v6.5.0), Lucide Icon guidelines
- **Environment & Security**: Standard Python library (`os`, `urllib.parse`, `ipaddress`, `logging`), Django Security Middleware

---

## User Flow

### 1. Customer Journey
1. **Discovery & Browsing**: User arrives on the homepage (`/`) featuring featured goods, new arrivals, and sales items, or accesses the catalog (`/store/products/`) with category, price, search, and sorting filters.
2. **Product Details**: User clicks through to `/store/products/<slug>/` to view detailed specs, stock status, and related products.
3. **Cart Management**: 
   - User adds products to cart (`/store/cart/add/<id>/`) with stock limit validation.
   - User views cart at `/store/cart/`, modifying quantities or removing items.
4. **Authentication**: If unauthenticated, user is guided to register (`/accounts/register/`) or login (`/accounts/login/`). Open-redirect attacks on `?next=` parameters are actively blocked.
5. **Checkout**: User submits delivery information at `/store/checkout/`. The order creation, inventory decrement, and cart clearing execute within an atomic transaction (`transaction.atomic`).
6. **Order Tracking**: User tracks active and completed orders at `/store/orders/` and cancels pending orders when needed via POST requests.
7. **Profile Management**: User updates personal contact details, bio, avatar image (under 2MB), and password at `/accounts/profile/`.

### 2. Admin & Staff Journey
1. **Access Control**: Staff user accesses `/panel/` (`admin_required` guard enforces `is_authenticated` and `is_staff`). Non-staff users are redirected to login.
2. **Dashboard Overview**: Metrics overview displays total products, customers, orders, revenue, inventory alerts, and breakdown by status.
3. **Inventory & Category Operations**: Staff performs CRUD operations on products and categories, toggling active states with instant feedback.
4. **Order Management**: Staff reviews customer orders and updates fulfillment status (`pending` → `processing` → `shipped` → `delivered` / `cancelled`).
5. **Customer Administration**: Staff searches customer accounts, reviews order histories, and manages account active statuses. Self-deletion and self-deactivation are strictly forbidden to prevent lockout.

---

## Component Map

| Component / Template | Purpose | Handled States |
|---|---|---|
| `templates/base.html` | Root layout shell with navigation, search, wishlist/cart badges, mobile drawer, flash notifications, and footer. | Default, Authenticated, Anonymous, Mobile Drawer Open/Closed, Alerts auto-dismiss. |
| `templates/home.html` | Hero showcase, featured grid, category pills, new arrivals, and special discount highlights. | Default, Empty sections, Sale badges, Out-of-stock indicators. |
| `templates/store/products.html` | Catalog grid with filter sidebar (search, category, price range, sorting). | Default, Filtered, Empty search results, Hover lift, Pagination. |
| `templates/store/product_detail.html` | Product showcase with high-resolution image, stock status, quantity picker, description, and related products. | In Stock, Out of Stock, Sale Discount, Disabled add-to-cart button. |
| `templates/store/cart.html` | Shopping cart table with quantity increment/decrement, remove actions, and order summary card. | Default (items present), Empty Cart with Call-To-Action. |
| `templates/store/checkout.html` | Delivery address form, pre-filled user profile data, and payment summary. | Form Default, Submitting (Loading), Field Validation Errors. |
| `templates/store/orders.html` | Customer order history list with color-coded status badges and cancel modal. | Default list, Empty orders state, Pending vs Non-cancellable. |
| `templates/accounts/login.html` | Clean authentication form with password visibility and redirection parameters. | Default, Focus, Invalid Credentials error, Redirect. |
| `templates/accounts/register.html` | Customer registration with real-time password policy validation. | Default, Duplicate email/username error, Password mismatch. |
| `templates/accounts/profile.html` | Account management dashboard: profile details, avatar upload, password change, and danger zone (account deletion). | Default, Tab switching, Upload validation error, Success toast. |
| `templates/dashboard/home.html` | Admin control panel with KPI metric cards, revenue graphs, recent orders, and stock alerts. | Default, Empty data states, Status breakdown. |
| `templates/dashboard/products.html` | Product inventory table with search, category filtering, status toggle, and edit/delete actions. | Default, Filtered results, Empty inventory. |
| `templates/dashboard/orders.html` | Admin order fulfillment queue with status filters and quick status update forms. | All statuses, Single status filter, Empty state. |

---

## API Routes

| Endpoint | HTTP Method | Auth / Role | Description |
|---|---|---|---|
| `/` | `GET` | Public | Homepage featuring highlighted products and categories |
| `/store/products/` | `GET` | Public | Product catalog with search, price, and category filters |
| `/store/products/<slug>/` | `GET` | Public | Product detail page |
| `/store/cart/` | `GET` | Public | View current user/session shopping cart |
| `/store/cart/add/<product_id>/` | `POST` | Public | Add item to cart with stock validation (`@require_POST`) |
| `/store/cart/update/<item_id>/` | `POST` | Public | Increase, decrease, or remove cart item (`@require_POST`) |
| `/store/cart/remove/<item_id>/` | `POST` | Public | Remove item from cart (`@require_POST`) |
| `/store/checkout/` | `GET`, `POST` | Authenticated | Place order with atomic transaction & stock validation |
| `/store/orders/` | `GET` | Authenticated | List orders belonging to authenticated user |
| `/store/orders/<pk>/` | `GET` | Authenticated | View order details (IDOR protected: user-scoped) |
| `/store/orders/<pk>/cancel/` | `POST` | Authenticated | Cancel pending order (`@require_POST`) |
| `/accounts/register/` | `GET`, `POST` | Anonymous | Customer registration |
| `/accounts/login/` | `GET`, `POST` | Anonymous | Login with Open-Redirect protection |
| `/accounts/logout/` | `POST` | Authenticated | Safe CSRF-protected logout |
| `/accounts/profile/` | `GET` | Authenticated | User account details and order history |
| `/accounts/profile/update/` | `POST` | Authenticated | Update profile details and avatar (size/type verified) |
| `/accounts/profile/change-password/` | `POST` | Authenticated | Change user password with session preservation |
| `/accounts/profile/delete/` | `POST` | Authenticated | Delete account with password confirmation |
| `/panel/` | `GET` | Staff | Management dashboard summary & metrics |
| `/panel/products/` | `GET` | Staff | Product management table |
| `/panel/products/create/` | `GET`, `POST` | Staff | Create new product with image & SSRF validation |
| `/panel/products/<pk>/edit/` | `GET`, `POST` | Staff | Edit existing product |
| `/panel/products/<pk>/delete/` | `POST` | Staff | Delete product |
| `/panel/products/<pk>/toggle/` | `GET`, `POST` | Staff | Toggle product active status |
| `/panel/categories/` | `GET` | Staff | Category management list |
| `/panel/categories/create/` | `GET`, `POST` | Staff | Create new category |
| `/panel/categories/<pk>/edit/` | `GET`, `POST` | Staff | Edit existing category |
| `/panel/categories/<pk>/delete/` | `POST` | Staff | Delete category |
| `/panel/orders/` | `GET` | Staff | Admin order list with status filter |
| `/panel/orders/<pk>/` | `GET`, `POST` | Staff | View order detail and update status |
| `/panel/users/` | `GET` | Staff | User management list |
| `/panel/users/<pk>/` | `GET` | Staff | View user profile & customer orders |
| `/panel/users/<pk>/toggle/` | `GET`, `POST` | Staff | Toggle user active status (self-toggle protected) |
| `/panel/users/<pk>/delete/` | `POST` | Staff | Delete user (self-deletion protected) |

---

## Security Notes (OWASP Top 10 Protections Applied)

### A01 — Broken Access Control
- **Open Redirect Guard**: `login_view` uses `url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()})`. Malicious URLs (e.g. `//attacker.com`, `https://phishing.site`) are discarded, defaulting to `'home'`.
- **IDOR Protection**: Order queries in `store/views.py` (`order_detail`, `cancel_order`) strictly filter by `user=request.user`.
- **Role Separation**: Dashboard views are guarded by `admin_required` (`is_authenticated and is_staff`).
- **Superuser & Self-Destruction Guard**: In `dashboard/views.py`, admins cannot toggle or delete their own accounts, nor can superusers be deactivated or deleted through the panel. In `accounts/views.py`, the primary administrator account cannot be deleted.
- **HTTP Method Enforcement**: State mutations (`cancel_order`, cart operations) enforce `@require_POST` to block CSRF and unwanted GET executions.

### A02 — Cryptographic Failures
- **Secret Management**: `SECRET_KEY` is decoupled from source code and read from the `DJANGO_SECRET_KEY` environment variable.
- **Dynamic Seed Credentials**: In `seed_data.py`, superuser passwords are read dynamically from `DJANGO_SUPERUSER_PASSWORD`, eliminating hardcoded production backdoors.
- **Secure Cookies & Transport**:
  - `SESSION_COOKIE_HTTPONLY = True` & `CSRF_COOKIE_HTTPONLY = True`
  - `SESSION_COOKIE_SAMESITE = 'Lax'` & `CSRF_COOKIE_SAMESITE = 'Lax'`
  - `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE` are activated when `DEBUG=False`.
  - HSTS enabled via `SECURE_HSTS_SECONDS = 31536000`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`, and `SECURE_HSTS_PRELOAD`.

### A03 — Injection
- **SQL Injection Prevention**: All queries use Django ORM parameterized queries (`Product.objects.filter(...)`). No raw string-concatenated SQL queries exist.
- **Account Collision Defense**: `UserUpdateForm` and `RegisterForm` validate email uniqueness (`clean_email`), preventing account collision and impersonation.
- **File Upload Hardening**:
  - Avatar uploads (`ProfileUpdateForm`) enforce a strict 2MB maximum file size and restrict extensions to `.jpg`, `.jpeg`, `.png`, and `.webp`.
  - Product images (`ProductForm`) enforce a 5MB maximum file size and image format whitelist.

### A04 — Insecure Design
- **Atomic Checkout**: The checkout pipeline is wrapped in `with transaction.atomic():`. If inventory reduction, order item creation, or cart clearing fails, the transaction rolls back cleanly.
- **Inventory Concurrency Defense**: Stock availability is checked both before order placement and during the atomic lock, preventing overselling or negative inventory.
- **Cart Input Sanitization**: Quantity inputs are validated and clamped to positive integers (`1 <= quantity <= stock`).

### A05 — Security Misconfiguration
- **Security Headers Activated**:
  - `X_FRAME_OPTIONS = 'DENY'` (Clickjacking mitigation)
  - `SECURE_CONTENT_TYPE_NOSNIFF = True` (MIME sniffing mitigation)
  - `SECURE_BROWSER_XSS_FILTER = True` (Reflected XSS protection)
  - `SECURE_REFERRER_POLICY = 'same-origin'` (Referrer leakage protection)
- **Deployment Flags**: `DEBUG` defaults to `False` unless explicitly enabled in `.env`.
- **Media Serving Guard**: In `shopnow/urls.py`, user media file routes are only mounted when `settings.DEBUG` is True.
- **Static Files Warning Resolved**: Created `static/.gitkeep` eliminating Django `(staticfiles.W004)` deployment check warnings.

### A06 — Vulnerable and Outdated Components
- `requirements.txt` pins stable, maintained packages: `Django>=4.2,<5.0` and `Pillow>=10.0.0`.

### A07 — Identification & Authentication Failures
- **Login Brute-Force Rate Limiting**: `login_view` tracks consecutive failed login attempts per client IP via Django cache, locking out requests after 5 failed attempts for 5 minutes.
- `AUTH_PASSWORD_VALIDATORS` configured with length, similarity, common password, and numeric checks.
- Password change keeps sessions valid via `update_session_auth_hash(request, user)`.
- Failed login attempts and account deletion attempts are logged for security auditing.

### A08 — Software and Data Integrity
- Static assets and external fonts loaded over HTTPS.

### A09 — Security Logging and Monitoring
- Configured structured logging under `shopnow/settings.py` for `django.security` and `accounts.security`.
- Failed logins, rate-limit triggers, user registration, password changes, account deletions, order cancellations, and admin mutations (deletions/toggles) emit structured log events with actor and IP addresses.

### A10 — Server-Side Request Forgery (SSRF)
- `ProductForm` validates `image_url` to ensure schemes are restricted to `http` or `https`.
- Resolves and rejects private, reserved, link-local, loopback, or localhost targets (`127.0.0.1`, `0.0.0.0`, `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `169.254.169.254`, `::1`).

---

## Design Decisions
- **Zero-Emoji Compliance**: Removed emojis from system messages, flash toasts, and placeholders in compliance with enterprise UI guidelines.
- **Color Palette & Contrast**: High-contrast red/slate theme (`--p: #E8192C`, `--t9: #111827`, `--bg: #F7F8FA`) with WCAG AA compliance.
- **Micro-Animations & Feedback**: Card hover lift, smooth transitions, and auto-dismissing system notification banners.

---

## Responsive Breakpoints
- **Mobile (< 640px)**: Collapsible hamburger navigation, single/dual column product grid, full-width inputs, touch targets >= 44px.
- **Tablet (640px – 1024px)**: 2-3 column product layout, collapsible side drawer.
- **Desktop (>= 1024px)**: Persistent left sidebar navigation, multi-column product display, sticky summary columns.

---

## Test Suite & Verification
The project features automated test suites verifying models, forms, access controls, business logic, and OWASP security boundaries.

### Automated Test Runner (`test.py`)
Run all test suites across the repository:
```bash
python test.py
```

Or target specific applications and test classes:
```bash
python test.py accounts
python test.py store
python test.py dashboard
python test.py accounts.tests.SecurityHardeningTest
```

### Coverage Highlights
- **Accounts (`accounts/tests.py`)**: Profile signals, registration validations, open-redirect neutralization, login rate limiting, password changes, and primary administrator deletion immunity.
- **Store (`store/tests.py`)**: Catalog filters, cart operations, atomic checkout with inventory decrements, and ProductForm SSRF prevention.
- **Dashboard (`dashboard/tests.py`)**: Staff-only access guards (`admin_required`), dashboard metrics accuracy, product/category lifecycle, order management, and superuser protection guards.

---

## Known Limitations
- Payment gateway is currently simulated via instant order placement (ready for Stripe / Paystack webhook integration).
- Background asynchronous tasks (e.g. Celery / Redis for transactional email notifications) are deferred for external worker integration.

