from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from ..models import UserProfile, ProfileType
from .serializers import UserProfileSerializer
from .permissions import IsProfileOwner


class ProfilePagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size' 
    max_page_size = 50 

class UserProfileViewSet(mixins.RetrieveModelMixin, 
                         mixins.UpdateModelMixin, 
                         viewsets.GenericViewSet):
    """
    ViewSet für UserProfile: Abrufen, eigenes Aktualisieren, Listen nach Typ.
    Kein Standard 'list' oder 'create' Endpunkt.
    """
    queryset = UserProfile.objects.select_related('user').all()
    serializer_class = UserProfileSerializer
    pagination_class = ProfilePagination
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_permissions(self):
        """ Setzt zusätzliche Objekt-Berechtigung für Update/Patch. """
        if self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsProfileOwner()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='business')
    def list_business(self, request):
        """ GET /api/profile/business/ - Gibt paginierte Liste der Business-Profile zurück. """
        queryset = self.get_queryset().filter(profile_type=ProfileType.BUSINESS)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='customer')
    def list_customer(self, request):
        """ GET /api/profile/customer/ - Gibt paginierte Liste der Customer-Profile zurück. """
        queryset = self.get_queryset().filter(profile_type=ProfileType.CUSTOMER)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)