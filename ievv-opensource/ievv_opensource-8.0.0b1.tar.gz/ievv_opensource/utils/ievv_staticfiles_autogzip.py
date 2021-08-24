from django.conf import settings
from django.templatetags.static import static as django_static


def get_setting():
    return getattr(settings, 'IEVV_STATICFILES_AUTOGZIP', None) or {}


def is_enabled_for_context(autogzip_context):
    return get_setting().get(autogzip_context, False)


def static_path(path, autogzip_context):
    """
    If the ``autogzip_context`` is set to True in the 
    django setting IEVV_STATICFILES_AUTOGZIP (a dict), the provided
    path is suffixed with ``.gz`` and returned. Otherwise,
    ``path`` is returned unmodified.
    """
    if is_enabled_for_context(autogzip_context):
        return f'{path}.gz'
    return path


def static(path, autogzip_context):
    """
    Just like ``django.contrib.staticfiles.templatetags.static()``,
    but if the ``autogzip_context`` is set to True in the
    django setting IEVV_STATICFILES_AUTOGZIP (a dict), the provided
    path is suffixed with ``.gz``.
    """
    return django_static(static_path(path, autogzip_context))
