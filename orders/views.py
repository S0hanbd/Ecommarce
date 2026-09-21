import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction, DatabaseError
from .models import Order, OrderItem
from .forms import OrderCreateForm
from shop.cart import Cart

logger = logging.getLogger(__name__)

def order_create(request):
    try:
        cart = Cart(request)
        if len(cart) == 0:
            messages.info(request, "Your cart is empty. Add items before checking out.")
            return redirect('shop:product_list')

        if request.method == 'POST':
            form = OrderCreateForm(request.POST)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        order = form.save(commit=False)
                        if request.user.is_authenticated:
                            order.user = request.user
                        order.total_price = cart.get_total_price()
                        order.save()

                        for item in cart:
                            OrderItem.objects.create(
                                order=order,
                                product=item['product'],
                                price=item['price'],
                                quantity=item['quantity']
                            )

                        cart.clear()
                        request.session['last_order_id'] = order.id
                        messages.success(request, "Thank you! Your order has been placed successfully.")
                        return redirect('orders:order_success', order_id=order.id)
                except (DatabaseError, Exception) as e:
                    logger.exception("Database error while creating order: %s", e)
                    messages.error(request, "Failed to complete your order due to a system error. Please try again.")
            else:
                messages.error(request, "Please review the checkout form and correct the errors.")
        else:
            initial_data = {}
            if request.user.is_authenticated:
                initial_data = {
                    'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
                    'email': request.user.email,
                }
            form = OrderCreateForm(initial=initial_data)

        return render(request, 'orders/checkout.html', {'cart': cart, 'form': form})
    except Exception as e:
        logger.exception("Unexpected error in order_create view: %s", e)
        messages.error(request, "An unexpected error occurred during checkout.")
        return redirect('shop:cart_detail')


def order_success(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id)
        
        # Privacy / IDOR Protection:
        # Allow viewing if:
        # 1. The logged-in user is the owner of the order
        # 2. Or the current session placed this order (for guest checkouts)
        # 3. Or the user is a staff member
        is_owner = request.user.is_authenticated and order.user == request.user
        is_session_creator = request.session.get('last_order_id') == order.id
        is_staff = request.user.is_authenticated and request.user.is_staff

        if not (is_owner or is_session_creator or is_staff):
            logger.warning("Unauthorized attempt to access order %s by user %s", order_id, request.user)
            raise PermissionDenied("You do not have permission to view this order.")

        return render(request, 'orders/success.html', {'order': order})
    except PermissionDenied:
        raise
    except Exception as e:
        logger.exception("Error loading order_success for order %s: %s", order_id, e)
        return render(request, '500.html', status=500)


@login_required
def my_orders(request):
    try:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        return render(request, 'orders/my_orders.html', {'orders': orders})
    except Exception as e:
        logger.exception("Error fetching orders for user %s: %s", request.user, e)
        messages.error(request, "Unable to load your order history.")
        return render(request, 'orders/my_orders.html', {'orders': []})

