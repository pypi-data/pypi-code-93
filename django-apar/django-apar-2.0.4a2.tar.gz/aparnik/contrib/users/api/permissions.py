from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS


class IsAdminPermission(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_admin:
            return True
        return False
