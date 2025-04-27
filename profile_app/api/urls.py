# profil_app/urls.py

from django.urls import path
# Passe View-Import an
from . import views

app_name = 'profil_app'

urlpatterns = [
    path('profiles/business/',
         views.UserProfileViewSet.as_view({'get': 'list_business'}),
         name='profile-list-business'),
    path('profiles/customer/',
         views.UserProfileViewSet.as_view({'get': 'list_customer'}),
         name='profile-list-customer'),
    path('profile/<int:pk>/',
         views.UserProfileViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}),
         name='profile-detail'), 
]