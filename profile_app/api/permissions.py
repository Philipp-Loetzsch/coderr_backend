from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Allows read access for everyone, but write access only for the profile owner.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsOwner(permissions.BasePermission):
    """
    Allows access only for the owner of the object.
    Assumption: The object has a user field.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
