from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.core.validators import MinValueValidator, MaxValueValidator
from ..models import Review 

CustomUser = get_user_model()

class ReviewUserSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying minimal user information (reviewer or reviewed_user)
    within a Review.
    """
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name')
        read_only_fields = fields 

class ReviewDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for the detailed representation of a Review.
    Includes nested user details for both the reviewer and the reviewed business user.
    Used for retrieving a single review.
    """
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
    """
    Serializer for representing a Review in a list view with a flat structure.
    Displays reviewer and business_user as IDs and 'comment' as 'description'.
    """
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
    """
    Serializer for creating a new Review.
    Expects 'business_user_id' (maps to reviewed_user), 'rating', and 'description' (maps to comment).
    The 'reviewer' is automatically set from the request context.
    Handles unique constraint violations for reviewer/reviewed_user pairs.
    """
    # Renamed from business_user_id to business_user to match request body
    business_user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(type='business'),
        source='reviewed_user', # Maps to the 'reviewed_user' field on the Review model
        write_only=True
    )
    rating = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    description = serializers.CharField(source='comment', required=False, allow_blank=True)

    class Meta:
        model = Review
        fields = ('business_user', 'rating', 'description') # Use 'business_user' as the input field name

    def create(self, validated_data):
        """
        Creates and returns a new Review instance, setting the reviewer
        from the request context.
        """
        validated_data['reviewer'] = self.context['request'].user
        try:
            # 'reviewed_user' is already set in validated_data due to source mapping
            return super().create(validated_data)
        except IntegrityError:
            raise serializers.ValidationError({
                "detail": "You have already reviewed this user."
            })

class ReviewUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing Review (partially).
    Allows updating 'rating' and 'description' (maps to comment).
    """
    rating = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], required=False
    )
    description = serializers.CharField(source='comment', required=False, allow_blank=True)

    class Meta:
        model = Review
        fields = ('rating', 'description')
