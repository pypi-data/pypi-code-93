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
from requests import get, post
from tenacity import retry, stop_after_delay, stop_after_attempt, wait_fixed

from meutils.zk_utils import zk_cfg


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


#############todo: 以下将弃用

@logger.catch()
def get_articleinfo(docid):
    return get(f"{zk_cfg.ac_assistant_url}/{docid}").json().get('item', {})


@logger.catch()
def get_simbert_vectors(titles):
    if isinstance(titles, str):
        titles = [titles]
    return post(f"{zk_cfg.simbert_url}", json={"texts": titles}).json().get('vectors')  # [[...]]


@logger.catch()
def ann_search(url, text='不知道', topk=5, vector_name='embedding', fields=None, only_return_ids=False):
    query_embeddings = get_simbert_vectors(text)
    body = {
        "query": {
            "bool": {
                "must": [
                    {
                        "vector": {
                            vector_name: {
                                "topk": topk,
                                "values": query_embeddings,
                                "metric_type": "IP",
                                "params": {
                                    "nprobe": 1
                                }
                            }
                        }
                    }
                ]
            }
        },
        "fields": fields if fields else []
    }

    r = get(url, json=body).json()
    if only_return_ids:
        return [i['id'] for i in r['data']['result'][0]]
    else:
        return r


@logger.catch()
def mongo_find(collection, attribute='find_one', filter_=None):
    if filter_ is None:
        filter_ = {}
    r = get(f"{zk_cfg.mongo_find_url}/{collection}/{attribute}?filter={filter_}").json()
    return r.get(f"{collection}.{attribute}", {})


if __name__ == '__main__':
    # from pprint import pprint
    #
    # title = '社区团购“团战”正酣，变革与较量中如何走出“最优”路径'
    # pprint(
    #     ann_search(
    #         zk_cfg.nh_choice_search_url,
    #         text=title,
    #         topk=5,
    #         only_return_ids=False,
    #         vector_name='title_vec',
    #         fields=[],
    #     )
    # )
    #
    # ids = ann_search(
    #     zk_cfg.nh_choice_search_url,
    #     text=title,
    #     topk=5,
    #     only_return_ids=True,
    #     vector_name='title_vec',
    #     fields=[],
    # )
    # for id in ids:
    #     print(mongo_find('nh_choice', filter_={'ann_id': int(id)}).get('title'))

    # print(mongo_find('nh_choice', filter_={'ann_id': 1607597490101257887}))

    request()
