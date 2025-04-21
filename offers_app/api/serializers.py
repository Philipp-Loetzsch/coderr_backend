from rest_framework import serializers
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Offer, OfferDetail, OfferDetailType
from profile_app.models import UserProfile 

User = get_user_model()

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']
        read_only_fields = fields

class OfferDetailSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='offerdetail-detail', 
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
    user_details = UserDetailsSerializer(source='user', read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='offer-detail', 
        lookup_field='pk',
        read_only=True
    )
    details = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=OfferDetail.objects.all(),
        required=False, 
        allow_null=True 
    )

    class Meta:
        model = Offer
        fields = [
            'id', 'url', 'user', 'user_details', 'title', 'image',
            'description', 'details', 'min_price', 'min_delivery_time',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['user', 'user_details', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """ Passt die Darstellung für Lese-Operationen an. """
        representation = super().to_representation(instance)
        representation['details'] = OfferDetailSerializer(
            instance.details.all(),
            many=True,
            context=self.context
        ).data
        return representation