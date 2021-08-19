
# -*- coding: utf-8 -*-

# ===================================================================
# The contents of this file are dedicated to the public domain.  To
# the extent that dedication to the public domain is not available,
# everyone is granted a worldwide, perpetual, royalty-free,
# non-exclusive license to exercise all rights associated with the
# contents of this file for any purpose whatsoever.
# KaisaGlobal rights are reserved.
# FinanceData
# ===================================================================
import sys
from os.path import dirname, abspath
import requests, datetime
import pandas as pd
import numpy as np
import json
from common.com import *
from pub_cls_com import *
'''Date: 2021.03.15'''

################################财务数据##################################
###### 基础财务数据(主要财务数据、三大报表)
def _handle_req_ret(period, report_type, code, market):
    # 基础财务数据: 公共统一处理请求和返回数据
    # 市场类型: 港股：hkg，美股：usa, a股：chn
    # 市场类型：1 CH/ 2 HK/ 3 USA
    this_market = FIN_MARKET_TYPE_DICT[market]
    if t_typeof(code) != 'str':
        return FIN_NOE_CODE_ERROR
    if market == 'usa' or market == 'chn':
        return ONLY_HK_MARKET_ERROR
    if code is None:return FIN_LOSS_CODE_ERROR
    body = {
        "reportType": report_type,
        "periodMark": period,
        "stockCode": code,
        "stockMarket": this_market
    }
    update_url = lambda url: url.replace("__kaisarooturl__", KAISA_ROOT_URL)
    _df_ = total_handle_req(body=body, URL=update_url(BASIC_FIN_POST_URL))
    return _df_

def get_basic_fin_data(code='00700', market=2, period=12):
    '''
    periodMark	integer($int32) null-全部 3-一季度，6-半年度，9-三季度，12-年度
    reportType	string 1：主要指标
    stockCode	string 股票代码
    stockMarket	string 港股：hkg，美股：usa,a股：chn
    Returns:
        df:
        主要财务指标  季度/年度的财务数据
    '''
    report_type = '1'
    basic_fin_df = _handle_req_ret(period, report_type, code, market)

    return basic_fin_df

def get_income_fin_data(code='00700', market=2, period=12):
    '''
    Args:
        code: string 股票代码
        market: string 港股：hkg，美股：usa,a股：chn
        period: integer($int32) null-全部 3-一季度，6-半年度，9-三季度，12-年度
        report_type: string 2：利润表
    Returns:
        df:
        income 季度/年度的财务数据
    '''
    report_type = '2'
    income_fin_df = _handle_req_ret(period, report_type, code, market)

    return income_fin_df

def get_balance_fin_data(code='00700', market=2, period=12):
    '''
    Args:
        code: string 股票代码
        market: string 港股：hkg，美股：usa,a股：chn
        period: integer($int32) null-全部 3-一季度，6-半年度，9-三季度，12-年度
        report_type: string 3：资产负债表
    Returns:
        df:
        balance 季度/年度的财务数据
    '''
    report_type = '3'
    balance_fin_df = _handle_req_ret(period, report_type, code, market)

    return balance_fin_df

def get_cashflow_fin_data(code='00700', market=2, period=12):
    '''
    Args:
        code: string 股票代码
        market: string 港股：hkg，美股：usa,a股：chn
        period: integer($int32) null-全部 3-一季度，6-半年度，9-三季度，12-年度
        report_type: string 4：现金流量表
    Returns:
        df
        cashflow  季度/年度的财务数据
    '''
    report_type = '4'
    cashflow_fin_df = _handle_req_ret(period, report_type, code, market)

    return cashflow_fin_df

###### 衍生财务数据(财务因子)

def _handle_ex_ret(code_list=['00700'], queryType=None, start_date=None, end_date=None, market=2, period=12, page=1):
    #

    if market == 3 or market == 1:
        return ONLY_HK_MARKET_ERROR
    if start_date is None and end_date is None:
        return PUB_DATENONE_ERROR
    if start_date is not None and end_date is not None:
        if start_date > end_date:
            return PUB_SMALLENDDATE_ERROR
    if start_date is not None and end_date is None:
        end_date = start_date
    if start_date is None and end_date is not None:
        start_date = end_date
    if queryType == BASE_FACE:
        body = {
            "codeList": code_list,
            "market": market,
            "queryType": queryType,
            "startDate": start_date,
            "endDate": end_date,
            "periodMark": period,
            "current": page
        }
    else:
        body = {
            "codeList": code_list,
            "market": market,
            "queryType": queryType,
            "periodMark": period,
            "current": page
        }
    update_url = lambda url: url.replace("__kaisarooturl__", KAISA_ROOT_URL)
    df_ = total_handle_req(body=body, URL=update_url(EX_FIN_POST_URL))

    return df_

