#!/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function
from builtins import (bytes, super, range, zip, round, pow, object)
import datetime
import json
import numpy as np
import pandas as pd
from .utils import *
from .tools._checkparam import *

from .global_config import *
import atexit


def __get_curr_report__(date: int):
    q_end = (331, 630, 930, 1231)
    m = (date - (date // 10000) * 10000) // 100
    return (date // 10000) * 10000 + q_end[(m - 1) // 3]


def __get_next_report__(report: int):
    q_end = (331, 630, 930, 1231)
    m = (report - (report // 10000) * 10000) // 100
    y = (report // 10000)
    q = (m - 1) // 3
    if q == 3:
        return (y + 1) * 10000 + q_end[0]
    return y * 10000 + q_end[q + 1]


def __get_prev_report__(report: int):
    q_end = (331, 630, 930, 1231)
    m = (report - (report // 10000) * 10000) // 100
    y = (report // 10000)
    q = (m - 1) // 3
    if q == 0:
        return (y - 1) * 10000 + q_end[3]
    return y * 10000 + q_end[q - 1]


def __get_report_from_q__(date: int, q: str):
    if len(q) == 6:
        qint = {'Q1': '331', 'Q2': '630', 'Q3': '930', 'Q4': '1231'}
        for i in ('Q1', 'Q2', 'Q3', 'Q4'):
            if q.endswith(i):
                return int(q.replace(i, qint.get(i)))

    if q not in ('Q1', 'Q2', 'Q3', 'Q4'):
        raise ValueError('invalid quarter value, q is Q1,Q2,Q3,Q4')
    report = 0
    q_end = (331, 630, 930, 1231)
    # q_range = [(401,430), (701,830), (1001, 1031), (101,430)]
    # md = date - (date//10000) * 10000
    report = (date // 10000) * 10000 + q_end[int(q[1]) - 1]
    if report >= date:
        return __get_prev_report__(report)
    return report


def cpp_data_frame_to_3ddf__(tfs):
    # 创建索引
    index = []
    index_first = []
    index_second = []

    for field in tfs:
        for time_stop in tfs[field].get_int_column("time_stop"):
            index_first.append(field)
            index_second.append(time_util.ms_to_datetime(time_stop))

    index.append(index_first)
    index.append(index_second)

    def get_values(stf, name, typ):
        if typ == 2:
            return stf.get_double_column(name)
        elif typ == 3:
            return stf.get_int_column(name)
        elif typ == 6:
            return [time_util.ms_to_datetime(x) for x in stf.get_int_column(name)]
        elif typ == 4:
            return stf.get_string_column(name)

    result = {}
    if len(tfs) is 0:
        return pd.DataFrame(result)

    columns = None
    for field in tfs:
        columns = tfs[field].get_columns()
        break

    data = {}
    flag = False
    for field in tfs:
        for i in range(0, len(columns)):
            column = columns[i]
            if column == "time_stop":
                continue
            if not flag:
                data[column] = []
                l = get_values(tfs[field], column, tfs[field].get_column_type(column))
                for i in l:
                    data[column].append(i)
            else:
                for i in get_values(tfs[field], column, tfs[field].get_column_type(column)):
                    data[column].append(i)
        flag = True

    return pd.DataFrame(data, index=index, columns=columns.remove("time_stop"))


def cpp_data_frame_to_df__(tf):
    if tf is None:
        return pd.DataFrame()
    columns = tf.get_columns()

    def get_values(stf, name, typ):
        if typ == 2:
            return stf.get_double_column(name)
        elif typ == 3:
            return stf.get_int_column(name)
        elif typ == 6:
            return [time_util.ms_to_datetime(x) for x in stf.get_int_column(name)]
        elif typ == 4:
            return stf.get_string_column(name)

    tmp = {}
    for i in range(0, len(columns)):
        column = columns[i]
        tmp[column] = list(get_values(tf, column, tf.get_column_type(column)))
    return pd.DataFrame(tmp)


def check_trade_date__(dt, dft):
    return dft if dt is None else dt


def process_bar(percent, start_str='', end_str='', total_length=40):
    bar = ''.join(['='] * int(percent * total_length)) + ('>' if int(percent) != 1 else '')
    bar = '\r' + start_str + ' {:>5.1f}% ['.format(percent * 100) + bar.ljust(total_length) + ']' + end_str
    print(bar, end=('' if int(percent) != 1 else '\n'), flush=True)


class DownloadProgress(DownloadSpi):
    def on_progress(self, title: str, progress: float, speed: float):
        process_bar(progress)
        return True


class DataProxy(object):
    def __init__(self, api):
        self.download_spi = DownloadProgress()
        self.data_api = api
        if self.data_api.downloader is not None:
            self.data_api.downloader.register_spi(self.download_spi)

    def __del__(self):
        release()
        self.download_spi = None
        self.data_api = None

    def is_suspend(self, symbol, trade_date=None):
        """
        判断标的是否停牌
        :param symbol: 标的
        :param trade_date: 交易日
        """
        trade_date = check_trade_date__(trade_date, self.get_last_trading_date())
        return self.data_api.is_suspend(symbol, trade_date)

    def is_ST(self, symbol, trade_date=None):
        """
        判断标的是否ST
        :param symbol: 标的
        :param trade_date: 交易日
        """
        trade_date = check_trade_date__(trade_date, self.get_last_trading_date())
        return self.data_api.is_ST(symbol, trade_date)

    def is_listed(self, symbol, trade_date=None):
        """
        判断标的是否上市
        :param symbol: 标的
        :param trade_date: 交易日
        """
        trade_date = check_trade_date__(trade_date, self.get_last_trading_date())
        return self.data_api.is_listed(symbol, trade_date)

    def get_ref_data(self, symbol):
        """
        获取标的基础信息
        :param symbol:
        :return algo::RefData:
        """
        return self.data_api.get_ref_data(symbol)

    def get_constituent_symbols(self, symbol, trade_date=None):
        """
        获取成分股标的数据
        :param  symbol_set: 指数代码、板块代码、指数代码列表或者行业板块代码列表
        :param trade_date: 交易日
        :return dict{string, list[string]}:
        """
        trade_date = check_trade_date__(trade_date, self.date_now())
        return self.data_api.get_symbols_by_set(symbol, trade_date, False)

    def get_continuous_symbol(self, symbol, trade_date=None):
        """
        获取当前日期连续标的数据
        :param symbol: 连续合约代码
        :param trade_date: 交易日
        :return str: 合约标的
        """

        trade_date = check_trade_date__(trade_date, self.date_now())
        return self.data_api.get_continuous_symbol(symbol, trade_date)

    def get_appointed_symbols(self, mode, trade_date=None):
        """
        获取指定合约集合
        :param mode: Z0/Z1/M0/M1/M3/M6
        :param trade_date: 交易日
        :return str: 标的
        """

        if trade_date is None:
            trade_date = self.get_last_trading_date()
        trade_date = check_trade_date__(trade_date, self.date_now())
        return self.data_api.get_appointed_symbols(mode, trade_date)

    def get_symbols_on_set(self, symbols: list, symbol: str, trade_date=None):
        """[summary]
        获取标的所在行业（板块）
        :param symbols: 标的列表
        :param symbol: 行业大类标的(申万一级行业："SW1PLA.SET", 申万二级行业：SW2PLA.SET, 优品行业：UPPLA.SET, 优品概念：UPCPT.SET )
        :param trade_date: 交易日
        :return dict: 标的->行业代码
        """
        if trade_date is None:
            trade_date = self.get_last_trading_date()
        trade_date = check_trade_date__(trade_date, self.date_now())
        return self.data_api.get_symbols_on_set(symbols, symbol, trade_date)

    def date_now(self):
        """
        获取当前日期
        """
        return time_util.date_now()

    def get_prev_trade_date(self, trade_date=None, market='CS'):
        """
        获取指定市场某个日期的前一个交易日
        :param trade_date: 日期，如20180101
        :param market: 市场，如CS，CF
        :return int:
        """
        market = check_market(market)

        if trade_date is None:
            trade_date = self.get_last_trading_date()
        trade_date = check_trade_date__(trade_date, self.date_now())
        return self.data_api.get_prev_trade_date(trade_date, market)

    def get_next_trade_date(self, trade_date=None, market='CS'):
        """
        获取指定市场某个日期的后一个交易日
        :param trade_date: 日期，如20180101
        :param market: 市场，如CS，CF 默认 CS
        :return int:
        """
        market = check_market(market)

        if trade_date is None:
            trade_date = self.get_last_trading_date()
        trade_date = check_trade_date__(trade_date, self.date_now())
        return self.data_api.get_next_trade_date(trade_date, market)

    def get_trade_dates(self, start_date, end_date=None, market='CS', period='D', index=1):
        """
        获取某个市场指定日期区间的交易日
        :param start_date: 日期，如20180101
        :param end_date:
        :param market: 市场，如CS，CF 默认 CS
        :return list[int]:
        """
        market = check_market(market)
        start_date = check_trade_date__(start_date, self.date_now())
        end_date = check_trade_date__(end_date, self.date_now())

        if start_date > end_date:
            raise StrategyException("end_date should not be earlier than start_date")

        return self.data_api.get_trade_dates(start_date, end_date, market, period, index)

    def get_prev_trade_dates(self, trade_date, count=1, market='CS', period='D', index=1):
        """
        获取某个市场截至到指定日期的count个交易日 (包含当前trade_date)
        :param trade_date: 日期，如20180101
        :param count: 交易日数量
        :param market: 市场，如CS，CF 默认 CS
        :return int:
        """
        market = check_market(market)

        if trade_date is None:
            trade_date = self.get_last_trading_date()
        trade_date = check_trade_date__(trade_date, self.date_now())
        if count < 1:
            raise StrategyException("count should be greater than zero")
        return self.data_api.get_prev_trade_dates(trade_date, count, market, period, index)

    def get_next_trade_dates(self, trade_date, count=1, market='CS', period='D', index=1):
        """
        获取某个市场指定日期开始的count个交易日 (包含当前trade_date)
        :param trade_date: 日期，如20180101
        :param count: 交易日数量
        :param market: 市场，如CS，CF 默认 CS
        :return int:
        """
        market = check_market(market)

        if trade_date is None:
            trade_date = self.get_last_trading_date()
        trade_date = check_trade_date__(trade_date, self.date_now())
        if count < 1:
            raise StrategyException("count should be greater than zero")
        return self.data_api.get_next_trade_dates(trade_date, count, market, period, index)

    def get_trade_day_interval(self, start_date, end_date, symbol):
        """
        获取交易日间隔
        :param symbol: 标的
        :param start_date: 日期，如20180101
        :param end_date: 日期，如20180201
        :return int: 包括start_date和end_date之间的交易日天数
        """
        start_date = check_trade_date__(start_date, self.date_now())
        end_date = check_trade_date__(end_date, self.date_now())

        if start_date > end_date:
            raise StrategyException("end_date should not be earlier than start_date")
        return self.data_api.get_trade_dates_interval(start_date, end_date, symbol)

    def get_trade_dates_interval(self, start_date, end_date, symbol):
        """
        获取交易日间隔
        :param symbol: 标的
        :param start_date: 日期，如20180101
        :param end_date: 日期，如20180201
        :return int: 包括start_date和end_date之间的交易日天数
        """
        start_date = check_trade_date__(start_date, self.date_now())
        end_date = check_trade_date__(end_date, self.date_now())

        if start_date > end_date:
            raise StrategyException("end_date should not be earlier than start_date")
        return self.data_api.get_trade_dates_interval(start_date, end_date, symbol)

    def is_trade_date(self, trade_date=None, market='CS'):
        """
        判断是否是交易日
        :param trade_date: 交易日,默认取当前日期
        :param market: 交易市场, 默认取A股交易市场 CS
        """
        market = check_market(market)
        trade_date = check_trade_date__(trade_date, self.date_now())
        return self.data_api.is_trade_date(trade_date, market)

    def get_last_trading_date(self, trade_date=None, market='CS'):
        """
        获取最近交易日
        :param trade_date: 交易日,默认取当前日期
        :param market: 交易市场, 默认取A股交易市场 CS
        """
        market = check_market(market)
        trade_date = check_trade_date__(trade_date, self.date_now())
        if self.is_trade_date(trade_date, market):
            return trade_date
        return self.data_api.get_prev_trade_date(trade_date, market)

    def get_nearest_trade_date(self, trade_date=None, symbol=None):
        """
        获取标的最近交易日
        :param trade_date: 交易日,默认取当前日期
        :param symbol: 标的
        """
        if symbol is None:
            return 0
        trade_date = check_trade_date__(trade_date, self.date_now())
        return self.data_api.get_nearest_trade_date(trade_date, symbol)

    def get_nearest_report(self, trade_date=None, market='CS'):
        """
        获取最近报告期
        :param trade_date: 交易日,默认取当前日期
        :param market: 交易市场, 默认取A股交易市场 CS
        """
        trade_date = check_trade_date__(trade_date, self.date_now())
        return self.data_api.get_nearest_report(trade_date, market)

    def get_one_field(self, field, symbols, start_date=None, end_date=None, count=None, strict=False):
        """
        获取数值类因子数据
        :param symbols: 标的
        :param field: 因子
        :param start_date:
        :param end_date:
        :param count: 交易日数, count 和 start_date 不能同时存在
        :param df:
        :return:
        """

        if (start_date is None) and (end_date is None):
            raise Exception("""'end_date' cannot be empty""")

        end_date = check_trade_date__(end_date, self.get_last_trading_date())
        # 是否按天取
        if count is not None:
            start_date = 0
        else:
            count = 0
        return cpp_data_frame_to_df__(self.data_api.factor.get_one_field(field, symbols if isinstance(symbols, list) else [symbols], start_date, end_date, count, strict))

    def get_field_one_day(self, fields, symbols, trade_date=None, report=None):
        """
        获取数值类因子数据
        :param symbols: 标的
        :param fields: 因子
        :param start_date:
        :param end_date:
        :param count: 交易日数, count 和 start_date 不能同时存在
        :param df:
        :return:
        """

        if isinstance(fields, str):
            fields = [fields]
        elif not isinstance(fields, list):
            raise StrategyException("invalid fields argument, expect list<str>")
        trade_date = check_trade_date__(trade_date, self.get_last_trading_date())
        if report is None:
            report = 0
        else:
            report = __get_report_from_q__(trade_date, report)
        return cpp_data_frame_to_df__(self.data_api.factor.get_field_one_day(fields if isinstance(fields, list) else [fields], symbols if isinstance(symbols, list) else [symbols], trade_date, report))

    def get_field_one_symbol(self, fields, symbol, start_date=None, end_date=None, count=None, strict=False):
        """
        获取数值类因子数据

        :param symbol: 标的
        :param fields: 因子
        :param start_date:
        :param end_date:
        :param count: 交易日数, count 和 start_date 不能同时存在
        :param strict:
        :return:
        """

        if (start_date is None) and (end_date is None):
            raise Exception("""'end_date' cannot be empty""")
        if isinstance(fields, str):
            fields = [fields]

        end_date = check_trade_date__(end_date, self.get_last_trading_date())
        if count is not None:
            start_date = 0
        else:
            count = 0
        return cpp_data_frame_to_df__(self.data_api.factor.get_field_one_symbol(fields if isinstance(fields, list) else [fields], symbol, start_date, end_date, count, strict))

    def get_table_data(self, field, symbols, start_date=None, end_date=None, count=None, columns=None):
        """
        获取表格类因子数据
        :param symbol: 标的
        :param field:
        :param start_date:
        :param end_date:
        :param count: 交易日数量, count 和 start_date 不能同时存在
        :param columns:
        :param df:
        :return:
        """

        if columns is None:
            columns = []
        if not isinstance(field, str):
            raise StrategyException("invalid field argument, expect str")

        if (start_date is None) and (end_date is None):
            raise Exception("""'end_date' cannot be empty""")

        if (start_date is None) and (count is None):
            raise Exception("""'start_date' and 'count' cannot be empty at the same time """)

        end_date = check_trade_date__(end_date, self.get_last_trading_date())
        # 是否按天取
        if count is not None:
            start_date = 0
        else:
            count = 0
        return cpp_data_frame_to_df__(self.data_api.factor.get_table_data(field, symbols if isinstance(symbols, list) else [symbols], start_date, end_date, count, columns))

    def get_bars(self, symbols, timespan, start_date=None, end_date=None, count=None, price_mode='pre', fields=None, skip_suspended=True):
        """
        拉取一个标的历史k线列表
        :param symbol: 标的
        :param timespan:
        :param start_date: 开始交易日
        :param end_date: 结束日期
        :param count: 指定拉取的条数, 截至到end_date; count 和 start_date 不能同时使用
        :param price_mode: 复权模式，0为不复权，1为前复权
        :param fields:
        :param skip_suspended: 停牌填充, True 前值填充, False NaN 填充
        :return: DataFrame or dict{DataFrame}
        """
        end_date = check_trade_date__(end_date, self.get_last_trading_date())
        count = check_count(count)
        fields = check_columns(fields, [], bar_columns)
        op = BarOptions()
        op.price_mode = price_mode
        if fields is not None:
            op.fields = fields
        if len(fields) == 0:
            raise Exception('unknown fields!!!')
        if not skip_suspended:
            op.pre_fill = False
        if count is None:
            if isinstance(symbols, str):
                # 單個symbol且爲string時，默認爲全部fields, 防止用戶傳入fields報錯
                op.fields = bar_column
                return pd.DataFrame(cpp_data_frame_to_df__(self.data_api.kbar.get_bar(start_date, end_date, symbols, timespan, op)[symbols]))
            else:
                symbols = check_symbols(symbols)
                return cpp_data_frame_to_3ddf__(self.data_api.kbar.get_bars(start_date, end_date, symbols, timespan, op))
        else:
            # 單個symbol且爲string時，默認爲全部fields, 防止用戶傳入fields報錯
            if isinstance(symbols, str):
                op.fields = bar_column
                return pd.DataFrame(cpp_data_frame_to_df__(self.data_api.kbar.get_bar_by_count(time_util.date_int_to_timestamp_ms(end_date) + (18 * 3600) * 1000, count, symbols, timespan, op)[symbols]))
            else:
                symbols = check_symbols(symbols)
                return cpp_data_frame_to_3ddf__(self.data_api.kbar.get_bars_by_count(time_util.date_int_to_timestamp_ms(end_date) + (18 * 3600) * 1000, count, symbols, timespan, op))

    def sync_data(self, table, start_date, end_date, symbols=None, force=False):
        """
        :param table: 要同步下载的因子或者k线表名
        :param start_date: 起始日期
        :param end_date: 截止日期
        :param symbols: 分钟k数据可用
        :param force: 是否强制远程拉取
        """
        if symbols is None:
            symbols = []
        if self.data_api.downloader is None:
            raise ValueError('not enable cache module')
        tbl = ''
        if isinstance(table, list):
            tbl = ','.join(table)
        else:
            tbl = table
        return self.data_api.downloader.sync_data(tbl, start_date, end_date, symbols, force)

    def clear_data(self, table):
        """
        :param table: 要同步下载的因子或者k线表名
        """
        tbl = ''
        if isinstance(table, list):
            tbl = ','.join(table)
        else:
            tbl = table
        return self.data_api.downloader.clear_data(tbl)
