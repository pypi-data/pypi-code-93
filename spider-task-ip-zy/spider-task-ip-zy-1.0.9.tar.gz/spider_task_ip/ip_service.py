# -*- coding: utf-8 -*-
# ===============================================================
#   @author: liheyou@zhiyitech.cn
#   @date: 2018/5/24 上午10:57
#   @brief: 维护代理队列

# ================================================================

import time
import logging
import json
import redis
import traceback
from .config import log_config


class IpService(object):

    def __init__(self, redis_config: dict = None, project_name: str = None,
                 spider_name: str = None, ip_queue_len: int = 0, ip_type_flag: str = ''):

        if redis_config is None or project_name is None or spider_name is None:
            raise Exception('redis_config or project_name or spider_name is None')

        self.ip_queue_len = ip_queue_len
        self.project_name = project_name
        self.spider_name = spider_name
        self.ip_type_flag = ''
        self.queue_redis_key = ''
        self.config_redis_key = ''

        self.set_ip_type_flag(ip_type_flag)

        redis_config = redis_config.copy()
        redis_config['db'] = 7
        redis_config['socket_timeout'] = 2
        self.pool = redis.ConnectionPool(**redis_config)
        self.redis_client = redis.Redis(connection_pool=self.pool)

        logging.basicConfig(**log_config)
        self.logger = logging.getLogger()

    def set_ip_type_flag(self, ip_type_flag: str = ''):
        if ip_type_flag:
            self.ip_type_flag = '_' + ip_type_flag.lower()
        self.queue_redis_key = f'(ip_queue{self.ip_type_flag})list_{self.project_name}_{self.spider_name}'
        self.config_redis_key = f'(ip_config{self.ip_type_flag})hash_{self.project_name}_{self.spider_name}'
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
            return int(ip_config.get(b'failed_num', 40))
        except:
            self.logger.warning(f'获取ip配置信息失败:: {self.config_redis_key}')
            return 40

    def set_ip_config(self, conf: dict = None):
        """
        :param conf: IP配置信息
        :return:
        """
        if conf is None:
            self.logger.warning('redis_config or value is None')
            return

        conf.setdefault('failed_num', 20)

        redis_key = f'(ip_config{self.ip_type_flag})hash_{conf["project_name"]}_{conf["spider_name"]}'
        self.redis_client.hmset(name=redis_key, mapping=conf)
        logging.info(f'ip队列名字: (ip_queue{self.ip_type_flag})list_{conf["project_name"]}_{conf["spider_name"]}')
        logging.info(f'配置信息: {self.redis_client.hgetall(redis_key)}')

    def get_ip(self):
        """
        获取IP数据
        :return: ip的数据
        """
        try:
            ip_data = self.redis_client.rpop(self.queue_redis_key)
            if isinstance(ip_data, (str, bytes)) and len(ip_data) > 0:
                return json.loads(ip_data)
        except:
            self.logger.warning(traceback.format_exc())
            self.redis_client = redis.Redis(connection_pool=self.pool)
            return None

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
            self.redis_client.lpush(self.queue_redis_key, json.dumps(ip_data))
            return True

        try:
            # 更新监控数据
            monitor_data = {
                'project_name': self.project_name,
                'spider_name': self.spider_name,
                'ip_name': ip_data['ip_name']
            }
            monitor_redis_key = f'(ip_monitor)hash_{self.project_name}_{self.spider_name}_{monitor_data["ip_name"]}'
            self.redis_client.hmset(monitor_redis_key, monitor_data)

            # 不管请求是否成功，都需要更新使用时间
            now_time = int(time.time())
            ip_data['use_last_time'] = now_time
            if status is True:  # 请求成功，把统计成功次数+1
                self.redis_client.hincrby(monitor_redis_key, 'success_num')
            elif status is False:  # 请求失败，更新失败次数、失败时间、并把统计失败次数+1
                ip_data['failed_num'] += 1
                ip_data['failed_last_time'] = now_time
                self.redis_client.hincrby(monitor_redis_key, 'failed_num')

            # expire_time = int(time.mktime(time.strptime(ip_data['expire_time'], '%Y-%m-%d %H:%M:%S')))
            failed_num = self._get_config()
            # if int(ip_data['failed_num']) < failed_num:
            # if now_time < expire_time and int(ip_data['failed_num']) < failed_num:
            if int(ip_data['failed_num']) < failed_num:
                # 不丢弃, 更新ip数据
                self.redis_client.lpush(self.queue_redis_key, json.dumps(ip_data))
            else:
                # 丢弃，并统计使用的ip次数
                self.redis_client.hincrby(monitor_redis_key, 'used_ip')
            return True
        except:
            self.redis_client.lpush(self.queue_redis_key, json.dumps(ip_data))
            self.logger.warning(f'存放ip失败\n{traceback.format_exc()}')
            return False