def _handle_get_fina_data_cls(_data_, data_type, code_list, start_date, end_date, market, period):
    # 统一get财务数据
    try:
        info_date = 'info_publ_date'
        date_type_dic = {BASE_FACE: 'trading_day', PROFIT: info_date,
                         CASHFLOW: info_date, OPERATION: info_date, DEBTPAY: info_date, GROWTH: info_date}

        dt_filter_field = date_type_dic[data_type]

        pageSize = _data_['totalPage']
        page1_data = _data_['result']
        df1_ = pd.DataFrame(page1_data)
        for pageC in range(2, pageSize + 1):
            profit_data_next = _handle_ex_ret(code_list, data_type, start_date, end_date, market, period, pageC)
            page_n_data = profit_data_next['result']
            df1_ = pd.concat([df1_, pd.DataFrame(page_n_data)], axis=0)

        df1_ = df1_.drop_duplicates(subset=['secu_code', dt_filter_field])   # 去重
        if start_date is not None and end_date is not None:
            df1_ = df1_[(df1_[dt_filter_field] >= start_date) & (df1_[dt_filter_field] <= end_date)]
            ch_sign = 2
        else:
            cur_dt = end_date if start_date is None else start_date
            ch_sign = 1
            df1_ = df1_[df1_[dt_filter_field] <= cur_dt]


        __ = _get___(df1_, ch_sign, dt_filter_field)
        __ = __.reset_index(drop=True)
    except Exception as exp:
        return PUB_WRONG_MSG_ERROR
    return __

def _get___(df, ch_sign=None, dt_filter_field='info_publ_date'):
    '''
    Args:
        df: 原始数据
        dt_type: 时间类型【start_date/end_date】
    Returns:
    返回所需的衍生财务/基本面因子数据
    '''
    # 统一过滤得到最后需要的财务数据-df
    __ = pd.DataFrame()
    gp_df = df.groupby(by=['secu_code'])
    for gp, ___ in gp_df:
        if ch_sign == 1:
            ___ = ___.sort_values(by=[dt_filter_field], ascending=False)
            ___ = ___.head(1)
        if __.empty:
            __ = ___.copy()
        else:
            __ = pd.concat([__, ___], axis=0)
    return __

def get_profit_factor_fin_data(code_list=['00700'], start_date=None, end_date=None, market=2, period=12):
    '''
        获取盈利能力因子数据
        Args:
            code_list: 股票篮子 ['00700']/['00700','06969']
            start_date: 开始日期 如 ‘2016-12-31’
            end_date: 结束日期 如 ‘2018-12-31’
            market: 市场类型：1 CH/ 2 HK/ 3 USA
            period: 报表类型：0全部, 3一季报,6中报,9三季报,12年报
        Returns:
        PS： 1.如果指定了start_date和end_date那返回的是这个区间的财务因子数据,(时间对应的是上市公司公布财报的日期)
            2.如果只指定了开始日期或者结束日期则取这个日期的最近一期的财务因子数据
            3.如果两个日期都没指定，则取最近一期的财务因子数据
        对应股票篮子的历史财务数据
    '''
    __ = _all_fina_factor_handle_method(code_list, PROFIT, start_date, end_date, market, period)
    return __

def get_cash_flow_factor_fin_data(code_list=['00700'], start_date=None, end_date=None, market=2, period=12):
    '''
        获取现金流因子数据
        Args:
            code_list: 股票篮子 ['00700']/['00700','06969']
            start_date: 开始日期 如 ‘2016-12-31’
            end_date: 结束日期 如 ‘2018-12-31’
            market: 市场类型：1 CH/ 2 HK/ 3 USA
            period: 报表类型：0全部, 3一季报,6中报,9三季报,12年报
        Returns:
        PS： 1.如果指定了start_date和end_date那返回的是这个区间的财务因子数据,(时间对应的是上市公司公布财报的日期)
            2.如果只指定了开始日期或者结束日期则取这个日期的最近一期的财务因子数据
            3.如果两个日期都没指定，则取最近一期的财务因子数据
        对应股票篮子的历史财务数据
    '''
    data_type = 'cashFlow'
    __ = _all_fina_factor_handle_method(code_list, CASHFLOW, start_date, end_date, market, period)
    return __

