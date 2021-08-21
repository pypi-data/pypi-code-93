import datetime
import os
import sys

import environ
from configurations import Configuration, values

env = environ.Env()


def to_bool(value):
    return value.lower() in ["true", "yes", "y", "t", "1", "on"]


class BaseCommon(Configuration):
    p = os.environ["DJANGO_SETTINGS_MODULE"].split(".")[0]
    TESTING = "test" in sys.argv
    ROOT_URLCONF = f"{p}.base.urls"
    WSGI_APPLICATION = f"{p}.base.wsgi.application"

    TOKEN_EXPIRE_SECONDS = int(os.environ.setdefault("TOKEN_EXPIRE_SECONDS", "0"))

    EMAIL_HOST = os.environ.setdefault("EMAIL_HOST", "unset_email_host")
    EMAIL_HOST_USER = os.environ.setdefault("EMAIL_HOST_USER", "unset_email_host_user")
    EMAIL_HOST_PASSWORD = os.environ.setdefault(
        "EMAIL_HOST_PASSWORD", "unset_email_host_password"
    )
    EMAIL_PORT = os.environ.setdefault("EMAIL_PORT", "unset_email_port")
    EMAIL_USE_TLS = to_bool(os.environ.setdefault("EMAIL_USE_TLS", "False"))
    EMAIL_USE_SSL = to_bool(os.environ.setdefault("EMAIL_USE_SSL", "False"))
    DEFAULT_FROM_EMAIL = os.environ.setdefault(
        "DEFAULT_FROM_EMAIL", "noreply@email.com"
    )

    LOGIN_URL = "login"
    PASSWORD_RESET_TIMEOUT = 3600 * 6
    LOGOUT_REDIRECT_URL = "admin"

    GUNICORN_BIND = "127.0.0.1:8000"
    GUNICORN_WORKERS = 2

    INTERNAL_IPS = [
        "127.0.0.1",
    ]
    CORS_ALLOW_ALL_ORIGINS = True
    ALLOWED_HOSTS = ["*"]
    LANGUAGE_CODE = "en-us"
    TIME_ZONE = "UTC"
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True
    STATIC_URL = "/static/"
    STATIC_ROOT = "compiled_static/"
    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "django_q",
        "corsheaders",
        "tuhls_core.apps.TuhlsCoreConfig",
        "rest_framework",
        "djoser",
        "rest_framework.authtoken",
        "drf_spectacular",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [],
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

    DATABASES = {"default": env.db()}
    DATABASES["default"]["ENGINE"] = "django.db.backends.postgresql_psycopg2"

    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "verbose": {
                "format": "{levelname} {asctime} {module} {process:d} {thread:d}: {message}",
                "style": "{",
            },
            "simple": {
                "format": "{levelname} {message}",
                "style": "{",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "root": {
            "handlers": ["console"],
            "level": "WARNING",
        },
        "loggers": {
            "django": {
                "handlers": ["console"],
                "level": "INFO",
                "propagate": False,
            },
            "hoarder": {
                "handlers": ["console"],
                "level": "DEBUG",
                "propagate": False,
            },
        },
    }

    CACHES = {"default": env.cache("DEFAULT_CACHE"), "queue": env.cache("QUEUE_CACHE")}

    Q_CLUSTER = {
        "name": "DJRedis",
        "workers": 2,
        "django_redis": "queue",
        "timeout": 10,
        "max_attempts": 3,
        "retry": 120,
        "queue_limit": 10,
        "bulk": 10,
    }
    REST_FRAMEWORK = {
        "DEFAULT_RENDERER_CLASSES": ("rest_framework.renderers.JSONRenderer",),
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework_simplejwt.authentication.JWTAuthentication",
            # "rest_framework.authentication.TokenAuthentication",
            "tuhls_core.auth.ExpiringTokenAuthentication",
            "tuhls_core.auth.QueryStringBasedTokenAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.IsAuthenticated",
        ],
        "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
        "DEFAULT_THROTTLE_CLASSES": [
            "rest_framework.throttling.AnonRateThrottle",
            "rest_framework.throttling.UserRateThrottle",
        ],
        "TEST_REQUEST_DEFAULT_FORMAT": "json",
    }

    SIMPLE_JWT = {
        "AUTH_HEADER_TYPES": ("JWT",),
    }

    SPECTACULAR_SETTINGS = {
        "TITLE": "API spec",
        "DESCRIPTION": "",
        "CONTACT": {"url": "https://tuhls.com/contact"},
        "LICENSE": {"name": "TLB", "url": "https://tlb.com"},
        "VERSION": "1.7.3",
        "SERVE_INCLUDE_SCHEMA": True,
        "TAGS": [
            {"name": "Settings"},
            {"name": "User"},
            {"name": "User files"},
            {"name": "Groups"},
            {"name": "Group invitations"},
            {"name": "Templates"},
            {"name": "Applications"},
            {"name": "Database tables"},
            {"name": "Database table fields"},
            {"name": "Database table views"},
            {"name": "Database table view filters"},
            {"name": "Database table view sortings"},
            {"name": "Database table grid view"},
            {"name": "Database table rows"},
            {"name": "Database tokens"},
        ],
    }

    @classmethod
    def pre_setup(cls):
        super().pre_setup()
        if not cls.TESTING:
            cls.REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {
                "anon": "60/minute",
                "user": "120/minute",
            }


