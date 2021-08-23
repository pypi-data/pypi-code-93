from contextlib import suppress
from importlib import import_module
from typing import Optional

from jsm_user_services.exception import ApplicationSettingsNotFound
from jsm_user_services.support.import_utils import import_module_otherwise_none


def get_django_settings():
    django_conf = import_module_otherwise_none("django.conf")
    if django_conf and django_conf.settings.configured:
        return django_conf.settings
    return None


def get_flask_settings():
    with suppress(ImportError, RuntimeError):
        flask = import_module("flask")
        return flask.current_app.config


def get_setting_from_app(setting_name: str, default_value: Optional[str] = None):
    django_settings, flask_settings = get_django_settings(), get_flask_settings()
    if django_settings is not None:
        return getattr(django_settings, setting_name, default_value)

    if flask_settings is not None:
        return flask_settings.get(setting_name, default_value)

    raise ApplicationSettingsNotFound


USER_API_HOST = get_setting_from_app("USER_API_HOST")
USER_API_TOKEN = get_setting_from_app("USER_API_TOKEN")
JSM_USER_SERVICE_HTTP_TIMEOUT = get_setting_from_app("JSM_USER_SERVICE_HTTP_TIMEOUT", "30")
GOOGLE_RECAPTCHA_URL = get_setting_from_app("GOOGLE_RECAPTCHA_URL")
GOOGLE_RECAPTCHA_SECRET_KEY = get_setting_from_app("GOOGLE_RECAPTCHA_SECRET_KEY")
GOOGLE_RECAPTCHA_SCORE_THRESHOLD = get_setting_from_app("GOOGLE_RECAPTCHA_SCORE_THRESHOLD")
EVEREST_API_KEY = get_setting_from_app("EVEREST_API_KEY")
EVEREST_API_HOST = get_setting_from_app("EVEREST_API_HOST")
EVEREST_LIST_INVALIDS_STATUS_RESPONSES = get_setting_from_app("EVEREST_LIST_INVALIDS_STATUS_RESPONSES")
