from threading import local

from django.conf import settings
from django.utils import translation
from ievv_opensource.ievv_i18n_url.base_url import BaseUrl

_active = local()


def get_default_languagecode():
    """
    Get the default language code activated within the current thread.

    I.e.: This returns the default languagecode that the
    :class:`ievv_opensource.ievv_i18n_url.middleware.LocaleMiddleware` sets
    as default.

    If this is called without using the middleware, or in management scripts
    etc. where the middleware is not applied, we fall back on ``settings.LANGUAGE_CODE``.

    Returns:
        str: The default languagecode for the current thread.
    """
    default_languagecode = getattr(_active, 'default_languagecode', None)
    return default_languagecode or settings.LANGUAGE_CODE


def set_default_languagecode(default_languagecode):
    """
    Used by :class:`ievv_opensource.ievv_i18n_url.middleware.LocaleMiddleware`
    to set the default languagecode in the current thread.

    .. warning::

        You will normally not want to use this, but it may be useful in management
        scripts along with calling :func:`.activate`.
    """
    _active.default_languagecode = default_languagecode


def get_active_languagecode():
    """
    Get the active language code activated within the current thread.

    I.e.: This returns the active languagecode that the
    :class:`ievv_opensource.ievv_i18n_url.middleware.LocaleMiddleware` sets
    as active. This may not be the same as the languagecode django.utils.translation.get_language()
    returns if the handler overrides
    :meth:`~ievv_opensource.ievv_i18n_url.handlers.abstract_handler.AbstractHandler.get_translation_to_activate_for_languagecode`.

    If this is called without using the middleware, or in management scripts
    etc. where the middleware is not applied, we fall back on ``settings.LANGUAGE_CODE``.

    Returns:
        str: The active languagecode for the current thread.
    """
    active_languagecode = getattr(_active, 'active_languagecode', None)
    return active_languagecode or settings.LANGUAGE_CODE


def set_active_languagecode(active_languagecode):
    """
    Used by :class:`ievv_opensource.ievv_i18n_url.middleware.LocaleMiddleware`
    to set the active languagecode in the current thread.

    .. warning::

        You will normally not want to use this, but it may be useful in management
        scripts along with calling :func:`.activate`.
    """
    _active.active_languagecode = active_languagecode


def get_active_language_urlpath_prefix():
    """
    Get the active URL path prefix within the current thread.

    I.e.: This returns the language url path prefix that the
    :class:`ievv_opensource.ievv_i18n_url.middleware.LocaleMiddleware`
    sets as active.

    If this is called without using the middleware, or in management scripts
    etc. where the middleware is not applied, we fall back on empty string.

    Returns:
        str: The URL path prefix for active language in the current thread.
    """
    active_language_urlpath_prefix = getattr(_active, 'active_language_urlpath_prefix', None)
    return active_language_urlpath_prefix or ''


def set_active_language_urlpath_prefix(urlpath_prefix):
    """
    Used by :class:`ievv_opensource.ievv_i18n_url.middleware.LocaleMiddleware`
    to set the active language url prefix in the current thread.

    .. warning::

        You will normally not want to use this, but it may be useful in management
        scripts along with calling :func:`.activate`.
    """
    _active.active_language_urlpath_prefix = urlpath_prefix


def get_active_base_url():
    """
    Get the BaseUrl activated within the current thread.

    I.e.: This returns BaseUrl that the
    :class:`ievv_opensource.ievv_i18n_url.middleware.LocaleMiddleware`
    sets as active.

    If this is called without using the middleware, or in management scripts
    etc. where the middleware is not applied, we fall back on ``BaseUrl()``.

    Returns:
        ievv_opensource.ievv_i18n_url.base_url.BaseUrl: The active BaseUrl.
    """
    active_base_url = getattr(_active, 'active_base_url', None)
    if active_base_url:
        return active_base_url
    return BaseUrl()


def set_active_base_url(active_base_url):
    """
    Used by :class:`ievv_opensource.ievv_i18n_url.middleware.LocaleMiddleware`
    to set the active language url prefix in the current thread.

    .. warning::

        You will normally not want to use this, but it may be useful in management
        scripts along with calling :func:`.activate`.
    """
    base_url = active_base_url
    _active.active_base_url = base_url


def activate(active_languagecode=None, default_languagecode=None, active_translation_languagecode=None,
             active_base_url=None, active_language_urlpath_prefix=None):
    """Activate a translation.

    This works much like ``django.utils.translation.activate()`` (and it calls that function),
    but it stores all of the stuff `ievv_i18n_url` needs to function in the current thread context.

    Args:
        active_languagecode (str): Language code to set as the active languagecode in the current thread. Defaults
            to settings.LANGUAGE_CODE. The only reason to call this without the active_languagecode argument is
            to reset the active language to the defaults. E.g.: Call ``activate()`` to reset to defaults from
            settings.
        default_languagecode (str): Default language code for the current thread. Defaults to ``active_languagecode``.
        active_translation_languagecode (str): Language code to set as the active translation in the current thread.
            I.e.: The languagecode we send to ``django.utils.translation.activate()``.
            Defaults to ``active_languagecode``.
        active_base_url (ievv_opensource.ievv_i18n_url.base_url.BaseUrl): The active base URL (E.g.: https://example.com/).
            Defaults to settings.IEVV_I18N_URL_FALLBACK_BASE_URL. Can be provided as a urllib.parse.ParseResult
            or as a string.
        active_language_urlpath_prefix (str): URL path prefix for the active language.
    """
    translation.activate(active_translation_languagecode or active_languagecode or settings.LANGUAGE_CODE)
    set_active_languagecode(active_languagecode)
    set_default_languagecode(default_languagecode or active_languagecode)
    set_active_base_url(active_base_url)
    set_active_language_urlpath_prefix(active_language_urlpath_prefix)
