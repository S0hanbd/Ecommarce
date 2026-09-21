from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib import messages
from .models import Category, Product
from .cart import Cart
from .wishlist import Wishlist
from .forms import CartAddProductForm

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(is_available=True)
    
    query = request.GET.get('q')
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

    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'name':
        products = products.order_by('name')

    context = {
        'category': category,
        'categories': categories,
        'products': products,
        'query': query,
        'sort': sort,
        'price_range': price_range,
    }
    return render(request, 'shop/product_list.html', context)


def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, is_available=True)
    cart_product_form = CartAddProductForm()

    # Track Recently Viewed in Session
    recently_viewed_ids = request.session.get('recently_viewed', [])
    if product.id in recently_viewed_ids:
        recently_viewed_ids.remove(product.id)
    recently_viewed_ids.insert(0, product.id)
    # Keep last 5
    recently_viewed_ids = recently_viewed_ids[:5]
    request.session['recently_viewed'] = recently_viewed_ids

    # Fetch recently viewed objects excluding current
    recently_viewed_products = Product.objects.filter(id__in=recently_viewed_ids).exclude(id=product.id)[:4]

    related_products = Product.objects.filter(category=product.category, is_available=True).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'cart_product_form': cart_product_form,
        'related_products': related_products,
        'recently_viewed_products': recently_viewed_products,
    }
    return render(request, 'shop/product_detail.html', context)


@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    override = request.POST.get('override', 'False') == 'True'
    cart.add(product=product, quantity=quantity, override_quantity=override)
    messages.success(request, f"Added {product.name} to your cart!")
    return redirect('shop:cart_detail')


@require_POST
def buy_now(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity, override_quantity=False)
    return redirect('orders:order_create')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    messages.info(request, f"Removed {product.name} from your cart.")
    return redirect('shop:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    coupon = request.session.get('coupon', None)
    total_price = cart.get_total_price()
    discount_amount = 0

    if coupon:
        discount_amount = (total_price * coupon['discount']) / 100
        final_price = total_price - discount_amount
    else:
        final_price = total_price

    context = {
        'cart': cart,
        'coupon': coupon,
        'discount_amount': discount_amount,
        'final_price': final_price,
    }
    return render(request, 'cart/detail.html', context)


@require_POST
def apply_coupon(request):
    code = request.POST.get('code', '').strip().upper()
    if code in ['SAVE10', 'SHOPCART10']:
        request.session['coupon'] = {'code': code, 'discount': 10}
        messages.success(request, "Promo code SAVE10 applied! You get 10% off.")
    elif code in ['DISCOUNT20', 'LUXE20']:
        request.session['coupon'] = {'code': code, 'discount': 20}
        messages.success(request, "Promo code DISCOUNT20 applied! You get 20% off.")
    else:
        messages.error(request, "Invalid coupon code. Try 'SAVE10' or 'DISCOUNT20'.")
    return redirect('shop:cart_detail')


def wishlist_toggle(request, product_id):
    wishlist = Wishlist(request)
    product = get_object_or_404(Product, id=product_id)
    added = wishlist.toggle(product.id)
    if added:
        messages.success(request, f"Added {product.name} to your Wishlist!")
    else:
        messages.info(request, f"Removed {product.name} from your Wishlist.")
    
    next_url = request.META.get('HTTP_REFERER') or 'shop:product_list'
    return redirect(next_url)


def wishlist_detail(request):
    wishlist = Wishlist(request)
    return render(request, 'shop/wishlist.html', {'wishlist': wishlist})


def deals_list(request):
    products = Product.objects.filter(is_available=True)
    context = {
        'products': products,
        'title': "Exclusive Deals & Special Offers",
    }
    return render(request, 'shop/deals.html', context)


def delivery_info(request):
    return render(request, 'delivery.html')


def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        messages.success(request, f"Thank you {name}! Your message has been sent. We'll reply to {email} shortly.")
        return redirect('contact')
    return render(request, 'contact.html')
