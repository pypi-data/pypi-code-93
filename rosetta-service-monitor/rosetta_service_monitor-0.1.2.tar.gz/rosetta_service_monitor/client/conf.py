#!/usr/bin/env python  
# -*- coding:utf-8 _*-
""" 
@author: xl
@file: conf.py 
@time: 2021/08/09
@contact: 
@site:  
@software: PyCharm 
"""
import os

import attrdict
from dotenv import load_dotenv
from loguru import logger

load_dotenv(verbose=True)

MQ_SERVER = os.environ.get('MQ_SERVER', '')
TOPIC = os.environ.get('TOPIC', '')
FEI_SHU = os.environ.get('FEI_SHU', '')
DISABLE_SERVICE_MONITOR_MQ = os.environ.get('DISABLE_SERVICE_MONITOR_MQ', "True")

KAFKA_CONFIG = attrdict.AttrDict({
    'TOPIC': TOPIC,
    'KAFKA_SERVER': MQ_SERVER.strip().split('|'),

})

CONF = attrdict.AttrDict({
    "KAFKA_CONFIG": KAFKA_CONFIG,
    "FEI_SHU": FEI_SHU,
    'DISABLE_SERVICE_MONITOR_MQ': DISABLE_SERVICE_MONITOR_MQ == "FALSE"
})

logger.info(CONF)
