<div align="center">

# Aerixis-ShopNow

**A full-stack e-commerce web application built with Django**

Aerixis-ShopNow is a full-stack e-commerce app I built for a client. Features a storefront with product browsing, cart, checkout and order tracking — plus a custom admin dashboard for managing products, orders and users in real time. Built with Django, SQLite, HTML and CSS. A Cybersecurity student proving I can build beyond my core discipline.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-092E20?style=flat&logo=django&logoColor=white)](https://djangoproject.com)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat&logo=sqlite&logoColor=white)](https://sqlite.org)
[![License](https://img.shields.io/badge/License-MIT-red?style=flat)](LICENSE)

</div>

---

## 📸 Screenshots

### 🏠 Homepage — Desktop
![Homepage Desktop](screenshots/homepage_desktop.png)

### 📱 Homepage — Mobile
![Homepage Mobile](screenshots/homepage_mobile.png)

### 🛍️ Product Listing — Desktop
![Products Desktop](screenshots/products_desktop.png)

### 📱 Product Listing — Mobile
![Products Mobile](screenshots/products_mobile.png)

### 🌐 Full Storefront View
![Full Storefront](screenshots/storefront_full.png)

### 🎛️ Admin Dashboard — Overview
![Admin Dashboard](screenshots/admin_dashboard.png)

### 👥 Admin Dashboard — User Management
![Admin Users](screenshots/admin_users.png)

---

## ⚙️ Tech Stack

| Layer      | Technology                      |
|------------|---------------------------------|
| Backend    | Django 4.2                      |
| Database   | SQLite                          |
| Frontend   | HTML5, CSS3, Vanilla JavaScript |
| Icons      | Font Awesome 6                  |
| Images     | Pillow + Unsplash URLs          |
| Auth       | Django built-in auth system     |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- pip
- Git

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/anim-michael-asante/Aerixis-ShopNow.git
cd Aerixis-ShopNow
```

**2. Create and activate a virtual environment**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**3. Install dependencies**
```powershell
pip install django pillow
```

**4. Run database migrations**
```powershell
python manage.py makemigrations accounts
python manage.py makemigrations store
python manage.py migrate
```

**5. Seed the database with sample data**
```powershell
python manage.py seed_data
```

**6. Start the development server**
```powershell
python manage.py runserver
```

Open your browser and go to `http://127.0.0.1:8000/`

---

## 🔑 Default Credentials

| Role       | Username | Password   | URL                           |
|------------|----------|------------|-------------------------------|
| Admin      | `admin`  | `admin123` | http://127.0.0.1:8000/panel/  |
| Demo User  | `demo`   | `demo1234` | http://127.0.0.1:8000/        |

> ⚠️ Change these credentials before deploying to production.

---

## 📋 Application URLs

| Page             | URL                                      |
|------------------|------------------------------------------|
| Storefront       | `http://127.0.0.1:8000/`                |
| Shop             | `http://127.0.0.1:8000/store/products/` |
| Cart             | `http://127.0.0.1:8000/store/cart/`     |
| Custom Dashboard | `http://127.0.0.1:8000/panel/`          |
| Django Admin     | `http://127.0.0.1:8000/admin/`          |

---

## ✅ Features

### 🎛️ Custom Admin Dashboard — `/panel/`

- **Overview** — live stats for products, users, orders and total revenue
- **Products** — add, edit, delete with image upload or URL; toggle active/featured status instantly
- **Categories** — full CRUD with Font Awesome icon class support
- **Orders** — filter by status, update pipeline: `pending → processing → shipped → delivered`
- **Users** — search, activate, deactivate, delete accounts; view full order history per user

### 🛒 Customer Storefront

- Browse products with search, category filter and sort controls
- Product detail pages with image and related product suggestions
- Shopping cart — add items, update quantities, remove products
- Secure checkout with full delivery information form
- Order history with live status tracking and cancellation
- User profile — update personal info, change password, delete account
- Fully responsive — works on desktop, tablet and mobile

---

## 🗂️ Project Structure

```
Aerixis-ShopNow/
├── accounts/               # User auth, profiles, registration
│   ├── models.py           # UserProfile model
│   ├── views.py            # Login, register, profile, delete
│   └── forms.py
├── store/                  # Core e-commerce logic
│   ├── models.py           # Product, Category, Cart, Order
│   ├── views.py            # Storefront views
│   └── management/
│       └── commands/
│           └── seed_data.py
├── dashboard/              # Custom admin panel
│   ├── views.py            # CRUD views for admin
│   └── urls.py
├── templates/
│   ├── base.html           # Storefront base layout
│   ├── dashboard/          # Admin dashboard templates
│   ├── store/              # Shop, cart, checkout templates
│   └── accounts/           # Auth templates
├── screenshots/            # README screenshots
├── manage.py
└── requirements.txt
```

---

## 🔐 Security Notes

- CSRF protection enabled on all forms
- Login required decorators on all protected views
- Staff-only access enforced on the entire admin dashboard
- Password hashing handled by Django's built-in auth system
- User account deletion requires password confirmation

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built by [@anim-michael-asante](https://github.com/anim-michael-asante)

</div>
