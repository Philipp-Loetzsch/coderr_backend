from rest_framework import permissions

class IsProfileOwner(permissions.BasePermission):
    """
    Erlaubt Zugriff nur, wenn der request.user der User ist,
    zu dem das UserProfile-Objekt gehört (für Objekt-Level-Prüfung).
    """
    message = "Sie dürfen nur Ihr eigenes Profil bearbeiten."

    def has_object_permission(self, request, view, obj):
        """
        Prüft, ob der anfragende User der User ist, der im UserProfile-Objekt ('obj')
        referenziert wird. 'obj' ist hier die UserProfile-Instanz.
        """
        return obj.user == request.user