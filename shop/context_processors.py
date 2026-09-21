import logging
from .cart import Cart
from .wishlist import Wishlist
from .models import Category

logger = logging.getLogger(__name__)

def cart(request):
    try:
        return {'cart': Cart(request)}
    except Exception as e:
        logger.exception("Error in cart context processor: %s", e)
        return {'cart': []}

def wishlist(request):
    try:
        return {'wishlist': Wishlist(request)}
    except Exception as e:
        logger.exception("Error in wishlist context processor: %s", e)
        return {'wishlist': []}

def categories_processor(request):
    try:
        return {'all_categories': Category.objects.all()}
    except Exception as e:
        logger.exception("Error in categories_processor context processor: %s", e)
        return {'all_categories': []}

