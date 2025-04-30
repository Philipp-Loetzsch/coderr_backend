# from django.db.models import Q
# from rest_framework import viewsets, permissions, filters, generics, status, views, mixins, serializers
# from rest_framework.response import Response
# from rest_framework.pagination import PageNumberPagination
# from django_filters.rest_framework import DjangoFilterBackend
# from ..models import Order, Review, OrderStatus
# from .serializers import OrderSerializer, OrderStatusUpdateSerializer, ReviewSerializer
# from .permissions import IsOrderParticipant, CanCreateReview, IsReviewerOrAdminOrReadOnly

# class StandardResultsSetPagination(PageNumberPagination):
#     page_size = 10
#     page_size_query_param = 'page_size'
#     max_page_size = 50
# class OrderViewSet(viewsets.ModelViewSet):
#     """
#     API Endpunkt für Orders (Bestellungen).
#     """
#     serializer_class = OrderSerializer
#     pagination_class = StandardResultsSetPagination
#     permission_classes = [permissions.IsAuthenticated]
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_fields = ['status']
#     ordering_fields = ['created_at']
#     ordering = ['-created_at'] 

#     def get_queryset(self):
#         """
#         Filtert Bestellungen: User sieht nur die, bei denen er Käufer ODER Verkäufer ist.
#         """
#         user = self.request.user
#         return Order.objects.filter(Q(buyer=user) | Q(seller=user)).select_related(
#             'offer', 'offer_detail', 'buyer', 'seller'
#         ).distinct()

#     def get_serializer_class(self):
#         """ Wählt den Serializer für Status-Updates bei PATCH. """
#         if self.action == 'partial_update':
#             return OrderStatusUpdateSerializer
#         return OrderSerializer 

#     def get_permissions(self):
#         """ Setzt Objekt-Level-Permissions für Detail-Aktionen. """
#         if self.action in ['retrieve', 'partial_update', 'destroy']:
#             self.permission_classes = [permissions.IsAuthenticated, IsOrderParticipant]
#         return super().get_permissions()

#     def perform_create(self, serializer):
#         """ Setzt Käufer und Verkäufer beim Erstellen einer neuen Bestellung. """
#         offer = serializer.validated_data.get('offer') 
#         if not offer: 
#              raise serializers.ValidationError("Angebot nicht gefunden in validierten Daten.")
#         serializer.save(buyer=self.request.user, seller=offer.user)

# class ReviewViewSet(mixins.CreateModelMixin, 
#                     mixins.RetrieveModelMixin,
#                     mixins.UpdateModelMixin,   
#                     mixins.DestroyModelMixin,  
#                     mixins.ListModelMixin,    
#                     viewsets.GenericViewSet):
#     """
#     API Endpunkt für Reviews (Bewertungen).
#     """
#     serializer_class = ReviewSerializer
#     pagination_class = StandardResultsSetPagination
#     permission_classes = [IsReviewerOrAdminOrReadOnly]
#     filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
#     filterset_fields = ['rating', 'order'] 
#     ordering_fields = ['created_at', 'rating']
#     ordering = ['-created_at']

#     def get_queryset(self):
#         """
#         Filtert Bewertungen: User sieht nur die, die er gegeben oder erhalten hat.
#         """
#         user = self.request.user
#         if user.is_authenticated:
#             return Review.objects.filter(Q(reviewer=user) | Q(reviewee=user)).select_related(
#                 'order', 'reviewer', 'reviewee' 
#             ).distinct()
#         return Review.objects.none() 

#     def get_permissions(self):
#         """ Setzt zusätzliche Berechtigung für das Erstellen. """
#         if self.action == 'create':
#             self.permission_classes = [permissions.IsAuthenticated, CanCreateReview]
#         return super().get_permissions()

#     def perform_create(self, serializer):
#         """ Setzt Reviewer und Reviewee beim Erstellen einer neuen Bewertung. """
#         order = serializer.validated_data.get('order')
#         if not order:
#             raise serializers.ValidationError("Bestellung nicht gefunden in validierten Daten.")
#         serializer.save(reviewer=self.request.user, reviewee=order.seller)

# class OrderCountInProgressView(views.APIView):
#     """ Gibt die Anzahl der 'in Arbeit'-Bestellungen für den eingeloggten Verkäufer zurück. """
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         count = Order.objects.filter(seller=request.user, status=OrderStatus.IN_PROGRESS).count()
#         return Response({'count': count}, status=status.HTTP_200_OK)


