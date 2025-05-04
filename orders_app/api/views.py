from rest_framework import generics, status, views, permissions
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.db.models import Q, Count
from django.contrib.auth import get_user_model

from ..models import Order
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderUpdateStatusSerializer
)
from .permissions import IsCustomerUser, IsOrderParticipant, IsOrderCustomer, IsOrderProvider
from offers_app.models import OfferDetail 

CustomUser = get_user_model()

class OrderListCreateView(generics.ListCreateAPIView):
    """Lists orders relevant to the logged-in user (GET) or creates a new order (POST)."""

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            Q(customer=user) | Q(offer_detail__offer__user=user)
        ).select_related(
            'customer', 'offer_detail', 'offer_detail__offer', 'offer_detail__offer__user'
        ).distinct()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        response_serializer = OrderSerializer(order, context=self.get_serializer_context())
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieves (GET), updates status (PATCH), or deletes (DELETE) a specific order."""
    queryset = Order.objects.select_related(
        'customer', 'offer_detail', 'offer_detail__offer', 'offer_detail__offer__user'
    ).all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return OrderUpdateStatusSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated(), IsOrderParticipant()]
        elif self.request.method == 'PATCH':
            return [permissions.IsAuthenticated(), IsOrderProvider()]
        elif self.request.method == 'DELETE':
            return [permissions.IsAuthenticated(), permissions.IsAdminUser()]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        instance.refresh_from_db()
        response_serializer = OrderSerializer(instance, context=self.get_serializer_context())
        return Response(response_serializer.data)

class BusinessOrderListView(generics.ListAPIView):
    """Lists all orders associated with a specific business user (provider)."""
    serializer_class = OrderSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        business_user_id = self.kwargs.get('business_user_id')
        if not business_user_id:
            return Order.objects.none()
        return Order.objects.filter(
            offer_detail__offer__user__id=business_user_id
        ).select_related(
            'customer', 'offer_detail', 'offer_detail__offer', 'offer_detail__offer__user'
        )

class CompletedOrdersCountView(views.APIView):
    """Returns the count of completed orders for a specific business user."""
    permission_classes = [AllowAny]

    def get(self, request, business_user_id, *args, **kwargs):
        try:
            if not CustomUser.objects.filter(id=business_user_id, type='business').exists():
                 return Response({'error': 'Business user not found.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
             return Response({'error': 'Invalid business user ID.'}, status=status.HTTP_400_BAD_REQUEST)

        count = Order.objects.filter(
            offer_detail__offer__user__id=business_user_id,
            status=Order.STATUS_COMPLETED
        ).count()
        return Response({'completed_order_count': count}, status=status.HTTP_200_OK)

class InProgressOrdersCountView(views.APIView):
    """Returns the count of 'in_progress' orders for a specific business user."""
    permission_classes = [AllowAny]

    def get(self, request, business_user_id, *args, **kwargs):
        try:
            if not CustomUser.objects.filter(id=business_user_id, type='business').exists():
                 return Response({'error': 'Business user not found.'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError:
             return Response({'error': 'Invalid business user ID.'}, status=status.HTTP_400_BAD_REQUEST)

        count = Order.objects.filter(
            offer_detail__offer__user__id=business_user_id,
            status=Order.STATUS_IN_PROGRESS
        ).count()
        return Response({'order_count': count}, status=status.HTTP_200_OK)