class IpServiceSimple(object):

    def __init__(self, logger=None, redis_client=None, redis_config: dict = None):
        self.logger = logger
        self.redis_client = redis_client

        if not self.redis_client:
            redis_config = redis_config.copy()
            redis_config['db'] = 7
            redis_config['socket_timeout'] = 2
            self.pool = redis.ConnectionPool(**redis_config)
            self.redis_client = redis.Redis(connection_pool=self.pool)

        if not self.logger:
            logging.basicConfig(**log_config)
            self.logger = logging.getLogger()

    def get_ip(self, ip_type_flag: str, queue_name: str):
        """
        :param ip_type_flag:
        :param queue_name: {project_name}_{spider_name}
        :return:
        """
        try:
            if ip_type_flag:
                ip_type_flag = '_' + ip_type_flag.lower()
            queue_redis_key = f'(ip_queue{ip_type_flag})list_{queue_name}'

            ip_data = self.redis_client.rpop(queue_redis_key)
            if isinstance(ip_data, (str, bytes)) and len(ip_data) > 0:
                return json.loads(ip_data)
        except:
            self.logger.warning(traceback.format_exc())
            self.redis_client = redis.Redis(connection_pool=self.pool)
            return None

    def set_ip(self, ip_type_flag: str, queue_name: str, ip_data: dict = None, status: bool = None):
        """
        :param ip_type_flag: 代理类型标记
        :param queue_name: {project_name}_{spider_name}
        :param ip_data: ip数据
        :param status: None: 代理没有使用、True: 请求成功、False: 请求失败
        :return:
        """
        if not ip_data:
            return ip_data

        if ip_type_flag:
            ip_type_flag = '_' + ip_type_flag.lower()
        queue_redis_key = f'(ip_queue{ip_type_flag})list_{queue_name}'

        # 没有使用该ip，则直接放到队列，不进行任何数据的更新
        if status is None:
            self.redis_client.lpush(queue_redis_key, json.dumps(ip_data))
            return True

        try:
            # 不管请求是否成功，都需要更新使用时间
            now_time = int(time.time())
            ip_data['use_last_time'] = now_time
            if status is True:  # 请求成功，把统计成功次数+1
                pass
            elif status is False:  # 请求失败，更新失败次数、失败时间、并把统计失败次数+1
                ip_data['failed_num'] += 1
                ip_data['failed_last_time'] = now_time

            # expire_time = int(time.mktime(time.strptime(ip_data['expire_time'], '%Y-%m-%d %H:%M:%S')))
            failed_num = self._get_config()
            # if int(ip_data['failed_num']) < failed_num:
            # if now_time < expire_time and int(ip_data['failed_num']) < failed_num:
            if int(ip_data['failed_num']) < failed_num:
                # 不丢弃, 更新ip数据
                self.redis_client.lpush(queue_redis_key, json.dumps(ip_data))
            else:
                # 丢弃，并统计使用的ip次数
                pass
            return True
        except:
            self.redis_client.lpush(queue_redis_key, json.dumps(ip_data))
            self.logger.warning(f'存放ip失败\n{traceback.format_exc()}')
            return False

    def _get_config(self, ip_type_flag: str, queue_name: str):
        """
        获取配置信息，主要是额定失败次数
        :param ip_type_flag: 代理类型标记
        :param queue_name: {project_name}_{spider_name}
        :return:
        """
        try:
            if ip_type_flag:
                ip_type_flag = '_' + ip_type_flag.lower()
            redis_key = f'(ip_config{ip_type_flag})hash_{queue_name}'

            ip_config = self.redis_client.hgetall(redis_key)
            return int(ip_config.get(b'failed_num', 40))
        except:
            self.logger.warning(f'获取ip配置信息失败')
            return 40

    def set_ip_config(self, ip_type_flag: str, queue_name: str, conf: dict = None):
        """
        :param ip_type_flag: 代理类型标记
        :param queue_name: {project_name}_{spider_name}
        :param conf: IP配置信息
        :return:
        """
        if conf is None:
            self.logger.warning('config or value is None')
            return

        conf.setdefault('failed_num', 20)

        if ip_type_flag:
            ip_type_flag = '_' + ip_type_flag.lower()
        redis_key = f'(ip_config{ip_type_flag})hash_{queue_name}'

        self.redis_client.hmset(name=redis_key, mapping=conf)
        logging.info(f'ip队列名字: {redis_key}')
        logging.info(f'配置信息: {self.redis_client.hgetall(redis_key)}')
