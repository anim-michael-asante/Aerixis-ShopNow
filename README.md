# 🛍️ ShopNow — Django E-Commerce App
### Group 4 · CRUD Assignment · UMaT CSE

---

## 🚀 Quick Start (Windows PowerShell)

```powershell
cd shopnow_final
python -m venv .venv
.venv\Scripts\activate
pip install django pillow
python manage.py makemigrations accounts
python manage.py makemigrations store
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

## 🔑 Login Credentials

| Role      | Username | Password  | URL                        |
|-----------|----------|-----------|----------------------------|
| Admin     | admin    | admin123  | http://127.0.0.1:8000/panel/ |
| Demo User | demo     | demo1234  | http://127.0.0.1:8000/      |

---

## 📋 URLs

| Page            | URL                              |
|-----------------|----------------------------------|
| Storefront      | http://127.0.0.1:8000/           |
| Admin Dashboard | http://127.0.0.1:8000/panel/     |
| Django Admin    | http://127.0.0.1:8000/admin/     |

---

## ✅ Features

### 🎛️ Custom Admin Dashboard (/panel/)
- Stats overview (products, users, orders, revenue)
- Add / Edit / Delete Products with image upload & URL
- Toggle product active/featured status
- Manage Categories with Font Awesome icon
- View & update Order status (pending → processing → shipped → delivered)
- Manage Users — activate/deactivate/delete, view order history

### 🛒 Customer Storefront
- Browse all products with search, filter, sort
- Product detail with related products
- Shopping cart (add, update qty, remove)
- Checkout with delivery info
- Order history & cancellation
- Profile update, password change, account deletion

---

*Group 4 · UMaT CSE*
