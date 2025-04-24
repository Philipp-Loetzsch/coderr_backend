from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.pagination import PageNumberPagination


from ..models import Offer, OfferDetail
from .serializers import OfferSerializer, OfferDetailSerializer
from .filters import OfferFilter
from .permissions import IsBusinessUser, IsOwnerOrReadOnly


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size'
    max_page_size = 50 
class OfferViewSet(viewsets.ModelViewSet):
    """
    API Endpunkt für Offers (Angebote).
    Bietet LIST, CREATE, RETRIEVE, UPDATE, PARTIAL_UPDATE, DESTROY Aktionen.
    Mit Filterung, Suche, Sortierung und benutzerdefinierten Berechtigungen.
    """
  
    queryset = Offer.objects.select_related('user').prefetch_related('details').all()
    serializer_class = OfferSerializer
    pagination_class = StandardResultsSetPagination 

   
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter 
    search_fields = ['title', 'description'] 
    ordering_fields = ['created_at', 'min_price']
    ordering = ['-created_at'] 
    permission_classes = [IsOwnerOrReadOnly]

    def get_permissions(self):
        """
        Setzt zusätzliche Berechtigungen für bestimmte Aktionen.
        """
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsBusinessUser()]
        return super().get_permissions()

    def perform_create(self, serializer):
        """
        Setzt den 'user' des Angebots automatisch auf den aktuell
        eingeloggten Benutzer, wenn ein neues Angebot erstellt wird.
        """
        serializer.save(user=self.request.user)

class OfferDetailViewSet(viewsets.ModelViewSet):
    """
    API Endpunkt für Offer Details (Merkmale).
    Beispiel: Lesen für alle erlaubt, Schreiben nur für Admins.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.IsAdminUser | permissions.DjangoModelPermissionsOrAnonReadOnly]