from rest_framework import permissions
from profile_app.models import UserProfile, ProfileType 

class IsBusinessUser(permissions.BasePermission):
    """
    Erlaubt Zugriff nur für eingeloggte Benutzer mit dem Profiltyp 'Business'.
    """
    message = "Nur Business-Benutzer dürfen diese Aktion ausführen."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            profile = request.user.user_profile 
            return profile.profile_type == ProfileType.BUSINESS
        except UserProfile.DoesNotExist:
            return False
        except AttributeError:
             print(f"FEHLER: Falscher related_name ('userprofile'?) für UserProfile in IsBusinessUser verwendet!")
             return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Erlaubt Lesezugriff für jeden Request, aber Schreibzugriff
    (Ändern, Löschen) nur für den Eigentümer des Objekts.
    """
    message = "Du darfst nur deine eigenen Objekte bearbeiten oder löschen."

    def has_object_permission(self, request, view, obj):
        """
        Wird nur für Detail-Views aufgerufen (z.B. /offers/{id}/).
        Prüft die Berechtigung für ein spezifisches Objekt 'obj'.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user