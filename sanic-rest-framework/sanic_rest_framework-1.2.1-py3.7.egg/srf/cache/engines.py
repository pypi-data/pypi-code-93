from srf.utils import ObjectDict
import time
from typing import Any
from aredis import StrictRedis, ConnectionPool
__all__ = ("BaseCacheEngine",
           "DataBlock",
           "DictCacheEngine",
           "RedisCacheEngine",)


class BaseCacheEngine:
    max_queue_count = 3000
    has_db = False

    def set(self, key, value, expire) -> bool:
        """
        设置缓存

        :param key: 缓存唯一键
        :param value: 需要缓存的值
        :param expire: 生命周期，单位秒
        :return: True or False
        :rtype: bool
        """
        pass

    def get(self, key) -> Any:
        """
        通过唯一键得到缓存的值
            键超时将抛出异常 CacheExpireEXC

        :param key: 缓存唯一键
        :return: 对应的值
        :rtype: Any
        """
        pass

    def delete(self, key) -> bool:
        """
        通过唯一键删除缓存的值

        :param key: 缓存唯一键
        :return: True or False
        :rtype: bool
        """
        pass

    async def _create_connection(self, config):
        if self.has_db:
            raise NotImplementedError()

    async def _disconnect_connection(self):
        if self.has_db:
            raise NotImplementedError()


class DataBlock:
    """内存数据块"""

    def __init__(self, name: str, value: Any, expire: float = None):
        """
        :param name: key名
        :param value: 存储value
        :param expire: 生命周期，单位秒
        """
        self._name = name
        self._value = value
        self.et = time.time() - 1
        if expire:
            self.et += expire
        else:
            self._ttl = -1

    @property
    def val(self):
        if self.ttl < 0:
            return None
        return self._value

    @property
    def ttl(self):
        if hasattr(self, '_ttl'):
            return self._ttl
        return self.et - time.time()

    def __repr__(self):
        return f'<name={self._name}>'


class DictCacheEngine(BaseCacheEngine):
    """
    本地字典缓存引擎
    """

    def __init__(self) -> None:
        self._cache: dict[DataBlock] = ObjectDict()
        self._last_clear_time = 0
        self._check_interval = 60

    async def set(self, key, value, expire):
        """
        设置缓存

        :param key: 缓存唯一键
        :param value: 需要缓存的值
        :param expire: 缓存时间（秒）
        :return: None
        """
        self._clear_expire()
        data = DataBlock(key, value, expire)
        self._cache[key] = data

    async def get(self, key) -> Any:
        """
        通过唯一键得到缓存的值
            键超时将抛出异常 CacheExpireEXC

        :param key: 缓存唯一键
        :return: 对应的值
        :rtype: Any
        """
        self._clear_expire()
        if key not in self._cache:
            return None
        return self._cache[key].val

    async def delete(self, key):
        """
        通过唯一键删除缓存的值

        :param key: 缓存唯一键
        :return: None
        """
        if key in self._cache:
            del self._cache[key]

    def _clear_expire(self):
        """
        清除超时的内容
        """
        delkey_list = []
        check_time = self._last_clear_time + self._check_interval
        if time.time() > check_time:
            for key, block in self._cache.items():
                if block.ttl < 0:
                    delkey_list.append(key)
        for delkey in delkey_list:
            self._cache.pop(delkey)


class RedisCacheEngine(BaseCacheEngine):
    has_db = True

    def __init__(self, conn):
        self.conn = conn

    async def set(self, key, value, expire):
        await self.conn.set(key, value, ex=expire)

    async def get(self, key) -> Any:
        return await self.conn.get(key)

    async def delete(self, key):
        """
        通过唯一键删除缓存的值

        :param key: 缓存唯一键
        :return: None
        """
        await self.conn.delete(key)

    @classmethod
    async def _create_connection(cls, config):
        pool = ConnectionPool(**config)
        redis = StrictRedis(connection_pool=pool)
        return redis

    async def _disconnect_connection(self):
        self.conn.connection_pool.disconnect()
