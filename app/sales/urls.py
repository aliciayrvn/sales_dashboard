from django.urls import path
from . import views
from .views import OrderListView,  OrderUpdateView, OrderDeleteView, sales_report, order_create_view

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/edit/', OrderUpdateView.as_view(), name='order-edit'),
    path('orders/<int:pk>/delete/', OrderDeleteView.as_view(), name='order-delete'),
    path('reports/sales/', sales_report, name='sales-report'),
    path('orders/create/', order_create_view, name='order-create'),
]