#!/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function
from builtins import (bytes, str, super, range, zip, round, pow, object)

from .context import *
from .utils import *
from .global_config import *
from .data import *
import pandas as pd
import os
import pickle
import argparse


class FileAnalyzerSpi(StrategyAnalyzer):
    def __init__(self, file_path):
        super(FileAnalyzerSpi, self).__init__()

        self.file_path = file_path
        self.funcs = dict()
        with open(self.file_path, encoding='utf-8') as f:
            file_context = f.read()
            code = compile(file_context, self.file_path, 'exec')
            exec(code, self.funcs)
        self.api = None

    def on_initialize(self, api):
        if self.api is None:
            self.api = AnalyzerApi(api)
        if 'on_initialize' in self.funcs:
            self.funcs['on_initialize'](self.api)

    def on_before_market_open(self, api, market_param):
        if 'on_before_market_open' in self.funcs:
            self.funcs['on_before_market_open'](self.api, market_param.trade_date)

    def on_first_depth(self, api, depth):
        if 'on_first_depth' in self.funcs:
            self.funcs['on_first_depth'](self.api, depth)

    def on_depth(self, api, depth):
        if 'on_depth' in self.funcs:
            self.funcs['on_depth'](self.api, depth)

    def on_bar(self, api, bar):
        if 'on_bar' in self.funcs:
            self.funcs['on_bar'](self.api, bar)

    def on_handle_data(self, api, time_now):
        if 'on_handle_data' in self.funcs:
            self.funcs['on_handle_data'](self.api, time_util.ms_to_datetime(time_now))

    def on_terminate(self, api, exit_info):
        if 'on_terminate' in self.funcs:
            self.funcs['on_terminate'](self.api, exit_info)

    def on_timer(self, api):
        if 'on_timer' in self.funcs:
            self.funcs['on_timer'](self.api)

    def on_order_update(self, api, order_info):
        if 'on_order_update' in self.funcs:
            self.funcs['on_order_update'](self.api, order_info)