# class OrderCountCompletedView(views.APIView):
#     """ Gibt die Anzahl der abgeschlossenen Bestellungen für den eingeloggten Verkäufer zurück. """
#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         count = Order.objects.filter(seller=request.user, status=OrderStatus.COMPLETED).count()
#         return Response({'count': count}, status=status.HTTP_200_OK)

# orders/api/views.py
from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Q, Count
from django.contrib.auth import get_user_model

from ..models import Order
from .serializers import (
    OrderListSerializer,
    OrderCreateSerializer,
    OrderUpdateStatusSerializer
)
from .permissions import IsCustomerUser, IsOrderParticipant, IsOrderCustomer

# Importiere OfferDetail für Zähl-View
from offers_app.models import OfferDetail

CustomUser = get_user_model()

class OrderListCreateView(generics.ListCreateAPIView):
    """
    API View zum Auflisten der eigenen Orders (GET) und Erstellen einer neuen Order (POST).
    """

    def get_serializer_class(self):
        if self.request.method == 'POST':
            # Response soll auch die volle Struktur haben
            return OrderCreateSerializer # Request braucht nur ID
        return OrderListSerializer # GET

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()] # Nur eingeloggte User sehen ihre Orders

    def get_queryset(self):
        user = self.request.user
        # Zeige Orders, bei denen der User Kunde ODER Anbieter ist
        return Order.objects.filter(
            Q(customer=user) | Q(offer_detail__offer__user=user)
        ).select_related(
            'customer', 'offer_detail', 'offer_detail__offer', 'offer_detail__offer__user'
        ).distinct() # distinct() falls Join über offer_detail zu Duplikaten führt

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save() # Ruft create im Serializer auf
        # Verwende ListSerializer für die Response
        response_serializer = OrderListSerializer(order, context=self.get_serializer_context())
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API View zum Abrufen (GET), Status-Ändern (PATCH) und Löschen (DELETE)
    einer spezifischen Order.
    """
    queryset = Order.objects.select_related(
        'customer', 'offer_detail', 'offer_detail__offer', 'offer_detail__offer__user'
    ).all()
    lookup_field = 'id' # Oder pk

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return OrderUpdateStatusSerializer
        # Für GET und DELETE Response (obwohl DELETE keine hat)
        return OrderListSerializer

    def get_permissions(self):
        # Annahme: Nur Teilnehmer dürfen Details sehen
        if self.request.method == 'GET':
            return [IsAuthenticated(), IsOrderParticipant()]
        elif self.request.method == 'PATCH':
            return [IsAuthenticated(), IsOrderParticipant()]
        elif self.request.method == 'DELETE':
            return [IsAuthenticated(), IsOrderCustomer()]
        return super().get_permissions() # Fallback


class BusinessOrderListView(generics.ListAPIView):
    """
    API View zum Auflisten aller Orders eines bestimmten Business Users.
    """
    serializer_class = OrderListSerializer
    permission_classes = [AllowAny] # Gemäß Spezifikation

    def get_queryset(self):
        business_user_id = self.kwargs.get('business_user_id')
        if not business_user_id:
            return Order.objects.none() # Keine ID, keine Orders

        return Order.objects.filter(
            offer_detail__offer__user__id=business_user_id
        ).select_related(
            'customer', 'offer_detail', 'offer_detail__offer', 'offer_detail__offer__user'
        )

class CompletedOrdersCountView(views.APIView):
    """
    API View zur Rückgabe der Anzahl abgeschlossener Bestellungen für einen Business User.
    """
    permission_classes = [AllowAny] # Gemäß Spezifikation

    def get(self, request, business_user_id, *args, **kwargs):
        try:
            # Optional: Prüfen, ob der business_user_id existiert und vom Typ 'business' ist
            # user = CustomUser.objects.get(id=business_user_id, type='business')
            count = Order.objects.filter(
                offer_detail__offer__user__id=business_user_id,
                status=Order.STATUS_COMPLETED
            ).count()
            return Response({'completed_order_count': count}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
             return Response({'error': 'Business user not found.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
             return Response({'error': 'Invalid business user ID.'}, status=status.HTTP_400_BAD_REQUEST)