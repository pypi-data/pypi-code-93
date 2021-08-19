# -*- coding: utf-8 -*-

from ..util.helper import (get, post)


def get_bf_chain_version(base_url):
    """
    获得Bfchain版本号: https://bfcc.dev/api/pc/1-2.html#_1-%E8%8E%B7%E5%BE%97bfchain%E7%89%88%E6%9C%AC%E5%8F%B7
    :param base_url: 基础URL
    :return: 请求成功时的返回值
    """
    url = base_url + '/api/basic/getBfchainVersion'
    return get(url, {})


def get_last_block(base_url):
    """
    获取本地节点当前最新区块: https://bfcc.dev/api/pc/1-2.html#_2-%E8%8E%B7%E5%8F%96%E6%9C%AC%E5%9C%B0%E8%8A%82%E7%82%B9%E5%BD%93%E5%89%8D%E6%9C%80%E6%96%B0%E5%8C%BA%E5%9D%97
    :param base_url: 基础URL
    :return: 请求成功时的返回值
    """
    url = base_url + '/api/basic/getLastBlock'
    return get(url, {})


def get_block(base_url, data=None):
    """
    获取指定区块: https://bfcc.dev/api/pc/1-2.html#_3-%E8%8E%B7%E5%8F%96%E6%8C%87%E5%AE%9A%E5%8C%BA%E5%9D%97
    :param base_url: 基础URL
    :param data: 请求数据
    :return: 请求成功时的返回值
    """
    if data is None:
        data = {}
    url = base_url + '/api/basic/getBlock'
    return post(url, data)


def get_transactions(base_url, data=None):
    """
    获取指定事件: https://bfcc.dev/api/pc/1-2.html#_4-%E8%8E%B7%E5%8F%96%E6%8C%87%E5%AE%9A%E4%BA%8B%E4%BB%B6
    :param base_url: 基础URL
    :param data: 请求数据
    :return: 请求成功时的返回值
    """
    if data is None:
        data = {}
    url = base_url + '/api/basic/getTransactions'
    return post(url, data)


def get_account_last_transaction(base_url, data=None):
    """
    获取账户的最后一笔交易: https://bfcc.dev/api/pc/1-2.html#_5-%E8%8E%B7%E5%8F%96%E8%B4%A6%E6%88%B7%E7%9A%84%E6%9C%80%E5%90%8E%E4%B8%80%E7%AC%94%E4%BA%A4%E6%98%93
    :param base_url: 基础URL
    :param data: 请求数据
    :return: 请求成功时的返回值
    """
    if data is None:
        data = {}
    url = base_url + '/api/basic/getAccountLastTransaction'
    return post(url, data)


def create_account(base_url, data=None):
    """
    创建账户: https://bfcc.dev/api/pc/1-2.html#_6-%E5%88%9B%E5%BB%BA%E8%B4%A6%E6%88%B7
    :param base_url: 基础URL
    :param data: 请求数据
    :return: 请求成功时的返回值
    """
    if data is None:
        data = {}
    url = base_url + '/api/basic/createAccount'
    return post(url, data)


def get_block_chain_status(base_url, data=None):
    """
    获取节点状态: https://bfcc.dev/api/pc/1-2.html#_7-%E8%8E%B7%E5%8F%96%E8%8A%82%E7%82%B9%E7%8A%B6%E6%80%81
    :param base_url: 基础URL
    :param data: 请求数据
    :return: 请求成功时的返回值
    """
    if data is None:
        data = {}
    url = base_url + '/api/basic/getBlockChainStatus'
    return get(url, data)


def get_account_last_type_transaction(base_url, data=None):
    """
    根据交易类型获取账户的最后一笔交易: https://bfcc.dev/api/pc/1-2.html#_8-%E6%A0%B9%E6%8D%AE%E4%BA%A4%E6%98%93%E7%B1%BB%E5%9E%8B%E8%8E%B7%E5%8F%96%E8%B4%A6%E6%88%B7%E7%9A%84%E6%9C%80%E5%90%8E%E4%B8%80%E7%AC%94%E4%BA%A4%E6%98%93
    :param base_url:
    :param data:
    :return:
    """
    if data is None:
        data = {}
    url = base_url + '/api/basic/getAccountLastTypeTransaction'
    return post(url, data)