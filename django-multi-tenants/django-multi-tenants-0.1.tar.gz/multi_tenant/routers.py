from django.conf import settings
from django.db.models.base import ModelBase
from django.db.utils import load_backend

from multi_tenant.constants import ALLOWED_BACKENDS
from multi_tenant.utils import get_engine_by_database, get_tenant_model


class TenantSyncRouter(object):
    """
    A router to control which applications will be synced,
    depending if we are syncing the shared apps or the tenant apps.
    """

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        # the imports below need to be done here else django <1.5 goes crazy
        # https://code.djangoproject.com/ticket/20704
        from django.db import connection

        from multi_tenant.postgresql_backend.base import (
            DatabaseWrapper as TenantDbWrapper
        )
        from multi_tenant.utils import app_labels, get_public_schema_name

        db_engine = get_engine_by_database(db)
        if not (
            db_engine in ALLOWED_BACKENDS
            or issubclass(
                getattr(load_backend(db_engine), 'DatabaseWrapper'),
                TenantDbWrapper
            )
        ):
            return None

        if isinstance(app_label, ModelBase):
            # In django <1.7 the `app_label` parameter is actually `model`
            app_label = app_label._meta.app_label

        # TODO apps labels cache y buscar mas rapido no asi
        if connection.schema_name == get_public_schema_name():
            if app_label not in app_labels(settings.SHARED_APPS):
                return False
        else:
            if isinstance(connection.tenant, get_tenant_model()):
                if connection.tenant.is_leading():
                    if app_label not in app_labels(settings.TENANT_APPS):
                        return False
                elif app_label not in app_labels(settings.TENANT_DETAIL_APPS):
                    return False

        return None
