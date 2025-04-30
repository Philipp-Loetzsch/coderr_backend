# offers_app/api/filters.py
from django_filters import rest_framework as filters
from ..models import Offer

class OfferFilter(filters.FilterSet):
    category_id = filters.NumberFilter(field_name='category__id')
    min_price = filters.NumberFilter(field_name='details__price', lookup_expr='gte')
    max_delivery_time = filters.NumberFilter(field_name='details__delivery_time_in_days', lookup_expr='lte') # Geändert

    class Meta:
        model = Offer
        fields = ['category_id', 'min_price', 'max_delivery_time']