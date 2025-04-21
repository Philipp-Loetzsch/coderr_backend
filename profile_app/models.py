from django.db import models
from django.conf import settings
from django.utils import timezone

class ProfileType(models.TextChoices):
    BUSINESS = 'business', 'business'
    CUSTOMER = 'customer', 'customer'

class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_profile",
        primary_key=True,
    )
    profile_picture = models.ImageField(
        upload_to='img/profile/',
        blank=True,
        null=True
    )
    location = models.CharField(max_length=255, blank=True)
    tel = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    working_hours = models.CharField(max_length=50, blank=True)
    profile_type = models.CharField(
        max_length=20,
        choices=ProfileType.choices,
    )
    created_at = models.DateTimeField(default=timezone.now, editable=False)

    def __str__(self):
        return f"Profile for {self.user.username}"

    @property
    def username(self):
        return self.user.username

    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

    @property
    def email(self):
        return self.user.email