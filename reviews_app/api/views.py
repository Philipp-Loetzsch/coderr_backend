from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from ..models import Review
from .serializers import (
    ReviewListSerializer,
    ReviewCreateSerializer,
    ReviewDetailSerializer,
    ReviewUpdateSerializer
)
from .permissions import IsCustomerUser, IsReviewOwner
from .filters import ReviewFilter

class ReviewListCreateView(generics.ListCreateAPIView):
    """
    API View zum Auflisten (GET) und Erstellen (POST) von Reviews.
    """
    queryset = Review.objects.select_related('reviewer', 'reviewed_user').all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['created_at', 'rating']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReviewCreateSerializer
        return ReviewListSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated(), IsCustomerUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = ReviewDetailSerializer(instance, context=self.get_serializer_context())
        headers = self.get_success_headers(response_serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API View zum Abrufen (GET), Aktualisieren (PATCH) und Löschen (DELETE)
    einer spezifischen Review.
    """
    queryset = Review.objects.select_related('reviewer', 'reviewed_user').all()
    lookup_field = 'id' 

    def get_serializer_class(self):
        if self.request.method == 'PATCH' or self.request.method == 'PUT':
            return ReviewUpdateSerializer
        return ReviewDetailSerializer 

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsReviewOwner()]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        response_serializer = ReviewDetailSerializer(instance, context=self.get_serializer_context())
        return Response(response_serializer.data)

    def perform_update(self, serializer):
        serializer.save()