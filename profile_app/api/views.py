from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from ..models import Profile
from .serializers import (
    ExactProfileSerializer,
    CustomerProfileListSerializer,
    BusinessProfileListSerializer
)
from .permissions import IsOwnerOrReadOnly

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """Retrieves (GET) or updates (PATCH) the profile of a specific user (identified by user PK)."""
    queryset = Profile.objects.select_related('user').all()
    serializer_class = ExactProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    lookup_field = 'user__pk'
    lookup_url_kwarg = 'pk'

class CustomerProfileListView(generics.ListAPIView):
    """Lists all profiles where the user type is 'customer'."""
    serializer_class = CustomerProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.select_related('user').filter(user__type='customer')

class BusinessProfileListView(generics.ListAPIView):
    """Lists all profiles where the user type is 'business'."""
    serializer_class = BusinessProfileListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.select_related('user').filter(user__type='business')