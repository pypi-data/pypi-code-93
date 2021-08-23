"""
This Django settings app is for use when the host codebase does not
use Django itself. It gets used by the scheduler automatically,
and it requires only the environment variable DATABASE_URL.
"""
import os

import dj_database_url

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "The workflows scheduler requires environment variable DATABASE_URL "
        "be populated with a PostgreSQL database connection string like "
        '"postgres://localhost/workflows". Alternatively you can integrate '
        'workflows with an existing Django installation by adding "workflows"'
        "to your INSTALLED_APPS list."
    )
DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = ["workflows"]

SECRET_KEY = "not used by workflows"

TIME_ZONE = "UTC"
USE_TZ = True
