from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Min, Max
from ..models import Offer, OfferDetail, Category

CustomUser = get_user_model()

class OfferListUserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username')
        read_only_fields = fields

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        for field_name in ['first_name', 'last_name']:
            if field_name in representation and representation[field_name] is None:
                representation[field_name] = ""
        return representation

class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(allow_null=True)
    class Meta:
        model = Category
        fields = ('id', 'name')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if representation.get('name') is None:
            representation['name'] = ""
        return representation

class SimpleOfferDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
         view_name='offers_api:offerdetail-detail',
         lookup_field='id'
     )
    class Meta:
         model = OfferDetail
         fields = ('id', 'url')

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
            'price',
            'delivery_time_in_days',
            'revisions',
            'features',
            'offer_type'
        )

class OfferDetailUpdateSerializer(serializers.ModelSerializer):
    offer_type = serializers.ChoiceField(choices=OfferDetail.OFFER_TYPE_CHOICES, required=True)
    title = serializers.CharField(required=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    delivery_time_in_days = serializers.IntegerField(required=False)
    revisions = serializers.IntegerField(required=False)
    features = serializers.JSONField(required=False)

    class Meta:
        model = OfferDetail
        fields = (
            'offer_type', 'title', 'price', 'delivery_time_in_days',
            'revisions', 'features'
        )

class OfferListSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='user.id', read_only=True)
    details = SimpleOfferDetailSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = OfferListUserDetailsSerializer(source='user', read_only=True)
    image = serializers.ImageField(read_only=True, allow_null=True)
    description = serializers.CharField(read_only=True, allow_blank=True, allow_null=True)

    class Meta:
        model = Offer
        fields = (
            'id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time', 'user_details'
        )

    def get_min_price(self, obj):
        if obj.details.exists():
            min_data = obj.details.aggregate(min_p=Min('price'))
            return min_data.get('min_p')
        return None
    def get_min_delivery_time(self, obj):
        if obj.details.exists():
            min_data = obj.details.aggregate(min_dt=Min('delivery_time_in_days'))
            return min_data.get('min_dt')
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        fields_to_empty_string_if_null = ['image', 'description']
        for field_name in fields_to_empty_string_if_null:
            if field_name in representation and representation[field_name] is None:
                representation[field_name] = ""
        if representation.get('min_price') is None:
            representation['min_price'] = ""
        if representation.get('min_delivery_time') is None:
            representation['min_delivery_time'] = ""
        return representation

class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailCreateSerializer(many=True, required=True)
    image = serializers.ImageField(required=False, allow_null=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Offer
        fields = ('title', 'image', 'description', 'category', 'details')

    def create(self, validated_data):
        details_data = validated_data.pop('details')
        user = self.context['request'].user
        offer = Offer.objects.create(user=user, **validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

class OfferResponseSerializer(serializers.ModelSerializer):
     details = OfferDetailSpecificSerializer(many=True, read_only=True)
     image = serializers.ImageField(read_only=True, allow_null=True)
     category = CategorySerializer(read_only=True, allow_null=True)
     description = serializers.CharField(read_only=True, allow_blank=True, allow_null=True)

     class Meta:
        model = Offer
        fields = ('id', 'title', 'image', 'description', 'category', 'details')

     def to_representation(self, instance):
        representation = super().to_representation(instance)
        fields_to_empty_string_if_null = ['image', 'description']
        if representation.get('category') is None:
            pass
        for field_name in fields_to_empty_string_if_null:
            if field_name in representation and representation[field_name] is None:
                representation[field_name] = ""
        return representation

class OfferRetrieveSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    details = SimpleOfferDetailSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    image = serializers.ImageField(read_only=True, allow_null=True)
    category = CategorySerializer(read_only=True, allow_null=True)
    description = serializers.CharField(read_only=True, allow_blank=True, allow_null=True)

    class Meta:
        model = Offer
        fields = (
            'id', 'user', 'title', 'image', 'description', 'category', 'created_at', 'updated_at',
            'details', 'min_price', 'min_delivery_time',
        )

    def get_min_price(self, obj):
        if obj.details.exists():
            min_data = obj.details.aggregate(min_p=Min('price'))
            return min_data.get('min_p')
        return None
    def get_min_delivery_time(self, obj):
        if obj.details.exists():
            min_data = obj.details.aggregate(min_dt=Min('delivery_time_in_days'))
            return min_data.get('min_dt')
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        fields_to_empty_string_if_null = ['image', 'description']
        if representation.get('category') is None:
            pass
        for field_name in fields_to_empty_string_if_null:
            if field_name in representation and representation[field_name] is None:
                representation[field_name] = ""
        if representation.get('min_price') is None:
            representation['min_price'] = ""
        if representation.get('min_delivery_time') is None:
            representation['min_delivery_time'] = ""
        return representation

class OfferUpdateSerializer(serializers.ModelSerializer):
    details = OfferDetailUpdateSerializer(many=True, required=False)
    title = serializers.CharField(required=False)
    image = serializers.ImageField(required=False, allow_null=True)
    description = serializers.CharField(required=False, allow_blank=True)
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )
    class Meta:
        model = Offer
        fields = ('title', 'image', 'description', 'category', 'details')

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)

        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.category = validated_data.get('category', instance.category)
        if 'image' in validated_data:
            instance.image = validated_data.get('image')
        instance.save()

        if details_data is not None:
            existing_details_map = {detail.offer_type: detail for detail in instance.details.all()}

            for detail_data_item in details_data:
                item_offer_type = detail_data_item.get('offer_type')
                if not item_offer_type:
                    continue

                detail_instance = existing_details_map.get(item_offer_type)

                if detail_instance:
                    update_payload = {k: v for k, v in detail_data_item.items() if k != 'offer_type'}

                    detail_serializer = OfferDetailUpdateSerializer(
                        instance=detail_instance, data=update_payload, partial=True
                    )
                    if detail_serializer.is_valid(raise_exception=True):
                        detail_serializer.save()
        return instance
