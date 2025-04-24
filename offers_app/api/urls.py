from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'offers_app'
router = DefaultRouter()
router.register(r'offers', views.OfferViewSet, basename='offer')
router.register(r'offerdetails', views.OfferDetailViewSet, basename='offerdetail')
urlpatterns = [
    path('', include(router.urls)),
]

