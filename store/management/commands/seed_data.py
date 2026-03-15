from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product

CATEGORIES = [
    {"name": "Electronics",   "icon": "fa-microchip",          "description": "Phones, laptops & gadgets"},
    {"name": "Fashion",       "icon": "fa-shirt",              "description": "Clothing, shoes, accessories"},
    {"name": "Home & Living", "icon": "fa-house",              "description": "Furniture, decor & kitchen"},
    {"name": "Sports",        "icon": "fa-dumbbell",           "description": "Fitness & sportswear"},
    {"name": "Books",         "icon": "fa-book-open",          "description": "Textbooks & fiction"},
    {"name": "Beauty",        "icon": "fa-spray-can-sparkles", "description": "Skincare & makeup"},
]

PRODUCTS = [
    {"name": "Samsung Galaxy A54", "category": "Electronics",
     "price": 1800.00, "sale_price": 1600.00, "stock": 15, "featured": True,
     "image_url": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=600&h=600&fit=crop&auto=format",
     "description": "6.4\" Super AMOLED display, 50MP camera, 5000mAh battery. Perfect for everyday use with stunning visuals."},
    {"name": "Wireless Bluetooth Earbuds", "category": "Electronics",
     "price": 250.00, "sale_price": 199.00, "stock": 30, "featured": True,
     "image_url": "https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=600&h=600&fit=crop&auto=format",
     "description": "True wireless ANC earbuds. 30-hour total battery life. IPX5 water resistant."},
    {"name": "HP Laptop 15.6\"", "category": "Electronics",
     "price": 3500.00, "sale_price": None, "stock": 8, "featured": True,
     "image_url": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&h=600&fit=crop&auto=format",
     "description": "Intel Core i5, 8GB RAM, 512GB SSD. Windows 11 Home, Full HD IPS display."},
    {"name": "Smart Watch Pro", "category": "Electronics",
     "price": 450.00, "sale_price": 380.00, "stock": 20, "featured": False,
     "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&h=600&fit=crop&auto=format",
     "description": "Heart rate, GPS, 7-day battery. Compatible with iOS and Android. 50m water resistant."},
    {"name": "Power Bank 20000mAh", "category": "Electronics",
     "price": 180.00, "sale_price": None, "stock": 25, "featured": False,
     "image_url": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=600&h=600&fit=crop&auto=format",
     "description": "Fast charging 20W, dual USB-A + USB-C. Charge your phone 5 times over."},
    {"name": "Men's Classic Polo Shirt", "category": "Fashion",
     "price": 85.00, "sale_price": 65.00, "stock": 50, "featured": True,
     "image_url": "https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=600&h=600&fit=crop&auto=format",
     "description": "100% breathable cotton polo. Machine washable. Perfect for casual and semi-formal occasions."},
    {"name": "Women's Ankara Dress", "category": "Fashion",
     "price": 120.00, "sale_price": None, "stock": 35, "featured": True,
     "image_url": "https://images.unsplash.com/photo-1515886657613-9f3515b0c78f?w=600&h=600&fit=crop&auto=format",
     "description": "Vibrant African print Ankara dress. Knee-length, fitted silhouette with zipper back."},
    {"name": "Classic White Sneakers", "category": "Fashion",
     "price": 220.00, "sale_price": 180.00, "stock": 40, "featured": False,
     "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&h=600&fit=crop&auto=format",
     "description": "Clean minimal leather sneakers with cushioned insole for all-day comfort."},
    {"name": "Slim Fit Denim Jeans", "category": "Fashion",
     "price": 150.00, "sale_price": None, "stock": 60, "featured": False,
     "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=600&h=600&fit=crop&auto=format",
     "description": "Premium stretch denim, slim fit. 5-pocket design. Dark blue and black options."},
    {"name": "Non-Stick Cookware Set", "category": "Home & Living",
     "price": 320.00, "sale_price": 260.00, "stock": 18, "featured": True,
     "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600&h=600&fit=crop&auto=format",
     "description": "5-piece aluminum cookware set. Dishwasher safe and induction compatible."},
    {"name": "Modern LED Desk Lamp", "category": "Home & Living",
     "price": 95.00, "sale_price": None, "stock": 22, "featured": False,
     "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=600&h=600&fit=crop&auto=format",
     "description": "Adjustable brightness, USB charging port, touch control. Eye-care LED technology."},
    {"name": "Memory Foam Pillow", "category": "Home & Living",
     "price": 140.00, "sale_price": 110.00, "stock": 30, "featured": False,
     "image_url": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=600&h=600&fit=crop&auto=format",
     "description": "Contour memory foam for neck & spine support. Hypoallergenic cover."},
    {"name": "Adjustable Dumbbell Set", "category": "Sports",
     "price": 480.00, "sale_price": 420.00, "stock": 12, "featured": True,
     "image_url": "https://images.unsplash.com/photo-1571019614242-c5c5dee9f50b?w=600&h=600&fit=crop&auto=format",
     "description": "5-25kg adjustable dumbbells. Compact home gym solution with knurled grip."},
    {"name": "Premium Yoga Mat", "category": "Sports",
     "price": 110.00, "sale_price": None, "stock": 45, "featured": False,
     "image_url": "https://images.unsplash.com/photo-1601925228984-68fcf0aae3ed?w=600&h=600&fit=crop&auto=format",
     "description": "6mm non-slip TPE mat, eco-friendly. 183x61cm with carrying strap."},
    {"name": "Python Programming Guide", "category": "Books",
     "price": 75.00, "sale_price": 60.00, "stock": 100, "featured": False,
     "image_url": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=600&h=600&fit=crop&auto=format",
     "description": "Complete beginner's Python guide. OOP, file handling, web scraping with exercises."},
    {"name": "Rich Dad Poor Dad", "category": "Books",
     "price": 55.00, "sale_price": None, "stock": 80, "featured": True,
     "image_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=600&h=600&fit=crop&auto=format",
     "description": "Kiyosaki's bestselling personal finance book. Essential financial literacy reading."},
    {"name": "Shea Butter Moisturizer", "category": "Beauty",
     "price": 65.00, "sale_price": 50.00, "stock": 70, "featured": False,
     "image_url": "https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=600&h=600&fit=crop&auto=format",
     "description": "Pure natural shea butter moisturizer. Fragrance-free, all skin types. 250ml."},
    {"name": "Men's Grooming Kit", "category": "Beauty",
     "price": 185.00, "sale_price": None, "stock": 25, "featured": True,
     "image_url": "https://images.unsplash.com/photo-1503951914875-452162b0f3f1?w=600&h=600&fit=crop&auto=format",
     "description": "8-piece grooming kit: trimmer, comb, scissors, razor & skincare in a premium case."},
]


