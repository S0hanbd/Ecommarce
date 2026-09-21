from .cart import Cart
from .wishlist import Wishlist
from .models import Category

def cart(request):
    return {'cart': Cart(request)}

def wishlist(request):
    return {'wishlist': Wishlist(request)}

def categories_processor(request):
    return {'all_categories': Category.objects.all()}
