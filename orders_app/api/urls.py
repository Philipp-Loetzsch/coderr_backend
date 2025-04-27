from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'orders_app'

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'reviews', views.ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('order-count/', views.OrderCountInProgressView.as_view(), name='order-count-inprogress'),
    path('completed-order-count/', views.OrderCountCompletedView.as_view(), name='order-count-completed'),
]