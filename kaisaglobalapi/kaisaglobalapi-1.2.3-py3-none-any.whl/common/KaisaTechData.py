
# -*- coding: utf-8 -*-

# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# KaisaGlobal rights are reserved.
# Technical index data
# ===================================================================
import sys
from os.path import dirname, abspath
import requests, datetime
import pandas as pd
import numpy as np
import json
from common.com import *
from pub_cls_com import *
'''Date: 2021.03.16'''

def _handle_ex_ret(code_list=['00700'], queryType=None, start_date=None, end_date=None, market=2, unit='1d', page=1, fre=2):

    # 查询最长周期: 1年时间
    if unit != '1d':
        return TECH_ONLY_DAY_DATA_ERROR
    if market == 3 or market == 1:
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
        s_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        e_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d')

        day_count = (e_dt - s_dt).days
        if day_count > 365 * 1:
            return TECH_ONLY_1_YEAR_DATA_ERROR
    body = {
        "codeList": code_list,
        "market": market,
        "queryType": queryType,
        "startDate": start_date,
        "endDate": end_date,
        "unit": unit,
        "ifRehabili": fre,
        "current": page,
        "size": 100
    }
    update_url = lambda url: url.replace("__kaisarooturl__", KAISA_ROOT_URL)
    df_ = total_handle_req(body=body, URL=update_url(BE_TECH_POST_URL))

    return df_

