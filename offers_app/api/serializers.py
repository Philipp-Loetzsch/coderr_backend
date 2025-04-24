from rest_framework import serializers
from django.urls import reverse
from django.contrib.auth import get_user_model
from ..models import Offer, OfferDetail, OfferDetailType
from profile_app.models import UserProfile 
from django.db import transaction

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


# class OfferSerializer(serializers.ModelSerializer):
#     user_details = UserDetailsSerializer(source='user', read_only=True)
#     url = serializers.HyperlinkedIdentityField(
#         view_name='offer-detail', 
#         lookup_field='pk',
#         read_only=True
#     )
#     details = serializers.PrimaryKeyRelatedField(
#         many=True,
#         queryset=OfferDetail.objects.all(),
#         required=False, 
#         allow_null=True 
#     )

#     class Meta:
#         model = Offer
#         fields = [
#             'id', 'url', 'user', 'user_details', 'title', 'image',
#             'description', 'details', 'min_price', 'min_delivery_time',
#             'created_at', 'updated_at',
#         ]
#         read_only_fields = ['user', 'user_details', 'created_at', 'updated_at']

#     def to_representation(self, instance):
#         """ Passt die Darstellung für Lese-Operationen an. """
#         representation = super().to_representation(instance)
#         representation['details'] = OfferDetailSerializer(
#             instance.details.all(),
#             many=True,
#             context=self.context
#         ).data
#         return representation

class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer für das Offer-Modell.
    Unterstützt das verschachtelte Lesen und Erstellen/Aktualisieren von OfferDetails.
    """
    user_details = UserDetailsSerializer(source='user', read_only=True)
    url = serializers.HyperlinkedIdentityField(
        view_name='offer-detail',
        lookup_field='pk',
        read_only=True
    )
    details = OfferDetailSerializer(many=True)
 
    class Meta:
        model = Offer
        fields = [
            'id', 'url', 'user', 'user_details', 'title', 'image',
            'description', 'details', 'min_price', 'min_delivery_time', 'created_at', 'updated_at',
        ]
        read_only_fields = ['user','user_details', 'created_at', 'updated_at']

    @transaction.atomic 
    def create(self, validated_data):
        """ Überschreibt die Standard-Create-Methode, um verschachtelte Details zu erstellen. """
        details_data = validated_data.pop('details', []) 
        offer = Offer.objects.create(**validated_data)
        created_details = []
        for detail_data in details_data:
            detail = OfferDetail.objects.create(**detail_data)
            created_details.append(detail)
        if created_details:
            offer.details.set(created_details) 
        return offer

    @transaction.atomic
    def update(self, instance, validated_data):
        """ Überschreibt die Update-Methode, um verschachtelte Details zu aktualisieren. """

        details_data = validated_data.pop('details', None)
        instance = super().update(instance, validated_data)
        if details_data is not None:
            instance.details.clear() 
            created_details = []
            for detail_data in details_data:
                detail = OfferDetail.objects.create(**detail_data)
                created_details.append(detail)

            if created_details:
                instance.details.set(created_details) 

        return instance