import logging
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme
from .models import Category, Product
from .cart import Cart
from .wishlist import Wishlist
from .forms import CartAddProductForm

logger = logging.getLogger(__name__)

def product_list(request, category_slug=None):
    try:
        category = None
        categories = Category.objects.all()
        products = Product.objects.filter(is_available=True)
        
        query = (request.GET.get('q') or '').strip()[:100]
        sort = request.GET.get('sort')
        price_range = request.GET.get('price')

        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=category)

        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        if price_range == 'under_50':
            products = products.filter(price__lt=50)
        elif price_range == '50_200':
            products = products.filter(price__gte=50, price__lte=200)
        elif price_range == 'over_200':
            products = products.filter(price__gt=200)

        valid_sorts = {
            'price_asc': 'price',
            'price_desc': '-price',
            'newest': '-created_at',
            'name': 'name',
        }
        if sort in valid_sorts:
            products = products.order_by(valid_sorts[sort])

        context = {
            'category': category,
            'categories': categories,
            'products': products,
            'query': query,
            'sort': sort,
            'price_range': price_range,
        }
        return render(request, 'shop/product_list.html', context)
    except Exception as e:
        logger.exception("Error loading product list: %s", e)
        messages.error(request, "Unable to load products at this moment. Please try again.")
        return render(request, 'shop/product_list.html', {'categories': [], 'products': []})


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, is_available=True)
    cart_product_form = CartAddProductForm()

    try:
        # Track Recently Viewed in Session defensively
        raw_recently_viewed = request.session.get('recently_viewed', [])
        if not isinstance(raw_recently_viewed, list):
            raw_recently_viewed = []

        recently_viewed_ids = []
        for item in raw_recently_viewed:
            try:
                recently_viewed_ids.append(int(item))
            except (ValueError, TypeError):
                continue

        if product.id in recently_viewed_ids:
            recently_viewed_ids.remove(product.id)
        recently_viewed_ids.insert(0, product.id)
        recently_viewed_ids = recently_viewed_ids[:5]
        request.session['recently_viewed'] = recently_viewed_ids

        recently_viewed_products = Product.objects.filter(
            id__in=recently_viewed_ids, is_available=True
        ).exclude(id=product.id)[:4]

        related_products = Product.objects.filter(
            category=product.category, is_available=True
        ).exclude(id=product.id)[:4]
    except Exception as e:
        logger.warning("Error computing related/recently viewed for product %s: %s", product.id, e)
        recently_viewed_products = []
        related_products = []
    
    context = {
        'product': product,
        'cart_product_form': cart_product_form,
        'related_products': related_products,
        'recently_viewed_products': recently_viewed_products,
    }
    return render(request, 'shop/product_detail.html', context)


@require_POST
def cart_add(request, product_id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id, is_available=True)
        
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1
        quantity = max(1, min(quantity, 99))

        override = request.POST.get('override', 'False') == 'True'
        cart.add(product=product, quantity=quantity, override_quantity=override)
        messages.success(request, f"Added {product.name} to your cart!")
    except Exception as e:
        logger.exception("Error adding product %s to cart: %s", product_id, e)
        messages.error(request, "Could not add item to cart. Please try again.")
    return redirect('shop:cart_detail')


