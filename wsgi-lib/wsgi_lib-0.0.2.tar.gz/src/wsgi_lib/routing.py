import re
from typing import List, Tuple, Callable, Dict, Any, Iterable

from wsgi_lib.request import Request
from wsgi_lib.response import DefaultResponse


class NotFoundError(Exception):
    """
    This error is used in the router below to signal that the route is not found and 404 error will be returned
    """
    pass


class Router:
    """
    This class allows to create routes and match them with function-based views. Nested routes are also supported.

    :ivar routes: list of routes, each route is a tuple that contains regexp and function-based view (or nested route).
    Function-based views should receive request object instance (see wsgi_lib.request.Request class) and kwargs that
    are parsed from route URL.
    Function-based views should return instances derived from wsgi_lib.response.DefaultResponse class.

    :Example:
        Router([
            (r'admin/', lambda request: ...),
            (r'users/(?P<user_id>.+)/', lambda request, user_id: ...),
            (r'nested/(?P<nested_id>.+)/', Router([
                (r'hello/(?P<hello_id>.+)/', lambda request, nested_id, hello_id: ...),
                (r'hello/', lambda request, nested_id: ...),
                (r'', lambda request, nested_id: ...)
            ])),
            (r'', lambda request: ...)
        ])

    More comprehensive example is located in `examples` directory.
    """
    def __init__(self, routes: List[Tuple[str, Callable[..., DefaultResponse]]]):
        """
        :param routes: list of routes that will be saved to instance attribute.
        """
        self.routes = routes

    def _get_matching_func(self, path: str, prefix: str = '/'):
        """
        This function finds matching function-based view based on path.

        :param path: path of URL (example /admin/, will match first route in the example above)
        :param prefix: prefix that will be applied to each route (is used for nested routes)

        :return: matching function-based view or NotFoundError is thrown
        """
        for route_path, func in self.routes:
            route_match = re.match(prefix + route_path, path)
            if route_match:
                if isinstance(func, Router):
                    return func._get_matching_func(path, prefix=prefix + route_path)
                return func, route_match.groupdict()
        raise NotFoundError(f'Route for path {path} not found')

    def __call__(self, environ: Dict[str, Any], start_response: Callable) -> Iterable:
        """
        This function is called by WSGI server to get response.

        :param environ: WSGI environ dict.
        Content is specified in PEP 3333 https://www.python.org/dev/peps/pep-3333/#environ-variables
        :param start_response: callable passed by WSGI server to pass status_code and headers of response from the app.

        :return: iterable with response body
        """
        request = Request(environ)
        try:
            func_view, params = self._get_matching_func(request.path)
            return func_view(request, **params).send_response(environ, start_response)
        except NotFoundError:
            return DefaultResponse(status_code=404).send_response(environ, start_response)
