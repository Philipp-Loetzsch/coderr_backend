from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Erlaubt Lesezugriff für jeden, aber Schreibzugriff nur für den Profilbesitzer.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user
class IsOwner(permissions.BasePermission):
     """
     Erlaubt Zugriff nur für den Besitzer des Objekts.
     Annahme: Das Objekt hat ein `user`-Feld.
     """
     def has_object_permission(self, request, view, obj):
         return obj.user == request.user