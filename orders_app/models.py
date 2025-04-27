from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

try:
    from offers_app.models import Offer, OfferDetail
except ImportError:
    raise ImportError("Stelle sicher, dass offers_app mit Offer und OfferDetail existiert.")

class OrderStatus(models.TextChoices):
    """ Status einer Bestellung """
    PENDING = 'pending', 'Ausstehend'
    IN_PROGRESS = 'in_progress', 'In Arbeit'
    COMPLETED = 'completed', 'Abgeschlossen'
    CANCELLED = 'cancelled', 'Storniert'

class Order(models.Model):
    """ Repräsentiert eine Bestellung eines Angebots-Pakets. """
    offer = models.ForeignKey(
        Offer,
        related_name='orders',
        on_delete=models.SET_NULL, 
        null=True 
    )
    offer_detail = models.ForeignKey(
        OfferDetail,
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True 
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='orders_bought',
        on_delete=models.CASCADE 
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='orders_sold',
        on_delete=models.CASCADE
    )
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        offer_title = self.offer.title if self.offer else "Gelöschtes Angebot"
        detail_title = self.offer_detail.title if self.offer_detail else "Gelöschtes Detail"
        return f"Bestellung #{self.id}: '{detail_title}' von '{offer_title}' (Käufer: {self.buyer.username})"

class Review(models.Model):
    """ Repräsentiert eine Bewertung für eine abgeschlossene Bestellung. """
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='review'
    )

    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='reviews_given', 
        on_delete=models.CASCADE 
    )
    reviewee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='reviews_received', 
        on_delete=models.CASCADE
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        

    def __str__(self):
        return f"Bewertung für Bestellung #{self.order_id} von {self.reviewer.username}"