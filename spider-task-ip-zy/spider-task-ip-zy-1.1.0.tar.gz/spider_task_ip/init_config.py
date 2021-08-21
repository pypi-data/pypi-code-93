# ===============================================================
# -*- coding: utf-8 -*-
# @Author  : liheyou@zhiyitech.cn
# @Date    : 2018/9/19 下午6:46
# @Brief   : 
# ===============================================================
import json
import redis
import logging
from .config import log_config

logging.basicConfig(**log_config)
logger = logging.getLogger()


def ip_config(redis_config: dict = None, values: list = None, ip_type_flag: str = ''):
    """
    :param redis_config: redis配置
    :param values: IP配置信息
    :return:
    """
    if redis_config is None or values is None:
        logger.warning('redis_config or values is None')
        return
    redis_config = redis_config.copy()
    redis_config['db'] = 7

    pool = redis.ConnectionPool(**redis_config)
    redis_client = redis.Redis(connection_pool=pool)

    if ip_type_flag:
        ip_type_flag = '_' + ip_type_flag.lower()

    for value in values:
        value.setdefault('failed_num', 20)
        redis_key = f'(ip_config{ip_type_flag})hash_{value["project_name"]}_{value["spider_name"]}'
        redis_client.hmset(name=redis_key, mapping=value)
        logging.info(f'ip队列名字: (ip_queue{ip_type_flag})list_{value["project_name"]}_{value["spider_name"]}')
        logging.info(f'配置信息: {redis_client.hgetall(redis_key)}')
