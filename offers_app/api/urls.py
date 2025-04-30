from django.urls import path
from .views import (
    OfferListCreateView,
    OfferRetrieveUpdateDestroyView,
    OfferDetailSpecificView
)

app_name = 'offers_api'

urlpatterns = [
    path('offers/', OfferListCreateView.as_view(), name='offer-list-create'),
    path('offers/<int:id>/', OfferRetrieveUpdateDestroyView.as_view(), name='offer-detail'),
    path('offerdetails/<int:id>/', OfferDetailSpecificView.as_view(), name='offerdetail-detail'),
]