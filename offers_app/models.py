from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import os 
class Category(models.Model):
    name = models.CharField(_("Name"), max_length=100, unique=True)
    class Meta:
        verbose_name = _("Category")
        verbose_name_plural = _("Categories")
    def __str__(self):
        return self.name

class Offer(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='offers',
        verbose_name=_("User"),
        limit_choices_to={'type': 'business'}
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='offers',
        verbose_name=_("Category")
    )
    title = models.CharField(_("Title"), max_length=200)
    description = models.TextField(_("Description"), blank=True)
    image = models.ImageField(
        _("Image"),
        upload_to='offer_images/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    __original_image = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_image = self.image.name if self.image else None

    def save(self, *args, **kwargs):
        new_image_name = self.image.name if self.image else None
        if self.pk and new_image_name != self.__original_image:
            if self.__original_image:
                old_image_path = os.path.join(settings.MEDIA_ROOT, self.__original_image)
                if os.path.isfile(old_image_path):
                    os.remove(old_image_path)
        
        super().save(*args, **kwargs)
        self.__original_image = self.image.name if self.image else None

    def delete(self, *args, **kwargs):
        if self.image:
            image_path = os.path.join(settings.MEDIA_ROOT, self.image.name)
            if os.path.isfile(image_path):
                os.remove(image_path)
        super().delete(*args, **kwargs)
    
    
    def __str__(self):
        return self.title

class OfferDetail(models.Model):
    OFFER_TYPE_CHOICES = (
        ('basic', 'Basic'),
        ('standard', 'Standard'),
        ('premium', 'Premium'),
    )
    offer = models.ForeignKey(
        Offer,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name=_("Offer")
    )
    title = models.CharField(_("Detail Title"), max_length=100)
    price = models.DecimalField(_("Price"), max_digits=10, decimal_places=2)
    delivery_time_in_days = models.IntegerField(_("Delivery Time (days)"))
    revisions = models.IntegerField(_("Revisions"))
    features = models.JSONField(_("Features"), default=list)
    offer_type = models.CharField(
        _("Offer Type"),
        max_length=20,
        choices=OFFER_TYPE_CHOICES,
        default='basic'
    )
    def __str__(self):
        return f"{self.offer.title} - {self.title}"