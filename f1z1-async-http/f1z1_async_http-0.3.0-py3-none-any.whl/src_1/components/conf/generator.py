# @Time     : 2021/7/18
# @Project  : f1z1-g
# @IDE      : PyCharm
# @Author   : Angel
# @Email    : 376355670@qq.com
from .base import IConfReader, IConfigGenerator
from .config import Config


class ConfigGenerator(IConfigGenerator):

    def __init__(self, reader: IConfReader):
        self._reader = reader

    def generate(self):
        config_reader = self._reader
        return Config(
            base_url=config_reader.read_base_url(),
            timeout=config_reader.read_timeout(),
            max_connection=config_reader.read_max_connection(),
            max_keepalive=config_reader.read_max_keepalive()
        )
