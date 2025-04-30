# offers_app/api/views.py
from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

from ..models import Offer, OfferDetail
from .serializers import (
    OfferListSerializer,
    OfferCreateSerializer,
    OfferRetrieveSerializer,
    OfferUpdateSerializer,
    OfferResponseSerializer,
    OfferDetailSpecificSerializer
)
from .permissions import IsBusinessUser, IsOfferOwner
from .filters import OfferFilter

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class OfferListCreateView(generics.ListCreateAPIView):
    queryset = Offer.objects.select_related('user').prefetch_related('details').all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = OfferFilter
    search_fields = ['title', 'description', 'user__username', 'details__title']
    ordering_fields = ['created_at', 'details__price', 'details__delivery_time_in_days'] # Angepasst
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return OfferCreateSerializer
        return OfferListSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsBusinessUser()]
        return [AllowAny()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = OfferResponseSerializer(instance, context=self.get_serializer_context())
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OfferRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Offer.objects.select_related('user').prefetch_related('details').all()
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method == 'PATCH' or self.request.method == 'PUT':
            return OfferUpdateSerializer
        return OfferRetrieveSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated(), IsOfferOwner()]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        response_serializer = OfferResponseSerializer(instance, context=self.get_serializer_context())
        return Response(response_serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class OfferDetailSpecificView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSpecificSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'