###### 基础类技术面指标
def get_sar_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
        获取SAR技术指标数据
        Args:
            code_list: 合约列表
            queryType:数据类型
            market: 市场类型：1 CH/ 2 HK/ 3 USA
            unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
            start_date: 开始日期
            end_date: 结束日期
            fre:是否复权  1 不复权/2 前复权/3 后复权
        Returns: 返回因子数据
    '''
    factor_names = ['SecuCode', 'Trend', 'WhetherTurn', 'AF', 'SAR1', 'SAR2', 'TradingDay']
    data_type = 'tradition'

    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_obv_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取OBV技术指标数据
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权  1 不复权/2 前复权/3 后复权
    Returns: 返回因子数据
    '''
    factor_names = ['SecuCode', 'OBV', 'TradingDay']
    data_type = 'tradition'

    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_boll_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取BOLL技术指标数据
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权  1 不复权/2 前复权/3 后复权
    Returns: 返回因子数据
    '''
    factor_names = ['SecuCode', 'MID', 'UPPERValue', 'LOWERValue', 'TradingDay']
    data_type = 'tradition'
    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    try:
        __.columns = ['SecuCode', 'MidLine', 'UpLine', 'DownLine', 'TradingDay']
    except:
        return __
    return __

def get_wr_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取WR技术指标数据
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权  1 不复权/2 前复权/3 后复权
    Returns: 返回因子数据
    '''
    factor_names = ['SecuCode', 'WR6', 'WR10', 'WR13', 'WR34', 'WR89', 'TradingDay']
    data_type = 'tradition'
    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_rsi_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取RSI技术指标数据
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权  1 不复权/2 前复权/3 后复权
    Returns: 返回因子数据
    '''
    factor_names = ['SecuCode', 'RSI', 'RS', 'TradingDay']
    data_type = 'tradition'
    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_kdj_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取kdj技术指标数据
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权  1 不复权/2 前复权/3 后复权
    Returns: 返回因子数据
    '''
    factor_names = ['SecuCode', 'HighestInNine', 'LowestInNine', 'RSV', 'Kvalue', 'Dvalue', 'Jvalue', 'TradingDay']
    data_type = 'tradition'
    # f_data_ = _handle_ex_ret(code_list, data_type, start_date, end_date, market, unit, 1, fre)
    # __ = _get__(f_data_, factor_names, data_type, code_list, start_date, end_date, market, unit, fre)
    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_macd_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取macd技术指标数据
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权  1 不复权/2 前复权/3 后复权
    Returns: 返回因子数据
    '''
    factor_names = ['SecuCode', 'EMA12', 'EMA26', 'DIF', 'DEA', 'MACD', 'TradingDay']
    data_type = 'tradition'
    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def _get__(f_data_, factor_names, data_type, code_list, start_date, end_date, market, unit, fre):
    '''
    Args:
        factor_names:  所选因子字段
        f_data_: 后台api返回的数据
        data_type: 技术指标类型 tradition 传统技术指标；derived 衍生技术指标
        code_list: 合约列表
        start_date: 开始日期
        end_date: 结束日期
        market: 市场类型 1 CH/ 2 HK/ 3 USA
        unit: 频率 默认 '1d' 日级别数据
        fre: 是否复权  1 不复权/2 前复权/3 后复权
    Returns:
    '''

    pageSize = f_data_['totalPage']
    page1_data = f_data_['result']
    res_df = pd.DataFrame(page1_data)
    if pageSize > 1:
        res_df = _get_other_data(res_df, factor_names, pageSize, data_type, code_list, start_date, end_date, market, unit, fre)
    __ = res_df[factor_names]
    __ = __.reset_index(drop=True)
    return __

def _get_other_data(page1_data, factor_names, page_size, data_type, code_list, start_date, end_date, market, unit, fre=2):
    # 获取剩下页码的数据
    df1_ = page1_data.copy()
    for pageC in range(2, page_size + 1):
        profit_data_next = _handle_ex_ret(code_list, data_type, start_date, end_date, market, unit, pageC, fre)

        page_n_data = profit_data_next['result']
        df1_ = pd.concat([df1_, pd.DataFrame(page_n_data)], axis=0)
    return df1_

##### 衍生类技术面指标
def get_hbeta_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取Hbeta技术指标数据
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权 默认不复权
    Returns: 返回macd的因子数据
    '''
    factor_names = ['secu_code', 'hbeta', 'trading_day']
    data_type = 'derived'
    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_halpha_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取Halpha技术指标数据
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权 默认不复权
    Returns: 返回macd的因子数据
    '''
    factor_names = ['secu_code', 'halpha', 'trading_day']
    data_type = 'derived'
    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_hsigma_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取Hsigma技术指标数据
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权 默认不复权
    Returns: 返回macd的因子数据
    '''
    factor_names = ['secu_code', 'hsigma', 'trading_day']
    data_type = 'derived'
    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_dmsens_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取Dmsens技术指标数据
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权 默认不复权
    Returns: 返回macd的因子数据
    '''
    factor_names = ['secu_code', 'dmsens', 'trading_day']
    data_type = 'derived'
    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_oilsen_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取Oilsen技术指标数据
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权 默认不复权
    Returns: 返回macd的因子数据
    '''
    factor_names = ['secu_code', 'oilsen', 'trading_day']
    data_type = 'derived'
    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_dsbeta_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取Dsbeta技术指标数据
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权 默认不复权
    Returns: 返回macd的因子数据
    '''
    factor_names = ['secu_code', 'dsbeta', 'trading_day']
    data_type = 'derived'
    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_cmra_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取Cmra技术指标数据
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权 默认不复权
    Returns: 返回macd的因子数据
    '''
    factor_names = ['secu_code', 'cmra', 'trading_day']
    data_type = 'derived'
    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_stom_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取Stom技术指标数据
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权 默认不复权
    Returns: 返回macd的因子数据
    '''
    factor_names = ['secu_code', 'stom', 'trading_day']
    data_type = 'derived'
    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_stoq_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取Stoq技术指标数据
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权 默认不复权
    Returns: 返回macd的因子数据
    '''
    factor_names = ['secu_code', 'stoq', 'trading_day']
    data_type = 'derived'
    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_stoa_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取Stoa技术指标数据
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权 默认不复权
    Returns: 返回macd的因子数据
    '''
    factor_names = ['secu_code', 'stoa', 'trading_day']
    data_type = 'derived'

    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_dastd_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取中期波动率技术指标数据  Dastd
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权 默认不复权
    Returns: 返回macd的因子数据
    '''
    factor_names = ['secu_code', 'dastd', 'trading_day']
    data_type = 'derived'

    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_season_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取周期性技术指标数据 Season
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权 默认不复权
    Returns: 返回因子数据
    '''
    factor_names = ['secu_code', 'season', 'trading_day']
    data_type = 'derived'

    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_rstr_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取中期动量技术指标数据  Rstr
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权 默认不复权
    Returns: 返回因子数据
    '''
    factor_names = ['secu_code', 'rstr', 'trading_day']
    data_type = 'derived'

    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def get_strev_factor_data(code_list=['00700'], market=2, unit='1d', start_date=None, end_date=None, fre=2):
    '''
    获取短期反转技术指标数据  strev
    Args:
        code_list: 合约列表
        queryType:数据类型
        market: 市场类型：1 CH/ 2 HK/ 3 USA
        unit: 频率 默认为 '1d', 将支持如下周期: '5m', '15m', '30m', '1d', '1w', '1M'. '1w' 表示一周, '1M' 表示一月
        start_date: 开始日期
        end_date: 结束日期
        fre:是否复权 默认不复权
    Returns: 返回因子数据
    '''
    factor_names = ['secu_code', 'strev', 'trading_day']
    data_type = 'derived'

    __ = total_cls_handle(code_list, factor_names, data_type, start_date, end_date, market, unit, fre)
    return __

def total_cls_handle(code_list, factor_names, data_type=None, start_date=None, end_date=None, market=None, unit=None, fre=None):
    # 统一处理返回值
    try:
        code_list = list(set(code_list))
        f_data_ = _handle_ex_ret(code_list, data_type, start_date, end_date, market, unit, 1, fre)
        if t_typeof(f_data_) == 'str' or PUB_HELLO in f_data_ or PUB_SOR in f_data_:
            return f_data_
        if len(f_data_['result']) == 0:
            return PUB_WRONG_DATE_AROUND_ERROR
        __ = _get__(f_data_, factor_names, data_type, code_list, start_date, end_date, market, unit, fre)
    except Exception as xp:
        __ = xp
    return __


if __name__ == '__main__':
    pass
