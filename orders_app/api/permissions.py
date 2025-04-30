# from rest_framework import permissions
# from profile_app.models import ProfileType, UserProfile

# class IsOrderParticipant(permissions.BasePermission):
#     """
#     Erlaubt Zugriff nur, wenn der User der Käufer ODER Verkäufer der Order ist.
#     """
#     message = "Sie haben keine Berechtigung, auf diese Bestellung zuzugreifen."

#     def has_object_permission(self, request, view, obj):
#         return obj.buyer == request.user or obj.seller == request.user

# class CanReviewOrder(permissions.BasePermission):
#     """
#     Erlaubt das Erstellen einer Bewertung nur, wenn:
#     - Der User der Käufer der Bestellung ist.
#     - Die Bestellung abgeschlossen ist.
#     - Der User diese Bestellung noch nicht bewertet hat.
#     - Der User nicht der Verkäufer ist.
#     """
#     message = "Sie können diese Bestellung nicht bewerten (Bedingungen nicht erfüllt)."

#     def has_permission(self, request, view):
#         return request.user and request.user.is_authenticated

# class IsReviewerOrAdminOrReadOnly(permissions.BasePermission):
#     """
#     Erlaubt Lesen für jeden.
#     Erlaubt Löschen/Ändern nur für den Reviewer oder Admins.
#     """
#     message = "Sie dürfen nur Ihre eigenen Bewertungen ändern/löschen."

#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         return obj.reviewer == request.user or request.user.is_staff

# class IsBusinessUser(permissions.BasePermission):
#     message = "Nur Business-Benutzer dürfen diese Aktion ausführen."
#     def has_permission(self, request, view):
#         if not request.user or not request.user.is_authenticated:
#             return False
#         try:
#             profile = request.user.userprofile
#             return profile.profile_type == ProfileType.BUSINESS
#         except UserProfile.DoesNotExist:
#             return False
#         except AttributeError:
#              print(f"FEHLER: Falscher related_name für UserProfile in IsBusinessUser verwendet!")
#              return False


# from rest_framework import permissions
# from ..models import OrderStatus, Review
# # Passe Importpfad an
# # from profil_app.models import ProfileType, UserProfile # Nur für IsBusinessUser

# class IsOrderParticipant(permissions.BasePermission):
#     message = "Sie haben keine Berechtigung, auf diese Bestellung zuzugreifen."
#     def has_object_permission(self, request, view, obj):
#         return obj.buyer == request.user or obj.seller == request.user

# class CanCreateReview(permissions.BasePermission):
#     message = "Sie können diese Bestellung nicht bewerten (Bedingungen nicht erfüllt)."
#     def has_permission(self, request, view):
#         # Basis-Check, Detail-Validierung im Serializer
#         return request.user and request.user.is_authenticated

# class IsReviewerOrAdminOrReadOnly(permissions.BasePermission):
#     message = "Sie dürfen nur Ihre eigenen Bewertungen ändern/löschen."
#     def has_object_permission(self, request, view, obj):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         return obj.reviewer == request.user or request.user.is_staff

# # Ggf. IsBusinessUser hierher kopieren oder zentral definieren
# # class IsBusinessUser(permissions.BasePermission): ...

# orders/api/permissions.py
from rest_framework import permissions

class IsCustomerUser(permissions.BasePermission):
    """
    Erlaubt Zugriff nur für Benutzer mit dem Typ 'customer'.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.type == 'customer')

class IsOrderParticipant(permissions.BasePermission):
    """
    Erlaubt Objekt-Zugriff nur für den Kunden oder den Anbieter der Bestellung.
    """
    def has_object_permission(self, request, view, obj):
        # Annahme: obj ist eine Order-Instanz
        is_customer = obj.customer == request.user
        # Prüfe, ob OfferDetail und Offer existieren, bevor auf User zugegriffen wird
        is_provider = False
        if obj.offer_detail and obj.offer_detail.offer:
            is_provider = obj.offer_detail.offer.user == request.user
        return is_customer or is_provider

class IsOrderCustomer(permissions.BasePermission):
    """
    Erlaubt Objekt-Zugriff nur für den Kunden (Besteller) der Bestellung.
    """
    def has_object_permission(self, request, view, obj):
        # Annahme: obj ist eine Order-Instanz
        return obj.customer == request.user

# AllowAny, IsAuthenticated werden direkt importiert