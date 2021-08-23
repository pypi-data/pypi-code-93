#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@File    : ty.py
@Time    : 2021/3/28 16:33
@Author  : ZENKR
@Email   : zenkr@qq.com
@Software: PyCharm
@Desc    :
@license : Copyright (c) 2021 WingEase Technology Co.,Ltd. All Rights Reserved.
"""
import datetime
import json
import os
import random
import time
from urllib.request import urlopen

from we_pyutils.t.ip import get_my_ip

DEFAULT_GET_IP_URL = os.getenv('PROXY_TY_GET_IP_URL', '')
DEFAULT_GET_PACK_INFO_URL = os.getenv('PROXY_TY_GET_PACK_INFO_URL', '')
DEFAULT_ADD_WHITE_IP_URL = os.getenv('PROXY_TY_ADD_WHITE_IP_URL', '')
DEFAULT_DEL_WHITE_IP_URL = os.getenv('PROXY_TY_DEL_WHITE_IP_URL', '')
DEFAULT_ACCOUNT_NAME = os.getenv('PROXY_TY_ACCOUNT_NAME', '')
DEFAULT_ACCOUNT_KEY = os.getenv('PROXY_TY_ACCOUNT_KEY', '')
DEFAULT_NEEK = os.getenv('PROXY_TY_NEEK', '')
DEFAULT_APPKEY = os.getenv('PROXY_TY_APPKEY', '')

ADD_WHITE_IP_URL = f'ty-http-d.hamir.net/index/white/add?neek={"ACCOUNT_NAME"}&appkey={"ACCOUNT_KEY"}&white={"IP"}'
DEL_WHITE_IP_URL = f'ty-http-d.hamir.net/index/white/del?neek={"ACCOUNT_NAME"}&appkey={"ACCOUNT_KEY"}&white={"IP"}'
LIST_WHITE_IP_URL = f'ty-http-d.hamir.net/index/index/white_list?neek={"NEEK"}&appkey={"APPKEY"}'
GET_PACK_INFO_URL = f'ty-http-d.hamir.net/index/index/get_my_pack_info?neek={"NEEK"}&appkey={"APPKEY"}'
GET_PACKAGE_BALANCE_URL = f'ty-http-d.hamir.net/index/index/get_my_package_balance?neek={"NEEK"}&appkey={"APPKEY"}&ac={"AC"}'


class ProxyIP:
    """
    自定义太阳代理IP格式
    """
    ip: str
    port: int
    expire_time: datetime
    city: str
    isp: str
    used_times: int
    ip_dict: dict

    def __init__(self,
                 ip: str = None,
                 port: int = None,
                 expire_time=None,
                 city: str = None,
                 isp: str = None,
                 used_times: int = 0,
                 ip_dict: dict = None
                 ):
        if ip_dict:
            if 'ip' in ip_dict and ip_dict['ip']:
                self.ip = ip_dict['ip']
            if 'port' in ip_dict and ip_dict['port']:
                self.port = int(ip_dict['port'])
            if 'expire_time' in ip_dict and ip_dict['expire_time']:
                self.expire_time = self.format_expire_time(ip_dict['expire_time'])
            if 'city' in ip_dict and ip_dict['city']:
                self.city = ip_dict['city']
            if 'isp' in ip_dict and ip_dict['isp']:
                self.isp = ip_dict['isp']
            if 'used_times' in ip_dict and ip_dict['used_times']:
                self.used_times = ip_dict['used_times']
            else:
                self.used_times = used_times
        else:
            if ip:
                self.ip = ip
            else:
                raise ValueError
            if port:
                self.port = port if isinstance(port, int) else int(port)
            else:
                self.port = port
            if isinstance(expire_time, str):
                self.expire_time = self.format_expire_time(expire_time)
            else:
                self.expire_time = expire_time
            if used_times:
                self.used_times = used_times if isinstance(used_times, int) else int(used_times)
            else:
                self.used_times = used_times
            self.city = city
            self.isp = isp

    def __str__(self):
        return f'IP:{self.ip}:{self.port}, Used:{self.used_times} times.'

    def __eq__(self, obj):
        return self.__dict__ == obj.__dict__

    def use_ip_str(self):
        self.used_times_add()
        return self.proxy_str()

    def proxy_str(self):
        return f'{self.ip}:{self.port}'

    def get_used_times(self):
        return self.used_times

    def used_times_add(self, times=1):
        self.used_times += times

    @staticmethod
    def format_expire_time(expire_time_str: str) -> datetime:
        return datetime.datetime.strptime(expire_time_str, '%Y-%m-%d %H:%M:%S')


class ProxyIPPool:
    def __init__(self, ip_dict: dict = None):
        self.ip_pool: dict = {} if ip_dict is None else ip_dict

    def __len__(self):
        return len(self.ip_pool)

    def __eq__(self, obj):
        return self.ip_pool == obj.ip_pool

    def __dict__(self):
        return self.ip_pool

    def enlarge_ip_pool(self, ip_dict: dict):
        self.ip_pool.update(ip_dict)
        return self.ip_pool

    def enlarge_ip_pool_b(self, ip_list: list):
        ip_pool_tmp = {}
        for ip_item in ip_list:
            ip = ProxyIP(ip_dict=ip_item)
            ipstr = ip.ip
            ip_pool_tmp[ip.ip] = ip
        self.ip_pool.update(ip_pool_tmp)
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


class Singleton(object):
    def __new__(cls, *args, **kw):
        if not hasattr(cls, '_instance'):
            orig = super(Singleton, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance


class ProxyTYClient(Singleton):
    get_pack_info_count = 0
    max_ip_used_times = 65
    packs_info = {}

    def __init__(self, get_ip_url=None, get_pack_info_url=None,
                 add_white_ip_url=None, del_white_ip_url=None,
                 account_name=None, account_key=None, neek=None, appkey=None
                 ):
        self.get_ip_url = get_ip_url if get_ip_url else DEFAULT_GET_IP_URL
        self.get_pack_info_url = get_pack_info_url if get_pack_info_url else DEFAULT_GET_PACK_INFO_URL
        self.add_white_ip_url = add_white_ip_url if add_white_ip_url else DEFAULT_ADD_WHITE_IP_URL
        self.del_white_ip_url = del_white_ip_url if del_white_ip_url else DEFAULT_DEL_WHITE_IP_URL
        self.account_name = account_name if account_name else DEFAULT_ACCOUNT_NAME
        self._account_key = account_key if account_key else DEFAULT_ACCOUNT_KEY
        self.neek = neek if neek else DEFAULT_NEEK
        self._appkey = appkey if appkey else DEFAULT_APPKEY

    def get_ips(self, pack_id, ip_nums=1, proxy_regions=None, times=0):
        if times >= 10:
            return False
        if proxy_regions is None:
            proxy_regions = []
        print(f'Get new proxy IPs ... ({times} times)')
        try:
            url = f'{self.get_ip_url}' + \
                  f'?num={ip_nums}&type=2&pro=0&city=0&yys=0&port=11&' + \
                  f'pack={pack_id}&ts=1&ys=1&cs=1&lb=1&sb=0&pb=4&mr=0&regions=' + \
                  ','.join(proxy_regions)
            res = urlopen(url, timeout=2).read().decode('utf-8')
            res_json = json.loads(res)

            if res_json.get('code', -1) > 0:
                my_ip = get_my_ip()
                if my_ip:
                    self.add_white_ip(my_ip)
                time.sleep(5)
                return self.get_ips(pack_id, ip_nums, proxy_regions, times=times + 1)
            elif res_json.get('success', False):
                ips = res_json.get('data', {})
                return ips
            return False
        except Exception as e:
            print(f'Get new proxy IPs FAILED. {e}')
            return False

    def get_pack_info(self, count=0):
        try:
            if len(self.packs_info) > 0:
                return self.packs_info
            if count >= 10:
                return False
            self.get_pack_info_count += 1
            print(f'Get Proxy Pack Info ({count} times)')
            gpi_url = f'{self.get_pack_info_url}?neek={self.neek}&appkey={self._appkey}'
            gpi_json = urlopen(gpi_url, timeout=4).read().decode('utf-8')
            self.packs_info = json.loads(gpi_json)
            return self.packs_info
        except Exception as e:
            print(f'No Available Packs!!! 10s Later Retry...({count} times)')
            print(e)
            my_ip = get_my_ip()
            if my_ip:
                self.add_white_ip(my_ip)
            time.sleep(10)
            return self.get_pack_info(count=count + 1)

    def check_and_add_white_ip(self):
        my_ip = get_my_ip()
        if my_ip:
            self.add_white_ip(my_ip)
        time.sleep(5)
        return my_ip

    def add_white_ip(self, ip):
        try:
            add_ip_url = f'{self.add_white_ip_url}?neek={self.account_name}&appkey={self._account_key}&white={ip}'
            res = urlopen(add_ip_url, timeout=2).read().decode('utf-8')
            res_json = json.loads(res)
            if res_json['success']:
                print(f'Add white ip:{ip}')
                return True
        except Exception as e:
            print(f'Add white ip ({ip}) FAILED.')
            print(e)
            return False

    def del_white_ip(self):
        pass

    @staticmethod
    def check_pack_usable(pack):
        all_num = int(pack['all_num'])
        balance = int(pack['balance'])
        name = pack['name']
        near_fill_time = pack['near_fill_time']
        now_timestamps = time.time()
        if name == '包年套餐':
            if all_num > 0:
                return True
            return False
        elif name == '单月包量套餐':
            if (balance > 0) and (near_fill_time is None or now_timestamps < near_fill_time):
                return True
        else:
            return False

    def check_ip_usable(self, ip: ProxyIP, expire_seconds: int = 120):
        if ip.used_times >= self.max_ip_used_times:
            return False
        now = datetime.datetime.now()
        if ip.expire_time <= now:
            return False
        c = ip.expire_time - now
        if c.seconds < expire_seconds:
            return False
        return True


if __name__ == '__main__':
    # 功能测试
    import environ
    from we_pyutils.env import GetEnv

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(BASE_DIR)))
    HOME_DIR = os.path.expanduser('~')
    dir_list = [
        BASE_DIR,
        PROJECT_DIR,
        HOME_DIR,
    ]

    e = GetEnv(dir_list)
    env_path = e.get_env()
    env = environ.Env()
    if env_path:
        env.read_env(env_path)
    get_ip_url = env.str('PROXY_TY_GET_IP_URL', '')
    get_pack_info_url = env.str('PROXY_TY_GET_PACK_INFO_URL', '')
    add_white_ip_url = env.str('PROXY_TY_ADD_WHITE_IP_URL', '')
    del_white_ip_url = env.str('PROXY_TY_DEL_WHITE_IP_URL', '')
    account_name = env.str('PROXY_TY_ACCOUNT_NAME', '')
    account_key = env.str('PROXY_TY_ACCOUNT_KEY', '')
    neek = env.str('PROXY_TY_NEEK', '')
    appkey = env.str('PROXY_TY_APPKEY', '')

    proxy = ProxyTYClient(
        get_ip_url, get_pack_info_url,
        add_white_ip_url, del_white_ip_url,
        account_name, account_key, neek, appkey
    )
    pass
