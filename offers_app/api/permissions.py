from rest_framework import permissions

class IsBusinessUser(permissions.BasePermission):
    """
    Allows access only to authenticated users with type 'business'.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.type == 'business')


class IsOfferOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an offer to access or modify it.
    Assumes the model instance has a `user` attribute.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
