
from typing import List, Dict
import pandas as pd
import numpy as np
import math
import datetime
import traceback
import json
import statsmodels.api as sm
import time
from scipy.optimize import Bounds, minimize
from statsmodels.tsa.ar_model import AutoReg
from pandas.tseries.offsets import DateOffset
from ...api.raw import RawDataApi
from ...api.basic import BasicDataApi
from ...view.derived_models import FundIndicatorGroup
from .derived_data_helper import DerivedDataHelper


class FundIndicatorProcessorGroup:

    _TRADING_DAYS_PER_YEAR = 242
    _NATURAL_DAYS_PER_YEAR = 360
    _RISK_FEE_RATE = 0.011
    _RISK_FEE_RATE_PER_DAY = _RISK_FEE_RATE / _TRADING_DAYS_PER_YEAR
    _REPORT_DATE_LIST = ['0331', '0630', '0930', '1231']
    _FUND_CLASSIFIER = {
        'QDII': ['国际(QDII)股票型基金', '国际(QDII)债券型基金', '国际(QDII)另类投资基金', '国际(QDII)混合型基金', '股票多空', '商品型基金', 'REITs'],
        'stock': ['偏股混合型基金', '普通股票型基金', '被动指数型基金', '增强指数型基金'], 
        'bond': ['增强指数型债券基金','混合债券型二级基金', '中长期纯债型基金', '混合债券型一级基金', '短期纯债型基金', '偏债混合型基金', '被动指数型债券基金'],
        'mmf': ['货币市场型基金'],
        'mix': ['平衡混合型基金', '灵活配置型基金'],
    }
    _REPLACE_DICT = {'stock': 'csi_stockfund', 'bond': 'national_debt', 'mmf': 'mmf', 'QDII': 'csi_f_qdii', 'mix': 'csi_f_hybrid'}

    def __init__(self, data_helper: DerivedDataHelper, data_cycle: int):
        self._data_helper = data_helper
        # 单位: 年
        self._data_cycle = data_cycle
        self._data_cycle_days = data_cycle * self._TRADING_DAYS_PER_YEAR
        self._basic_api = BasicDataApi()
        self._rank_dic: Dict[pd.DataFrame] = {}
        self._res: List[pd.Series] = []

    def init(self, end_date: str, is_print_time: bool=False):
        # self.log = []
        self._wind_type_dict = {}
        for type_i, type_list in self._FUND_CLASSIFIER.items():
            for _ in type_list:
                self._wind_type_dict.update({_:type_i})
        # 获取待计算的基金列表
        self.fund_info: pd.DataFrame = self._basic_api.get_fund_info().drop(columns='_update_time')
        self._wind_class_2_dict = self.fund_info.set_index('fund_id')['wind_class_2'].to_dict()
        
        # 向前取N年
        start_date: str = (pd.to_datetime(end_date, infer_datetime_format=True) - DateOffset(years=self._data_cycle+1)).strftime('%Y%m%d')
        # 获取区间内交易日列表
        all_trading_days: pd.Series = self._basic_api.get_trading_day_list().drop(columns='_update_time').set_index('datetime')
        self._trading_days: pd.Series = all_trading_days.loc[pd.to_datetime(start_date, infer_datetime_format=True).date():pd.to_datetime(end_date, infer_datetime_format=True).date()]
        # 使用实际trading day的最后一天作为end_date
        self.end_date = self._trading_days.index.array[-1]

        # 基金净值数据、指数价格数据的index对齐到交易日列表
        _tm_loads_nav_0 = time.time()
        self._fund_list = self.fund_info[(self.fund_info.end_date > self.end_date) 
                                       & (self.fund_info.structure_type <= 1)
                                       & (~self.fund_info.wind_class_2.isnull())]
        fund_nav: pd.DataFrame = self._basic_api.get_fund_nav_with_date(start_date=start_date, end_date=self.end_date, fund_list=self._fund_list.fund_id.tolist())
        self._fund_nav_origin: pd.DataFrame = fund_nav.pivot_table(index='datetime', columns='fund_id', values='adjusted_net_value').reindex(self._trading_days.index).fillna(method='ffill')
        _tm_loads_nav_1 = time.time()
        # 选取成立满半年的 而且近半年波动率不为0，并排除掉异常净值基金
        self.one_day_jump = self._fund_nav_origin.pct_change(1).abs().max()
        self.three_day_jump = self._fund_nav_origin.pct_change(3).abs().max()
        normal_fund_list = []
        self.abnormal_reason = []
        for fund_id in self._fund_nav_origin:
            _df = self._fund_nav_origin[fund_id].dropna()
            if _df.shape[0] > 120:
                if _df.iloc[-120:].var() > 1e-6:
                    wind_class_2 = self._wind_class_2_dict[fund_id]
                    select_type = self._wind_type_dict.get(wind_class_2, None)
                    if select_type is None:
                        continue
                    one_day_jump_i = self.one_day_jump[fund_id]
                    three_day_jump_i = self.three_day_jump[fund_id]
                    if select_type in ['stock','QDII']:
                        if (one_day_jump_i < 0.1) & (three_day_jump_i < 0.25):
                            normal_fund_list.append(fund_id)
                        else:
                            self.abnormal_reason.append({'fund_id':fund_id,'abnormal_reason':f'high_risk: jump_max_1d {round(one_day_jump_i,3)} jump_max_3d {round(three_day_jump_i, 3)}'})
                    
                    elif select_type in ['bond','mix','mmf']:
                        if (one_day_jump_i < 0.05) & (three_day_jump_i < 0.15):
                            normal_fund_list.append(fund_id)
                        else:
                            self.abnormal_reason.append({'fund_id':fund_id,'abnormal_reason':f'low_risk: jump_max_1d {round(one_day_jump_i,3)} jump_max_3d {round(three_day_jump_i, 3)}'})
                else:
                    self.abnormal_reason.append({'fund_id':fund_id,'abnormal_reason':'price_inactive'})

            else:
                self.abnormal_reason.append({'fund_id':fund_id,'abnormal_reason':'less_than_half_y'})
        # 全部计算 
        self._fund_nav = self._fund_nav_origin.copy()#[normal_fund_list].copy()
        _tm_filter_nav = time.time()
        index_price: pd.DataFrame = self._basic_api.get_index_price_dt(start_date, end_date, columns=['close'])
        _tm_load_index = time.time()
        # 有的index最近没有数据，如活期存款利率/各种定期存款利率等，需要先reindex到全部的交易日列表上ffill
        self._index_price: pd.DataFrame = index_price.pivot_table(index='datetime', columns='index_id', values='close').reindex(self._trading_days.index).fillna(method='ffill')
        _bank_rate_df: pd.DataFrame = self._basic_api.get_index_price(index_list=['ddir', 'nonor', 'tmd_1y', 'tmd_2y', 'tmd_3m', 'tmd_3y', 'tmd_5y', 'tmd_6m', 'tmd_7d'])
        _bank_rate_df = _bank_rate_df.pivot_table(index='datetime', columns='index_id', values='close').reindex(all_trading_days.index).fillna(method='ffill').reindex(self._trading_days.index)
        drop_list = [i for i in self._index_price if i in _bank_rate_df]
        self._index_price = self._index_price.drop(drop_list, axis=1)
        self._index_price: pd.DataFrame = pd.concat([self._index_price, _bank_rate_df], axis=1)
        
        self.fund_type_benchmark = self._index_price[[self._REPLACE_DICT[fund_type] for fund_type in self._FUND_CLASSIFIER]]
        self.fund_type_benchmark = self.fund_type_benchmark.rename(columns={v : f'{k}_bench' for k, v in self._REPLACE_DICT.items()})
        # 再reindex到参与计算的交易日列表上
        # self._index_price: pd.DataFrame = index_price.reindex(self._trading_days.index)
        pd.testing.assert_index_equal(self._fund_nav.index, self._index_price.index)
        
        macroeco = RawDataApi().get_em_macroeconomic_daily(codes=['EX_DR_RATIO']).drop(columns='_update_time')
        self._macroeco: pd.DataFrame = macroeco.pivot_table(index='datetime', columns='codes', values='value').reindex(all_trading_days.index).fillna(method='ffill').reindex(self._trading_days.index)
        pd.testing.assert_index_equal(self._fund_nav.index, self._macroeco.index)
        try:
            # 这个指数有一天的点数是0，特殊处理一下
            self._index_price['spi_spa'] = self._index_price['spi_spa'].where(self._index_price.spi_spa != 0).fillna(method='ffill')
        except KeyError:
            pass

        # 对数净值取差分并且去掉第一个空值，得到基金对数收益率数列
        self._fund_ret: pd.DataFrame = np.log(self._fund_nav).diff().iloc[1:, :]

        self._fund_size: pd.DataFrame = self._basic_api.get_fund_size_range(start_date, end_date)
        self._fund_size = self._fund_size.pivot_table(index='datetime', columns='fund_id', values='size')
        self._fund_size = self._fund_size.reindex(self._fund_ret.index.union(self._fund_size.index)).fillna(method='ffill').reindex(self._fund_ret.index)
        pd.testing.assert_index_equal(self._fund_ret.index, self._fund_size.index)

        # 计算benchmark return，且index对齐到fund_ret
        self._fund_benchmark_df: pd.DataFrame = self._basic_api.get_fund_benchmark().drop(columns='_update_time')
        _tm_other_processor = time.time()
        benchmark_ret: pd.DataFrame = self._get_benchmark_return()
        _tm_other_processor_tmp = time.time()
        self._benchmark_ret: pd.DataFrame = benchmark_ret.reindex(self._fund_ret.index)
        benchmark_cols = self._benchmark_ret.columns.tolist()
        for fund_id in self._fund_nav.columns:
            benchmark_id = fund_id
            if not benchmark_id in benchmark_cols:    
                wind_class_2 = self._wind_class_2_dict[fund_id]
                select_type = self._wind_type_dict[wind_class_2]
                _benchmark_ret = self._index_price[self._REPLACE_DICT[select_type]].pct_change(1).rename(benchmark_id)
                self._benchmark_ret = self._benchmark_ret.join(_benchmark_ret)

        pd.testing.assert_index_equal(self._fund_ret.index, self._benchmark_ret.index)
        self._fund_ret = self._fund_ret.join(self._benchmark_ret, rsuffix='_b')
        _tm_benchmakr_ret = time.time()
        # 获取wind一级分类
        self._wind_class_1: np.ndarray = self._fund_list.wind_class_1.unique()
        # 按wind二级分类计算基金收益率排名
        self._get_continue_stats_tool()
        # 取出沪深300收益率
        self._hs300 = self._basic_api.get_index_price(['hs300'])[['datetime', 'close']]
        self._hs300 = self._hs300.set_index('datetime')['close']
        self._hs300 = self._hs300.apply(np.log).diff()[1:]
        self._fund_ret = self._fund_ret.join(self._hs300.rename('close_hs300'))
        # 取出货币基金指数收益率
        self._mmf = self._basic_api.get_index_price(['mmf'])[['datetime', 'close']]
        self._mmf = self._mmf.set_index('datetime')['close']
        self._mmf = self._mmf.apply(np.log).diff()[1:]
        self._fund_ret = self._fund_ret.join(self._mmf.rename('close_mmf'))
        self._fund_ret = self._fund_ret.join(self.fund_type_benchmark.pct_change(1))
        # 获取年报/半年报的发布日期
        end_date_dt = pd.to_datetime(end_date, infer_datetime_format=True)
        md = end_date_dt.strftime('%m%d')
        sentry_date = pd.Series(self._REPORT_DATE_LIST)
        sentry = sentry_date[sentry_date <= md]
        # 为半年报/年报发布预留一个季度的缓冲时间
        if sentry.empty:
            real_date = datetime.date(end_date_dt.year - 1, 6, 30)
        elif len(sentry) <= 2:
            real_date = datetime.date(end_date_dt.year - 1, 12, 31)
        else:
            real_date = datetime.date(end_date_dt.year, 6, 30)

        # 取出持仓数据
        self._fund_hold = self._basic_api.get_history_fund_size(start_date=real_date, end_date=real_date)
        self._fund_hold = self._fund_hold[['fund_id', 'institution_holds', 'hold_num']].set_index('fund_id')
        # 取出货基风险相关数据
        self._risk_metric = self._basic_api.get_fund_hold_asset_by_id(start_date=real_date, end_date=real_date)
        self._risk_metric = self._risk_metric[['fund_id', 'first_repo_to_nav', 'avg_ptm']].set_index('fund_id')
        _tm_ret_process = time.time()
        if is_print_time:
            print(f'\t[time] fetch fund nav : {_tm_loads_nav_1 - _tm_loads_nav_0}')
            print(f'\t[time] filter nav : {_tm_filter_nav - _tm_loads_nav_1}')
            print(f'\t[time] fetch index price : {_tm_load_index - _tm_filter_nav}')
            print(f'\t[time] fetch fund size and benchmark info : {_tm_other_processor - _tm_load_index}')
            print(f'\t[time] calc fund benchmark ret : {_tm_other_processor_tmp - _tm_other_processor}')
            print(f'\t[time] add fund benchmark ret : {_tm_benchmakr_ret - _tm_other_processor_tmp}')
            print(f'\t[time] combine fund rets : {_tm_ret_process - _tm_benchmakr_ret}')
            
    def history_load_data(self, end_date):
        self._wind_type_dict = {}
        for type_i, type_list in self._FUND_CLASSIFIER.items():
            for _ in type_list:
                self._wind_type_dict.update({_:type_i})
        # 获取待计算的基金列表
        self.fund_info: pd.DataFrame = self._basic_api.get_fund_info().drop(columns='_update_time')
        self._wind_class_2_dict = self.fund_info.set_index('fund_id')['wind_class_2'].to_dict()
        self._fund_list: pd.DataFrame = self.fund_info[self.fund_info.structure_type <= 1]
       
        # 获取区间内交易日列表
        self._trading_days_all: pd.Series = self._basic_api.get_trading_day_list().drop(columns='_update_time').set_index('datetime')
        # 基金净值数据、指数价格数据的index对齐到交易日列表
        self._fund_nav_all: pd.DataFrame = self._basic_api.get_fund_nav_with_date(end_date=end_date,fund_list=self._fund_list.fund_id.tolist())
        self._fund_nav_all = self._fund_nav_all.pivot_table(index='datetime', columns='fund_id', values='adjusted_net_value')
        self._index_price_all: pd.DataFrame = self._basic_api.get_index_price_dt(end_date=end_date, columns=['close'])
        self._index_price_all = self._index_price_all.pivot_table(index='datetime', columns='index_id', values='close')
        _bank_rate_df: pd.DataFrame = self._basic_api.get_index_price(index_list=['ddir', 'nonor', 'tmd_1y', 'tmd_2y', 'tmd_3m', 'tmd_3y', 'tmd_5y', 'tmd_6m', 'tmd_7d'])
        self._bank_rate_df = _bank_rate_df.pivot_table(index='datetime', columns='index_id', values='close').reindex(self._trading_days_all.index).fillna(method='ffill')
        drop_list = [i for i in self._index_price_all if i in self._bank_rate_df]
        self._index_price_all = self._index_price_all.drop(columns=drop_list)
        self._macroeco_all = RawDataApi().get_em_macroeconomic_daily(codes=['EX_DR_RATIO']).drop(columns='_update_time')
        self._macroeco_all = self._macroeco_all.pivot_table(index='datetime', columns='codes', values='value').reindex(self._trading_days_all.index).fillna(method='ffill')
        self._fund_size: pd.DataFrame = self._basic_api.get_fund_size_range(end_date=end_date)
        self._fund_size = self._fund_size.pivot_table(index='datetime', columns='fund_id', values='size')
        # 获取待计算的基金列表
        fund_list: pd.DataFrame = self._basic_api.get_fund_info().drop(columns='_update_time')
        self._fund_list: pd.DataFrame = fund_list[fund_list.structure_type <= 1]
        # 获取wind一级分类
        self._wind_class_1: np.ndarray = fund_list.wind_class_1.unique()
        # 取出沪深300收益率
        self._hs300 = self._basic_api.get_index_price(['hs300'])[['datetime', 'close']]
        self._hs300 = self._hs300.set_index('datetime')['close']
        self._hs300 = self._hs300.apply(np.log).diff()[1:]
        # 取出货币基金指数收益率
        self._mmf = self._basic_api.get_index_price(['mmf'])[['datetime', 'close']]
        self._mmf = self._mmf.set_index('datetime')['close']
        self._mmf = self._mmf.apply(np.log).diff()[1:]
        self._fund_benchmark_df: pd.DataFrame = self._basic_api.get_fund_benchmark().drop(columns='_update_time')

    def history_init(self, end_date):
        start_date: datetime.date = (pd.to_datetime(end_date, infer_datetime_format=True) - DateOffset(years=self._data_cycle+1)).date()
        print(f'start date for data: {start_date}')
        end_date: datetime.date = pd.to_datetime(end_date, infer_datetime_format=True).date()

        _trading_days: pd.Series = self._trading_days_all.loc[start_date:end_date]
        # 使用实际trading day的最后一天作为end_date
        self.end_date = _trading_days.index.array[-1]
        # 基金净值数据、指数价格数据的index对齐到交易日列表
        fund_nav: pd.DataFrame = self._fund_nav_all.loc[start_date:end_date, :]
        self._fund_nav_origin: pd.DataFrame = fund_nav.reindex(_trading_days.index).fillna(method='ffill')
        self.one_day_jump = self._fund_nav_origin.pct_change(1).abs().max()
        self.three_day_jump = self._fund_nav_origin.pct_change(3).abs().max()
        normal_fund_list = []
        self.abnormal_reason = []
        for fund_id in self._fund_nav_origin:
            _df = self._fund_nav_origin[fund_id].dropna()
            if _df.shape[0] > 120:
                if _df.iloc[-120:].var() > 1e-6:
                    wind_class_2 = self._wind_class_2_dict[fund_id]
                    select_type = self._wind_type_dict.get(wind_class_2, None)
                    if select_type is None:
                        continue
                    one_day_jump_i = self.one_day_jump[fund_id]
                    three_day_jump_i = self.three_day_jump[fund_id]
                    if select_type in ['stock','QDII']:
                        if (one_day_jump_i < 0.1) & (three_day_jump_i < 0.25):
                            normal_fund_list.append(fund_id)
                        else:
                            self.abnormal_reason.append({'fund_id':fund_id,'abnormal_reason':f'high_risk: jump_max_1d {round(one_day_jump_i,3)} jump_max_3d {round(three_day_jump_i, 3)}'})
                    
                    elif select_type in ['bond','mix','mmf']:
                        if (one_day_jump_i < 0.05) & (three_day_jump_i < 0.15):
                            normal_fund_list.append(fund_id)
                        else:
                            self.abnormal_reason.append({'fund_id':fund_id,'abnormal_reason':f'low_risk: jump_max_1d {round(one_day_jump_i,3)} jump_max_3d {round(three_day_jump_i, 3)}'})
                else:
                    self.abnormal_reason.append({'fund_id':fund_id,'abnormal_reason':'price_inactive'})

            else:
                self.abnormal_reason.append({'fund_id':fund_id,'abnormal_reason':'less_than_half_y'})
        self._fund_nav = self._fund_nav_origin[normal_fund_list].copy()
        index_price: pd.DataFrame = self._index_price_all.loc[start_date:end_date, :]
        # 有的index最近没有数据，如活期存款利率/各种定期存款利率等，需要先reindex到全部的交易日列表上ffill
        self._index_price: pd.DataFrame = index_price.reindex(_trading_days.index).fillna(method='ffill')
        _bank_rate_df = self._bank_rate_df.reindex(_trading_days.index)
        self._index_price: pd.DataFrame = pd.concat([self._index_price, _bank_rate_df], axis=1).dropna(how='all', axis=1)
        # 再reindex到参与计算的交易日列表上
        # self._index_price: pd.DataFrame = index_price.reindex(_trading_days.index)
        pd.testing.assert_index_equal(self._fund_nav.index, self._index_price.index)
        
        self._macroeco: pd.DataFrame = self._macroeco_all.reindex(_trading_days.index)
        pd.testing.assert_index_equal(self._fund_nav.index, self._macroeco.index)
        try:
            # 这个指数有一天的点数是0，特殊处理一下
            self._index_price['spi_spa'] = self._index_price['spi_spa'].where(self._index_price.spi_spa != 0).fillna(method='ffill')
        except KeyError:
            pass

        # 对数净值取差分并且去掉第一个空值，得到基金对数收益率数列
        self._fund_ret: pd.DataFrame = np.log(self._fund_nav).diff().iloc[1:, :]

        self._fund_size = self._fund_size.reindex(self._fund_ret.index.union(self._fund_size.index)).fillna(method='ffill').reindex(self._fund_ret.index)
        pd.testing.assert_index_equal(self._fund_ret.index, self._fund_size.index)

        # 计算benchmark return，且index对齐到fund_ret
        self._benchmark_ret: pd.DataFrame = self._get_benchmark_return()
        self._benchmark_ret = self._benchmark_ret.reindex(self._fund_ret.index).dropna(how='all', axis=1)
        benchmark_cols = self._benchmark_ret.columns.tolist()
        for fund_id in self._fund_nav.columns:
            benchmark_id = fund_id
            if not benchmark_id in benchmark_cols:    
                wind_class_2 = self._wind_class_2_dict[fund_id]
                select_type = self._wind_type_dict[wind_class_2]
                _benchmark_ret = self._index_price[self._REPLACE_DICT[select_type]].pct_change(1).rename(benchmark_id)
                self._benchmark_ret = self._benchmark_ret.join(_benchmark_ret)
        pd.testing.assert_index_equal(self._fund_ret.index, self._benchmark_ret.index)
        self._fund_ret = self._fund_ret.join(self._benchmark_ret, rsuffix='_b')
        # 按wind二级分类计算基金收益率排名
        self._get_continue_stats_tool()

        self._fund_ret = self._fund_ret.join(self._hs300.rename('close_hs300'))
        self._fund_ret = self._fund_ret.join(self._mmf.rename('close_mmf'))
        self._fund_ret = self._fund_ret.dropna(how='all', axis=1)
        
        self.fund_type_benchmark = self._index_price[[self._REPLACE_DICT[fund_type] for fund_type in self._FUND_CLASSIFIER]]
        self.fund_type_benchmark = self.fund_type_benchmark.rename(columns={v : f'{k}_bench' for k, v in self._REPLACE_DICT.items()})
        self._fund_ret = self._fund_ret.join(self.fund_type_benchmark.pct_change(1))
        # 获取年报/半年报的发布日期
        md = end_date.strftime('%m%d')
        sentry_date = pd.Series(self._REPORT_DATE_LIST)
        sentry = sentry_date[sentry_date <= md]
        # 为半年报/年报发布预留一个季度的缓冲时间
        if sentry.empty:
            real_date = datetime.date(end_date.year - 1, 6, 30)
        elif len(sentry) <= 2:
            real_date = datetime.date(end_date.year - 1, 12, 31)
        else:
            real_date = datetime.date(end_date.year, 6, 30)

        # 取出持仓数据
        self._fund_hold = self._basic_api.get_history_fund_size(start_date=real_date, end_date=real_date)
        self._fund_hold = self._fund_hold[['fund_id', 'institution_holds', 'hold_num']].set_index('fund_id')
        # 取出货基风险相关数据
        self._risk_metric = self._basic_api.get_fund_hold_asset_by_id(start_date=real_date, end_date=real_date)
        self._risk_metric = self._risk_metric[['fund_id', 'first_repo_to_nav', 'avg_ptm']].set_index('fund_id')

    def df_resample(self, df):
        df.index = pd.to_datetime(df.index)
        df = df.resample('1W').sum()
        df.index = df.index.date
        return df

    def stutzer_index(self, ex_return: np.ndarray):
        information_statistic = lambda theta: np.log(np.mean(np.exp(theta[0] * ex_return)))
        theta0 = [-1.]
        bounds = Bounds((-np.inf), (0))
        result = minimize(information_statistic, theta0, method='SLSQP', bounds=bounds, tol=1e-16)
        if result.success:
            information_statistic = -result.fun
            if information_statistic <= 0:
                return 0
            stutzer_index = np.abs(np.mean(ex_return)) / np.mean(ex_return) * np.sqrt(2 * information_statistic)
            # result = {'information_statistic': information_statistic,
            #         'stutzer_index': stutzer_index,
            #         'theta': result.x[0]}
            return stutzer_index
        else:
            # result = {'information_statistic': information_statistic,
            #
            #   'stutzer_index': np.nan,
            #         'theta': result.x[0]}
            # print('未找到Information Statistic最大值')
            return np.nan

    def _lambda_cl(self, total: np.ndarray):
        if total.shape[0] <= 1:
            return {'beta':np.nan,
                    'alpha':np.nan,
                    'alpha_t':np.nan,
                    'alpha_p':np.nan,
                    'beta_t':np.nan,
                    'beta_p':np.nan,
                    }
        X = np.array([total[:, 1], total[:, 1]]).T
        X[:, 1][X[:, 1] > 0] = 0
        if np.count_nonzero(X[:, 1]) == 0:
            return {'beta':np.nan,
                    'alpha':np.nan,
                    'alpha_t':np.nan,
                    'alpha_p':np.nan,
                    'beta_t':np.nan,
                    'beta_p':np.nan,
                    }
        X[:, 0][X[:, 0] < 0] = 0
        est2 = sm.OLS(total[:, 0], sm.add_constant(X, prepend=False)).fit()
        return {'beta':est2.params[0] - est2.params[1],
                'alpha':est2.params[-1],
                'alpha_t':est2.tvalues[-1],
                'alpha_p':est2.pvalues[-1],
                # TODO beta 2 - beta 1 , p values and t values calculation is not correct
                'beta_t':est2.tvalues[1],
                'beta_p':est2.pvalues[1]
                }

    def _lambda_tm(self, total: np.ndarray):
        if not total.size:
            return {'beta':np.nan,
                    'alpha':np.nan,
                    'alpha_t':np.nan,
                    'alpha_p':np.nan,
                    'beta_t':np.nan,
                    'beta_p':np.nan,
                    }
        X = np.array([total[:, 1], total[:, 1] * total[:, 1]]).T
        est2 = sm.OLS(total[:, 0], sm.add_constant(X, prepend=False)).fit()
        return {'beta':est2.params[1],
                'alpha':est2.params[-1],
                'alpha_t':est2.tvalues[-1],
                'alpha_p':est2.pvalues[-1],
                'beta_t':est2.tvalues[1],
                'beta_p':est2.pvalues[1]
                }

    def _lambda_hm(self, total: np.ndarray):
        if not total.size:
            return {'beta':np.nan,
                    'alpha':np.nan,
                    'alpha_t':np.nan,
                    'alpha_p':np.nan,
                    'beta_t':np.nan,
                    'beta_p':np.nan,
                    }
        X = np.array([total[:, 1], total[:, 1]]).T
        X[:, 1][X[:, 1] < 0] = 0
        est2 = sm.OLS(total[:, 0], sm.add_constant(X, prepend=False)).fit()
        return {'beta':est2.params[1],
                'alpha':est2.params[-1],
                'alpha_t':est2.tvalues[-1],
                'alpha_p':est2.pvalues[-1],
                'beta_t':est2.tvalues[1],
                'beta_p':est2.pvalues[1]
                }

    def _lambda_alpha_beta(self, df_i):
        if np.count_nonzero(np.count_nonzero(df_i, axis=0)) < df_i.shape[1]:
            return np.nan, 0
        ploy_res = np.polyfit(y=df_i[:, 0], x=df_i[:, 1], deg=1)
        beta = ploy_res[0]
        alpha = ploy_res[1] * self._TRADING_DAYS_PER_YEAR
        return alpha, beta

    def _get_benchmark_return(self) -> pd.DataFrame:
        benchmark_list: Dict[str, float] = {}
        # 遍历每一只基金的benchmark进行处理
        for row in self._fund_benchmark_df.itertuples(index=False):
            values: List[pd.Series] = []
            cons: float = 0
            # 空的benchmark表明我们没有对应的指数或无法解析公式
            if row.benchmark_s:
                benchmark: Dict[str, float] = json.loads(row.benchmark_s)
                benchmark_raw: Dict[str, float] = eval(row.benchmark)
                for (index, weight), index_raw in zip(benchmark.items(), benchmark_raw.keys()):
                    if index == '1':
                        # 表示benchmark中该项为常数
                        cons += weight
                    elif index in ('ddir', 'nonor', 'tmd_1y', 'tmd_2y', 'tmd_3m', 'tmd_3y', 'tmd_5y', 'tmd_6m', 'tmd_7d'):
                        if weight == -1:
                            # 表示我们无法解析公式
                            # print(f'[benchmark_return] Error: Need fix {row.fund_id} {index} {index_raw}')
                            # self.log.append((row.fund_id, index))
                            break
                        else:
                            try:
                                if index == 'nonor':
                                    # 在这里我们用超额存款准备金率替代同业存款利率
                                    ra: pd.Series = self._macroeco.loc[:, 'EX_DR_RATIO']
                                else:
                                    ra: pd.Series = self._index_price.loc[:, index]
                            except KeyError:
                                # 表示我们没有该指数的价格数据
                                # print(f'[benchmark_return] Error: Data Missing: {row.fund_id} {index} {index_raw}')
                                # self.log.append((row.fund_id, index))
                                break
                            else:
                                values.append(ra.iloc[1:] * 0.01 * weight / self._TRADING_DAYS_PER_YEAR)
                    else:
                        if weight == -1:
                            # 表示我们无法解析公式
                            # print(f'[benchmark_return] Error: Need fix {row.fund_id} {index} {index_raw}')
                            # self.log.append((row.fund_id, index))
                            break
                        else:
                            try:
                                ra: pd.Series = self._index_price.loc[:, index]
                            except KeyError:
                                # 表示我们没有该指数的价格数据
                                # print(f'Error: Data Missing: {row.fund_id} {index} {index_raw}')
                                # self.log.append((row.fund_id, index))
                                break
                            else:
                                ra = np.log(ra).diff().iloc[1:]
                                values.append(ra * weight)
                else:
                    if values or cons:
                        the_sum: float = sum(values)
                        if cons:
                            the_sum += np.log(math.pow(1 + cons, 1 / self._TRADING_DAYS_PER_YEAR))
                        benchmark_list[row.fund_id] = the_sum

        return pd.DataFrame.from_dict(benchmark_list)

    def _lambda_make_rank_dic(self, x: pd.DataFrame):
        resample_ret: pd.DataFrame = self.df_resample(self._fund_ret.loc[:, self._fund_ret.columns.intersection(x.fund_id.array)])
        self._rank_dic[x.name] = resample_ret.rank(pct=True, axis=1).rename_axis(columns='fund_id')

    def _get_continue_stats_tool(self):
        self._fund_list.groupby(by='wind_class_2').apply(self._lambda_make_rank_dic)

    def get_scale(self, end_date, fund_id):
        try:
            scale = self._fund_size.loc[self.end_date, fund_id]
        except KeyError:
            scale = np.nan
        return scale

    def _calculate_item(self, fund_id: str, wind_2_class: str):
        # 取最后一年的有效净值
        _sr: pd.Series = self._fund_nav[fund_id]
        sr: pd.Series = _sr[_sr.notna()].tail(self._data_cycle_days)
        temp_nav = _sr.to_numpy()
        # 生成一个m*n的矩阵
        temp_nav = np.array([temp_nav[i:self._TRADING_DAYS_PER_YEAR//2 + i + 20] for i in range(0, temp_nav.shape[0] - 20 - self._TRADING_DAYS_PER_YEAR//2, 20)])
        ret: np.ndarray = temp_nav[:, 1:] / temp_nav[:, :-1]
        # 过滤掉全是nan或只有1个不是nan的行
        filter1 = (ret.shape[1] - np.count_nonzero(np.isnan(ret), axis=1) > 1)
        ret, temp_nav = ret[filter1], temp_nav[filter1]
        annual_vol: np.ndarray = np.nanstd(ret, axis=1, ddof=1) * np.sqrt(self._TRADING_DAYS_PER_YEAR)
        # 一维数组，所以这里直接用nonzero即可
        filter1 = annual_vol.nonzero()
        annual_vol, temp_nav = annual_vol[filter1], temp_nav[filter1]
        annual_ret = np.exp(np.log(temp_nav[:, -1] / temp_nav[:, 0]) / temp_nav.shape[1] * self._TRADING_DAYS_PER_YEAR) - 1
        _res = (annual_ret - self._RISK_FEE_RATE) / annual_vol
        _res = _res[~np.isnan(_res)]
        if _res.size < 6:
            continue_regress_v = np.nan
            continue_regress_t = np.nan
        else:
            mod = AutoReg(_res, 1)
            res = mod.fit()
            continue_regress_v = res.params[0]
            continue_regress_t = res.tvalues[0]

        if wind_2_class is not None:
            _rank_df = self._rank_dic[wind_2_class]
            res = []
            last = ''
            for idx, i in enumerate(_rank_df[fund_id]):
                now = 'W' if i > 0.5 else 'L'
                if idx != 0:
                    res.append(last+now)
                last = now
            ww = max(res.count('WW'), 1)
            ll = max(res.count('LL'), 1)
            wl = max(res.count('WL'), 1)
            lw = max(res.count('LW'), 1)
            continue_stats_v = ww * ll / wl / lw
        else:
            continue_stats_v = np.nan

        # 取最后一年的有效收益率+业绩比较基准收益率
        df_i: np.ndarray = self._fund_ret[[fund_id, fund_id+'_b']].to_numpy()
        df_i = df_i[(~np.isnan(df_i)).all(axis=1)]
        df_i = df_i[-self._data_cycle_days:]

        df_i_hs300: np.ndarray = self._fund_ret[[fund_id, 'close_hs300']].to_numpy()
        df_i_hs300 = df_i_hs300[(~np.isnan(df_i_hs300)).all(axis=1)]
        df_i_hs300 = df_i_hs300[-self._data_cycle_days:]

        df_i_mmf: np.ndarray = self._fund_ret[[fund_id, 'close_mmf']].to_numpy()
        df_i_mmf = df_i_mmf[(~np.isnan(df_i_mmf)).all(axis=1)]
        df_i_mmf = df_i_mmf[-self._data_cycle_days:]

        wind_class_2 = self._wind_class_2_dict[fund_id]
        fund_type = self._wind_type_dict[wind_class_2]
        df_i_cl = self._fund_ret[[fund_id]].join(self._fund_ret[[f'{fund_type}_bench']]).to_numpy()
        df_i_cl = df_i_cl[(~np.isnan(df_i_cl)).all(axis=1)]
        df_i_cl = df_i_cl[-self._data_cycle_days:]

        # alpha, beta
        alpha, beta = self._lambda_alpha_beta(df_i)
        # alpha, beta to the market
        alpha_hs300, beta_hs300 = self._lambda_alpha_beta(df_i_hs300)
        # mdd & len(mdd)
        mdd_part = sr / sr.cummax()
        mdd = 1 - mdd_part.min()
        mdd_date2 = mdd_part.idxmin()
        mdd_date1 = sr[:mdd_date2].idxmax()
        mdd_len = (mdd_date2 - mdd_date1).days
        # sharpe ratio
        annual_vol = (sr / sr.shift(1)).std(ddof=1) * np.sqrt(self._TRADING_DAYS_PER_YEAR)
        annual_ret = np.exp(np.log(sr.iloc[-1] / sr.fillna(method='bfill').iloc[0]) / sr.shape[0] * self._TRADING_DAYS_PER_YEAR) - 1
        sharpe = (annual_ret - self._RISK_FEE_RATE) / annual_vol
        # treynor ratio
        if beta != 0:
            treynor = (np.nanmean(df_i[:, 0]) - self._RISK_FEE_RATE_PER_DAY) / beta
        else:
            treynor = np.nan
        # calma ratio
        calma_ratio = annual_ret / mdd if mdd != 0 else np.nan
        # ex return
        _ex_return = df_i[:, 0] - df_i[:, 1]
        # excess return against hs300
        _ex_return_hs300 = df_i_hs300[:, 0] - df_i_hs300[:, 1]
        # excess return against mmf
        _ex_return_mmf = df_i_mmf[:, 0] - df_i_mmf[:, 1]
        # winning rate against mmf
        if len(_ex_return_mmf) != 0:
            winning_rate = len(_ex_return_mmf[_ex_return_mmf > 0]) / len(_ex_return_mmf)
        else:
            winning_rate = 0
        # track error
        track_err = np.nanstd(_ex_return, ddof=1) * np.sqrt(self._TRADING_DAYS_PER_YEAR)
        # track error agains hs300
        track_err_hs300 = np.nanstd(_ex_return_hs300, ddof=1) * np.sqrt(self._TRADING_DAYS_PER_YEAR)
        # information error
        info_ratio = alpha / track_err
        # information ratio against hs300
        info_ratio_hs300 = alpha_hs300 / track_err_hs300
        # scale
        scale = self.get_scale(self.end_date, fund_id)
        # VaR
        ret = df_i[:, 0]
        if ret.size > 0:
            VaR = np.quantile(ret, 0.05)
            CVaR = ret[ret <= VaR].mean()
        else:
            VaR = np.nan
            CVaR = np.nan
        # institution holds & hold_num
        try:
            temp_hold = self._fund_hold.loc[fund_id, :]
            ins_holds = temp_hold.institution_holds
            hold_num = temp_hold.hold_num
        except KeyError:
            ins_holds = np.nan
            hold_num = np.nan
        #
        try:
            temp_risk = self._risk_metric.loc[fund_id, :]
            leverage = temp_risk.first_repo_to_nav
            ptm = temp_risk.avg_ptm
        except KeyError:
            leverage = np.nan
            ptm = np.nan

        stock_tm_res = self._lambda_tm(df_i_cl)
        stock_tm_alpha = stock_tm_res['alpha']
        stock_tm_alpha_t = stock_tm_res['alpha_t']
        stock_tm_alpha_p = stock_tm_res['alpha_p']
        stock_tm_beta = stock_tm_res['beta']
        stock_tm_beta_t = stock_tm_res['beta_t']
        stock_tm_beta_p = stock_tm_res['beta_p']

        stock_hm_res = self._lambda_hm(df_i_cl)
        stock_hm_alpha = stock_hm_res['alpha']
        stock_hm_alpha_t = stock_hm_res['alpha_t']
        stock_hm_alpha_p = stock_hm_res['alpha_p']
        stock_hm_beta = stock_hm_res['beta']
        stock_hm_beta_t = stock_hm_res['beta_t']
        stock_hm_beta_p = stock_hm_res['beta_p']

        stock_cl_res = self._lambda_cl(df_i_cl)
        stock_cl_alpha = stock_cl_res['alpha']
        stock_cl_alpha_t = stock_cl_res['alpha_t']
        stock_cl_alpha_p = stock_cl_res['alpha_p']
        stock_cl_beta = stock_cl_res['beta']
        stock_cl_beta_t = stock_cl_res['beta_t']
        stock_cl_beta_p = stock_cl_res['beta_p']

        # stutzer
        stutzer = self.stutzer_index(df_i[:, 0]-self._RISK_FEE_RATE_PER_DAY) * np.sqrt(self._TRADING_DAYS_PER_YEAR)
        # stutzer = self.stutzer_index(np.array(self._fund_ret.tail(self._TRADING_DAYS_PER_YEAR)[fund_id] - self._benchmark_ret.tail(self._TRADING_DAYS_PER_YEAR)[fund_id]))
        return pd.Series({
            'fund_id':fund_id,
            'datetime':self.end_date,
            'alpha':alpha,
            'beta':beta,
            'annual_vol':annual_vol,
            'annual_ret':annual_ret,
            'track_err':track_err,
            'mdd': mdd,
            'mdd_len':mdd_len,
            'winning_rate':winning_rate,
            'VaR':VaR,
            'CVaR':CVaR,
            'ins_holds':ins_holds,
            'hold_num':hold_num,
            'leverage':leverage,
            'ptm':ptm,
            'continue_regress_v':continue_regress_v,
            'continue_regress_t':continue_regress_t,
            'continue_stats_v':continue_stats_v,

            'stock_cl_alpha':stock_cl_alpha,
            'stock_cl_alpha_t':stock_cl_alpha_t,
            'stock_cl_alpha_p':stock_cl_alpha_p,
            'stock_cl_beta':stock_cl_beta,
            'stock_cl_beta_t':stock_cl_beta_t,
            'stock_cl_beta_p':stock_cl_beta_p,

            'stock_tm_alpha':stock_tm_alpha,
            'stock_tm_alpha_t':stock_tm_alpha_t,
            'stock_tm_alpha_p':stock_tm_alpha_p,
            'stock_tm_beta':stock_tm_beta,
            'stock_tm_beta_t':stock_tm_beta_t,
            'stock_tm_beta_p':stock_tm_beta_p,

            'stock_hm_alpha':stock_hm_alpha,
            'stock_hm_alpha_t':stock_hm_alpha_t,
            'stock_hm_alpha_p':stock_hm_alpha_p,
            'stock_hm_beta':stock_hm_beta,
            'stock_hm_beta_t':stock_hm_beta_t,
            'stock_hm_beta_p':stock_hm_beta_p,
            'info_ratio':info_ratio,
            'info_ratio_hs300':info_ratio_hs300,
            'treynor':treynor,
            'sharpe':sharpe,
            'calma_ratio':calma_ratio,
            'stutzer':stutzer,
            'scale':scale,
        })

    def calculate(self):
        fund_list = self._fund_list[['fund_id', 'wind_class_2']]
        # 对fund_nav, fund_list二者交集的每个fund_id进行计算
        self._result = fund_list[fund_list.fund_id.isin(self._fund_nav.columns.to_list())].apply(lambda x: self._calculate_item(x.fund_id, x.wind_class_2), axis=1)
        self._result['ins_holds'] = self._result['ins_holds'].fillna(0)
        self._result['hold_num'] = self._result['hold_num'].fillna(0)
        # add abnormal
        _df = pd.DataFrame(self.abnormal_reason)
        _df['datetime'] = self.end_date
        self._result = pd.merge(left=self._result, right=_df, how='outer', on=['fund_id','datetime'])
        self._result['data_cycle'] = str(self._data_cycle) + 'Y'
        self._result = self._result.replace({np.inf: np.nan, -np.inf: np.nan})

    def process(self, start_date: str, end_date: str, end_date_dt: datetime.date) -> List[str]:
        print(f'indicator group update on the last day of week {end_date_dt}')
        failed_tasks: List[str] = []
        try:
            self.init(end_date)
            print('init done, to calc indicators')
            self.calculate()
            self._data_helper._upload_derived(self._result, FundIndicatorGroup.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(f'fund_indicator_group({self._data_cycle}Y)')
        return failed_tasks

    @staticmethod
    def update_history(end_date: str, data_cycle: int):
        from ...wrapper.mysql import BasicDatabaseConnector
        from ...view.basic_models import TradingDayList
        with BasicDatabaseConnector().managed_session() as quant_session:
            query = quant_session.query(TradingDayList)
            trade_days = pd.read_sql(query.statement, query.session.bind)

        fipg = FundIndicatorProcessorGroup(DerivedDataHelper(), data_cycle)
        fipg.history_load_data(end_date)
        dts = trade_days[(trade_days.datetime >= datetime.date(2010, 1, 1)) &
                         (trade_days.datetime < pd.to_datetime(end_date, infer_datetime_format=True))].datetime.tolist()
        dts.reverse()
        dts = [dt for dt in dts if dt.weekday() == 4]
        for date in dts:
            fipg.history_init(date)
            fipg.calculate()
            fipg._data_helper._upload_derived(fipg._result, FundIndicatorGroup.__table__.name)
            print(f'{date} done')


if __name__ == '__main__':
    date = '20210618'
    fipg = FundIndicatorProcessorGroup(DerivedDataHelper(), 5)
    fipg.process(date, date, pd.to_datetime(date).date())
    # FundIndicatorProcessorGroup.update_history('20201009', 5)
