# from rest_framework import viewsets, mixins, permissions
# from rest_framework.decorators import action
# from rest_framework.response import Response
# from rest_framework.pagination import PageNumberPagination
# from ..models import UserProfile, ProfileType
# from .serializers import UserProfileSerializer
# from .permissions import IsProfileOwner


# class ProfilePagination(PageNumberPagination):
#     page_size = 10 
#     page_size_query_param = 'page_size' 
#     max_page_size = 50 

# class UserProfileViewSet(mixins.RetrieveModelMixin, 
#                          mixins.UpdateModelMixin, 
#                          viewsets.GenericViewSet):
#     """
#     ViewSet für UserProfile: Abrufen, eigenes Aktualisieren, Listen nach Typ.
#     Kein Standard 'list' oder 'create' Endpunkt.
#     """
#     queryset = UserProfile.objects.select_related('user').all()
#     serializer_class = UserProfileSerializer
#     pagination_class = ProfilePagination
#     permission_classes = [permissions.IsAuthenticated]
#     lookup_field = 'pk'

#     def get_permissions(self):
#         """ Setzt zusätzliche Objekt-Berechtigung für Update/Patch. """
#         if self.action in ['update', 'partial_update']:
#             return [permissions.IsAuthenticated(), IsProfileOwner()]
#         return super().get_permissions()

#     @action(detail=False, methods=['get'], url_path='business')
#     def list_business(self, request):
#         """ GET /api/profile/business/ - Gibt paginierte Liste der Business-Profile zurück. """
#         queryset = self.get_queryset().filter(profile_type=ProfileType.BUSINESS)
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)

#     @action(detail=False, methods=['get'], url_path='customer')
#     def list_customer(self, request):
#         """ GET /api/profile/customer/ - Gibt paginierte Liste der Customer-Profile zurück. """
#         queryset = self.get_queryset().filter(profile_type=ProfileType.CUSTOMER)
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)

from rest_framework import viewsets, mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
# Entferne Pagination-Import, wenn nirgends mehr verwendet
# from rest_framework.pagination import PageNumberPagination

# Passe Importe an
from ..models import UserProfile, ProfileType
from .serializers import UserProfileSerializer
from .permissions import IsProfileOwner

# Pagination-Klasse entfernen oder auskommentieren, wenn sie nicht mehr gebraucht wird
# class ProfilePagination(PageNumberPagination):
#     page_size = 10
#     page_size_query_param = 'page_size'
#     max_page_size = 50

class UserProfileViewSet(mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):
    """
    ViewSet für UserProfile. Behandelt Abruf, eigenes Aktualisieren, Listen nach Typ.
    Listen geben jetzt ein flaches Array zurück (keine Pagination).
    """
    queryset = UserProfile.objects.select_related('user').all()
    serializer_class = UserProfileSerializer
    # --- KEINE Pagination-Klasse hier definieren, wenn sie global deaktiviert werden soll ---
    # pagination_class = ProfilePagination # Auskommentieren oder entfernen
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def get_permissions(self):
        if self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(), IsProfileOwner()]
        return super().get_permissions()

    @action(detail=False, methods=['get'], url_path='business')
    def list_business(self, request):
        """ GET /api/profiles/business/ - Gibt *flache Liste* der Business-Profile zurück. """
        queryset = self.get_queryset().filter(profile_type=ProfileType.BUSINESS)

        # --- KEINE Pagination ---
        # page = self.paginate_queryset(queryset) # Entfernt
        # if page is not None: # Entfernt
        #     serializer = self.get_serializer(page, many=True) # Entfernt
        #     return self.get_paginated_response(serializer.data) # Entfernt
        # --------------------

        # Direktes Serialisieren des gesamten Querysets
        serializer = self.get_serializer(queryset, many=True)
        # Rückgabe der reinen Liste (Array)
        return Response(serializer.data) # <-- Gibt direkt das Array zurück

    @action(detail=False, methods=['get'], url_path='customer')
    def list_customer(self, request):
        """ GET /api/profiles/customer/ - Gibt *flache Liste* der Customer-Profile zurück. """
        queryset = self.get_queryset().filter(profile_type=ProfileType.CUSTOMER)

        # --- KEINE Pagination ---
        # page = self.paginate_queryset(queryset) # Entfernt
        # if page is not None: # Entfernt
        #     serializer = self.get_serializer(page, many=True) # Entfernt
        #     return self.get_paginated_response(serializer.data) # Entfernt
        # --------------------

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data) # <-- Gibt direkt das Array zurück

    # --- retrieve Methode (angepasst aus vorherigem Schritt) ---
    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/profile/<pk>/. Gibt das Profil als Liste mit einem Element zurück.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        # Gibt Liste mit einem Objekt zurück, damit .map() im Frontend funktioniert
        response_data = [serializer.data]
        return Response(response_data)
    # -------------------------------------------------------------

    # partial_update wird vom Mixin gehandhabt und bleibt unberührt