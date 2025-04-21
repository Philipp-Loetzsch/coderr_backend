from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views 

router = DefaultRouter()
router.register(r'profiles', views.ProfileViewSet, basename='profile')

urlpatterns = [
    path('profile/', views.CurrentUserProfileView.as_view(), name='current-user-profile'),
    path('', include(router.urls)),
]