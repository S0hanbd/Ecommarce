from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'discount_price', 'stock', 'is_available', 'created_at']
    list_filter = ['is_available', 'created_at', 'category']
    list_editable = ['price', 'discount_price', 'stock', 'is_available']
    prepopulated_fields = {'slug': ('name',)}
