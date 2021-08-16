# -*- coding: utf-8 -*-
# @Time    : 2020-07-02 19:27
# @Author  : xzr
# @File    : increment_id
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    : 根据字符串 通过 redis 生成自增ID

import redis


class IncrementId(object):
    incr_lookup = '__tol_num'

    def __init__(self, key, client=None):
        self.key = key
        self.client = client or redis.StrictRedis('10.19.200.185', password='123456', socket_timeout=5,
                                                  max_connections=5, decode_responses=False)
        self.init_key()

    def init_key(self):
        if not self.client.exists(self.key):
            self.client.hincrby(self.key, self.incr_lookup, 0)

    def get_tol_num(self):
        """
        获取生成自增id数量
        :return:
        """
        return int(self.client.hget(self.key, self.incr_lookup))

    def generate_field_name(self, filed_name):
        return str(filed_name)[:64]

    def get_incr_id(self, filed_name):
        """
        根据字符串获取自增id
        :param filed_name:
        :return:
        """
        filed_name = self.generate_field_name(filed_name)
        incr_id = self.client.hget(self.key, filed_name)
        if not incr_id:
            incr_id = self._get_incr_num()
            self.client.hset(self.key, filed_name, incr_id)
        return int(incr_id)

    def _get_incr_num(self):
        return self.client.hincrby(self.key, self.incr_lookup, 1)


if __name__ == '__main__':
    i = IncrementId('device')


    def test():

        for ss in range(100000):
            s = i.get_incr_id(ss)
            # print(i.get_incr_id(ss))
        print(i.get_tol_num())


    import cProfile

    cProfile.run("test()")
