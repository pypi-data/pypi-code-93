from django.conf import settings
from django.db import models
from tenant_schemas.models import TenantMixin


class MultiTenantMixin(TenantMixin):
    """Restrict only one inheritance level."""

    tenant = models.ForeignKey(
        settings.TENANT_MODEL,
        related_name='tenants',
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.schema_name

    def is_leading(self):
        """Check if it's main tenant."""

        return not self.tenant_id
