from django.urls import path
from .views import ReviewListCreateView, ReviewDetailView

app_name = 'reviews_api'

urlpatterns = [
    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<int:id>/', ReviewDetailView.as_view(), name='review-detail'),
]