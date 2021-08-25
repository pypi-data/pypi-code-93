from django.conf import settings
from django.utils.module_loading import import_string


_handler_class = None


def get_handler_class():
    """
    Get the configured `ievv_i18n_url` handler class.

    E.g. import the handler class from the class path configured in the ``IEVV_I18N_URL_HANDLER`` setting.

    Returns:
        ievv_opensource.ievv_i18n_url.handlers.abstract_handler.AbstractHandler: A handler class.
    """
    global _handler_class
    if _handler_class is None:
        handler_classpath = getattr(settings, 'IEVV_I18N_URL_HANDLER', None)
        if not handler_classpath:
            raise Exception(
                'No ievv_i18n_url_handler configured. Please set the IEVV_I18N_URL_HANDLER. Refer to the docs for '
                'ievv_i18n_url in ievv_opensource for more info.')
        _handler_class = import_string(handler_classpath)
    return _handler_class


def get_handler():
    return get_handler_class()()
