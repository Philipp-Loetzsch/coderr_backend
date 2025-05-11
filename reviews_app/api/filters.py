from django_filters import rest_framework as filters
from ..models import Review

class ReviewFilter(filters.FilterSet):
    """
    FilterSet for filtering reviews by reviewed business user ID,
    reviewer user ID, and rating.

    - `business_user_id`: filters reviews where the reviewed user has this ID.
    - `reviewer_id`: filters reviews written by a specific user.
    - `rating`: filters reviews by their rating value.
    """

    business_user_id = filters.NumberFilter(field_name='reviewed_user__id')
    reviewer_id = filters.NumberFilter(field_name='reviewer__id')

    class Meta:
        model = Review
        fields = ['business_user_id', 'reviewer_id', 'rating']
