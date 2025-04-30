from rest_framework import permissions

class IsCustomerUser(permissions.BasePermission):
    """
    Erlaubt Zugriff nur für Benutzer mit dem Typ 'customer'.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.type == 'customer')


class IsReviewOwner(permissions.BasePermission):
    """
    Erlaubt Objekt-Zugriff nur für den Ersteller der Bewertung.
    """
    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user
