from rest_framework import viewsets, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import UserProfile, ProfileType
from .serializers import ( ProfileBusinessListSerializer, ProfileCustomerListSerializer, CurrentUserProfileSerializer,)
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser

class IsAdminOrForbiddenMessage(IsAdminUser):
     # Überschreibe die Standard-Nachricht
     message = 'Aktion fehlgeschlagen: Nur Administratoren haben hier Zugriff.'

class ProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UserProfile.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'list_business':
            return ProfileBusinessListSerializer
        elif self.action == 'list_customer':
            return ProfileCustomerListSerializer
        elif self.action == 'retrieve':
            return CurrentUserProfileSerializer 
        return CurrentUserProfileSerializer
    
    def get_permissions(self):
        """
        Setzt Berechtigungen dynamisch basierend auf der Aktion.
        Beschränkt die Standard 'list'-Aktion auf Admin-Benutzer.
        """
        if self.action == 'list':
            self.permission_classes = [IsAdminOrForbiddenMessage]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='business')
    def list_business(self, request):
        list_business = UserProfile.objects.filter(profile_type=ProfileType.BUSINESS)
        page = self.paginate_queryset(list_business)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(list_business, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='customer')
    def list_customer(self, request):
        list_customer = UserProfile.objects.filter(profile_type=ProfileType.CUSTOMER)
        page = self.paginate_queryset(list_customer)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(list_customer, many=True)
        return Response(serializer.data)


class CurrentUserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = CurrentUserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.user_profile