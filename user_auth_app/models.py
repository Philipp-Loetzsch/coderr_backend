from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Erweitertes Benutzermodell mit Unterscheidung nach Typ.
    """
    USER_TYPE_CHOICES = (
        ('customer', 'customer'),
        ('business', 'business'),
    )
    email = models.EmailField(
        _("email address"),
        unique=True,
        blank=False          
    )
    type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')

    def __str__(self):
        return self.username