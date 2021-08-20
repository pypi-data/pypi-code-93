from rest_framework.permissions import BasePermission, SAFE_METHODS
from huscy.projects.models import Membership


class AllowAnyToCreate(BasePermission):
    def has_permission(self, request, view):
        return request.method == 'POST'


class IsProjectCoordinator(BasePermission):
    def has_permission(self, request, view):
        return Membership.objects.filter(project=view.project, user=request.user,
                                         is_coordinator=True).exists()


class IsProjectMember(BasePermission):
    def has_permission(self, request, view):
        return Membership.objects.filter(project=view.project, user=request.user).exists()


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
