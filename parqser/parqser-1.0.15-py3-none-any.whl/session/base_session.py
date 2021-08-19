from typing import Dict, Union
from requests import Session


class BaseSession:
    def __init__(self, proxies: Union[Dict[str, str], None] = None):
        self._session = Session()
        self.proxies = proxies

    def get(self, url: str):
        """Downloads page by url using proxies if provided"""
        return self._session.get(url, proxies=self.proxies)

    def auth(self, *args):
        """Executes authentication for given site with given credentials"""
        raise NotImplemented