def get_operation_factor_fin_data(code_list=['00700'], start_date=None, end_date=None, market=2, period=12):
    '''
        获取运营能力因子数据
        Args:
            code_list: 股票篮子 ['00700']/['00700','06969']
            start_date: 开始日期 如 ‘2016-12-31’
            end_date: 结束日期 如 ‘2018-12-31’
            market: 市场类型：1 CH/ 2 HK/ 3 USA
            period: 报表类型：0全部, 3一季报,6中报,9三季报,12年报
        Returns:
        PS： 1.如果指定了start_date和end_date那返回的是这个区间的财务因子数据,(时间对应的是上市公司公布财报的日期)
            2.如果只指定了开始日期或者结束日期则取这个日期的最近一期的财务因子数据
            3.如果两个日期都没指定，则取最近一期的财务因子数据
        对应股票篮子的历史财务数据
    '''
    data_type = 'operation'
    __ = _all_fina_factor_handle_method(code_list, OPERATION, start_date, end_date, market, period)
    return __

def get_growth_factor_fin_data(code_list=['00700'], start_date=None, end_date=None, market=2, period=12):
    '''
        获取成长能力因子数据
        Args:
            code_list: 股票篮子 ['00700']/['00700','06969']
            start_date: 开始日期 如 ‘2016-12-31’
            end_date: 结束日期 如 ‘2018-12-31’
            market: 市场类型：1 CH/ 2 HK/ 3 USA
            period: 报表类型：0全部, 3一季报,6中报,9三季报,12年报
        Returns:
        PS： 1.如果指定了start_date和end_date那返回的是这个区间的财务因子数据,(时间对应的是上市公司公布财报的日期)
            2.如果只指定了开始日期或者结束日期则取这个日期的最近一期的财务因子数据
            3.如果两个日期都没指定，则取最近一期的财务因子数据
        对应股票篮子的历史财务数据
    '''
    data_type = 'growth'
    __ = _all_fina_factor_handle_method(code_list, GROWTH, start_date, end_date, market, period)
    return __

def get_debtpay_factor_fin_data(code_list=['00700'], start_date=None, end_date=None, market=2, period=12):
    '''
        获取偿债能力因子数据
        Args:
            code_list: 股票篮子 ['00700']/['00700','06969']
            start_date: 开始日期 如 ‘2016-12-31’
            end_date: 结束日期 如 ‘2018-12-31’
            market: 市场类型：1 CH/ 2 HK/ 3 USA
            period: 报表类型：0全部, 3一季报,6中报,9三季报,12年报
        Returns:
        PS： 1.如果指定了start_date和end_date那返回的是这个区间的财务因子数据,(时间对应的是上市公司公布财报的日期)
            2.如果只指定了开始日期或者结束日期则取这个日期的最近一期的财务因子数据
            3.如果两个日期都没指定，则取最近一期的财务因子数据
        对应股票篮子的历史财务数据
    '''
    data_type = 'debtPay'
    __ = _all_fina_factor_handle_method(code_list, DEBTPAY, start_date, end_date, market, period)
    return __

def get_baseface_factor_fin_data(code_list=['00700'], start_date=None, end_date=None, market=2, period=12):
    '''
        获取一般基本面因子数据
        Args:
            code_list: 股票篮子 ['00700']/['00700','06969']
            start_date: 开始日期 如 ‘2016-12-31’
            end_date: 结束日期 如 ‘2018-12-31’
            market: 市场类型：1 CH/ 2 HK/ 3 USA
            period: 报表类型：0全部, 3一季报,6中报,9三季报,12年报
        Returns:
        PS： 1.如果指定了start_date和end_date那返回的是这个区间的财务因子数据,(时间对应的是每日行情数据更新后的交易日)
            2.如果只指定了开始日期或者结束日期则取这个日期的最近一期的财务因子数据
            3.如果两个日期都没指定，则取最近一期的财务因子数据
        对应股票篮子的历史财务数据
    '''
    data_type = 'baseFace'
    if t_typeof(code_list) != 'list': return pd.DataFrame()
    if end_date is None and start_date is None:
        return PUB_DATENONE_ERROR

    if end_date is None and start_date is not None:
        end_date = start_date
    if end_date is not None and start_date is None:
        start_date = end_date
    __ = _all_fina_factor_handle_method(code_list, BASE_FACE, start_date, end_date, market, period)
    return __

def _all_fina_factor_handle_method(code_list=['00700'], data_type=None, start_date=None, end_date=None, market=2, period=12):
    # 集中处理_handle_ex_ret/_handle_get_fina_data_cls
    code_list = list(set(code_list))
    if t_typeof(code_list) != 'list':
        return PUB_ONLY_LIST_TYPE_ERROR
    _data_ = _handle_ex_ret(code_list, data_type, start_date, end_date, market, period)
    try:
        if PUB_HELLO in _data_ or PUB_SOR in _data_:
            return _data_
        if len(_data_['result']) == 0:
            return PUB_WRONG_DATE_AROUND_ERROR
        __ = _handle_get_fina_data_cls(_data_, data_type, code_list, start_date, end_date, market, period)

        return __
    except:
        return _data_


################################财务数据##################################