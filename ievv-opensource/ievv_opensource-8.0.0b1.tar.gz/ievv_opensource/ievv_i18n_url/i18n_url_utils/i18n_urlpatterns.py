import re

from django.urls import path, URLResolver
from django.conf import settings

from ievv_opensource.ievv_i18n_url import active_i18n_url_translation
from ievv_opensource.ievv_i18n_url.views import RedirectToLanguagecodeView

#
# Note: Basically copy and tuning from https://github.com/django/django/blob/1.11.29/django/conf/urls/i18n.py
#
# When updating for Django 2+, see https://github.com/django/django/blob/master/django/conf/urls/i18n.py
#


def i18n_patterns(*urls, include_redirect_view=True):
    """
    Adds the language code prefix to every URL pattern within this
    function. This may only be used in the root URLconf, not in an included
    URLconf.
    """
    if not settings.USE_I18N:
        return list(urls)
    new_urls = []
    if include_redirect_view:
        new_urls.append(
            path('_ievv-i18n-redirect-to/<str:languagecode>/<path:path>',
                 RedirectToLanguagecodeView.as_view(),
                 name='ievv_i18n_url_redirect_to_languagecode'),
        )
    new_urls.append(
        URLResolver(
            I18nLocalePrefixPattern(),
            list(urls)
        )
    )
    return new_urls


class I18nLocalePrefixPattern:
    def __init__(self, prefix_default_language=True):
        self.prefix_default_language = prefix_default_language
        self.converters = {}

    @property
    def regex(self):
        # This is only used by reverse() and cached in _reverse_dict.
        return re.compile(self.language_prefix)

    @property
    def language_prefix(self):
        urlpath_prefix = active_i18n_url_translation.get_active_language_urlpath_prefix()
        if urlpath_prefix:
            return f'{urlpath_prefix}/'
        else:
            return ''

    def match(self, path):
        language_prefix = self.language_prefix
        if path.startswith(language_prefix):
            return path[len(language_prefix):], (), {}
        return None

    def check(self):
        return []

    def describe(self):
        return "'{}'".format(self)

    def __str__(self):
        return self.language_prefix
