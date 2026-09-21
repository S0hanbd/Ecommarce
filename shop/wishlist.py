import logging
from .models import Product

logger = logging.getLogger(__name__)
WISHLIST_SESSION_ID = 'wishlist'

class Wishlist:
    def __init__(self, request):
        self.session = request.session
        wishlist = self.session.get(WISHLIST_SESSION_ID)
        if not isinstance(wishlist, list):
            wishlist = self.session[WISHLIST_SESSION_ID] = []
        self.wishlist = wishlist

    def toggle(self, product_id):
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            logger.warning("Invalid product_id passed to Wishlist.toggle: %s", product_id)
            return False

        if product_id in self.wishlist:
            self.wishlist = [pid for pid in self.wishlist if pid != product_id]
            self.session[WISHLIST_SESSION_ID] = self.wishlist
            added = False
        else:
            self.wishlist.append(product_id)
            added = True
        self.save()
        return added

    def save(self):
        self.session.modified = True

    def __iter__(self):
        valid_ids = []
        for item in self.wishlist:
            try:
                valid_ids.append(int(item))
            except (ValueError, TypeError):
                continue

        products = Product.objects.filter(id__in=valid_ids, is_available=True)
        for product in products:
            yield product

    def __len__(self):
        return len(self.wishlist)

    def contains(self, product_id):
        try:
            return int(product_id) in self.wishlist
        except (ValueError, TypeError):
            return False

    def clear(self):
        self.session.pop(WISHLIST_SESSION_ID, None)
        self.save()

