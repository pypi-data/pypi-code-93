from django.test import Client


class TenantClient(Client):
    def __init__(self, tenant, enforce_csrf_checks=False, **defaults):
        super().__init__(enforce_csrf_checks, **defaults)
        self.tenant = tenant

    def get_tenant_header(self, **extra):
        raise NotImplementedError(
            'Subclasess must define tenant header method.'
        )

    def get(self, *args, **kwargs):
        """Construct a GET request."""
        kwargs = self.get_tenant_header(**kwargs)
        return super().get(*args, **kwargs)

    def trace(self, *args, **kwargs):
        """Construct a TRACE request."""
        kwargs = self.get_tenant_header(**kwargs)
        return super().trace(*args, **kwargs)

    def head(self, *args, **kwargs):
        """Construct a HEAD request."""
        kwargs = self.get_tenant_header(**kwargs)
        return super().head(*args, **kwargs)

    def options(self, *args, **kwargs):
        """Construct a OPTIONS request."""
        kwargs = self.get_tenant_header(**kwargs)
        return super().options(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Construct a POST request."""
        kwargs = self.get_tenant_header(**kwargs)
        return super().post(*args, **kwargs)

    def patch(self, *args, **kwargs):
        """Construct a PATCH request."""
        kwargs = self.get_tenant_header(**kwargs)
        return super().patch(*args, **kwargs)

    def put(self, *args, **kwargs):
        """Construct a PUT request."""
        kwargs = self.get_tenant_header(**kwargs)
        return super().put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Construct a DELETE request."""
        kwargs = self.get_tenant_header(**kwargs)
        return super().delete(*args, **kwargs)
