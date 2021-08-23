# @Time     : 2021/7/18
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from collections import defaultdict

from .base import IConfig, IConfigManager, IntOrFloat

DEFAULT_TIMEOUT = 3600
DEFAULT_MAX_CONNECTION = 100
DEFAULT_MAX_KEEPALIVE = 20


class Config(IConfig):

    def __init__(self,
                 base_url: str = None,
                 max_connection: int = None,
                 max_keepalive: int = None,
                 timeout: IntOrFloat = None):
        self._base_url = base_url if base_url else ""
        self._timeout = timeout if timeout else DEFAULT_TIMEOUT
        self._max_connection = max_connection if max_connection else DEFAULT_MAX_CONNECTION
        self._max_keepalive = max_keepalive if max_keepalive else DEFAULT_MAX_KEEPALIVE

    @property
    def base_url(self):
        return self._base_url

    @property
    def max_connection(self):
        return abs(self._max_connection)

    @property
    def max_keepalive(self):
        return abs(self._max_keepalive)

    @property
    def timeout(self):
        return abs(self._timeout)


class ConfigManager(IConfigManager):
    __slots__ = ["_configs"]

    def __init__(self):
        self._configs = defaultdict(Config)

    def get(self, node: str) -> IConfig:
        return self[node]

    def set(self, node: str, config: IConfig):
        self[node] = config

    def __getitem__(self, item):
        return self._configs[item]

    def __setitem__(self, key, value: IConfig):
        self._configs[key] = value