@require_POST
def buy_now(request, product_id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id, is_available=True)
        try:
            quantity = int(request.POST.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1
        quantity = max(1, min(quantity, 99))

        cart.add(product=product, quantity=quantity, override_quantity=False)
        return redirect('orders:order_create')
    except Exception as e:
        logger.exception("Error processing buy now for product %s: %s", product_id, e)
        messages.error(request, "Unable to proceed to checkout. Please try again.")
        return redirect('shop:product_list')


@require_POST
def cart_remove(request, product_id):
    try:
        cart = Cart(request)
        product = get_object_or_404(Product, id=product_id)
        cart.remove(product)
        messages.info(request, f"Removed {product.name} from your cart.")
    except Exception as e:
        logger.exception("Error removing product %s from cart: %s", product_id, e)
        messages.error(request, "Could not remove item from cart.")
    return redirect('shop:cart_detail')


def cart_detail(request):
    try:
        cart = Cart(request)
        coupon = request.session.get('coupon', None)
        total_price = cart.get_total_price()
        discount_amount = Decimal('0.00')

        if coupon and isinstance(coupon, dict) and 'discount' in coupon:
            try:
                discount_percent = Decimal(str(coupon['discount']))
                discount_amount = (total_price * discount_percent) / Decimal('100')
                final_price = max(Decimal('0.00'), total_price - discount_amount)
            except Exception as e:
                logger.warning("Error calculating coupon discount: %s", e)
                final_price = total_price
                discount_amount = Decimal('0.00')
        else:
            final_price = total_price

        context = {
            'cart': cart,
            'coupon': coupon,
            'discount_amount': discount_amount,
            'final_price': final_price,
        }
        return render(request, 'cart/detail.html', context)
    except Exception as e:
        logger.exception("Error rendering cart detail: %s", e)
        messages.error(request, "There was an error displaying your cart.")
        return render(request, 'cart/detail.html', {'cart': [], 'discount_amount': 0, 'final_price': 0})


@require_POST
def apply_coupon(request):
    try:
        code = request.POST.get('code', '').strip().upper()[:30]
        if code in ['SAVE10', 'SHOPCART10']:
            request.session['coupon'] = {'code': code, 'discount': 10}
            messages.success(request, "Promo code applied! You received 10% off.")
        elif code in ['DISCOUNT20', 'LUXE20']:
            request.session['coupon'] = {'code': code, 'discount': 20}
            messages.success(request, "Promo code applied! You received 20% off.")
        else:
            messages.error(request, "Invalid coupon code. Try 'SAVE10' or 'DISCOUNT20'.")
    except Exception as e:
        logger.exception("Error applying coupon: %s", e)
        messages.error(request, "Failed to apply coupon. Please try again.")
    return redirect('shop:cart_detail')


def wishlist_toggle(request, product_id):
    try:
        wishlist = Wishlist(request)
        product = get_object_or_404(Product, id=product_id)
        added = wishlist.toggle(product.id)
        if added:
            messages.success(request, f"Added {product.name} to your Wishlist!")
        else:
            messages.info(request, f"Removed {product.name} from your Wishlist.")
    except Exception as e:
        logger.exception("Error toggling wishlist for product %s: %s", product_id, e)
        messages.error(request, "Could not update your wishlist.")

    referer = request.META.get('HTTP_REFERER')
    if referer and url_has_allowed_host_and_scheme(
        url=referer,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure()
    ):
        return redirect(referer)
    return redirect('shop:product_list')


def wishlist_detail(request):
    try:
        wishlist = Wishlist(request)
        return render(request, 'shop/wishlist.html', {'wishlist': wishlist})
    except Exception as e:
        logger.exception("Error displaying wishlist: %s", e)
        messages.error(request, "Could not load wishlist.")
        return redirect('shop:product_list')


def deals_list(request):
    try:
        products = Product.objects.filter(is_available=True)
        context = {
            'products': products,
            'title': "Exclusive Deals & Special Offers",
        }
        return render(request, 'shop/deals.html', context)
    except Exception as e:
        logger.exception("Error loading deals list: %s", e)
        return render(request, 'shop/deals.html', {'products': [], 'title': "Deals"})


def delivery_info(request):
    return render(request, 'delivery.html')


def contact_view(request):
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()[:100]
        email = (request.POST.get('email') or '').strip()[:100]
        message = (request.POST.get('message') or '').strip()[:2000]

        if not name or not email or not message:
            messages.error(request, "Please fill in all required fields.")
            return render(request, 'contact.html')

        logger.info("Contact form submitted by %s <%s>", name, email)
        messages.success(request, f"Thank you {name}! Your message has been received. We will reply to {email} shortly.")
        return redirect('contact')
    return render(request, 'contact.html')