class AnalyzerApi:
    def __init__(self, api):
        self.api = api
        self.init_time = True
        self.context = None
        self.data_api = api.data_api()
        if self.data_api is None:
            return
        self.progress = DownloadProgress()
        if self.api.data_api().downloader is not None:
            self.api.data_api().downloader.register_spi(self.progress)

    def __del__(self):
        # self.data_api = None
        # self.api = None
        pass

    def __repr__(self):
        return 'api(context={})'.format(self.context)

    def set_context(self, context):
        self.context = context

    def set_vwap_algrithm(self, avg_count, timespan, end_time='14:55'):
        """
        初始化vwap策略下单逻辑
        :param avg_count:
        :param timespan:
        :param end_time:
        :return:
        """
        param = AlgrParam()
        param.on = True
        param.avg_count = 5
        param.timespan = timespan
        param.end_time = end_time
        self.api.set_algr_param(param)

    def set_focus_symbols(self, symbols):
        """
        设置关注的标的
        :param symbols:
        :return:
        """
        symbols = check_symbols(symbols)
        if isinstance(symbols, list):
            symbols = set(symbols)
        self.api.set_focus_symbols(symbols)
    
    def get_focus_and_position_symbols(self):
        return self.api.get_focus_and_position_symbols()

    def set_symbol_pool(self, instset: list, symbols: list):
        symbols = check_symbols(symbols)
        self.api.set_symbol_pool(instset, symbols)

    def target_position(self, symbol, qty, price=0.0, side='long', tif='', remark="", price_list='', algo=None):
        """
        下单操作
        :param symbol:
        :param qty:
        :param price:
        :param side:
        :param tif:
        :param remark:
        :param price_list:
        :param algo:
        :return:
        """
        symbol = check_symbol(symbol)
        remark = check_msg(remark)

        if algo is None:
            return self.api.target_position(symbol, qty, price, side, tif, remark, price_list)
        elif isinstance(algo, str):
            self.api.target_position(algo, symbol, qty, side)

    def target_percent(self, symbol, percent, price=0.0, side='long', tif='', remark=""):
        check_valid_percent(percent)
        symbol = check_symbol(symbol)
        remark = check_msg(remark)
        # print("##############targetPositon #################")
        return self.api.target_percent(symbol, percent, price, side, tif, remark)

    def cancel_order(self, symbol, side='long', remark=""):
        """
        撤单
        :param symbol:
        :param side:
        :param remark:
        :return:
        """
        symbol = check_symbol(symbol)
        remark = check_msg(remark)

        # print("##############targetPositon #################")
        return self.api.cancel_order(symbol, side, remark)

    def get_one_field(self, field, symbols, start_date=None, end_date=None, count=None, strict=False):
        """
        获取数值类因子数据
        :param strict:
        :param symbols:
        :param fields:
        :param end_date:
        :param start_date:
        :param count:
        :param df:
        :return:
        """
        if end_date is None:
            end_date = self.get_prev_trade_date(self.date_now(), 'CS')
        # 是否按天取
        if count is not None:
            start_date = 0
        else:
            count = 0
        return cpp_data_frame_to_df__(self.api.get_one_field(field, symbols if isinstance(symbols, list) else [symbols], start_date, end_date, count, strict))

    def get_field_one_day(self, fields, symbols, trade_date=None):
        """
        获取数值类因子数据
        :param symbols:
        :param fields:
        :param trade_date:
        :return:
        """

        if trade_date is None:
            trade_date = self.get_prev_trade_date(self.date_now(), 'CS')
        return cpp_data_frame_to_df__(self.api.get_field_one_day(fields if isinstance(fields, list) else [fields], symbols if isinstance(symbols, list) else [symbols], trade_date))

    def get_field_one_symbol(self, fields, symbol, start_date=None, end_date=None, count=None, strict=False):
        """
        获取数值类因子数据
        :param symbols:
        :param fields:
        :param end_date:
        :param start_date:
        :param count:
        :param strict:
        :return:
        """

        if end_date is None:
            end_date = self.get_prev_trade_date(self.date_now(), 'CS')
        if count is not None:
            start_date = 0
        else:
            count = 0
        return cpp_data_frame_to_df__(self.api.get_field_one_symbol(fields if isinstance(fields, list) else [fields], symbol, start_date, end_date, count, strict))

    def get_table_data(self, field: str, symbols: list, start_date=None, end_date=None, count=None, columns=None):
        """
        获取表格类因子数据
        :param field:
        :param symbols:
        :param end_date:
        :param start_date:
        :param count:
        :param columns:
        :return:
        """
        if columns is None:
            columns = []
        if not isinstance(columns, list):
            raise StrategyException("invalid columns argument, expect list<string>")

        if end_date is None:
            end_date = self.get_prev_trade_date(self.date_now(), 'CS')

        # 是否按天取
        if count is not None:
            start_date = 0
        else:
            count = 0
        return cpp_data_frame_to_df__(self.api.get_table_data(field, symbols if isinstance(symbols, list) else [symbols], start_date, end_date, count, columns))

    def get_ref_data(self, symbol):
        """
        获取标的基础信息
        :param symbol:
        :return:
        """
        return self.api.get_ref_data(symbol)

    def get_trade_dates(self, start_date, end_date, market='CS', period=('D', 1)):
        """
        获取区间日期内所有交易日
        :param start_date:开始日期
        :param end_date:截止日期
        :param market:市场
        :param period:变频参数 支持D-每天一值、W-每周一值、M-每月一值、Q-每季度一值、S-每半年一值、Y-每年一值;1-第一个交易日，-1-最后一个交易日;不填默认返回全部即(D,1)
        :return: list[trade_date]
        """
        return self.api.get_trade_dates(start_date, end_date, market)

    def get_prev_trade_dates(self, trade_date=None, count=1, market='CS', period=('D', 1)):
        """
        获取向前count个交易日的列表
        :param trade_date:
        :param count:
        :param market:
        :param period:变频参数 支持D-每天一值、W-每周一值、M-每月一值、Q-每季度一值、S-每半年一值、Y-每年一值;1-第一个交易日，-1-最后一个交易日;不填默认返回全部即(D,1)
        :return:
        """
        trade_date = check_trade_date(trade_date, self.date_now())
        return self.api.get_prev_trade_dates(trade_date, count, market)

    def get_next_trade_dates(self, trade_date=None, count=1, market='CS'):
        """
        获取向后count个交易日的列表
        :param trade_date:
        :param count:
        :param market:
        :return:
        """
        trade_date = check_trade_date(trade_date, self.date_now())
        return self.api.get_next_trade_dates(trade_date, count, market)

    def get_prev_trade_date(self, trade_date=None, market='CS', symbol=None):
        """
        获取前一个交易日
        :param trade_date:
        :param market:
        :param symbol:
        :return:
        """
        trade_date = check_trade_date(trade_date, self.date_now())
        if symbol is None:
            return self.data_api.get_prev_trade_date(trade_date, market)
        return self.data_api.get_prev_trade_date(trade_date, market)

    def get_next_trade_date(self, trade_date=None, market='CS', symbol=None):
        """
        获取后一个交易日
        :param trade_date:
        :param market:
        :param symbol:
        :return:
        """
        trade_date = check_trade_date(trade_date, self.date_now())
        if symbol is None:
            return self.data_api.get_next_trade_date(trade_date, market)
        return self.api.get_next_trade_date(trade_date, market)

    def error_code_to_string(self, error_code):
        """
        错误码转换为错误信息
        :param error_code:
        :return: 错误信息
        """
        return self.api.error_code_to_string(error_code)

    def get_trade_day_interval(self, start_date, end_date, symbol):
        """
        获取日期区间的交易日数目
        :param symbol:
        :param start_date:
        :param end_date:
        :return:
        """
        return self.api.get_trade_day_interval(start_date, end_date, symbol)

    def get_constituent_symbols(self, symbol, trade_date=None):
        """
        获取标的集合包含的标的
        :param symbol: 集合标的
        :param trade_date:
        :return:
        """
        trade_date = check_trade_date(trade_date, self.date_now(), 'trade_date')
        return self.api.get_constituent_symbols(symbol, trade_date)

    def get_continuous_symbol(self, symbol, trade_date=None):
        """
        获取当前日期连续标的数据
        :param symbol: 连续合约代码
        :param trade_date:
        :return: 对应标的
        """
        trade_date = check_trade_date(trade_date, self.date_now(), 'trade_date')
        return self.api.get_continuous_symbol(symbol, trade_date)

    def get_appointed_symbols(self, mode, trade_date=None):
        """
        获取指定合约集合
        :param mode: Z0/Z1/M0/M1/M3/M6
        :param trade_date:
        :return: 对应标的
        """
        trade_date = check_trade_date(trade_date, self.date_now(), 'trade_date')
        return self.api.get_appointed_symbols(mode, trade_date)

    def get_symbols_on_set(self, symbols:list, symbol:str, trade_date=None):
        """[summary]
        获取标的所在行业（板块）
        :param symbols: 标的列表
        :param symbol: 行业大类标的(申万一级行业："SW1PLA.SET", 申万二级行业：SW2PLA.SET, 优品行业：UPPLA.SET, 优品概念：UPCPT.SET )
        :param trade_date: 交易日
        :return dict: 标的->行业代码
        """
        trade_date = check_trade_date(trade_date, self.date_now(), 'trade_date')
        return self.data_api.get_symbols_on_set(symbols, symbol, trade_date)

    def is_suspend(self, symbol, trade_date=None):
        """
        是否停盘
        :param symbol:
        :param trade_date:
        :return:
        """
        trade_date = check_trade_date(trade_date, self.date_now())
        return self.api.is_suspend(symbol, trade_date)

    def is_ST(self, symbol, trade_date=None):
        """
        是否ST
        :param symbol:
        :param trade_date:
        :return:
        """
        trade_date = check_trade_date(trade_date, self.date_now())
        return self.api.is_ST(symbol, trade_date)

    def is_listed(self, symbol, trade_date=None):
        """
        是否上市
        :param symbol:
        :param trade_date:
        :return:
        """
        trade_date = check_trade_date(trade_date, self.date_now())
        return self.api.is_listed(symbol, trade_date)

    def get_overall_positions(self):
        """
        持仓汇总信息列表
        :return:
        """
        return self.api.get_overall_positions()

    def get_strategy_pnl(self):
        """
        获取策略盈亏
        :return:
        """
        return self.api.get_strategy_pnl()

    def get_dynamic_value(self, field):
        """
        获取动态参数值
        :param field:
        :return:
        """
        field = check_field(field)
        tp = self.api.get_value_type(field)
        if tp == "int64":
            return self.api.get_value_as_long(field)
        elif tp == "double":
            return self.api.get_value_as_double(field)
        elif tp == "string":
            return self.api.get_value_as_string(field)
        else:
            return None

    def print_dynamic(self):
        """
        输出所有支持的动态参数
        :return:
        """
        return self.api.print_dynamic_value()

    @staticmethod
    def get_define_data(name, default_value="", dtype=str):
        """
        获取自定义命令行参数
        :param name:
        :param default_value:
        :param dtype:
        :return:
        """
        command_line = argparse.ArgumentParser()
        command_line.add_argument('--' + name, type=dtype, default=default_value, help='self definition')
        args = command_line.parse_known_args()
        return getattr(args[0], name)

    def is_back_test(self):
        """
        是否回测
        :return:
        """
        return self.api.is_back_test()

    def is_real_env(self):
        """
        是否实盘
        :return:
        """
        return self.api.is_real_env()

    def is_sim_env(self):
        """
        是否模拟盘
        :return:
        """
        return not self.is_back_test() and not self.is_real_env()

    def get_bars_history(self, symbol, timespan, count=None, price_mode='pre', fields=None, skip_suspended = True):
        """
        拉取一个标的历史k线列表
        :param symbol:
        :param timespan:
        :param count: 指定拉取的条数
        :param price_mode: 复权模式，0为不复权，1为前复权
        :param skip_suspended: 是否跳过停牌的数据，0表示不跳过，1跳过
        :param fields:
        :return: list(Bar)
        """
        count = check_count(count, 1)

        fields = check_columns(fields, [], bar_columns)

        if len(fields) == 0:
            raise SyntaxError('fields unknown or empty!!!')

        options = BarOptions(price_mode, skip_suspended, fields)

        if isinstance(symbol, str):
            # 單個symbol且爲string時，默認爲全部fields, 防止用戶傳入fields報錯
            options.fields = GlobalUtil.bar_columns
            return pd.DataFrame(cpp_data_frame_to_df__(self.api.get_bars_history(symbol, timespan, count, options)))
        else:
            symbol= check_symbols(symbol)
            return cpp_data_frame_to_3ddf__(self.api.get_bars_history(symbol, timespan, count, options))


    def get_bar_current(self, symbols):
        """
        获取当前收齐的k线
        :param symbols:
        :return:
        """
        return self.api.get_bar_current(symbols)

    def send_custom_message(self, msg):
        """
        设置用户自定义运行消息，会显示在界面上
        :param msg:
        :return:
        """
        check_msg(msg)
        self.api.send_custom_message(msg)

    def set_log_level(self, level):
        """
        设置日志级别
        :param level:
        :return:
        """
        self.api.set_log_level(level)

    def is_trading_now(self, symbol):
        """
        当前是否是交易时间
        :param self:
        :param symbol:
        :return:
        """
        check_symbol(symbol)
        return self.api.is_trading_now(symbol)

    def time_now(self):
        """
        获取当前时间
        :return: 当前（回测）时间
        """
        return TimeUtil.ms_to_datetime(self.api.time_now())

    def date_now(self):
        """
        获取当前交易日
        :return: 当前（回测）交易日
        """
        return self.api.date_now()

    def get_symbol_pool(self):
        """
        获取缓存的股票池
        :return:
        """
        return self.api.get_symbol_pool()

    def get_account(self, symbol=None, market='CS'):
        """
        账户信息
        :param symbol:
        :param market:
        :return:
        """
        if symbol is None and market is None:
            raise StrategyException("market and symbols cannot be both None!")

        symbol = check_symbol(symbol, '')
        market = check_symbol(market, '')
        return self.api.get_account(symbol, market)

    def get_overall_position(self, symbol):
        """
        单标的账户持仓汇总信息
        :param symbol:
        :return:
        """
        symbol = check_symbol(symbol)
        return self.api.get_overall_position(symbol)

    def get_symbol_position(self, symbol, side='long'):
        symbol = check_symbol(symbol)
        position = self.api.get_symbol_position(symbol, side)
        return position

    def get_symbol_positions(self):
        return self.api.get_symbol_positions()
