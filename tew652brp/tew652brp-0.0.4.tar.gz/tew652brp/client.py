import requests

from tew652brp.core.login.handler import LoginHandler
from tew652brp.core.access.virtual.handler import VirtualHandler


class Client:
    """
    Main interface class. Contains all handlers.

    Usage::

    >>> from tew652brp.client import Client
    >>> client = Client("http://192.168.10.1")  # Init client session
    >>> client.login.login(...) # executes login method through login handler
    >>> servers = client.virtual.get_servers()  # executes get_servers method through virtual servers handler
    """
    def __init__(self, base_url: str):
        self._base_url = base_url
        self._session = requests.Session()

        self.virtual = VirtualHandler(self._session, self._base_url)
        self.login = LoginHandler(self._session, self._base_url)
