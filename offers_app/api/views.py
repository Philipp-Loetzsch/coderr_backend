from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import OfferDetailSerializer, OfferSerializer, OfferDetailType
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

class OffersViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = OfferSerializer.objects.all()
    permission_classes = [AllowAny]
    
    