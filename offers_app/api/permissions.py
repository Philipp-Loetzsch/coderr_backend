# offers_app/api/permissions.py
from rest_framework import permissions

class IsBusinessUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.type == 'business')

class IsOfferOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user