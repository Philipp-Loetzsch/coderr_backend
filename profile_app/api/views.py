from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..models import Profile
from .serializers import (
    ExactProfileSerializer,
    CustomerProfileListSerializer,
    BusinessProfileListSerializer
)
try:
    from .permissions import IsOwnerOrReadOnly
except ImportError:
    from ..api.permissions import IsOwnerOrReadOnly


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    API View zum Abrufen und Aktualisieren des eigenen Profils.
    Verwendet jetzt ExactProfileSerializer.
    """
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ExactProfileSerializer 
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'user__pk'
    lookup_url_kwarg = 'pk'

class CustomerProfileListView(generics.ListAPIView):
    """
    API View zum Auflisten aller Kundenprofile ('customer').
    """
    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.select_related('user').filter(user__type='customer')

class BusinessProfileListView(generics.ListAPIView):
    """
    API View zum Auflisten aller Geschäftsprofile ('business').
    """
    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.select_related('user').filter(user__type='business')