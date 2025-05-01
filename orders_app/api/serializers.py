from rest_framework import serializers
from django.contrib.auth import get_user_model

from ..models import Order
from offers_app.models import OfferDetail
from offers_app.api.serializers import OfferDetailSpecificSerializer as NestedOfferDetailSerializer
from user_auth_app.api.serializers import UserDetailsSerializer as NestedCustomerSerializer # Assuming UserDetailsSerializer provides needed fields

CustomUser = get_user_model()

class OrderSerializer(serializers.ModelSerializer):
    customer_user = serializers.IntegerField(source='customer.id', read_only=True)
    business_user = serializers.SerializerMethodField()
    title = serializers.CharField(source='offer_detail.title', read_only=True)
    revisions = serializers.IntegerField(source='offer_detail.revisions', read_only=True)
    delivery_time_in_days = serializers.IntegerField(source='offer_detail.delivery_time_in_days', read_only=True)
    price = serializers.DecimalField(source='offer_detail.price', read_only=True, max_digits=10, decimal_places=2)
    features = serializers.JSONField(source='offer_detail.features', read_only=True)
    offer_type = serializers.CharField(source='offer_detail.offer_type', read_only=True)

    class Meta:
        model = Order
        fields = (
            'id', 'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at'
        )

    def get_business_user(self, obj):
        try:
            return obj.offer_detail.offer.user.id
        except AttributeError:
            return None

class OrderCreateSerializer(serializers.Serializer):
    offer_detail_id = serializers.PrimaryKeyRelatedField(
        queryset=OfferDetail.objects.all(),
        write_only=True
    )

    def create(self, validated_data):
        offer_detail = validated_data['offer_detail_id']
        customer = self.context['request'].user
        order = Order.objects.create(
            customer=customer,
            offer_detail=offer_detail,
            status=Order.STATUS_PENDING
        )
        return order

class OrderUpdateStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ('status',)