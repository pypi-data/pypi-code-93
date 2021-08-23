import os
import socket

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Application definition

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.auth",
    "django.contrib.admin",
    "corsheaders",
    "rest_framework",
    "rest_framework_swagger",
    "server.apps.documentation",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "server.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            "server/apps/documentation/templates/"
            # Add templates here
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
DATABASES = {}

LOG_FOLDER = os.path.join(BASE_DIR, "logs", socket.gethostname())
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(name)s %(process)d %(thread)d %(message)s at %(pathname)s:%(lineno)d"
        }
    },
    "handlers": {
        "django_server": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_FOLDER, "django_server.log"),
            "formatter": "verbose",
            "level": "DEBUG",
        },
        "app_logs": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_FOLDER, "app_logs.log"),
            "formatter": "verbose",
            "level": "DEBUG",
        },
        "uncatched": {
            "class": "logging.FileHandler",
            "filename": os.path.join(LOG_FOLDER, "uncatched.log"),
            "formatter": "verbose",
            "level": "DEBUG",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": "DEBUG",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
        },
        "django.server": {"handlers": ["django_server"], "propagate": False},
        "server.apps": {"handlers": ["django_server"], "propagate": False},
    },
    "root": {"handlers": ["uncatched"], "level": "DEBUG"},
}

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_RENDERER_CLASSES": ("jaad.renderers.PrettyJsonRenderer",),
    "EXCEPTION_HANDLER": "jaad.exceptions.exception_handler",
}

# Internationalization
# https://docs.djangoproject.com/en/1.10/topics/i18n/

DEFAULT_CHARSET = "utf-8"

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = False

USE_L10N = False

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = []

# WARNING: The line below should be the last in the file
sys.path.append(os.path.join(BASE_DIR, "apps"))
