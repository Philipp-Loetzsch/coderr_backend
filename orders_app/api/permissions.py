from rest_framework import permissions

class IsCustomerUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.type == 'customer')

class IsOrderParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        is_customer = obj.customer == request.user
        is_provider = False
        try:
            if obj.offer_detail and obj.offer_detail.offer:
                is_provider = obj.offer_detail.offer.user == request.user
        except AttributeError:
            pass
        return is_customer or is_provider

class IsOrderCustomer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
         return obj.customer == request.user

class IsOrderProvider(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
         is_provider = False
         try:
             if obj.offer_detail and obj.offer_detail.offer and obj.offer_detail.offer.user:
                 is_provider = (obj.offer_detail.offer.user == request.user and
                                request.user.type == 'business')
         except AttributeError:
             pass
         return bool(request.user and request.user.is_authenticated and is_provider)