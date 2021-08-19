# -*- coding: utf-8 -*-


from src.util.helper import (get, post,get_address,get_pk_sk_from_mnemonic_words)


def tr_dapp(base_url, data=None):
    """
    创建发行 dapp 事件: https://bfcc.dev/api/pc/1-3.html#_8-1-%E5%88%9B%E5%BB%BA%E5%8F%91%E8%A1%8C-dapp-%E4%BA%8B%E4%BB%B6
    :param base_url: 基础URL
    :param data: 基础数据
    :return: 请求成功时的返回值
    """
    if data is None:
        data = {}
    url = base_url + '/api/transaction/trDapp'
    return post(url, data)


def tr_dapp_with_sign(base_url, data=None):
    """
    创建发行 dapp 事件(带安全密钥): https://bfcc.dev/api/pc/1-3.html#_8-2-%E5%88%9B%E5%BB%BA%E5%8F%91%E8%A1%8C-dapp-%E4%BA%8B%E4%BB%B6-%E5%B8%A6%E5%AE%89%E5%85%A8%E5%AF%86%E9%92%A5
    :param base_url: 基础URL
    :param data: 基础数据
    :return: 请求成功时的返回值
    """
    if data is None:
        data = {}
    url = base_url + '/api/transaction/trDappWithSign'
    return post(url, data)


def dapp(base_url, data=None):
    """
    发送发行 dapp 事件: https://bfcc.dev/api/pc/1-3.html#_8-3-%E5%8F%91%E9%80%81%E5%8F%91%E8%A1%8C-dapp-%E4%BA%8B%E4%BB%B6
    :param base_url: 基础URL
    :param data: 基础数据
    :return: 请求成功时的返回值
    """
    if data is None:
        data = {}
    url = base_url + '/api/transaction/send/dapp'
    return post(url, data)


def tr_dapp_purchasing(base_url, data=None):
    """
    创建 dapp 购买事件: https://bfcc.dev/api/pc/1-3.html#_9-1-%E5%88%9B%E5%BB%BA-dapp-%E8%B4%AD%E4%B9%B0%E4%BA%8B%E4%BB%B6
    :param base_url: 基础URL
    :param data: 基础数据
    :return:
    """
    if data is None:
        data = {}
    url = base_url + '/api/transaction/trDappPurchasing'
    return post(url, data)


def tr_dapp_purchasing_with_sign(base_url, data=None):
    """
    创建 dapp 购买事件(带安全密钥): https://bfcc.dev/api/pc/1-3.html#_9-2-%E5%88%9B%E5%BB%BA-dapp-%E8%B4%AD%E4%B9%B0%E4%BA%8B%E4%BB%B6-%E5%B8%A6%E5%AE%89%E5%85%A8%E5%AF%86%E9%92%A5
    :param base_url: 基础URL
    :param data: 基础数据
    :return:
    """
    if data is None:
        data = {}
    url = base_url + '/api/transaction/trDappPurchasingWithSign'
    return post(url, data)


def dapp_purchasing(base_url, data=None):
    """
    创建 dapp 购买事件(带安全密钥): https://bfcc.dev/api/pc/1-3.html#_9-3-%E5%8F%91%E9%80%81-dapp-%E8%B4%AD%E4%B9%B0%E4%BA%8B%E4%BB%B6
    :param base_url: 基础URL
    :param data: 基础数据
    :return:
    """
    if data is None:
        data = {}
    url = base_url + '/api/transaction/send/dappPurchasing'
    return post(url, data)