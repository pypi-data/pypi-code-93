from rest_framework.permissions import BasePermission
from ..exceptions import PemissionDeniedExp


class BasePermissionPerm(BasePermission):
    code = 0

    def has_permission(self, request, view):
        try:
            if request.user.permcode % self.code == 0:
                return True
            else:
                raise PemissionDeniedExp('Permission Denied')
        except AttributeError:
            raise PemissionDeniedExp('Permission Denied')
        except ZeroDivisionError:
            raise PemissionDeniedExp('Permission Denied')
