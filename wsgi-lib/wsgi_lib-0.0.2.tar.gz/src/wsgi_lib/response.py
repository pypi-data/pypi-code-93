from dataclasses import dataclass, field
from typing import Callable, Dict, Any, Iterable


HTTP_STATUS_CODES = {
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    103: "Early Hints",  # see RFC 8297
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi Status",
    208: "Already Reported",  # see RFC 5842
    226: "IM Used",  # see RFC 3229
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    306: "Switch Proxy",  # unused
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",  # unused
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Request Entity Too Large",
    414: "Request URI Too Long",
    415: "Unsupported Media Type",
    416: "Requested Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I'm a teapot",  # see RFC 2324
    421: "Misdirected Request",  # see RFC 7540
    422: "Unprocessable Entity",
    423: "Locked",
    424: "Failed Dependency",
    425: "Too Early",  # see RFC 8470
    426: "Upgrade Required",
    428: "Precondition Required",  # see RFC 6585
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    449: "Retry With",  # proprietary MS extension
    451: "Unavailable For Legal Reasons",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    506: "Variant Also Negotiates",  # see RFC 2295
    507: "Insufficient Storage",
    508: "Loop Detected",  # see RFC 5842
    510: "Not Extended",
    511: "Network Authentication Failed",
}


@dataclass
class DefaultResponse:
    """
    This class is a wrapper for default response (contains `status_code`, `headers` and `body`) and encapsulates logic
    to send response to WSGI server based on current state, `environ` and `start_response` params.
    """
    body: bytes = b''
    headers: Dict[str, str] = field(default_factory=dict)
    status_code: int = 200

    @property
    def status_code_text(self) -> str:
        """
        This property method converts int self.status_code to string with message. Result of this method is passed to
        WSGI `start_response` callback.
        :Example: self.status_code = 200 -> '200 OK'

        :return: string that contains status code with message
        """
        return f'{self.status_code} {HTTP_STATUS_CODES[self.status_code]}'

    def set_headers(self, environ: Dict[str, Any]) -> None:
        """
        This method sets headers before sending response.

        :param environ: WSGI environ dict.
        Content is specified in PEP 3333 https://www.python.org/dev/peps/pep-3333/#environ-variables

        :return: None
        """
        pass

    def send_response(self, environ: Dict[str, Any], start_response: Callable) -> Iterable:
        """
        This method sends response to WSGI server by calling start_response callable and returning iterable object with
        response body.

        :param environ: WSGI environ dict.
        Content is specified in PEP 3333 https://www.python.org/dev/peps/pep-3333/#environ-variables
        :param start_response: callable passed by WSGI server to pass status_code and headers of response from the app.

        :return: iterable with response body
        """
        self.set_headers(environ)
        start_response(self.status_code_text, self.headers.items())
        return [self.body]


@dataclass
class UnicodeResponse(DefaultResponse):
    """
    This class accepts `body` in str format (not in bytes) and sets `Content-Type` header to `text/html; charset=utf-8`
    """
    body: str = ''  # type: ignore

    def set_headers(self, environ: Dict[str, Any]):
        self.headers['Content-Type'] = 'text/html; charset=utf-8'

    def send_response(self, environ: Dict[str, Any], start_response: Callable) -> Iterable:
        result = super().send_response(environ, start_response)
        return [i.encode() for i in result]


@dataclass
class RedirectResponse(DefaultResponse):
    """
    This response class redirects user to specified by `redirect_location` param location.
    """
    redirect_location: str = ''
    status_code: int = 301

    def set_headers(self, environ: Dict[str, Any]):
        self.headers['Location'] = self.redirect_location
