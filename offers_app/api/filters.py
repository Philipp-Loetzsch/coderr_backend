from django_filters import rest_framework as filters
from ..models import Offer # Assuming models.py is in the parent directory

class OfferFilter(filters.FilterSet):
    """
    FilterSet for the Offer model.

    Provides filtering options for the Offer list endpoint based on:
    - category_id: Exact match for the category's ID.
    - min_price: Filters for offers where at least one of their details has a price
                 greater than or equal to the specified value.
    - max_delivery_time: Filters for offers where at least one of their details has a
                         delivery time less than or equal to the specified value.
    """
    category_id = filters.NumberFilter(field_name='category__id')
    min_price = filters.NumberFilter(field_name='details__price', lookup_expr='gte')
    max_delivery_time = filters.NumberFilter(field_name='details__delivery_time_in_days', lookup_expr='lte')

    class Meta:
        model = Offer
        fields = ['category_id', 'min_price', 'max_delivery_time']
