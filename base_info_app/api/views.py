from rest_framework import views, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Avg, Count
from django.contrib.auth import get_user_model
from reviews_app.models import Review
from offers_app.models import Offer

CustomUser = get_user_model()

class BaseInfoView(views.APIView):
    """Provides basic aggregated platform statistics."""
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        review_count = Review.objects.count()
        offer_count = Offer.objects.count()
        business_profile_count = CustomUser.objects.filter(type='business').count()

        average_rating_data = Review.objects.aggregate(average=Avg('rating'))
        average_rating = average_rating_data.get('average')
        if average_rating is not None:
            rounded_average_rating = round(average_rating, 1)
        else:
            rounded_average_rating = None

        data = {
            'review_count': review_count,
            'average_rating': rounded_average_rating,
            'business_profile_count': business_profile_count,
            'offer_count': offer_count,
        }
        return Response(data, status=status.HTTP_200_OK)