
<div align="center">

# Aerixis ShopNow

A production-style full-stack e-commerce platform built with Django.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=flat&logo=django&logoColor=white)](https://djangoproject.com)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-gray?style=flat)](LICENSE)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running Tests](#running-tests)
- [Default Credentials](#default-credentials)
- [Application Routes](#application-routes)
- [Security](#security)
- [Project Structure](#project-structure)
- [License](#license)

---

## Overview

Aerixis ShopNow is a full-stack e-commerce application that delivers a complete shopping experience for customers and a custom admin dashboard for store management.

The platform includes:

- A responsive storefront for browsing products
- Shopping cart and checkout workflows
- Order history and status tracking
- A custom dashboard for managing products, categories, orders, and users
- Built-in authentication and account management

---

## Screenshots

### Storefront
<img src="screenshots/homepage_desktop.png" width="780" alt="Homepage Desktop" />

### Mobile View
<img src="screenshots/homepage_mobile.png" width="320" alt="Homepage Mobile" />

### Product Listing
<img src="screenshots/products_desktop.png" width="780" alt="Product Listing Desktop" />

### Admin Dashboard
<img src="screenshots/admin_dashboard.png" width="780" alt="Admin Dashboard Overview" />

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| Backend | Django 4.2 |
| Database | SQLite |
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Media | Pillow, Unsplash image URLs |
| Icons | Font Awesome 6 |
| Authentication | Django built-in auth system |

---

## Features

### Customer Storefront

- Browse products with search, filter, and sort options
- View product details and related items
- Add, update, and remove cart items
- Complete checkout with delivery details
- Track order status and view order history
- Manage profile, password, and account settings

### Admin Dashboard

- View store metrics and revenue summaries
- Create, edit, and delete products
- Upload product images or use image URLs
- Manage categories and featured products
- Process orders through status stages
- Search, activate, deactivate, and delete users

---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip
- Git

### Installation

1. Clone the repository:

```bash
git clone https://github.com/anim-michael-asante/Aerixis-ShopNow.git
cd Aerixis-ShopNow
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install django pillow
```

4. Run migrations:

```bash
python manage.py makemigrations accounts
python manage.py makemigrations store
python manage.py migrate
```

5. Seed the database with sample data:

```bash
python manage.py seed_data
```

6. Start the development server:

```bash
python manage.py runserver
```

Then open:

```text
http://127.0.0.1:8000/
```

### Running Tests

Run the automated test runner:

```bash
# Run all test suites (accounts, store, dashboard)
python test.py

# Run specific app or test case
python test.py accounts
python test.py store
python test.py dashboard
python test.py accounts.tests.SecurityHardeningTest
```

---

## Default Credentials

| Role | Username | Password | URL |
| --- | --- | --- | --- |
| Admin | super_admin | `Aer!x1s#SuperAdm!n_2025` | http://127.0.0.1:8000/panel/ |
| Demo User | demo | `ShopNow#DemoUser!2025` | http://127.0.0.1:8000/ |

> Change all default credentials before deploying to any public environment.

---

## Application Routes

| Page | URL |
| --- | --- |
| Storefront | http://127.0.0.1:8000/ |
| Products | http://127.0.0.1:8000/store/products/ |
| Cart | http://127.0.0.1:8000/store/cart/ |
| Admin Dashboard | http://127.0.0.1:8000/panel/ |
| Django Admin | http://127.0.0.1:8000/admin/ |

---

## Security

The application follows an enterprise security-first model hardened against the OWASP Top 10 vulnerabilities:

| Control | Implementation |
| --- | --- |
| **Open Redirect Defense** | Validates all `?next=` parameters with `url_has_allowed_host_and_scheme` |
| **Authentication & Rate Limiting** | IP-based failed attempt throttling (5 attempts / 5 min lockout) via Django cache |
| **CSRF Protection** | Enforced across all forms and state-mutating requests (`@require_POST`) |
| **Security Headers** | `X-Frame-Options: DENY`, `Nosniff`, `Referrer-Policy: same-origin`, SSL & HSTS flags |
| **Data Integrity & Concurrency** | Atomic transactions (`transaction.atomic`) with inventory verification during checkout |
| **Input & Upload Sanitization** | Strict image MIME/size limits (<= 2MB/5MB) and SSRF URL whitelist |
| **Role & Privilege Protection** | `admin_required` decorators, superuser deletion immunity, and staff self-action guards |
| **Password Security** | Django PBKDF2 hashing with salt, password validation policies |

For an in-depth security breakdown and architecture details, see [documentation.md](documentation.md).

---

## Project Structure

```text
Aerixis-ShopNow/
├── accounts/               # User authentication, profiles, and security views
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── store/                  # Storefront, catalog, cart, orders, and checkout
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   └── management/commands/seed_data.py
├── dashboard/              # Staff management panel for products, categories, orders, and users
│   ├── context_processors.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── shopnow/                # Core project configuration and settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/                 # Static assets directory
├── templates/              # HTML5 templates
│   ├── accounts/
│   ├── dashboard/
│   ├── store/
│   └── base.html
├── screenshots/            # UI screenshots and previews
├── .env.example            # Environment variables template
├── documentation.md        # Comprehensive system documentation
├── manage.py
├── test.py                 # Automated test suite runner
└── requirements.txt
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <sub>Built by <a href="https://github.com/anim-michael-asante">0x1aerixis</a></sub>
</div>
