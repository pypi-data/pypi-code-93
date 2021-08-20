# coding: utf-8

__all__ = ["ProxyInfo"]

from urllib.parse import urlparse
from urllib.request import getproxies


class ProxyInfo(object):

    __proxies_info = None
    __no_proxy = None

    @classmethod
    def get_proxies_info(cls):
        if cls.__proxies_info is None:
            cls.__proxies_info = {}
            proxies = getproxies()
            for scheme, proxy_data in proxies.items():
                if scheme == "no":
                    cls.__no_proxy = proxy_data.split(",")
                    if not cls.__no_proxy:
                        # if no_proxy is empty, rely on default value (websocket._url.DEFAULT_NO_PROXY_HOST)
                        cls.__no_proxy = None
                else:
                    cls.__proxies_info[scheme] = ProxyInfo.proxy_info_from_url(
                        proxy_data, scheme
                    )

        return cls.__proxies_info

    @classmethod
    def get_no_proxy(cls):
        # call cls.get_proxies_info() to be sure class attr were initialized
        cls.get_proxies_info()
        return cls.__no_proxy

    @classmethod
    def get_proxy_info(cls, scheme):
        proxies_info = cls.get_proxies_info()
        return proxies_info[scheme] if scheme in proxies_info else None

    def __init__(
        self,
        proxy_type,
        proxy_host,
        proxy_port,
        proxy_user=None,
        proxy_pass=None,
    ):
        """Args:
        proxy_type: The type of proxy server ('http')
        proxy_host: The hostname or IP address of the proxy server.
        proxy_port: The port that the proxy server is running on.
        proxy_user: The username used to authenticate with the proxy server.
        proxy_pass: The password used to authenticate with the proxy server.
        """
        if isinstance(proxy_user, bytes):
            proxy_user = proxy_user.decode()
        if isinstance(proxy_pass, bytes):
            proxy_pass = proxy_pass.decode()
        (
            self._proxy_type,
            self._proxy_host,
            self._proxy_port,
            self._proxy_user,
            self._proxy_pass,
        ) = (
            proxy_type,
            proxy_host,
            proxy_port,
            proxy_user,
            proxy_pass,
        )

    @property
    def type(self):
        return self._proxy_type

    @property
    def host(self):
        return self._proxy_host

    @property
    def port(self):
        return self._proxy_port

    @property
    def user(self):
        return self._proxy_user

    @property
    def password(self):
        return self._proxy_pass

    @property
    def auth(self):
        if self._proxy_user and self._proxy_pass:
            return tuple(self._proxy_user, self._proxy_pass)

    def __repr__(self):
        return (
            f"<ProxyInfo type={self.type} host={self.host}:{self.port} "
            + f" user={self.user} pass={self.password}>"
        )

    def proxy_json_info(self):
        return {
            "type": self._proxy_type,
            "host": self._proxy_host,
            "port": self._proxy_port,
            "user": self._proxy_user,
            "pass": self._proxy_pass,
        }

    @staticmethod
    def proxy_info_from_url(url, method="http"):
        """Construct a ProxyInfo from a URL (such as http_proxy env var value)"""
        url = urlparse(url)
        username = None
        password = None
        port = None
        method = url[0]
        if "@" in url[1]:
            ident, host_port = url[1].split("@", 1)
            if ":" in ident:
                username, password = ident.split(":", 1)
            else:
                password = ident
        else:
            host_port = url[1]
        if ":" in host_port:
            host, port = host_port.split(":", 1)
        else:
            host = host_port

        if port:
            port = int(port)
        else:
            try:
                port = dict(https=443, http=80)[method]
            except KeyError:
                pass

        pi = ProxyInfo(
            proxy_type=method,
            proxy_host=host,
            proxy_port=port,
            proxy_user=username or None,
            proxy_pass=password or None,
        )
        return pi
