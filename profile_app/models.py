from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
import os 
class Profile(models.Model):
    """
    Represents a user's profile, extending the base User model with
    additional information like a profile picture, location, and other details.
    It also handles the deletion of associated image files when the
    profile picture is changed or the profile is deleted.
    """
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

    __original_profile_picture = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_profile_picture = self.profile_picture.name if self.profile_picture else None

    def save(self, *args, **kwargs):
        new_picture_name = self.profile_picture.name if self.profile_picture else None
        if self.pk and new_picture_name != self.__original_profile_picture:
            if self.__original_profile_picture:
                old_picture_path = os.path.join(settings.MEDIA_ROOT, self.__original_profile_picture)
                if os.path.isfile(old_picture_path):
                    try:
                        os.remove(old_picture_path)
                    except OSError as e:
                        print(f"Error deleting old profile picture {old_picture_path}: {e}")

        super().save(*args, **kwargs)
        self.__original_profile_picture = self.profile_picture.name if self.profile_picture else None

    def delete(self, *args, **kwargs):
        if self.profile_picture:
            picture_path = os.path.join(settings.MEDIA_ROOT, self.profile_picture.name)
            if os.path.isfile(picture_path):
                try:
                    os.remove(picture_path)
                except OSError as e:
                    print(f"Error deleting profile picture {picture_path}: {e}")
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Profile of {self.user.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver to create a Profile when a new User is created,
    and to ensure the Profile is saved when an existing User is saved.
    """
    if created:
        Profile.objects.create(user=instance)
    else:
        try:
            instance.profile.save()
        except Profile.DoesNotExist:
            Profile.objects.create(user=instance)

