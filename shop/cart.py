import copy
import logging
from decimal import Decimal, InvalidOperation
from .models import Product

logger = logging.getLogger(__name__)
CART_SESSION_ID = 'cart'

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_ID)
        if not isinstance(cart, dict):
            cart = self.session[CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, product, quantity=1, override_quantity=False):
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            quantity = 1

        # Clamp quantity to safe limits (1 to 99)
        quantity = max(1, min(quantity, 99))

        product_id = str(product.id)
        if product_id not in self.cart:
            try:
                price_str = str(product.effective_price)
            except Exception as e:
                logger.warning("Failed to get effective_price for product %s: %s", product_id, e)
                price_str = str(product.price)

            self.cart[product_id] = {
                'quantity': 0,
                'price': price_str
            }

        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            new_qty = self.cart[product_id].get('quantity', 0) + quantity
            self.cart[product_id]['quantity'] = min(new_qty, 99)
        self.save()

    def save(self):
        self.session.modified = True

    def remove(self, product):
        product_id = str(product.id) if hasattr(product, 'id') else str(product)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def __iter__(self):
        product_ids = list(self.cart.keys())
        products = Product.objects.filter(id__in=product_ids)
        cart_copy = copy.deepcopy(self.cart)

        existing_ids = set()
        for product in products:
            pid = str(product.id)
            existing_ids.add(pid)
            if pid in cart_copy:
                cart_copy[pid]['product'] = product

        # Clean up stale / deleted products from actual session cart
        stale_ids = [pid for pid in product_ids if pid not in existing_ids]
        if stale_ids:
            for pid in stale_ids:
                if pid in self.cart:
                    del self.cart[pid]
            self.save()

        for item in cart_copy.values():
            if 'product' in item:
                try:
                    item['price'] = Decimal(str(item.get('price', '0.00')))
                except (InvalidOperation, TypeError, ValueError):
                    item['price'] = Decimal('0.00')

                try:
                    qty = int(item.get('quantity', 1))
                except (ValueError, TypeError):
                    qty = 1

                item['quantity'] = qty
                item['total_price'] = item['price'] * qty
                yield item

    def __len__(self):
        total = 0
        for item in self.cart.values():
            try:
                total += int(item.get('quantity', 0))
            except (ValueError, TypeError):
                continue
        return total

    def get_total_price(self):
        total = Decimal('0.00')
        for item in self.cart.values():
            try:
                price = Decimal(str(item.get('price', '0.00')))
                qty = int(item.get('quantity', 0))
                total += price * qty
            except (InvalidOperation, TypeError, ValueError):
                continue
        return total

    def clear(self):
        self.session.pop(CART_SESSION_ID, None)
        self.save()

