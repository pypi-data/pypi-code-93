# -*- coding: utf-8 -*-
# ===============================================================
#   @author: liheyou@zhiyitech.cn
#   @date: 2018/5/24 上午10:57
#   @brief: 维护vps代理队列

# ================================================================

import time
import logging
import json
import redis
import random
import traceback
from .config import log_config


class IpVpsService(object):

    def __init__(self, redis_config: dict = None, project_name: str = None,
                 spider_name: str = None, ip_queue_len: int = 0, ip_type_flag: str = '', save_type: bool = True):

        if redis_config is None or project_name is None or spider_name is None:
            raise Exception('redis_config or project_name or spider_name is None')
        self.ip_queue_len = ip_queue_len
        self.project_name = project_name
        self.spider_name = spider_name
        self.ip_type_flag = ''
        self.queue_redis_key = ''
        self.config_redis_key = ''
        self.save_type = save_type
        redis_config = redis_config.copy()
        redis_config['db'] = 7
        redis_config['socket_timeout'] = 2
        self.pool = redis.ConnectionPool(**redis_config)
        self.redis_client = redis.Redis(connection_pool=self.pool)
        self.redis_type = self.get_redis_type()

        self.set_ip_type_flag(ip_type_flag)

        logging.basicConfig(**log_config)
        self.logger = logging.getLogger()

    def get_redis_type(self):
        self.redis_key = '(vps)ip_pool_config_hash'  # 配置队列
        redis_type = json.loads(self.redis_client.hget(self.redis_key, f'{self.project_name}_{self.spider_name}'))[
            'type']  # 获取key的类型
        return redis_type

    def set_ip_type_flag(self, ip_type_flag: str = ''):
        if ip_type_flag:
            self.ip_type_flag = '_' + ip_type_flag.lower()
        self.queue_redis_key = f'(vps)ip_pool_{self.redis_type}_{self.project_name}_{self.spider_name}'
        self.config_redis_key = self.redis_key
        if self.ip_queue_len > 0:
            conf = dict(project_name=self.project_name, spider_name=self.spider_name, rate_len=self.ip_queue_len)
            self.set_ip_config(conf)

    def _get_config(self):
        """
        获取配置信息，主要是额定失败次数
        :return:
        """
        try:
            ip_config = self.redis_client.hgetall(self.config_redis_key)
            return int(ip_config.get(b'failed_num', 20))
        except:
            self.logger.warning(f'获取ip配置信息失败:: {self.config_redis_key}')
            return 20

    def set_ip_config(self, conf: dict = None):
        """
        :param conf: IP配置信息
        :return:
        """
        if conf is None:
            self.logger.warning('redis_config or value is None')
            return

        conf.setdefault('failed_num', 20)

        logging.info(f'ip队列名字: (vps)ip_pool_{self.redis_type}_{conf["project_name"]}_{conf["spider_name"]}')
        logging.info(f'配置信息: {self.redis_client.hgetall(self.redis_type)}')

    def get_ip(self):
        """
        获取IP数据
        :return: ip的数据
        """
        try:
            if self.save_type:
                if self.redis_type == 'list':
                    key_len = self.redis_client.llen(self.queue_redis_key)
                    ip_data = self.redis_client.lindex(self.queue_redis_key, random.randint(0, (key_len - 1)))
                elif self.redis_type == 'set':
                    ip_data = self.redis_client.srandmember(self.queue_redis_key)
            else:
                if self.redis_type == 'list':
                    ip_data = self.redis_client.rpop(self.queue_redis_key)
                elif self.redis_type == 'set':
                    ip_data = self.redis_client.spop(self.queue_redis_key)
            if isinstance(ip_data, (str, bytes)) and len(ip_data) > 0:
                return json.loads(ip_data)
        except:
            self.logger.warning(traceback.format_exc())
            self.redis_client = redis.Redis(connection_pool=self.pool)
            return None

    def redis_save(self, ip_data):
        if self.redis_type == 'list':
            self.redis_client.lpush(self.queue_redis_key, json.dumps(ip_data))
        elif self.redis_type == 'set':
            self.redis_client.sadd(self.queue_redis_key, json.dumps(ip_data))

    def redis_del(self, ip_data):
        if self.redis_type == 'list':
            self.redis_client.lrem(self.queue_redis_key, json.dumps(ip_data), 0)
        elif self.redis_type == 'set':
            self.redis_client.srem(self.queue_redis_key, json.dumps(ip_data))

    def set_ip(self, ip_data: dict = None, status: bool = None):
        """
        返还ip
        :param ip_data: ip数据
        :param status: None: 代理没有使用、True: 请求成功、False: 请求失败
        :return:
        """
        if not ip_data:
            return ip_data

        # 没有使用该ip，则直接放到队列，不进行任何数据的更新
        if status is None:
            self.redis_save(ip_data=ip_data)
            return True

        try:
            copy_ip_data = ip_data.copy()
            if not ip_data.get('failed_num'):
                ip_data['failed_num'] = 0
            if status is True:
                return True
            elif status is False:
                ip_data['failed_num'] += 1
            failed_num = self._get_config()
            if int(ip_data['failed_num']) < failed_num:
                # 不丢弃, 更新ip数据
                self.redis_save(ip_data=ip_data)
                self.redis_del(ip_data=copy_ip_data)
            else:
                share_ip_data_value = self.redis_client.hget('(vps)hash_proxy_share_pool', ip_data['hash_key'])
                share_ip_data = json.loads(share_ip_data_value)['ip']
                self.redis_del(ip_data=copy_ip_data)
                if share_ip_data == ip_data['ip']:
                    # 丢弃，并更新(vps)hash_proxy_share_pool队列 need_switch为1
                    ip_data['need_switch'] = 1
                    self.redis_client.hset('(vps)hash_proxy_share_pool', ip_data['hash_key'], json.dumps(ip_data))

            return True
        except:
            self.redis_save(ip_data=ip_data)
            self.logger.warning(f'存放ip失败\n{traceback.format_exc()}')
            return False
