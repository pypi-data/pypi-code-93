from django.urls import reverse

from .get_handler import get_handler


def i18n_reverse(viewname, urlconf=None, args=None, kwargs=None, current_app=None, languagecode=None):
    """
    Serves kind of the same use case as the ``django.urls.reverse`` function, but with i18n URL support, AND
    this function returns an absolute URL.

    The reason why it returns absolute URL is because i18n URLs may be based on domains, not just URL paths.

    NOTE: Session based `ievv_i18n_url` handlers will ignore the languagecode argument and just return
    the URL for the default translation. This is because all their translations live at the same URL.
    See the *A warning about session based translations* in the docs for more details.

    Args:
        viewname: See the docs for ``django.urls.reverse``.
        urlconf: See the docs for ``django.urls.reverse``. Defaults to None.
        args: See the docs for ``django.urls.reverse``. Defaults to None.
        kwargs: See the docs for ``django.urls.reverse``. Defaults to None.
        current_app: See the docs for ``django.urls.reverse``. Defaults to None.
        languagecode (str, optional): The languagecode to reverse the URL in. Defaults to None, which means
            we reverse the URL in the current languagecode.

    Returns:
        str: An URL.
    """
    path = reverse(viewname=viewname, urlconf=urlconf, args=args, kwargs=kwargs, current_app=current_app)
    return get_handler().build_absolute_url(path=path, languagecode=languagecode)


def transform_url_to_languagecode(url, to_languagecode, from_languagecode=None):
    """Takes an URL, and finds the URL to the same content within a different languagecode.

    NOTE: Session based `ievv_i18n_url` handlers will ignore the languagecode argument and just return
    provided url. This is because all their translations live at the same URL.
    See the *A warning about session based translations* in the docs for more details.

    Args:
        url (str): The URL to transform.
        to_languagecode (str): The languagecode to transform the url into.
        from_languagecode (str): The languagecode to transform the url from.

    Returns:
        str: The transformed URL. If from_languagecode and to_languagecode is the same,
            the provided ``url`` is returned unchanged.
    """
    return get_handler().transform_url_to_languagecode(url=url, to_languagecode=to_languagecode)
