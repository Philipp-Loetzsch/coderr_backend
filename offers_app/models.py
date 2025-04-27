# offers_app/models.py
from django.db import models
from django.conf import settings # Für den User Foreign Key

class OfferDetailType(models.TextChoices):
    BASIC = 'basic', 'Basic'
    STANDARD = 'standard', 'Standard'
    PREMIUM = 'premium', 'Premium'
    # Füge weitere hinzu, falls nötig



class Offer(models.Model):
    """
    Repräsentiert ein Angebot eines Benutzers.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=200)
    image = models.ImageField(
        upload_to='img/offers/',
        null=True,              
        blank=True
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    min_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True, 
        blank=True
    )
    min_delivery_time = models.PositiveIntegerField(
        null=True, 
        blank=True,
        help_text="Minimale Lieferzeit in Tagen"
    )
    # details = models.ManyToManyField(
    #     OfferDetail,
    #     blank=True, 
    #     related_name='offers'
    #     )

    def __str__(self):
        return f"'{self.title}' von {self.user.username}"

    class Meta:
        ordering = ['-created_at'] 
        
        
class OfferDetail(models.Model):
    """
    Repräsentiert ein spezifisches Leistungspaket oder Detail eines Angebots.
    """
    
    offer = models.ForeignKey(Offer,
        on_delete=models.CASCADE, # <-- Sorgt für automatisches Löschen!
        related_name='details',     # Zugriff auf Details über offer.details.all()
        null=True
    )
    title = models.CharField(max_length=100) 
    revisions = models.PositiveIntegerField(default=0, help_text="Anzahl der erlaubten Revisionen")
    delivery_time_in_days = models.PositiveIntegerField(default=1, help_text="Lieferzeit in Tagen")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    features = models.JSONField(default=list, help_text="Liste der enthaltenen Features (Strings)")
    offer_type = models.CharField(max_length=20, choices=OfferDetailType.choices)

    def __str__(self):
        return f"{self.offer_id} for offer {self.title} ({self.offer_type})"