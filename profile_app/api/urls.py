from django.urls import path
from .views import (
    ProfileDetailView,
    CustomerProfileListView,
    BusinessProfileListView
)

app_name = 'profile_api'

urlpatterns = [
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('profiles/customer/', CustomerProfileListView.as_view(), name='customer-profile-list'),
    path('profiles/business/', BusinessProfileListView.as_view(), name='business-profile-list'),
]