from rest_framework import serializers
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db import transaction
from ..models import Offer, OfferDetail, OfferDetailType
from profile_app.models import UserProfile

User = get_user_model()


class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']
        read_only_fields = fields


class OfferDetailSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  
    url = serializers.HyperlinkedIdentityField(
        view_name='offers_app:offerdetail-detail',
        lookup_field='pk',
        read_only=True
    )

    class Meta:
        model = OfferDetail
        fields = [
            'id', 'url', 'title', 'revisions', 'delivery_time_in_days',
            'price', 'features', 'offer_type',
        ]


class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer für das Offer-Modell mit verschachtelter Unterstützung für OfferDetails.
    """
    # user_details = UserDetailsSerializer(source='user', read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='offers_app:offer-detail',
        lookup_field='pk',
        read_only=True
    )
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            'id', 'url', 'user', 'title', 'image',
            'description', 'details', 'min_price', 'min_delivery_time', 'created_at', 'updated_at',
        ]
        read_only_fields = ['user', 'user_details', 'created_at', 'updated_at']

    @transaction.atomic
    def create(self, validated_data):
        details_data = validated_data.pop('details', [])
        offer = Offer.objects.create(**validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer

    @transaction.atomic
    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            existing_details = {detail.id: detail for detail in instance.details.all()}

            for detail_data in details_data:
                detail_id = detail_data.get('id')
                if detail_id and detail_id in existing_details:
                    detail_instance = existing_details[detail_id]
                    for attr, value in detail_data.items():
                        setattr(detail_instance, attr, value)
                    detail_instance.save()
                else:
                    OfferDetail.objects.create(offer=instance, **detail_data)

        return instance
