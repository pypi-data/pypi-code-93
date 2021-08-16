from .base import BasePermissionPerm


class AllowAnyPerm(BasePermissionPerm):
    code = 1

    def has_permission(self, request, view):
        return True


class IsAdminUserPerm(BasePermissionPerm):
    code = 2

    def has_permission(self, request, view):
        request.user.is_admin = super().has_permission(request, view)
        return request.user.is_admin


class IsAuthenticatedPerm(BasePermissionPerm):
    code = 3
