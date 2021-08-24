from django.conf import settings


def get_fallback_base_url_setting():
    """Get the IEVV_I18N_URL_FALLBACK_BASE_URL.

    Raises:
        Exception: With a nice description if the setting is missing.

    Returns:
        str: The value of the setting
    """
    fallback_base_url = getattr(settings, 'IEVV_I18N_URL_FALLBACK_BASE_URL', None)
    if fallback_base_url:
        return fallback_base_url
    raise Exception(
        'The IEVV_I18N_URL_FALLBACK_BASE_URL setting is required. '
        'Refer to the docs for ievv_i18n_url (in ievv_opensource) for more info.')
