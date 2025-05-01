from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from offers_app.models import OfferDetail

class Order(models.Model):
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = (
        (STATUS_IN_PROGRESS, _('In Progress')),
        (STATUS_COMPLETED, _('Completed')),
        (STATUS_CANCELLED, _('Cancelled')),
    )

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders_as_customer',
        verbose_name=_("Customer")
    )
    offer_detail = models.ForeignKey(
        OfferDetail,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name=_("Offer Detail")
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_IN_PROGRESS
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} by {self.customer.username} for {self.offer_detail.title}"

    class Meta:
        ordering = ['-created_at']