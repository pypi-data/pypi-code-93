from django.conf import settings
from django.db import connection
from django.http import Http404

from multi_tenant.utils import get_public_schema_name, get_tenant_model


class BaseTenantMiddleware:
    """
    Subclass and override this to achieve desired behaviour. Given a
    request, return the tenant to use. Tenant should be an instance
    of TENANT_MODEL. We have two parameters for backwards compatibility
    (the request would be enough).
    """

    TENANT_NOT_FOUND_EXCEPTION = Http404

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        TenantModel = get_tenant_model()

        try:
            # get_tenant must be implemented by extending this class.
            tenant = self.get_tenant(TenantModel, request)
        except TenantModel.DoesNotExist:
            raise self.TENANT_NOT_FOUND_EXCEPTION('No tenant found')

        if not isinstance(tenant, TenantModel):
            raise self.TENANT_NOT_FOUND_EXCEPTION(
                'Invalid tenant {!r}'.format(request.tenant)
            )

        request.tenant = tenant
        connection.set_tenant(request.tenant)

        # Do we have a public-specific urlconf?
        if (
            hasattr(settings, "PUBLIC_SCHEMA_URLCONF")
            and request.tenant.schema_name == get_public_schema_name()
        ):
            request.urlconf = settings.PUBLIC_SCHEMA_URLCONF

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def get_tenant(self, model, request):
        raise NotImplementedError
