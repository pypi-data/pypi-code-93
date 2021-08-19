# -*- coding: utf-8 -*-

# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# KaisaGlobal rights are reserved.
# Quote data
# ===================================================================

import sys
from os.path import dirname, abspath
import requests, datetime
import pandas as pd
import numpy as np
import json, time
from com import *
from pub_cls_com import *

def to_get_all_data(body, URL, all_pages):
    # 统一获取数据的接口
    __ = pd.DataFrame()
    for p in range(1, all_pages + 1):
        body['pageNum'] = p

        _values_ = total_handle_hist_data_req(body, URL=URL)
        _t_df_ = pd.DataFrame(_values_)
        __ = pd.concat([__, _t_df_])

    return __


def __handle_hist_data_ex_ret(code_list=['00700'],
                              start_date=None,
                              end_date=None,
                              unit='1d',
                              market=100,
                              page=1,
                              fre='',
                              data_type=None):
    # 获取历史历史K线数据
    try:
        update_url = lambda url: url.replace("__kaisarooturl__", KAISA_ROOT_URL)
        if data_type is None or data_type not in ORI_DATA_TYPE_LIST:
            return DATETYPE_ERROR

        if market in [3, 1]:
            return ONLY_HK_MARKET_ERROR
        if start_date is None and end_date is None:
            return PUB_DATENONE_ERROR
        if start_date is not None and end_date is None:
            end_date = start_date
        if start_date is None and end_date is not None:

            start_date = end_date
        if start_date is not None and end_date is not None:
            if start_date > end_date:
                return PUB_SMALLENDDATE_ERROR

        if len(code_list) == 0:
            return LOSSCODES_ERROR
        code_market_types = HistQuote_MARKET_DICT[market]

        s_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        e_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        if data_type == KLINE:

            if len(code_list) == 1:
                day_count = (e_dt - s_dt).days
                if day_count > 365 * 10:
                    return OUTDATEFOR10_ERROR

            if len(code_list) > 1:
                day_count = (e_dt - s_dt).days
                if day_count > 30 * 1:
                    return OUTDATEFOR1MON_ERROR
            code_list = [code.upper() for code in code_list]

            if unit not in K_QUOTE_TYPE_DICT.keys():
                return WRIONGUNIT_ERROR

            if fre not in FRE_PRE_DICT.keys():
                return FRE_ERROR
            fre = FRE_PRE_DICT[fre]
            body = {
                "codes": code_list,
                "market": code_market_types,
                "quoteType": K_QUOTE_TYPE_DICT[unit],
                "startDate": start_date,
                "endDate": end_date,
                "adjFactorType": fre,
                "pageNum": page,
                "pageSize": 1000
            }

            URL = update_url(HK_STOCK_KLINE_POST_URL)   # HK_STOCK_KLINE_POST_URL
            _pages_ = handle_hist_data_req_pages(body=body, URL=URL)
            ori_cols = KLINE_ORI_COLS
            res_cols = KLINE_RES_COLS

        else:
            body = {
                "codes": code_list,
                "market": code_market_types,
                "startDate": start_date,
                "endDate": end_date,
                "pageNum": page,
                "pageSize": 1000
            }
            if data_type == TICKER:
                URL = update_url(HK_STOCK_TICK_POST_URL)  # HK_STOCK_TICK_POST_URL
                ori_cols = TICKER_ORI_COLS
                res_cols = TICKER_RES_COLS
            elif data_type == BROKER:
                URL = update_url(HK_STOCK_BROKER_URL)
                ori_cols = BROKER_ORI_COLS
                res_cols = BROKER_RES_COLS
                print('url:{}'.format(URL))
                print('ori_cols:{}'.format(ori_cols))
                print('res_cols:{}'.format(res_cols))

            elif data_type == LEVEL10:
                URL = update_url(HK_STOCK_LEVEL2_10_ORDER_URL)
                ori_cols = LEVEL10_ORI_COLS
                res_cols = LEVEL10_RES_COLS
            else:
                URL = ''
                ori_cols = []
                res_cols = []
            day_count = (e_dt - s_dt).days
            if day_count > 1:
                return '{},{}数据, {}'.format(PUB_HELLO, data_type, ONEDAYUPDATE_ERROR)

        _pages_ = handle_hist_data_req_pages(body=body, URL=URL)

        __ = to_get_all_data(body, URL, _pages_)
        __ = __.sort_values(by=['assetId'])
        __ = __[ori_cols]
        if data_type == KLINE:
            __[KLINE_TIMESTAMP] = [change_timestamp(dtt) for dtt in __[KLINE_TIMESTAMP]]

            __.sort_values(by=[KLINE_TIMESTAMP], inplace=True)
        __.columns = res_cols

        return __
    except Exception as xp:
        return '{}, 您填入的参数有误:{}, 请检查后重新请求!'.format(PUB_HELLO, xp)




def get_history_kline_data(code_list=['00700'], start_date=None, end_date=None, unit='', market=2, fre='pre'):
    '''
    # 获取合约代码历史区间K线数据
    '''

    __ = __handle_hist_data_ex_ret(code_list,
                                   start_date,
                                   end_date,
                                   unit=unit,
                                   market=market,
                                   page=1,
                                   fre=fre,
                                   data_type='Kline')

    return __

def get_history_ticker_data(code_list=['00700'], start_date=None, end_date=None, market=2):
    '''
    # 获取历史逐笔数据
    '''
    __ = __handle_hist_data_ex_ret(code_list, start_date, end_date, market=market, data_type='ticker')

    return __

def get_history_broker_data(code_list=['00700'], start_date=None, end_date=None, market=2):
    '''
    # 获取历史经纪商数据
    '''
    __ = __handle_hist_data_ex_ret(code_list, start_date, end_date, market=market, data_type='broker')

    return __

def get_history_level10_data(code_list=['00700'], start_date=None, end_date=None, market=2):
    '''
    # 获取历史Level10档盘口数据
    '''
    __ = __handle_hist_data_ex_ret(code_list, start_date, end_date, market=market, data_type='level10')

    return __

if __name__ == '__main__':
    pass




