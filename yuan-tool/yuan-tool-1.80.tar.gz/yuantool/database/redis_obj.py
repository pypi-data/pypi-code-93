# coding: utf-8
import redis
from redis._compat import urlparse
import logging

logger = logging.getLogger(__name__)


def url_change(redis_url):
    url = urlparse(redis_url)
    host = url.hostname, port = url.port, password = url.password
    return host, port, password


class RedisObj:
    def __init__(self, host, port, db, decode_responses=True):
        try:
            self.obj = redis.StrictRedis(
                host=host,
                port=port,
                db=db,
                decode_responses=decode_responses
            )
            # name = 'task_manage'
            # 先校验是否成功连接数据库
            # self.list_all(name)
        except redis.exceptions.ConnectionError as e:
            logger.error('redis 数据库连接失败')
            exit()

    @property
    def redis_obj(self):
        ''' 返回redis对象 '''
        return self.obj

    def length(self, name):
        ''' 获取list的长度 '''
        return self.obj.llen(name)

    def push(self, name, *value):
        ''' 默认为向list后面插入数据 '''
        return self.obj.rpush(name, *value)

    def pop(self, name):
        ''' 默认从list前面弹出数据 '''
        # return self.obj.brpop(name, timeout=self.timeout)
        return self.obj.lpop(name)

    def list_all(self, name):
        ''' 查看list的所有数据 '''
        return self.obj.lrange(name, 0, -1)

    def task_clear(self, name):
        ''' 清空指定的列表内元素 1表示已移除，0表示不存在'''
        return self.obj.delete(name)

    def task_list(self):
        ''' 查看所有任务列表 '''
        return self.obj.keys()

    def task_exists(self, task_id):
        ''' 判断任务是否存在 1为存在 0为不存在'''
        return self.obj.exists(task_id)
