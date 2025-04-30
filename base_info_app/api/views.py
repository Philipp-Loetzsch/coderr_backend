# base_app/api/views.py
from rest_framework import views, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Avg, Count
from django.contrib.auth import get_user_model

# Importiere Modelle aus anderen Apps
# Passe Importpfade ggf. an
from reviews_app.models import Review
from offers_app.models import Offer

CustomUser = get_user_model()

class BaseInfoView(views.APIView):
    """
    API View zur Rückgabe allgemeiner Plattform-Statistiken.
    """
    permission_classes = [AllowAny] # Gemäß Spezifikation

    def get(self, request, *args, **kwargs):
        review_count = Review.objects.count()
        offer_count = Offer.objects.count()
        business_profile_count = CustomUser.objects.filter(type='business').count()

        # Berechne Durchschnittsrating und runde
        average_rating_data = Review.objects.aggregate(average=Avg('rating'))
        average_rating = average_rating_data.get('average')
        if average_rating is not None:
            rounded_average_rating = round(average_rating, 1)
        else:
            rounded_average_rating = None # Oder 0.0?

        data = {
            'review_count': review_count,
            'average_rating': rounded_average_rating,
            'business_profile_count': business_profile_count,
            'offer_count': offer_count,
        }
        return Response(data, status=status.HTTP_200_OK)