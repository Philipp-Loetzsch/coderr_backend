from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Min
from ..models import Offer, OfferDetail, Category


class OfferListUserDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying basic user information related to an offer.
    """
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'username')
        read_only_fields = fields 


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category objects.
    """
    class Meta:
        model = Category
        fields = ('id', 'name')


class SimpleOfferDetailSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for OfferDetail, including only ID and URL.
    """
    url = serializers.HyperlinkedIdentityField(
        view_name='offers_api:offerdetail-detail',
        lookup_field='id'
    )

    class Meta:
        model = OfferDetail
        fields = ('id', 'url')


class OfferDetailSpecificSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed view of an OfferDetail.
    """
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
    """
    Serializer for creating new OfferDetail entries.
    """
    delivery_time_in_days = serializers.IntegerField()
    price = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = OfferDetail
        fields = (
            'title',
            'price',
            'delivery_time_in_days',
            'revisions',
            'features',
            'offer_type'
        )


class OfferDetailUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing OfferDetail entries.
    """
    id = serializers.IntegerField()
    title = serializers.CharField(required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    delivery_time_in_days = serializers.IntegerField(required=False)
    revisions = serializers.IntegerField(required=False)
    features = serializers.JSONField(required=False)
    offer_type = serializers.ChoiceField(choices=OfferDetail.OFFER_TYPE_CHOICES, required=False)

    class Meta:
        model = OfferDetail
        fields = (
            'id', 'title', 'price', 'delivery_time_in_days',
            'revisions', 'features', 'offer_type'
        )


class OfferListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing offers with minimal related detail info,
    user details, and calculated min price and delivery time.
    """
    user = serializers.IntegerField(source='user.id', read_only=True)
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
        """
        Returns the minimum price from related OfferDetail entries.
        """
        min_data = obj.details.aggregate(min_p=Min('price'))
        return min_data.get('min_p')

    def get_min_delivery_time(self, obj):
        """
        Returns the minimum delivery time from related OfferDetail entries.
        """
        min_data = obj.details.aggregate(min_dt=Min('delivery_time_in_days'))
        return min_data.get('min_dt')


class OfferCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating Offer with nested OfferDetails.
    """
    details = OfferDetailCreateSerializer(many=True, required=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Offer
        fields = ('title', 'image', 'description', 'details')

    def create(self, validated_data):
        """
        Creates an offer along with associated offer details.
        """
        details_data = validated_data.pop('details')
        user = self.context['request'].user
        offer = Offer.objects.create(user=user, **validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer


class OfferResponseSerializer(serializers.ModelSerializer):
    """
    Serializer used to return full details of an offer after creation or fetch.
    """
    details = OfferDetailSpecificSerializer(many=True, read_only=True) 
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Offer
        fields = ('id', 'title', 'image', 'description', 'details')


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving a single offer with related info and calculated fields.
    """
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
        """
        Returns the minimum price of all OfferDetails.
        """
        min_data = obj.details.aggregate(min_p=Min('price'))
        return min_data.get('min_p')

    def get_min_delivery_time(self, obj):
        """
        Returns the minimum delivery time of all OfferDetails.
        """
        min_data = obj.details.aggregate(min_dt=Min('delivery_time_in_days'))
        return min_data.get('min_dt')


class OfferUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an Offer and its nested OfferDetails.
    """
    details = OfferDetailUpdateSerializer(many=True, required=False)
    title = serializers.CharField(required=False)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Offer
        fields = ('title', 'image','details')

    def update(self, instance, validated_data):
        """
        Updates the offer and its nested details if provided.
        """
        details_data = validated_data.pop('details', None)
        instance.title = validated_data.get('title', instance.title)
        if 'image' in validated_data:
            instance.image = validated_data.get('image', instance.image)
        
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

        instance = super().update(instance, validated_data)
        return instance
