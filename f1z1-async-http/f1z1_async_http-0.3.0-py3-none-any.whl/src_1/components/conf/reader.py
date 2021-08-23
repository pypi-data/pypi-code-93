# @Time     : 2021/7/18
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from f1z1_common.src.conf import AbstractConfReader

from .base import IConfReader


class ConfigReader(IConfReader):

    def __init__(self, reader: AbstractConfReader, node: str):
        self._node = node
        self._reader = reader

    def read_base_url(self):
        return self._reader.get_string(self._node, "BASE_URL")

    def read_timeout(self):
        return self._reader.get_float(self._node, "TIMEOUT")

    def read_max_connection(self):
        return self._reader.get_int(self._node, "MAX_CONNECTION")

    def read_max_keepalive(self):
        return self._reader.get_int(self._node, "MAX_KEEPALIVE")
