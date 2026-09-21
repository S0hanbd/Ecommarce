from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from shop.models import Category, Product

class Command(BaseCommand):
    help = 'Seeds database with exact Shopcart demo categories and products.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding database with Shopcart dataset...")

        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

        categories_data = [
            {'name': 'Headphone', 'slug': 'electronics'},
            {'name': 'Shoe', 'slug': 'fashion-apparel'},
            {'name': 'Bag', 'slug': 'accessories'},
            {'name': 'Laptop', 'slug': 'home-living'},
        ]

        cat_objs = {}
        for cdata in categories_data:
            cat, _ = Category.objects.get_or_create(
                slug=cdata['slug'],
                defaults={'name': cdata['name']}
            )
            cat_objs[cdata['slug']] = cat

        products_data = [
            {
                'category': cat_objs['electronics'],
                'name': 'AirPods Max',
                'slug': 'airpods-max',
                'price': 549.00,
                'discount_price': None,
                'stock': 12,
                'description': 'A perfect balance of exhilarating high-fidelity audio and the effortless magic of AirPods.'
            },
            {
                'category': cat_objs['electronics'],
                'name': 'Gaming Headphone',
                'slug': 'gaming-headphone',
                'price': 239.00,
                'discount_price': None,
                'stock': 15,
                'description': 'Table with air purifier, stained veneer/black. Surround sound gaming audio.'
            },
            {
                'category': cat_objs['home-living'],
                'name': 'MacBook Pro 13"',
                'slug': 'macbook-pro-13',
                'price': 1099.00,
                'discount_price': None,
                'stock': 8,
                'description': '256, 8 core GPU, 8 GB unified memory for high-performance computing.'
            },
            {
                'category': cat_objs['electronics'],
                'name': 'HomePod mini',
                'slug': 'homepod-mini',
                'price': 59.00,
                'discount_price': None,
                'stock': 25,
                'description': '5 Colors Available. Room-filling 360-degree audio.'
            },
            {
                'category': cat_objs['accessories'],
                'name': 'Laptop sleeve MacBook',
                'slug': 'laptop-sleeve-macbook',
                'price': 59.00,
                'discount_price': None,
                'stock': 30,
                'description': 'Organic Cotton, fairtrade certified laptop protection sleeve.'
            },
            {
                'category': cat_objs['electronics'],
                'name': 'Wireless Earbuds, IPX8',
                'slug': 'wireless-earbuds-ipx8',
                'price': 89.00,
                'discount_price': None,
                'stock': 20,
                'description': 'Organic Cotton, fairtrade certified. Waterproof sports earbuds.'
            },
            {
                'category': cat_objs['electronics'],
                'name': 'Bose BT Earphones',
                'slug': 'bose-bt-earphones',
                'price': 289.00,
                'discount_price': None,
                'stock': 10,
                'description': 'Table with air purifier, stained veneer/black. Wireless noise canceling.'
            },
            {
                'category': cat_objs['electronics'],
                'name': 'VIVEFOX Headphones',
                'slug': 'vivefox-headphones',
                'price': 39.00,
                'discount_price': None,
                'stock': 18,
                'description': 'Wired Stereo Headsets With Mic for daily listening.'
            },
            {
                'category': cat_objs['electronics'],
                'name': 'JBL TUNE 600BTNC',
                'slug': 'jbl-tune-600btnc',
                'price': 59.00,
                'discount_price': None,
                'stock': 14,
                'description': 'Premium Wireless Active Noise Canceling On-Ear Bluetooth Headphones.'
            },
            {
                'category': cat_objs['electronics'],
                'name': 'Monster MNFLEX',
                'slug': 'monster-mnflex',
                'price': 89.75,
                'discount_price': None,
                'stock': 16,
                'description': 'Flex Active Noise Canceling Bluetooth Sports Headphones.'
            },
        ]

        for pdata in products_data:
            Product.objects.update_or_create(
                slug=pdata['slug'],
                defaults=pdata
            )

        self.stdout.write(self.style.SUCCESS("Successfully updated Shopcart seed dataset!"))
