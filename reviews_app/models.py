from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    """Modell für eine Bewertung eines Business Users durch einen Customer."""
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given',
        verbose_name=_("Reviewer (Customer)"),
        limit_choices_to={'type': 'customer'} 
    )
    reviewed_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received',
        verbose_name=_("Reviewed User (Business)"),
        limit_choices_to={'type': 'business'} 
    )
    rating = models.IntegerField(
        _("Rating"),
        validators=[MinValueValidator(1), MaxValueValidator(5)] 
    )
    comment = models.TextField(_("Comment"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['reviewer', 'reviewed_user'], name='unique_review_per_user_pair')
        ]

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.reviewed_user.username} ({self.rating} stars)"