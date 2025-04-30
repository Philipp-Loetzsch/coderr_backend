# offers_app/api/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Min
from ..models import Offer, OfferDetail, Category

class OfferListUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'username')

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name')

class SimpleOfferDetailSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    class Meta:
        model = OfferDetail
        fields = ('id', 'url')
    def get_url(self, obj):
        return f"/offerdetails/{obj.id}/"

class OfferDetailSpecificSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = (
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
        )

class OfferDetailCreateSerializer(serializers.ModelSerializer):
    delivery_time_in_days = serializers.IntegerField() 
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        model = OfferDetail
        fields = (
            'title',
            'description',
            'price',
            'delivery_time_in_days',
            'revisions',
            'features',
            'offer_type'
        )

class OfferDetailUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    delivery_time_in_days = serializers.IntegerField(required=False) # Uses model field name now
    revisions = serializers.IntegerField(required=False)
    features = serializers.JSONField(required=False)
    offer_type = serializers.ChoiceField(choices=OfferDetail.OFFER_TYPE_CHOICES, required=False)
    class Meta:
        model = OfferDetail
        fields = (
            'id', 'title', 'description', 'price', 'delivery_time_in_days',
            'revisions', 'features', 'offer_type'
        )

class OfferListSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    details = SimpleOfferDetailSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = OfferListUserDetailsSerializer(source='user', read_only=True)
    image = serializers.ImageField(read_only=True)
    class Meta:
        model = Offer
        fields = (
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time', 'user_details'
        )
    def get_min_price(self, obj):
        min_data = obj.details.aggregate(min_p=Min('price'))
        return min_data.get('min_p')
    def get_min_delivery_time(self, obj):
        min_data = obj.details.aggregate(min_dt=Min('delivery_time_in_days'))
        return min_data.get('min_dt')

class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailCreateSerializer(many=True, required=True)
    image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = Offer
        fields = ('title', 'image', 'description', 'details')
    def create(self, validated_data):
        details_data = validated_data.pop('details')
        user = self.context['request'].user
        offer = Offer.objects.create(user=user, **validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

class OfferResponseSerializer(serializers.ModelSerializer):
     user = OfferListUserDetailsSerializer(read_only=True)
     details = OfferDetailSpecificSerializer(many=True, read_only=True)
     image = serializers.ImageField(read_only=True)
     created_at = serializers.DateTimeField(read_only=True)
     updated_at = serializers.DateTimeField(read_only=True)
     class Meta:
        model = Offer
        fields = ('id', 'user', 'title', 'image', 'description',
                  'created_at', 'updated_at', 'details')

class OfferRetrieveSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    details = SimpleOfferDetailSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    image = serializers.ImageField(read_only=True)
    class Meta:
        model = Offer
        fields = (
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time'
        )
    def get_min_price(self, obj):
        min_data = obj.details.aggregate(min_p=Min('price'))
        return min_data.get('min_p')
    def get_min_delivery_time(self, obj):
        min_data = obj.details.aggregate(min_dt=Min('delivery_time_in_days'))
        return min_data.get('min_dt')

class OfferUpdateSerializer(serializers.ModelSerializer):
    details = OfferDetailUpdateSerializer(many=True, required=False)
    title = serializers.CharField(required=False)
    class Meta:
        model = Offer
        fields = ('title', 'details')
    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        if details_data is not None:
            detail_mapping = {detail.id: detail for detail in instance.details.all()}
            for detail_data in details_data:
                detail_id = detail_data.get('id')
                detail_instance = detail_mapping.get(detail_id)
                if detail_instance:
                    detail_serializer = OfferDetailUpdateSerializer(
                        instance=detail_instance, data=detail_data, partial=True
                    )
                    if detail_serializer.is_valid(raise_exception=True):
                         detail_serializer.save()
        return instance