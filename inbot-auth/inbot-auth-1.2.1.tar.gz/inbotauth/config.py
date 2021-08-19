import os
import distutils.util
from inbotauth.user import put_user


class BaseConfig:
    # Application Settings
    SECRET_KEY = os.environ.get('FLASK_OIDC_SECRET_KEY', 'base-dap-config-secret-key')
    WHITELISTED_ENDPOINTS = os.environ.get('FLASK_OIDC_WHITELISTED_ENDPOINTS',
                                           "status,healthcheck,health,login,mslogin,mscallback,"
                                           "glogin,gcallback,static")
    TENANT_BASED_LOGIN = bool(distutils.util.strtobool(os.environ.get('TENANT_BASED_LOGIN', 'True')))
    AUTH_MODELS_MODULE = os.environ.get('AUTH_MODELS_MODULE')
    AUTH_TENANT_CLASS_FUNC = os.environ.get('AUTH_TENANT_CLASS_FUNC')
    AUTH_USER_CLASS_FUNC = os.environ.get('AUTH_USER_CLASS_FUNC')

    # Logging Settings
    LOG_FORMAT = '%(asctime)s.%(msecs)03d [%(levelname)s] %(module)s.%(funcName)s:%(lineno)d (%(process)d:' \
                 + '%(threadName)s) - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
    LOG_LEVEL = 'INFO'

    OIDC_INTROSPECTION_AUTH_METHOD = 'client_secret_post'
    OIDC_ID_TOKEN_COOKIE_SECURE = False

    # Database and Sessions Settings
    SESSION_TYPE = 'sqlalchemy'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_DATABASE_URI = os.environ.get("FLASK_OIDC_SQLALCHEMY_DATABASE_URI", 'sqlite:///sessions.db')
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }

    # Microsoft login
    MS_CLIENT_ID = os.environ.get('MS_CLIENT_ID')
    MS_CLIENT_SECRET = os.environ.get('MS_CLIENT_SECRET')
    MS_USER_ENDPOINT = os.environ.get('MS_USER_ENDPOINT')

    MS_REDIRECT_PATH = "/mscallback"  # Used for forming an absolute URL to your redirect URI.
    # The absolute URL must match the redirect URI you set
    # in the app's registration in the Azure portal.

    # You can find the proper permission names from this document
    # https://docs.microsoft.com/en-us/graph/permissions-reference
    MS_SCOPE = ["User.ReadBasic.All"]

    # Google login
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    GOOGLE_DISCOVERY_URL = os.environ.get('GOOGLE_DISCOVERY_URL')

    GOOGLE_REDIRECT_PATH = "/gcallback"
    GOOGLE_SCOPE = ["openid", "email", "profile"]

    PUT_USER_METHOD = put_user
