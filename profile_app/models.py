from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_("User")
    )
    profile_picture = models.ImageField(
        _("Profile Picture"),
        upload_to='profile_pics/',
        null=True,
        blank=True
    )
    location = models.CharField(_("Location"), max_length=100, null=True, blank=True)
    description = models.TextField(_("Description"), null=True, blank=True)
    working_hours = models.CharField(_("Working Hours"), max_length=100, null=True, blank=True)
    tel = models.CharField(_("Telephone"), max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Erstellt automatisch ein Profil, wenn ein neuer Benutzer erstellt wird.
    """
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """
    Speichert das Profil, wenn der Benutzer gespeichert wird
    (falls das Profil-Modell direkt User-Felder bearbeiten könnte -
     aktuell nicht der Fall, aber schadet nicht).
    Stellt sicher, dass das Profil existiert.
    """
    try:
        instance.profile.save()
    except Profile.DoesNotExist:
        Profile.objects.create(user=instance)