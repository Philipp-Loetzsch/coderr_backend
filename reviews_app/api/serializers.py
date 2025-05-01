from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.validators import MinValueValidator, MaxValueValidator
from ..models import Review

CustomUser = get_user_model()

class ReviewUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name')

class ReviewDetailSerializer(serializers.ModelSerializer):
    reviewer = ReviewUserSerializer(read_only=True)
    business_user = ReviewUserSerializer(source='reviewed_user', read_only=True)

    class Meta:
        model = Review
        fields = (
            'id', 'rating', 'comment', 'reviewer', 'business_user',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'reviewer', 'business_user', 'created_at', 'updated_at')

class ReviewListSerializer(serializers.ModelSerializer):
    reviewer = serializers.IntegerField(source='reviewer.id', read_only=True)
    business_user = serializers.IntegerField(source='reviewed_user.id', read_only=True)
    description = serializers.CharField(source='comment', read_only=True)

    class Meta:
        model = Review
        fields = (
            'id', 'business_user', 'reviewer', 'rating', 'description',
            'created_at', 'updated_at'
        )
        read_only_fields = fields

class ReviewCreateSerializer(serializers.ModelSerializer):
    business_user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(type='business'),
        source='reviewed_user',
        write_only=True
    )
    rating = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    description = serializers.CharField(source='comment', required=False, allow_blank=True)

    class Meta:
        model = Review
        fields = ('business_user', 'rating', 'description')

    def create(self, validated_data):
        validated_data['reviewer'] = self.context['request'].user
        try:
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({
                "detail": "You have already reviewed this user."
            })

class ReviewUpdateSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], required=False
    )
    description = serializers.CharField(source='comment', required=False, allow_blank=True)

    class Meta:
        model = Review
        fields = ('rating', 'description')