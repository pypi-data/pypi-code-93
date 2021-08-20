import functools
import ssl
import locale

from http import HTTPStatus
from typing import Optional
from urllib.parse import urljoin

from requests import Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

_api_key = None
_base_url = ""
_preferred_language = ""
_session = Session()


class SecureRequestAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **kwargs):
        kwargs = kwargs or {}
        kwargs["ssl_version"] = ssl.PROTOCOL_TLSv1_2

        super().init_poolmanager(connections, maxsize, block, **kwargs)


# Require TLSv1.2 for all connections to the server
_session.mount("https://", SecureRequestAdapter())


def set_base_url(url: str):
    global _base_url
    _base_url = url


def get_base_url() -> str:  # pragma: no cover
    return _base_url


def set_api_key(key: str):
    """Sets the SermonAudio API key to use for authenticated requests. A key must be set before making any requests.

    :param key: Your API key. Broadcasters may obtain an API key by going to the Member's Only area of the site. If you
    are an application developer and would like to integrate SermonAudio into your product or website, please contact
    us at info@sermonaudio.com and we'll be happy to discuss with you.
    """
    global _api_key
    _api_key = key


def set_preferred_language(http_accept_language: str):
    """Sets the preferred language string globally. Defaults to your system locale environment variables.

    The format of the string should be an acceptable HTTP Accept-Language header. You may specify multiple languages,
    and the API will attempt to accommodate your preferences when possible. While content language will always be
    determined by the broadcasters individually, other strings, whenever possible, will be translated."""
    global _preferred_language
    _preferred_language = http_accept_language


# Set reasonable defaults
set_base_url("https://api.sermonaudio.com/v2/")
set_preferred_language((locale.getdefaultlocale()[0] or "en-US").replace("_", "-"))


def create_or_configure_session_with_retry(
    retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None
) -> Session:
    """Creates or configures a Session with retry logic.

    Only use this if you know what you're doing. You should be VERY careful about using this
    kind of logic for any non-GET requests. You can pass the session that you create (please re-use it!)
    to any request methods you call that need retries via the keyword argument `session`.
    """
    session = session or Session()
    retry = Retry(
        total=retries, read=retries, connect=retries, backoff_factor=backoff_factor, status_forcelist=status_forcelist
    )
    adapter = SecureRequestAdapter(max_retries=retry)

    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


class API:
    @classmethod
    def _get_request_headers(cls, preferred_language_override=None, show_content_in_any_language=True):
        result = {"X-API-Key": _api_key, "Accept-Language": preferred_language_override or _preferred_language}

        if show_content_in_any_language:
            result["X-Show-All-Languages"] = "True"

        return result

    @classmethod
    def _request(
        cls,
        path: str,
        method: str = "get",
        headers: Optional[dict] = None,
        preferred_language_override=None,
        show_content_in_any_language=True,
        session: Session = _session,
        parse_func=None,
        api_key_override: str = None,
        **kwargs,
    ):
        """Low-level API call helper.

        :param method: The HTTP method of the request.
        :param path: The path to the endpoint you want to call (e.g. /node/sermons/1234).
        :param headers: Additional headers to pass (the library handles authentication etc. automatically).
        :param preferred_language_override: An optional language preference override. The system default will be used.
        :param show_content_in_any_language: When false, only shows content in the preferred langauge.
        :param session: The request.Sesion object to use when making the request. Don't use without a good reason.
        :param parse_func: If present, this function will be invoked with the response, and the result of that
        invocation will be returned instead.
        :param kwargs: Any additional keyword arguments will be passed directly to session.request(). Note that in
        general, the params argument, when present, should be respected by all downstream methods. They will generally
        do a dict.update() of any params that they require, so if you add something stupid, expect it to be overridden.
        Otherwise, feel free to pass additional params. This allows for clean extension for internal use.
        """
        # Generate the URL using the path provided and the base URL
        url = urljoin(_base_url, path)

        # Update the headers passed in with our own required ones
        headers = headers or {}
        base_headers = cls._get_request_headers(preferred_language_override, show_content_in_any_language)
        headers.update(base_headers)

        if api_key_override:
            headers["X-API-Key"] = api_key_override  # pragma: no cover

        response = session.request(method, url, headers=headers, **kwargs)

        return parse_func(response) if parse_func is not None else response

    get = functools.partialmethod(_request, method="get")
    post = functools.partialmethod(_request, method="post")
    put = functools.partialmethod(
        _request,
        method="put",
        parse_func=lambda res: res.status_code in {HTTPStatus.OK, HTTPStatus.CREATED, HTTPStatus.NO_CONTENT},
    )
    patch = functools.partialmethod(
        _request,
        method="patch",
        parse_func=lambda res: res.status_code in {HTTPStatus.OK, HTTPStatus.ACCEPTED, HTTPStatus.NO_CONTENT},
    )
    delete = functools.partialmethod(
        _request,
        method="delete",
        parse_func=lambda res: res.status_code in {HTTPStatus.OK, HTTPStatus.ACCEPTED, HTTPStatus.NO_CONTENT},
    )


class APIException(Exception):
    pass
