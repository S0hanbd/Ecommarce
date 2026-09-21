from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from shop.models import Category, Product
from .models import Order, OrderItem

class OrderSecurityAndExceptionTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.category = Category.objects.create(name='Audio', slug='audio')
        self.product = Product.objects.create(
            category=self.category,
            name='Noise Cancelling Headphones',
            slug='nc-headphones',
            price=Decimal('150.00'),
            is_available=True
        )

    def test_order_creation_empty_cart_redirect(self):
        response = self.client.get(reverse('orders:order_create'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('shop:product_list'))

    def test_order_creation_success_flow(self):
        # Add to cart
        self.client.post(
            reverse('shop:cart_add', args=[self.product.id]),
            {'quantity': '2', 'override': 'False'}
        )
        
        # Post checkout form
        response = self.client.post(reverse('orders:order_create'), {
            'full_name': 'Alice Smith',
            'email': 'alice@example.com',
            'phone': '1234567890',
            'address': '123 Main St',
            'city': 'Metropolis',
            'postal_code': '12345'
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify order was created with items
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.full_name, 'Alice Smith')
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.total_price, Decimal('300.00'))

    def test_order_success_idor_protection(self):
        # Create an order belonging to user1
        order = Order.objects.create(
            user=self.user1,
            full_name='User One',
            email='user1@example.com',
            phone='1234567890',
            address='123 Main St',
            city='City',
            postal_code='10001',
            total_price=Decimal('100.00')
        )

        # Anonymous user attempting to view user1's order without session should be denied (403)
        anon_client = Client()
        response = anon_client.get(reverse('orders:order_success', args=[order.id]))
        self.assertEqual(response.status_code, 403)

        # User2 logged in attempting to view user1's order should be denied (403)
        user2_client = Client()
        user2_client.login(username='user2', password='password123')
        response = user2_client.get(reverse('orders:order_success', args=[order.id]))
        self.assertEqual(response.status_code, 403)

        # User1 logged in should be able to view their own order
        user1_client = Client()
        user1_client.login(username='user1', password='password123')
        response = user1_client.get(reverse('orders:order_success', args=[order.id]))
        self.assertEqual(response.status_code, 200)
