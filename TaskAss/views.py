import logging
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.utils.http import url_has_allowed_host_and_scheme

logger = logging.getLogger(__name__)

def about(request):
    try:
        return render(request, 'about.html')
    except Exception as e:
        logger.exception("Error rendering about page: %s", e)
        return render(request, '500.html', status=500)

def user_register(request):
    if request.user.is_authenticated:
        return redirect('shop:product_list')
    try:
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                messages.success(request, f"Welcome to Shopcart, {user.username}!")
                return redirect('shop:product_list')
            else:
                messages.error(request, "Please correct the errors below.")
        else:
            form = UserCreationForm()
        return render(request, 'accounts/register.html', {'form': form})
    except Exception as e:
        logger.exception("Error during user registration: %s", e)
        messages.error(request, "An unexpected error occurred. Please try again.")
        return redirect('register')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('shop:product_list')
    try:
        if request.method == 'POST':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url and url_has_allowed_host_and_scheme(
                    url=next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure()
                ):
                    return redirect(next_url)
                return redirect('shop:product_list')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            form = AuthenticationForm()
        return render(request, 'accounts/login.html', {'form': form})
    except Exception as e:
        logger.exception("Error during user login: %s", e)
        messages.error(request, "An unexpected error occurred during login.")
        return redirect('login')

def user_logout(request):
    try:
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    except Exception as e:
        logger.exception("Error during logout: %s", e)
    return redirect('shop:product_list')

# --- Custom HTTP Error Handlers ---

def custom_bad_request_view(request, exception=None):
    return render(request, '400.html', status=400)

def custom_permission_denied_view(request, exception=None):
    return render(request, '403.html', status=403)

def custom_page_not_found_view(request, exception=None):
    return render(request, '404.html', status=404)

def custom_server_error_view(request):
    return render(request, '500.html', status=500)