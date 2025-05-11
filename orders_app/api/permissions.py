from rest_framework import permissions

class IsCustomerUser(permissions.BasePermission):
    """
    Allows access only to authenticated users with user type 'customer'.
    """

    def has_permission(self, request, view):
        """
        Return True if the user is authenticated and has type 'customer'.
        """
        return bool(request.user and request.user.is_authenticated and request.user.type == 'customer')


class IsOrderParticipant(permissions.BasePermission):
    """
    Object-level permission to allow access to either the customer who placed the order
    or the provider assigned to it via the offer.
    """

    def has_object_permission(self, request, view, obj):
        """
        Return True if the request user is either the customer of the order
        or the provider associated with the offer detail.
        """
        is_customer = obj.customer == request.user
        is_provider = False
        try:
            if obj.offer_detail and obj.offer_detail.offer:
                is_provider = obj.offer_detail.offer.user == request.user
        except AttributeError:
            pass
        return is_customer or is_provider


class IsOrderCustomer(permissions.BasePermission):
    """
    Object-level permission to allow access only to the customer who placed the order.
    """

    def has_object_permission(self, request, view, obj):
        """
        Return True if the request user is the customer of the order.
        """
        return obj.customer == request.user


class IsOrderProvider(permissions.BasePermission):
    """
    Object-level permission to allow access only to the business user who is the provider of the order.
    """

    def has_object_permission(self, request, view, obj):
        """
        Return True if the request user is the provider associated with the offer detail
        and has the user type 'business'.
        """
        is_provider = False
        try:
            if obj.offer_detail and obj.offer_detail.offer and obj.offer_detail.offer.user:
                is_provider = (obj.offer_detail.offer.user == request.user and
                               request.user.type == 'business')
        except AttributeError:
            pass
        return bool(request.user and request.user.is_authenticated and is_provider)
