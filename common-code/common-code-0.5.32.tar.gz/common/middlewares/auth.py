from common.rest_extend.response import RESTResponse, Results, FORBID_CODE
from django.utils.deprecation import MiddlewareMixin
from tenant_auth.models import Tenant, TenantRole, Permission, RolePermissions

IGNORE_SOURCE = ["/"]


class AuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        path = request.path
        results = Results()
        if "login" not in path and path not in IGNORE_SOURCE:
            token = request.GET.get('token')
            if token:
                tenant = Tenant.objects.filter(token=token).first()
                authorization = self.permissions(request, tenant=tenant)
            else:
                account = request.session.get("account", None)
                if not account:
                    results.describe = "no permission!!!"
                    results.code = FORBID_CODE
                    return RESTResponse(results)
                authorization = self.permissions(request, account=account)
            if not authorization:
                results.describe = "no permission!!!"
                results.code = FORBID_CODE
                return RESTResponse(results)

    def permissions(self, request, account=None, tenant=None):

        method = request.method
        path = request.path
        if not tenant:
            tenant = Tenant.objects.filter(account=account).first()
        if tenant:
            if tenant.account == "admin":
                return True
            # permission = AuthPermission.objects.filter(action=method, source_id=path).first()
            permission = Permission.objects.filter(source_id=path).first()
            if permission:
                tenant_role = TenantRole.objects.filter(tenant_id=account).first()
                if tenant_role:
                    role_permissions = RolePermissions.objects.filter(
                        role_id=tenant_role.role_id, permission_id=permission.name
                    ).first()
                    if role_permissions:
                        return True

        return False
