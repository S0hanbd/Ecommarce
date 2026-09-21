from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from shop import views as shop_views
from . import views as main_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', main_views.about, name="about"),
    path('delivery/', shop_views.delivery_info, name="delivery"),
    path('contact/', shop_views.contact_view, name="contact"),
    path('login/', main_views.user_login, name="login"),
    path('register/', main_views.user_register, name="register"),
    path('logout/', main_views.user_logout, name="logout"),
    path('orders/', include('orders.urls', namespace='orders')),
    path('', include('shop.urls', namespace='shop')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
