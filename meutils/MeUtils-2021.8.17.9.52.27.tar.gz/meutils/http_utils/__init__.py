#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : MeUtils.
# @File         : http_utils
# @Time         : 2020/11/12 11:49 上午
# @Author       : yuanjie
# @Email        : yuanjie@xiaomi.com
# @Software     : PyCharm
# @Description  :

import requests

from loguru import logger
from tenacity import retry, stop_after_delay, stop_after_attempt, wait_fixed


@retry(wait=wait_fixed(3),  # 重试之前等待3秒
       stop=stop_after_delay(7) | stop_after_attempt(3),  # 同时满足用 | 没毛病：重试7秒重试3次
       retry_error_callback=lambda log: logger.error(log),
       reraise=True)
# @lru_cache()
def request(url=None, json=None, parser=lambda x: x, **kwargs):
    """

    :param url:
    :param json:
    :param parser: None 的时候返回r，否则返回 parser(r.json())
    :param kwargs:
    :return:
    """
    method = 'post' if json is not None else 'get'  # 特殊情况除外
    logger.info(f"Request Method: {method}")
    r = requests.request(method, url, json=json)

    r.encoding = r.apparent_encoding
    if parser is None:
        return r
    return parser(r.json())
