#!/usr/bin/env python
# -*- coding: utf-8 -*-

import warnings

from .base_utils import (AioQueue, DefaultDict, Dict, DictUnwrapper,
                         DictWrapper, JSONEncoder, Queue, Singleton, awaitable,
                         ceil, connect, floor, get_ip, int2ip, int2str, ip2int,
                         pprint, str2int, to_bytes, to_str, tqdm, yaml_dump,
                         yaml_load)
from .cached_property import cached_property
from .config_utils import Config
from .crypt import Crypt
from .db_utils import (AioMysql, AioRedis, Mongo, MongoClient, Motor,
                       MotorClient, Mysql, Redis, parse_uri)
from .decorator import aioretry, retry, smart_decorator, synchronize, timeit
from .email_utils import AioEmail, Email
from .fire import Fire
from .http_utils import Chrome, Response, patch_connection_pool
from .ip2region import Ip2Region
from .log_utils import Logger, WatchedFileHandler
from .rabbitmq import AioPika, Pika

try:
    import pycurl  # noqa

    from .curl_utils import Request
except:
    from .http_utils import Request

warnings.filterwarnings("ignore")

__all__ = [
    'awaitable', 'floor', 'ceil', 'to_str', 'to_bytes', 'tqdm', 'yaml_load', 'yaml_dump', 'pprint',
    'timeit', 'retry', 'aioretry', 'smart_decorator', 'synchronize', 'cached_property',
    'get_ip', 'connect', 'ip2int', 'int2ip', 'int2str', 'str2int', 'patch_connection_pool', 'parse_uri',
    'Fire', 'Ip2Region', 'Singleton', 'JSONEncoder',
    'Dict', 'DefaultDict', 'DictWrapper', 'DictUnwrapper',
    'Email', 'AioEmail', 'Queue', 'AioQueue',
    'Config', 'Logger', 'WatchedFileHandler',
    'Mongo', 'MongoClient', 'Redis', 'AioRedis', 'Motor', 'MotorClient',
    'Mysql', 'AioMysql', 'Pika', 'AioPika',
    'Request', 'Response', 'Chrome', 'Crypt'
]
