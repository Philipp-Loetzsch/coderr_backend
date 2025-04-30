# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from . import views

# app_name = 'orders_app'

# router = DefaultRouter()
# router.register(r'orders', views.OrderViewSet, basename='order')
# router.register(r'reviews', views.ReviewViewSet, basename='review')

# urlpatterns = [
#     path('', include(router.urls)),
#     path('order-count/', views.OrderCountInProgressView.as_view(), name='order-count-inprogress'),
#     path('completed-order-count/', views.OrderCountCompletedView.as_view(), name='order-count-completed'),
# ]


# from django.urls import path, include
# from rest_framework.routers import DefaultRouter
# from . import views

# app_name = 'orders_app'

# router = DefaultRouter()
# router.register(r'orders', views.OrderViewSet, basename='order')
# router.register(r'reviews', views.ReviewViewSet, basename='review')

# urlpatterns = [
#     path('', include(router.urls)),
#     path('order-count/', views.OrderCountInProgressView.as_view(), name='order-count-inprogress'),
#     path('completed-order-count/', views.OrderCountCompletedView.as_view(), name='order-count-completed'),
# ]

# orders/api/urls.py
from django.urls import path
from .views import (
    OrderListCreateView,
    OrderDetailView,
    BusinessOrderListView,
    CompletedOrdersCountView
)

app_name = 'orders_api'

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='order-list-create'),
    path('orders/<int:id>/', OrderDetailView.as_view(), name='order-detail'),
    path('orders/business/<int:business_user_id>/', BusinessOrderListView.as_view(), name='business-order-list'),
    path('completed-orders-count/<int:business_user_id>/', CompletedOrdersCountView.as_view(), name='completed-orders-count'),
]