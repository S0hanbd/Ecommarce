from .models import Product

WISHLIST_SESSION_ID = 'wishlist'

class Wishlist:
    def __init__(self, request):
        self.session = request.session
        wishlist = self.session.get(WISHLIST_SESSION_ID)
        if not wishlist:
            wishlist = self.session[WISHLIST_SESSION_ID] = []
        self.wishlist = wishlist

    def toggle(self, product_id):
        product_id = int(product_id)
        if product_id in self.wishlist:
            self.wishlist.remove(product_id)
            added = False
        else:
            self.wishlist.append(product_id)
            added = True
        self.save()
        return added

    def save(self):
        self.session.modified = True

    def __iter__(self):
        products = Product.objects.filter(id__in=self.wishlist, is_available=True)
        for product in products:
            yield product

    def __len__(self):
        return len(self.wishlist)

    def contains(self, product_id):
        return int(product_id) in self.wishlist
