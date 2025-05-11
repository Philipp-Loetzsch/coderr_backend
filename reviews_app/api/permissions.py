from rest_framework import permissions

class IsCustomerUser(permissions.BasePermission):
    """
    Allows access only to authenticated users with type 'customer'.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.type == 'customer')


class IsReviewOwner(permissions.BasePermission):
    """
    Object-level permission to only allow the reviewer (creator) of the review to access or modify it.
    Assumes the Review instance has a `reviewer` attribute.
    """

    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user
