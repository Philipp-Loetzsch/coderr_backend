from django.urls import path
from .views import (
    OrderListCreateView,
    OrderDetailView,
    BusinessOrderListView,
    CompletedOrdersCountView,
    InProgressOrdersCountView
)

app_name = 'orders_api'

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:id>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/business/<int:business_user_id>/', BusinessOrderListView.as_view(), name='business-order-list'),
    path('completed-order-count/<int:business_user_id>/', CompletedOrdersCountView.as_view(), name='completed-order-count'),
    path('order-count/<int:business_user_id>/', InProgressOrdersCountView.as_view(), name='inprogress-orders-count'),
]