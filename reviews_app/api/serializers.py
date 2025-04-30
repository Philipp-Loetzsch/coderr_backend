from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.validators import MinValueValidator, MaxValueValidator

from ..models import Review

CustomUser = get_user_model()
class ReviewUserSerializer(serializers.ModelSerializer):
    """Serializer für die Anzeige von User-Infos innerhalb einer Review."""
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name')


class ReviewDetailSerializer(serializers.ModelSerializer):
    """Serializer für Responses (GET single, POST, PATCH)."""
    reviewer = ReviewUserSerializer(read_only=True)
    business_user = ReviewUserSerializer(source='reviewed_user', read_only=True)

    class Meta:
        model = Review
        fields = (
            'id', 'rating', 'comment', 'reviewer', 'business_user',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'reviewer', 'business_user', 'created_at', 'updated_at')


class ReviewListSerializer(ReviewDetailSerializer):
    """Serializer für die Review-Liste (GET /reviews/). Identisch zu Detail."""
    pass


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer zur Erstellung einer Review."""
    business_user_id = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(type='business'),
        source='reviewed_user',
        write_only=True
    )
    rating = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        model = Review
        fields = ('business_user_id', 'rating', 'comment')

    def create(self, validated_data):
        validated_data['reviewer'] = self.context['request'].user
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({
                "detail": "You have already reviewed this user."
            })


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializer zur Aktualisierung einer Review (PATCH)."""
    rating = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], required=False
    )
    comment = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Review
        fields = ('rating', 'comment')