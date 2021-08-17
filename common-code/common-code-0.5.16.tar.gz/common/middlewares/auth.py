from common.rest_extend.response import RESTResponse, Results, FORBID_CODE
from django.utils.deprecation import MiddlewareMixin
from tenant_auth.models import AuthTenant, AuthTenantRole, AuthPermission, AuthRolePermissions

IGNORE_SOURCE = ["/"]


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path
        if "login" not in path and path not in IGNORE_SOURCE:
            account = request.session.get("account", None)
            results = Results()
            if not account:
                results.describe = "no permission!!!"
                results.code = FORBID_CODE
                return RESTResponse(results)
            authorization = self.permissions(request, account)
            if not authorization:
                results.describe = "no permission!!!"
                results.code = FORBID_CODE
                return RESTResponse(results)

    def permissions(self, request, account):

        method = request.method
        path = request.path
        tenant = AuthTenant.objects.filter(account=account).first()
        if tenant:
            if tenant.account == "admin":
                return True
            # permission = AuthPermission.objects.filter(action=method, source_id=path).first()
            permission = AuthPermission.objects.filter(source_id=path).first()
            if permission:
                tenant_role = AuthTenantRole.objects.filter(tenant_id=account).first()
                if tenant_role:
                    role_permissions = AuthRolePermissions.objects.filter(
                        role_id=tenant_role.role_id, permission_id=permission.name
                    ).first()
                    if role_permissions:
                        return True

        return False
