from django import forms
from django.forms import inlineformset_factory
from .models import Order, OrderItem

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'completed']  # Поля формы заказа

OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    fields=['product', 'quantity'],  # Поля формы для товаров
    extra=1,
    can_delete=True
)
