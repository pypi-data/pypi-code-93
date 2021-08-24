from django.template import Library, defaulttags

from ievv_opensource.ievv_i18n_url import i18n_url_utils

register = Library()

# TODO: {% url %} compatible template tag!
# @register.simple_tag(takes_context=True)
# def i18n_url(context, viewname, urlconf=None, args=None, kwargs=None, current_app=None, languagecode=None, **kwargs):
#     """Template tag for the ievv_i18n_utils.i18n_url function.

#     You should use this instead of ``{% url %}``, but be warned that this
#     is not a perfect drop in replacement because ``{% url %}`` does some
#     magic with the first argument that we have not re-implemented. I.e.: This
#     template tag is more similar to the ``reverse()`` function than the
#     ``{% url %}`` template tag.

#     Args:
#         viewname: See the docs for ``django.urls.reverse``.
#         urlconf: See the docs for ``django.urls.reverse``. Defaults to None.
#         current_app: See the docs for ``django.urls.reverse``. Defaults to None.
#         kwargs: See the docs for ``django.urls.reverse``. Defaults to no kwargs.

#     Returns:
#         str: An url.
#     """
#     request = context['request']
#     defaulttags.url()
#     return i18n_url_utils.i18n_url(request, *args, **kwargs)


@register.simple_tag(takes_context=True)
def transform_url_to_languagecode(context, *args, **kwargs):
    """Template tag for the ievv_i18n_utils.transform_url_to_languagecode function.

    See :func:`~ievv_opensource.ievv_i18n_url.i18n_url_utils.transform_url_to_languagecode` for
    the available arguments, but do not provide the ``request`` argument - we get that
    from ``context["request"]``.

    Returns:
        str: An url.
    """
    request = context['request']
    return i18n_url_utils.transform_url_to_languagecode(request, *args, **kwargs)