class BaseDev(BaseCommon):
    INSTALLED_APPS = BaseCommon.INSTALLED_APPS
    MIDDLEWARE = BaseCommon.MIDDLEWARE
    TEMPLATES = BaseCommon.TEMPLATES

    DEBUG = True
    SECRET_KEY = "donotuseinproduction"
    WERKZEUG_DEBUG_PIN = 1234
    TEMPLATE_DEBUG = True
    DEBUG_TOOLBAR = True
    ACCESS_TOKEN_LIFETIME = datetime.timedelta(minutes=60)
    SILENCED_SYSTEM_CHECKS = ["captcha.recaptcha_test_key_error"]

    @classmethod
    def pre_setup(cls):
        super().pre_setup()

        if cls.DEBUG_TOOLBAR:
            from debug_toolbar.settings import PANELS_DEFAULTS

            cls.DEBUG_TOOLBAR_PANELS = PANELS_DEFAULTS + [  # noqa
                "mail_panel.panels.MailToolbarPanel",
            ]
            cls.INSTALLED_APPS.append("debug_toolbar")  # noqa
            cls.INSTALLED_APPS.append("mail_panel")  # noqa

            cls.MIDDLEWARE.append(
                "debug_toolbar.middleware.DebugToolbarMiddleware"
            )  # noqa
            cls.EMAIL_BACKEND = "mail_panel.backend.MailToolbarBackend"
        cls.INSTALLED_APPS.append("django_extensions")  # noqa

        if cls.TEMPLATE_DEBUG:
            cls.TEMPLATES[0]["OPTIONS"]["debug"] = True  # noqa


class BaseProd(BaseCommon):
    DEBUG = False
    SECRET_KEY = values.Value("SECRET_KEY")
    TEMPLATE_DEBUG = False

    EMAIL_BACKEND = "django_q_email.backends.DjangoQBackend"
    DJANGO_REST_PASSWORDRESET_NO_INFORMATION_LEAKAGE = True
    DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME = 6

    @classmethod
    def pre_setup(cls):
        super().pre_setup()
        # conn_max_age is ok for single server setups. more than 1 app server on 1 postgres -> try pgbouncer
        # do not set in development -> pg connection leak
        cls.DATABASES["default"]["CONN_MAX_AGE"] = 60

    @classmethod
    def post_setup(cls):
        if env("SENTRY_DSN") != "":
            import sentry_sdk
            from sentry_sdk.integrations.django import DjangoIntegration

            sentry_sdk.init(
                dsn=env("SENTRY_DSN"),
                integrations=[DjangoIntegration()],
                send_default_pii=True,
            )

        cls.TEMPLATES = BaseCommon.TEMPLATES
        cls.TEMPLATES[0]["APP_DIRS"] = False  # noqa
        cls.TEMPLATES[0]["OPTIONS"]["loaders"] = [  # noqa
            (
                "django.template.loaders.cached.Loader",
                [
                    "django.template.loaders.filesystem.Loader",
                    "django.template.loaders.app_directories.Loader",
                ],
            ),
        ]

        cls.MIDDLEWARE = BaseCommon.MIDDLEWARE
        cls.MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa
        cls.STATICFILES_STORAGE = (
            "whitenoise.storage.CompressedManifestStaticFilesStorage"
        )
