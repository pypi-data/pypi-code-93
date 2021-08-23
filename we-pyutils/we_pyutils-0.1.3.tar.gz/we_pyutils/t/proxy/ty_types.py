#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : ty_types.py
@Time    : 2021-03-22 9:55
@Author  : ZENKR
@Email   : zenkr@qq.com
@Software: PyCharm
@Desc    :
@license : Copyright (c) 2021 WingEase Technology Co.,Ltd. All Rights Reserved.
"""
import datetime
import random


class ProxyIP:
    """
    自定义太阳代理IP格式
    """

    def __init__(self, ip: str, port=None, expire_time=None, city=None, isp=None, used_times=0):
        self.ip = ip
        self.port = port
        self.expire_time = expire_time
        self.used_times = used_times
        self.city = city
        self.isp = isp

    def __str__(self):
        return f'IP:{self.ip}:{self.port}, Used:{self.used_times} times.'

    def get_ip(self):
        self.used_times_add()
        return self.proxy_str()

    def proxy_str(self):
        return f'{self.ip}:{self.port}'

    def get_used_times(self):
        return self.used_times

    def used_times_add(self, times=1):
        self.used_times += times


class ProxyIPPool:
    def __init__(self, ip_dict: dict = None):
        self.ip_pool = {} if ip_dict is None else ip_dict

    def __len__(self):
        return len(self.ip_pool)

    def enlarge_ip_pool(self, ip_dict: dict):
        self.ip_pool.update(ip_dict)
        return self.ip_pool

    def add_ip(self, ip: ProxyIP):
        self.ip_pool[ip.ip] = ip
        return ip

    def update_ip(self, ip: ProxyIP):
        self.ip_pool[ip.ip] = ip
        return ip

    def remove_ip(self, ip: str):
        del self.ip_pool[ip]

    def random_choice_ip(self, count=1) -> ProxyIP:
        p = list(self.ip_pool.values())
        return random.choice(p)
        # return random.sample(p, count) # 选择多个IP（返回list）

    def get_ip_pool(self):
        return self.ip_pool


class ProxyIPDict:
    def __init__(self, ip_list: list):
        self.ip_dict = {}
        ip_list_initialized = self.init_ip_list(ip_list)
        self.ip_dict.update(ip_list_initialized)

    @staticmethod
    def init_ip_list(ip_list: list) -> dict:
        ip_dict = {}
        if isinstance(ip_list, list):
            for ip_item in ip_list:
                ip = ProxyIP(ip_item['ip'])
                if ip_item['port']:
                    ip.port = ip_item['port']
                if ip_item['expire_time']:
                    ip.expire_time = datetime.datetime.strptime(ip_item['expire_time'], '%Y-%m-%d %H:%M:%S')
                if ip_item['city']:
                    ip.city = ip_item['city']
                if ip_item['isp']:
                    ip.isp = ip_item['isp']
                ip_dict[ip_item['ip']] = ip
        else:
            raise ValueError
        return ip_dict

    def get_ip_dict(self):
        return self.ip_dict


if __name__ == '__main__':
    il = [
        {
            "city": "吉林省四平市",
            "expire_time": "2021-03-22 16:38:04",
            "ip": "221.9.134.198",
            "isp": "联通",
            "port": "4353"
        },
        {
            "city": "吉林省四平市",
            "expire_time": "2021-03-22 16:38:04",
            "ip": "221.9.134.199",
            "isp": "联通",
            "port": "4353"
        }
    ]
    ip_1 = ProxyIP('127.0.0.1', 4353)
    t1 = ip_1.get_ip()
    ip_2 = ProxyIP('127.0.0.2', 2222)
    ip_3 = ProxyIP('127.0.0.3', 3333)
    id = {
        '127.0.0.2': ip_2,
        '127.0.0.3': ip_3,
    }
    ip_dict = ProxyIPDict(il)
    ip_pool = ProxyIPPool()
    ip_pool.add_ip(ip_1)
    ip_pool.enlarge_ip_pool(id)
    l = len(ip_pool)
    # ip_pool.remove_ip('127.0.0.2')
    c1 = ip_pool.random_choice_ip()
    c2 = ip_pool.random_choice_ip(2)
    pass
