import logging
import posixpath
import urllib.parse

from django.conf import settings
from ievv_opensource.ievv_i18n_url.base_url import BaseUrl
from ievv_opensource.ievv_i18n_url.handlers.abstract_handler import \
    UrlTransformError

from . import abstract_handler


logger = logging.getLogger(__name__)


class UrlpathPrefixHandler(abstract_handler.AbstractHandler):
    """
    I18n url handler that matches languages based on a URL prefix.
    """

    #: URL path prefix before we look for the languagecode in the url.
    #: **Must not** start or end with ``/``.
    #:
    #: E.g.:
    #:
    #: - If your languages should be served at ``/<languagecode>``, this should be blank string.
    #: - If your languages should be served at ``/my/translations/<languagecode>``, this should be ``my/translations``.
    LANGUAGECODE_URLPATH_PREFIX = ''

    @classmethod
    def get_urlpath_prefix_for_languagecode(cls, base_url, languagecode):
        if languagecode == cls.detect_default_languagecode(base_url):
            return ''
        if cls.LANGUAGECODE_URLPATH_PREFIX:
            return f'{cls.LANGUAGECODE_URLPATH_PREFIX}/{languagecode}'
        return languagecode

    @classmethod
    def _get_full_urlpath_prefix(cls):
        return f'/{cls.LANGUAGECODE_URLPATH_PREFIX}/'

    @classmethod
    def _strip_languagecode_from_urlpath(cls, base_url, languagecode, path):
        if not cls.is_supported_languagecode(languagecode):
            return path
        if languagecode == cls.detect_default_languagecode(base_url):
            return path
        if cls.LANGUAGECODE_URLPATH_PREFIX:
            full_prefix = cls._get_full_urlpath_prefix()
            if not path.startswith(full_prefix):
                return path
            path_without_prefix = path[len(full_prefix):]
        else:
            path_without_prefix = path[1:]
        splitpath = path_without_prefix.split(posixpath.sep, 1)
        if not splitpath:
            return path
        languagecode_in_path = splitpath[0]
        if languagecode_in_path != languagecode:
            return path
        return f'/{splitpath[1]}'

    @classmethod
    def _detect_languagecode_from_urlpath(cls, path):
        if cls.LANGUAGECODE_URLPATH_PREFIX:
            full_prefix = cls._get_full_urlpath_prefix()
            if not path.startswith(full_prefix):
                return None
            path_without_prefix = path[len(full_prefix):]
        else:
            path_without_prefix = path[1:]
        splitpath = path_without_prefix.split(posixpath.sep, 1)
        if not splitpath:
            return None
        languagecode = splitpath[0]
        if cls.is_supported_languagecode(languagecode):
            return languagecode
        return None

    @classmethod
    def get_languagecode_from_url(cls, url):
        urlpath = urllib.parse.urlparse(url).path
        return cls._detect_languagecode_from_urlpath(urlpath) or settings.LANGUAGE_CODE

    @classmethod
    def _build_urlpath(cls, path, languagecode, base_url):
        prefix = cls.get_urlpath_prefix_for_languagecode(
            base_url=base_url, languagecode=languagecode)
        if prefix:
            full_path = f'/{prefix}{path}'
        else:
            full_path = path
        return full_path

    def build_urlpath(self, path, languagecode=None, base_url=None):
        real_languagecode = languagecode or self.active_languagecode
        return self.__class__._build_urlpath(
            path=path,
            languagecode=real_languagecode,
            base_url=base_url or self.active_base_url)

    def build_absolute_url(self, path, languagecode=None, base_url=None):
        base_url = base_url or self.active_base_url
        return base_url.build_absolute_url(
            self.build_urlpath(path=path, languagecode=languagecode, base_url=base_url))

    @classmethod
    def transform_url_to_languagecode(cls, url, languagecode, translate_path=True):
        from_languagecode = cls.get_languagecode_from_url(url)
        base_url = BaseUrl(url)
        path_without_languagecode = cls._strip_languagecode_from_urlpath(
            base_url=base_url,
            languagecode=from_languagecode,
            path=urllib.parse.urlparse(url).path)
        if translate_path:
            try:
                path_without_languagecode = cls.transform_urlpath_to_languagecode(
                    base_url=base_url,
                    path=path_without_languagecode,
                    from_languagecode=from_languagecode,
                    to_languagecode=languagecode)
            except UrlTransformError as e:
                logger.warning('Failed to translate %s. Error: %s', path_without_languagecode, e)
        return base_url.build_absolute_url(
            cls._build_urlpath(path=path_without_languagecode, languagecode=languagecode, base_url=base_url))
