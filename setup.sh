#!/bin/bash
# ════════════════════════════════════════════════════════════════
# ShopNow — Setup Script (Linux/Mac)
# ════════════════════════════════════════════════════════════════
set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║          ShopNow E-Commerce Setup        ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# 1. Create virtual environment
echo "▶ Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
echo "▶ Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# 3. Run migrations
echo "▶ Running database migrations..."
python manage.py migrate --run-syncdb

# 4. Seed data
echo "▶ Seeding sample data..."
python manage.py seed_data

echo ""
echo "✅ Setup complete!"
echo ""
echo "  Start the server:  source .venv/bin/activate && python manage.py runserver"
echo "  Admin panel:       http://127.0.0.1:8000/admin/  →  super_admin / Aer!x1s#SuperAdm!n_2025"
echo "  Store:             http://127.0.0.1:8000/"
echo "  Demo user:         demo / ShopNow#DemoUser!2025"
echo ""
