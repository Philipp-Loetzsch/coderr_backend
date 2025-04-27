from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import Order, Review, OrderStatus

try:
    from offers_app.models import Offer, OfferDetail
    from offers_app.api.serializers import OfferDetailSerializer
except ImportError:
    raise ImportError("Stelle sicher, dass offers_app mit Modellen/Serializern existiert.")

User = get_user_model()


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer für das Order-Modell.
    Behandelt Lesen (mit Details), Erstellen und Validierung.
    """
    offer_detail_info = OfferDetailSerializer(source='offer_detail', read_only=True)
    offer_title = serializers.CharField(source='offer.title', read_only=True)
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    offer = serializers.PrimaryKeyRelatedField(queryset=Offer.objects.all(), write_only=True)
    offer_detail = serializers.PrimaryKeyRelatedField(queryset=OfferDetail.objects.all(), write_only=True)
    status = serializers.CharField(read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'offer', 
            'offer_detail', 
            'buyer', 
            'seller', 
            'status',
            'created_at',
            'updated_at',
            'offer_detail_info',
            'offer_title', 
            'buyer_username',
            'seller_username', 
        ]
        read_only_fields = ['id', 'buyer', 'seller', 'status', 'created_at', 'updated_at']

    def validate(self, data):
        """ Zusätzliche Validierungen beim Erstellen einer Order. """
        offer = data.get('offer')
        offer_detail = data.get('offer_detail')
        request = self.context.get('request') 
        user = request.user if request else None

        if not offer or not offer_detail:
            raise serializers.ValidationError("Angebot und Angebotsdetail müssen angegeben werden.")

        if offer_detail not in offer.details.all():
            raise serializers.ValidationError("Das ausgewählte Detail gehört nicht zum angegebenen Angebot.")

        if offer.user == user:
            raise serializers.ValidationError("Sie können keine Bestellung für Ihr eigenes Angebot aufgeben.")
        return data

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Sehr einfacher Serializer, erlaubt nur die Änderung des Status-Feldes.
    Wird für PATCH /api/orders/{id}/ verwendet.
    """
    class Meta:
        model = Order
        fields = ['status']


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer für das Review-Modell.
    Behandelt Lesen und Erstellen.
    """
    reviewer_username = serializers.CharField(source='reviewer.username', read_only=True)
    reviewee_username = serializers.CharField(source='reviewee.username', read_only=True)
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())

    class Meta:
        model = Review
        fields = [
            'id', 'order', 'reviewer', 'reviewee', 'rating', 'comment', 'created_at',
            'reviewer_username', 'reviewee_username' 
        ]
        read_only_fields = ['id', 'reviewer', 'reviewee', 'created_at', 'reviewer_username', 'reviewee_username']

    def validate(self, data):
        """ Validierungen beim Erstellen einer Bewertung. """
        order = data.get('order')
        request = self.context.get('request')
        user = request.user if request else None

        if not order:
            raise serializers.ValidationError("Bestellung muss angegeben werden.")
        if order.buyer != user:
            raise serializers.ValidationError("Sie können nur Bestellungen bewerten, die Sie getätigt haben.")
        if order.seller == user:
             raise serializers.ValidationError("Sie können Ihr eigenes Angebot/Ihre eigene Dienstleistung nicht bewerten.")
        if order.status != OrderStatus.COMPLETED:
            raise serializers.ValidationError("Bewertungen können nur für abgeschlossene Bestellungen abgegeben werden.")
        if Review.objects.filter(order=order).exists():
            raise serializers.ValidationError("Für diese Bestellung wurde bereits eine Bewertung abgegeben.")
        return data