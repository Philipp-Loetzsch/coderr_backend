import django_filters
from ..models import Offer

class OfferFilter(django_filters.FilterSet):
    """
    FilterSet für das Offer-Modell.
    Ermöglicht Filterung nach Ersteller, Mindestpreis und maximaler Lieferzeit.
    """
    creator_id = django_filters.NumberFilter(field_name='user__id')
    min_price = django_filters.NumberFilter(field_name='min_price', lookup_expr='gte') 
    max_delivery_time = django_filters.NumberFilter(field_name='min_delivery_time', lookup_expr='lte') # lte = Less Than or Equal

    class Meta:
        model = Offer
        fields = ['creator_id', 'min_price', 'max_delivery_time']