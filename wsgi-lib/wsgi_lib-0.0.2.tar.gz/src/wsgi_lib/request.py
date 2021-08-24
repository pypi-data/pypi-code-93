from typing import Dict, Any
from urllib.parse import parse_qsl


class Request:
    """
    This class is a high-level wrapper for WSGI `environ` param.
    Instances of this class are passed to function-based views.

    :ivar path: path of the HTTP request (e.g. /, /hello)
    :ivar request_method: method of the HTTP request (e.g. GET, POST)
    :ivar query_string: raw query_string of the HTTP request (e.g. field1=value1&field2=value2&field3=value3)
    :ivar args: dict that contains parsed query_string of the HTTP request
    :ivar headers: dict that contains headers of HTTP request
    :ivar remote_address: remote address of the client
    :ivar body: byte string that represents body of the HTTP request
    :ivar environ: raw WSGI environ dict, can be used to get additional info about the HTTP request
    """
    def __init__(self, environ: Dict[str, Any]) -> None:
        """
        :param environ: WSGI environ dict.
        Content is specified in PEP 3333 https://www.python.org/dev/peps/pep-3333/#environ-variables
        """
        self.path = environ['PATH_INFO']
        self.request_method = environ['REQUEST_METHOD']
        self.query_string = environ['QUERY_STRING']
        self.args = dict(parse_qsl(self.query_string))
        self.headers = {}
        for k, v in environ.items():
            if k.startswith('HTTP_'):
                self.headers[k[5:]] = v
        self.remote_address = environ['REMOTE_ADDR']
        self.body = environ['wsgi.input'].read()
        self.environ = environ
