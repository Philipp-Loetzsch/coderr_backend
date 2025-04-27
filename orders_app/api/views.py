from django.db.models import Q
from rest_framework import viewsets, permissions, filters, generics, status, views, mixins, serializers
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from ..models import Order, Review, OrderStatus
from .serializers import OrderSerializer, OrderStatusUpdateSerializer, ReviewSerializer
from .permissions import IsOrderParticipant, CanReviewOrder, IsReviewerOrAdminOrReadOnly

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
class OrderViewSet(viewsets.ModelViewSet):
    """
    API Endpunkt für Orders (Bestellungen).
    """
    serializer_class = OrderSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['created_at']
    ordering = ['-created_at'] 

    def get_queryset(self):
        """
        Filtert Bestellungen: User sieht nur die, bei denen er Käufer ODER Verkäufer ist.
        """
        user = self.request.user
        return Order.objects.filter(Q(buyer=user) | Q(seller=user)).select_related(
            'offer', 'offer_detail', 'buyer', 'seller'
        ).distinct()

    def get_serializer_class(self):
        """ Wählt den Serializer für Status-Updates bei PATCH. """
        if self.action == 'partial_update':
            return OrderStatusUpdateSerializer
        return OrderSerializer 

    def get_permissions(self):
        """ Setzt Objekt-Level-Permissions für Detail-Aktionen. """
        if self.action in ['retrieve', 'partial_update', 'destroy']:
            self.permission_classes = [permissions.IsAuthenticated, IsOrderParticipant]
        return super().get_permissions()

    def perform_create(self, serializer):
        """ Setzt Käufer und Verkäufer beim Erstellen einer neuen Bestellung. """
        offer = serializer.validated_data.get('offer') 
        if not offer: 
             raise serializers.ValidationError("Angebot nicht gefunden in validierten Daten.")
        serializer.save(buyer=self.request.user, seller=offer.user)

class ReviewViewSet(mixins.CreateModelMixin, 
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,   
                    mixins.DestroyModelMixin,  
                    mixins.ListModelMixin,    
                    viewsets.GenericViewSet):
    """
    API Endpunkt für Reviews (Bewertungen).
    """
    serializer_class = ReviewSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsReviewerOrAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['rating', 'order'] 
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Filtert Bewertungen: User sieht nur die, die er gegeben oder erhalten hat.
        """
        user = self.request.user
        if user.is_authenticated:
            return Review.objects.filter(Q(reviewer=user) | Q(reviewee=user)).select_related(
                'order', 'reviewer', 'reviewee' 
            ).distinct()
        return Review.objects.none() 

    def get_permissions(self):
        """ Setzt zusätzliche Berechtigung für das Erstellen. """
        if self.action == 'create':
            self.permission_classes = [permissions.IsAuthenticated, CanReviewOrder]
        return super().get_permissions()

    def perform_create(self, serializer):
        """ Setzt Reviewer und Reviewee beim Erstellen einer neuen Bewertung. """
        order = serializer.validated_data.get('order')
        if not order:
            raise serializers.ValidationError("Bestellung nicht gefunden in validierten Daten.")
        serializer.save(reviewer=self.request.user, reviewee=order.seller)

class OrderCountInProgressView(views.APIView):
    """ Gibt die Anzahl der 'in Arbeit'-Bestellungen für den eingeloggten Verkäufer zurück. """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        count = Order.objects.filter(seller=request.user, status=OrderStatus.IN_PROGRESS).count()
        return Response({'count': count}, status=status.HTTP_200_OK)


class OrderCountCompletedView(views.APIView):
    """ Gibt die Anzahl der abgeschlossenen Bestellungen für den eingeloggten Verkäufer zurück. """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        count = Order.objects.filter(seller=request.user, status=OrderStatus.COMPLETED).count()
        return Response({'count': count}, status=status.HTTP_200_OK)