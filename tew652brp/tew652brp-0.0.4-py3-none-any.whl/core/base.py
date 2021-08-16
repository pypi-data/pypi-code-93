from typing import Callable

import requests

from tew652brp.core.utils import make_routes


class BaseAct:
    """
    Base class for actions ( requests to router ). Used to create custom actions.

    Usage::

        >>> class GetConnectedDevicesAct(BaseAct):
        ...     def __init__(self, request_method, url):
        ...         super().__init__(request_method, url)
        ...         params = {
        ...             'ccp_act': 'get',
        ...             ...,
        ...         }
        ...
        >>> resp = GetConnectedDevicesAct(...).submit()
    """
    def __init__(self, request_method: Callable, url: str, **extra):
        """
        :param request_method: method of Session ( from requests ).
        :param url: request url.
        :param extra: additional params e.g. login, id, password.
        """
        self._req_method = request_method
        self._url = url
        self._params = {}

    def submit(self) -> requests.Response:
        """
        Executes a request method with parameters.
        """
        return self._req_method(self._url, data=self._params)


class BaseHandler:
    """
    Base class for handlers. Used to create custom handlers.

    Usage::

        >>> class GetConnectedDevicesAct(BaseAct):
        ...     ...
        >>>
        >>> class GetConnectedDevicesHandler(BaseHandler):
        ...     def get_connected_devices(self):
        ...         resp = GetConnectedDevicesAct(
        ...             self._session.post,
        ...             self._routes['get_set']
        ...         ).submit()
        ...         ... # work with response
        ...         return resp
        ...
        >>> response = GetConnectedDevicesHandler()
    """
    def __init__(self, session: requests.Session, url: str):
        self._session = session
        self._url = url
        self._routes = make_routes(self._url)
