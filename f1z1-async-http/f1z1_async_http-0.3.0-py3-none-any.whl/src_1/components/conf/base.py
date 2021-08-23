# @Time     : 2021/7/18
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from typing import Union

IntOrFloat = Union[int, float]


class IConfig(object):

    @property
    def base_url(self) -> str:
        """
        base url config
        :return:
        """
        raise NotImplementedError("NotImplemented .base_url -> str")

    @property
    def max_connection(self) -> int:
        """
        connect pool max connection
        :return:
        """
        raise NotImplementedError("NotImplemented .max_connection -> int")

    @property
    def max_keepalive(self) -> int:
        """
        connect pool max keepalive
        :return:
        """
        raise NotImplementedError("NotImplemented .max_keepalive -> int")

    @property
    def timeout(self) -> IntOrFloat:
        """
        timeout
        :return:
        """
        raise NotImplementedError("NotImplemented .timeout -> int or float")


class IConfigManager(object):

    def set(self, node: str, config: IConfig):
        raise NotImplementedError("")

    def get(self, node: str) -> IConfig:
        raise NotImplementedError("")


class IConfReader(object):

    def read_base_url(self) -> str:
        raise NotImplementedError("")

    def read_timeout(self) -> IntOrFloat:
        raise NotImplementedError("")

    def read_max_connection(self) -> int:
        raise NotImplementedError("")

    def read_max_keepalive(self) -> int:
        raise NotImplementedError("")


class IConfigGenerator(object):

    def generate(self) -> IConfig:
        raise NotImplementedError("")
