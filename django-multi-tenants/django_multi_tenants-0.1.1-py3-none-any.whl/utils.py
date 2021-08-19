from django.conf import settings
from tenant_schemas.utils import *  # noqa


def get_engine_by_database(database):
    return settings.DATABASES[database]['ENGINE']
