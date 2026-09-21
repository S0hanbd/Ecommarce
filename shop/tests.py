from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from .models import Category, Product
from .cart import Cart
from .wishlist import Wishlist

class ExceptionHandlingAndSecurityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name='Electronics', slug='electronics')
        self.product = Product.objects.create(
            category=self.category,
            name='Wireless Headphones',
            slug='wireless-headphones',
            price=Decimal('99.99'),
            is_available=True
        )

    def test_cart_malformed_quantity_handled_gracefully(self):
        # Post non-integer quantity
        response = self.client.post(
            reverse('shop:cart_add', args=[self.product.id]),
            {'quantity': 'invalid_string', 'override': 'False'}
        )
        self.assertEqual(response.status_code, 302)
        
        # Verify cart defaulted to quantity 1
        cart_response = self.client.get(reverse('shop:cart_detail'))
        self.assertEqual(cart_response.status_code, 200)
        self.assertContains(cart_response, 'Wireless Headphones')

    def test_cart_excessive_quantity_clamped(self):
        # Post excessive quantity (e.g. 500)
        response = self.client.post(
            reverse('shop:cart_add', args=[self.product.id]),
            {'quantity': '500', 'override': 'True'}
        )
        self.assertEqual(response.status_code, 302)
        
        # Check session cart quantity is clamped to 99
        session = self.client.session
        self.assertEqual(session['cart'][str(self.product.id)]['quantity'], 99)

    def test_stale_deleted_product_in_cart_handled_gracefully(self):
        # Add product to cart
        self.client.post(
            reverse('shop:cart_add', args=[self.product.id]),
            {'quantity': '2', 'override': 'False'}
        )
        # Delete product from database
        self.product.delete()

        # Cart detail should not crash with 500; it should load cleanly
        response = self.client.get(reverse('shop:cart_detail'))
        self.assertEqual(response.status_code, 200)

    def test_wishlist_toggle_and_safe_redirect(self):
        # Wishlist toggle should work without crashing
        response = self.client.get(reverse('shop:wishlist_toggle', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)

        # Corrupted / malicious referer should fallback safely to product_list
        response = self.client.get(
            reverse('shop:wishlist_toggle', args=[self.product.id]),
            HTTP_REFERER='https://evil-hacker.com/phish'
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('shop:product_list'))

    def test_coupon_exception_handling(self):
        response = self.client.post(
            reverse('shop:apply_coupon'),
            {'code': 'INVALID_CODE_123'}
        )
        self.assertEqual(response.status_code, 302)

        response = self.client.post(
            reverse('shop:apply_coupon'),
            {'code': 'SAVE10'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.session.get('coupon'), {'code': 'SAVE10', 'discount': 10})

    def test_custom_404_error_page(self):
        response = self.client.get('/non-existent-page-url/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')
