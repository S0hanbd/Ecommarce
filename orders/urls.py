from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.order_create, name='order_create'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders, name='my_orders'),
]
