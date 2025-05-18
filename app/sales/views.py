from django.shortcuts import render, redirect
from .models import Order, Customer, Product, OrderItem
from django.views.generic import ListView,  UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models.functions import TruncMinute 
from django.db.models import Count, Sum, F, FloatField
from django import forms
from .forms import OrderForm, OrderItemFormSet


def dashboard(request):
    orders = Order.objects.all()
    return render(request, 'sales/dashboard.html', {'orders': orders})

class ReportFilterForm(forms.Form):
    start_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), required=False)

def sales_report(request):
    form = ReportFilterForm(request.GET or None)
    orders = Order.objects.all()

    if form.is_valid():
        if form.cleaned_data['start_date']:
            orders = orders.filter(created_at__gte=form.cleaned_data['start_date'])
        if form.cleaned_data['end_date']:
            orders = orders.filter(created_at__lte=form.cleaned_data['end_date'])
        if form.cleaned_data['customer']:
            orders = orders.filter(customer=form.cleaned_data['customer'])

    sales_data = (
        orders
        .annotate(minute=TruncMinute('created_at'))
        .values('minute')
        .annotate(
            total_orders=Count('id'),
            total_sales=Sum('items__product__price')
        )
        .order_by('minute')
    )

    labels = [entry['minute'].strftime('%H:%M') for entry in sales_data]
    order_counts = [entry['total_orders'] for entry in sales_data]
    order_sums = [float(entry['total_sales'] or 0) for entry in sales_data]

    context = {
        'form': form,
        'labels': labels,
        'order_counts': order_counts,
        'order_sums': order_sums,
    }
    # Подсчёт среднего чека
    total_sales = Order.objects.aggregate(
        total=Sum(F('items__product__price') * F('items__quantity'), output_field=FloatField())
    )['total'] or 0
    total_orders = Order.objects.count()
    average_order_value = total_sales / total_orders if total_orders else 0
    # Популярные продукты
    popular_products = (
        OrderItem.objects
        .values('product__name')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:5]
    )
    product_labels = [p['product__name'] for p in popular_products]
    product_data = [p['total_quantity'] for p in popular_products]

    context.update({
        'average_order_value': round(average_order_value, 2),
        'product_labels': product_labels,
        'product_data': product_data
    })  
    return render(request, 'sales/sales_report.html', context)

def order_create_view(request):
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if order_form.is_valid() and formset.is_valid():
            order = order_form.save()
            formset.instance = order
            formset.save()
            return redirect('order-list')  # куда нужно после сохранения
    else:
        order_form = OrderForm()
        formset = OrderItemFormSet()

    return render(request, 'orders/order_form.html', {
        'order_form': order_form,
        'formset': formset,
    })

class OrderListView(ListView):
    model = Order
    template_name = 'sales/order_list.html'


class OrderUpdateView(UpdateView):
    model = Order
    fields = ['customer', 'completed'] 
    template_name = 'sales/order_form.html'
    success_url = reverse_lazy('order-list')

class OrderDeleteView(DeleteView):
    model = Order
    template_name = 'sales/order_confirm_delete.html'
    success_url = reverse_lazy('order-list')