class Command(BaseCommand):
    help = 'Seed the database with sample data for ShopNow Group 4'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Seeding database...'))

        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@shopnow.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('+ Superuser: admin / admin123'))

        if not User.objects.filter(username='demo').exists():
            demo = User.objects.create_user(
                username='demo', email='demo@shopnow.com',
                password='demo1234', first_name='Kwame', last_name='Mensah'
            )
            demo.profile.phone = '0244123456'
            demo.profile.city = 'Accra'
            demo.profile.address = '12 Independence Ave, Accra'
            demo.profile.save()
            self.stdout.write(self.style.SUCCESS('+ Demo user: demo / demo1234'))

        cat_map = {}
        for c in CATEGORIES:
            cat, created = Category.objects.get_or_create(
                name=c['name'],
                defaults={'icon': c['icon'], 'description': c['description']}
            )
            cat_map[c['name']] = cat
            if created:
                self.stdout.write(f'  + Category: {cat.name}')

        for p in PRODUCTS:
            if not Product.objects.filter(name=p['name']).exists():
                Product.objects.create(
                    name=p['name'], category=cat_map[p['category']],
                    price=p['price'], sale_price=p['sale_price'],
                    stock=p['stock'], is_featured=p['featured'],
                    is_active=True, image_url=p['image_url'],
                    description=p['description'],
                )
                self.stdout.write(f'  + Product: {p["name"]}')

        self.stdout.write(self.style.SUCCESS('\n✅ Seeded! Admin: admin/admin123 | Demo: demo/demo1234'))
