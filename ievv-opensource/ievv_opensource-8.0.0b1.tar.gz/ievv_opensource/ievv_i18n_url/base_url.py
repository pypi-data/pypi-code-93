from django.utils.functional import cached_property
import urllib.parse
from ievv_opensource.ievv_i18n_url.i18n_url_settings import get_fallback_base_url_setting


class BaseUrl:
    """
    Defines ievv_i18n_url base url.

    The base URL is the URL to the root of the domain e.g: https://example.com, http://www.example.com:8080, etc.
    (NOT https://example.com/my/path, https://example.com/en, etc.).

    The constructor can take any valid absolute URL, or None
    (in which case it falls back on the IEVV_I18N_URL_FALLBACK_BASE_URL setting),
    but all the methods and properties work on a ``urllib.parse.ParseResult`` that
    does not have any of the URL parts after
    """
    def __init__(self, url_or_urllib_parseresult=None):
        self.url_or_urllib_parseresult = url_or_urllib_parseresult or get_fallback_base_url_setting()

    @cached_property
    def parsed_url(self):
        """Get the parsed URL.

        The returned URL only has scheme+domain+port (e.g.: scheme+netloc).

        Returns:
            urllib.parse.ParseResult: A parsed URL on the same format as urllib.parse.urlparse returns.
        """
        if isinstance(self.url_or_urllib_parseresult, urllib.parse.ParseResult):
            parsed_url = self.url_or_urllib_parseresult
        else:
            parsed_url = urllib.parse.urlparse(self.url_or_urllib_parseresult)
        return urllib.parse.ParseResult(
            scheme=parsed_url.scheme,
            netloc=parsed_url.netloc,
            path='', params='', query='', fragment='')

    @property
    def scheme(self):
        """Shortcut for parsed_url.scheme.

        See :obj:`~.BaseUrl.parsed_url`.

        Returns:
            str: The url scheme (e.g.: https, http, ...)
        """
        return self.parsed_url.scheme

    @property
    def netloc(self):
        """Shortcut for parsed_url.netloc.

        See :obj:`~.BaseUrl.parsed_url`.

        Returns:
            str: The url netloc (e.g.: www.example.com:9090)
        """
        return self.parsed_url.netloc

    @property
    def hostname(self):
        """Shortcut for parsed_url.hostname.

        See :obj:`~.BaseUrl.parsed_url`.

        Returns:
            str: The url hostname (e.g.: www.example.com)
        """
        return self.parsed_url.hostname

    @property
    def port(self):
        """Shortcut for parsed_url.port.

        See :obj:`~.BaseUrl.parsed_url`.

        Returns:
            str: The url port (e.g.: 8080, 80, ...)
        """
        return self.parsed_url.port

    def build_absolute_url(self, path_or_url):
        """Build absolute URL from the provided ``path_or_url``.

        If the provided ``path_or_url`` is an URL, it is returned unchanged.
        If the provided ``path_or_url`` is a URL path, it is appended to the base url.

        Examples.::

            BaseUrl('https://example.com').build_absolute_url('/my/path?a=2')
            # -> https://example.com/my/path?a=2

            BaseUrl('https://example.com').build_absolute_url('https://other.example.com/a/b')
            # -> https://other.example.com/a/b

        Args:
            path_or_url (str): URL path or an URL.

        Returns:
            [type]: [description]
        """
        return urllib.parse.urljoin(self.parsed_url.geturl(), path_or_url)

    def __str__(self):
        return self.parsed_url.geturl()
