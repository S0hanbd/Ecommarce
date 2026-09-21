from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'postal_code']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'John Doe'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'john@example.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+1 234 567 8900'}),
            'address': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '123 Main Street, Apt 4B'}),
            'city': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'New York'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '10001'}),
        }
