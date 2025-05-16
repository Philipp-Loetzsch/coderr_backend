from django_filters import rest_framework as filters
from rest_framework.filters import BaseFilterBackend
from ..models import Offer

class OfferFilter(filters.FilterSet):
    """
    Filters for the Offer list endpoint.

    Allows filtering by category_id, creator_id (user__id),
    min_offer_price (details__price__gte), max_offer_price (details__price__lte),
    and max_delivery_time (details__delivery_time_in_days__lte).
    """
    category_id = filters.NumberFilter(field_name='category__id')
    creator_id = filters.NumberFilter(field_name='user__id')
    min_price = filters.NumberFilter(method='filter_by_annotated_min_price')
    max_delivery_time = filters.NumberFilter(field_name='details__delivery_time_in_days', lookup_expr='lte')

    class Meta:
        model = Offer
        fields = ['creator_id', 'category_id', 'max_delivery_time']
        
    def filter_by_annotated_min_price(self, queryset, name, value):
         return queryset.filter(min_price_annotated__lte=value)
class CustomOfferOrderingFilter(BaseFilterBackend):
    """
    Custom ordering filter to handle 'min_price' and '-min_price' parameters
    by sorting on the 'min_price_annotated' or 'max_price_annotated' fields respectively.
    Handles 'updated_at' as well.
    """
    ordering_param = 'ordering'
    default_ordering = '-updated_at'

    def filter_queryset(self, request, queryset, view):
        """
        Applies ordering based on the 'ordering' query parameter.
        The queryset is expected to be annotated with 'min_price_annotated' and 'max_price_annotated'
        by the view's get_queryset method.
        """
        ordering_param_value = request.query_params.get(self.ordering_param)
        final_ordering_fields = []

        if ordering_param_value:
            orderings = [param.strip() for param in ordering_param_value.split(',')]
            for field in orderings:
                if field == 'min_price':
                    final_ordering_fields.append('min_price_annotated')
                elif field == '-min_price':
                    final_ordering_fields.append('-min_price_annotated')
                elif field == 'updated_at':
                    final_ordering_fields.append('updated_at')
                elif field == '-updated_at':
                    final_ordering_fields.append('-updated_at')

        if not final_ordering_fields:
            default = self.default_ordering
            if isinstance(default, str):
                 final_ordering_fields = [default]
            elif isinstance(default, (list, tuple)):
                 final_ordering_fields = default

        if final_ordering_fields:
            return queryset.order_by(*final_ordering_fields)

        return queryset

