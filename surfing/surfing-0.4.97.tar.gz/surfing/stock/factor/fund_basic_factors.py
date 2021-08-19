import pandas as pd
import numpy as np
import math
import json
import re
import datetime
from typing import Optional, List, Union, Dict
from .base import Factor
from .calculator import Calculator
from .utils import _START_DATE
from ...data.manager import DataManager
from ...data.manager.fund_info_filter import fund_info_update, get_conv_funds, filter_fund_info, active_fund_info as get_active_fund_info
from ...data.struct import AssetTimeSpan
from ...constant import FundFactorType

class FundInfo(Factor):

    def __init__(self):
        super().__init__(f_name='FundInfo', f_type=FundFactorType.BASIC, f_level='basic')

    def calc(self):
        self._factor = DataManager.basic_data(func_name='get_fund_info')
        self._factor = fund_info_update(self._factor).drop(columns=['_update_time'], errors='ignore')

class InMarketFundInfo(Factor):

    def __init__(self):
        super().__init__(f_name='InMarketFundInfo', f_type=FundFactorType.BASIC, f_level='basic')

    def calc(self):#TODO
        self._factor = DataManager.basic_data(func_name='get_fund_status').drop(columns=['_update_time'], errors='ignore')
        self._factor = self._factor[~self._factor['trade_status'].isnull()]
        self._factor = self._factor[~((self._factor.redem_status == '正常赎回') & (self._factor.purch_status == '正常申购'))]
        
class CloseFundInfo(Factor):

    def __init__(self):
        super().__init__(f_name='CloseFundInfo', f_type=FundFactorType.BASIC, f_level='basic')

    def calc(self):
        self._factor = DataManager.basic_data(func_name='get_fund_open_info').drop(columns=['_update_time'], errors='ignore')

class FilteredFundInfoI(Factor):
    
    def __init__(self):
        super().__init__(f_name='FilteredFundInfoI', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(FundInfo())
        self._deps.add(InMarketFundInfo())
        self._deps.add(CloseFundInfo())

    def calc(self):
        self._factor = FundInfo().get()
        index_list = list(AssetTimeSpan.__dataclass_fields__.keys())
        self._factor = filter_fund_info(self._factor, index_list)
        in_market_fund_info = InMarketFundInfo().get()
        close_fund_info = CloseFundInfo().get()
        self._factor = self._factor[(~self._factor.fund_id.isin(in_market_fund_info.fund_id))
                                & (~self._factor.fund_id.isin(close_fund_info.fund_id))]

class TradingDay(Factor):

    def __init__(self):
        super().__init__(f_name='TradingDay', f_type=FundFactorType.BASIC, f_level='basic')

    def calc(self):
        self._factor = DataManager.basic_data(func_name='get_trading_day_list').set_index('datetime').drop(columns=['_update_time'], errors='ignore')
        self._factor = self._factor[(self._factor.index >= pd.to_datetime(_START_DATE).date())
                                 & (self._factor.index < datetime.datetime.now().date())]

class IndexInfo(Factor):

    def __init__(self):
        super().__init__(f_name='IndexInfo', f_type=FundFactorType.BASIC, f_level='basic')

    def calc(self):
        self._factor = DataManager.basic_data(func_name='get_index_info').drop(columns=['_update_time'], errors='ignore')

class FundManagerInfo(Factor):

    def __init__(self):
        super().__init__(f_name='FundManagerInfo', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(FundInfo())

    def calc(self):
        self._factor = DataManager.derived_data(func_name='get_fund_manager_info').drop(columns=['_update_time'], errors='ignore')
        fund_info = FundInfo().get()
        self._factor = pd.merge(self._factor, fund_info[['fund_id','company_id','wind_class_2']], how='left', on='fund_id' )

class FundConvInfo(Factor):

    def __init__(self):
        super().__init__(f_name='FundConvInfo', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(FundInfo())

    def calc(self):
        fund_conv_stats = DataManager.basic_data(func_name='get_fund_conv_stats')
        fund_info = FundInfo().get()
        self._factor = get_conv_funds(fund_conv_stats, fund_info)
        self._factor = pd.DataFrame(self._factor,columns=['fund_id'])
        
class FundBenchmarkInfo(Factor):

    def __init__(self):
        super().__init__(f_name='FundBenchmarkInfo', f_type=FundFactorType.BASIC, f_level='basic')

    def calc(self):
        self._factor = DataManager.basic_data(func_name='get_fund_benchmark').drop(columns=['_update_time'], errors='ignore')

class FilteredFundInfoWhole(Factor):

    def __init__(self):
        super().__init__(f_name='FilteredFundInfoWhole', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(FundInfo())
        self._deps.add(FundBenchmarkInfo())
        self._deps.add(InMarketFundInfo())
        self._deps.add(CloseFundInfo())

    def calc(self):
        fund_info = FundInfo().get()
        benchmark_info = FundBenchmarkInfo().get()
        index_list = list(AssetTimeSpan.__dataclass_fields__.keys())
        fund_info_index = filter_fund_info(fund_info, index_list)
        fund_info_active = get_active_fund_info(fund_info, benchmark_info)
        in_market_fund_info = InMarketFundInfo().get()
        close_fund_info = CloseFundInfo().get()
        fund_info = fund_info[(fund_info.fund_id.isin(fund_info_active.fund_id))
                            | (fund_info.fund_id.isin(fund_info_index.fund_id))]
        self._factor = fund_info[(~fund_info.fund_id.isin(in_market_fund_info.fund_id))
                                & (~fund_info.fund_id.isin(close_fund_info.fund_id))]

class ActiveFundInfo(Factor): #based on fund_info fund_benchmark_info

    def __init__(self):
        super().__init__(f_name='ActiveFundInfo', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(FundInfo())
        self._deps.add(FundBenchmarkInfo())

    def calc(self):
        self._factor = get_active_fund_info(FundInfo().get(), FundBenchmarkInfo().get()).drop(columns=['_update_time'], errors='ignore')

class IndexCloseDaily(Factor):

    def __init__(self):
        super().__init__(f_name='IndexCloseDaily', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(TradingDay())

    def calc(self):
        self._factor = DataManager.basic_data(func_name='get_index_price_dt', start_date=_START_DATE, columns=['close']).drop(columns=['_update_time'], errors='ignore')
        self._factor = self._factor.pivot(index='datetime',columns='index_id',values='close')
        self._factor = Calculator.data_reindex_daily_trading_day(self._factor, TradingDay().get())##

class IndexRetDaily(Factor): # based on index_close_daily

    def __init__(self):
        super().__init__(f_name='IndexRetDaily', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(TradingDay())
        self._deps.add(IndexCloseDaily())

    def calc(self):
        self._factor = IndexCloseDaily().get()
        self._factor = np.log(self._factor).diff(1)
        self._factor = self._factor.replace(np.Inf,np.nan).replace(-np.Inf,np.nan)
        self._factor = Calculator.data_reindex_daily_trading_day(self._factor, TradingDay().get())

class IndexRetWeekly(Factor): # based on IndexRetDaily

    def __init__(self):
        super().__init__(f_name='IndexRetWeekly', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(IndexRetDaily())

    def calc(self):
        self._factor = IndexRetDaily().get()
        self._factor = Calculator.data_resample_weekly_ret(self._factor).dropna(axis=0, how='all')

class IndexRetMonthly(Factor): # based on IndexRetDaily

    def __init__(self):
        super().__init__(f_name='IndexRetMonthly', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(IndexRetDaily())

    def calc(self):
        self._factor = IndexRetDaily().get()
        self._factor = Calculator.data_resample_monthly_ret(self._factor).dropna(axis=0, how='all')

class FundNavDaily(Factor):

    def __init__(self):
        super().__init__(f_name='FundNavDaily', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(TradingDay())

    def calc(self):
        self._factor = DataManager.basic_data(func_name='get_fund_nav_with_date', start_date=_START_DATE).drop(columns=['_update_time'], errors='ignore')
        self._factor = self._factor.pivot(index='datetime',columns='fund_id',values='adjusted_net_value')
        self._factor = Calculator.data_reindex_daily_trading_day(self._factor, TradingDay().get())

class FundRetDaily(Factor): # based on FundNavDaily

    def __init__(self):
        super().__init__(f_name='FundRetDaily', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(TradingDay())
        self._deps.add(FundNavDaily())

    def calc(self):
        self._factor = FundNavDaily().get()
        self._factor = np.log(self._factor).diff(1)
        self._factor = Calculator.data_reindex_daily_trading_day(self._factor, TradingDay().get())

class FundSize(Factor):

    def __init__(self):
        super().__init__(f_name='FundSize', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(TradingDay())

    def calc(self):
        self._factor = DataManager.basic_data(func_name='get_fund_size_range', start_date=_START_DATE).drop(columns=['_update_time'], errors='ignore')
        self._factor = self._factor.pivot(index='datetime',columns='fund_id',values='size')
        self._factor = Calculator.data_reindex_daily_trading_day(self._factor, TradingDay().get())

class FundSizeCombine(Factor): # based on FundSize

    def __init__(self):
        super().__init__(f_name='FundSizeCombine', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(TradingDay())
        self._deps.add(FundInfo())
        self._deps.add(FundSize())

    def calc(self):
        fund_info = FundInfo().get()
        fund_size = FundSize().get()
        fund_info['trim_name'] = fund_info.desc_name.map(lambda x : re.subn(r'[ABCDEFR]{1,2}(\(人民币\)|\(美元现汇\)|\(美元现钞\)|1|2|3)?$', '', x)[0])
        trim_name_df = fund_info.set_index('fund_id')[['trim_name']]
        fund_id_df = fund_info.set_index('trim_name')[['fund_id']]
        self._factor = fund_size.T.join(trim_name_df).groupby('trim_name').sum()
        self._factor = self._factor.join(fund_id_df).set_index('fund_id').T
        self._factor = Calculator.data_reindex_daily_trading_day(self._factor, TradingDay().get())

class FundCompanyHold(Factor):

    def __init__(self):
        super().__init__(f_name='FundCompanyHold', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(TradingDay())

    def calc(self):
        self._factor = DataManager.basic_data(func_name='get_fund_company_hold', start_date=_START_DATE).drop(columns=['_update_time'], errors='ignore')
        self._factor = self._factor.pivot(index='datetime',columns='fund_id',values='institution_holds')
        self._factor = Calculator.data_reindex_daily_trading_day(self._factor, TradingDay().get())

class FundRetDailyModify(Factor): # based on fund_info fund_ret_daily

    def __init__(self):
        super().__init__(f_name='FundRetDailyModify', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(TradingDay())
        self._deps.add(FundInfo())
        self._deps.add(FundRetDaily())

    def calc(self):
        fund_info = FundInfo().get()
        fund_ret = FundRetDaily().get()
        _res = []
        _fund_ret_columns = fund_ret.columns.tolist()
        for fund_type, filter_ratio in Calculator.FILTER_NAV_RATIO.items():
            _info_fund_list = fund_info[fund_info['wind_class_2'].isin(Calculator.FUND_CLASSIFIER[fund_type])].fund_id.tolist()
            _fund_list = list(set(_info_fund_list).intersection(_fund_ret_columns))
            _fund_ret = fund_ret[_fund_list].copy()
            _fund_ret[_fund_ret > filter_ratio] = 0
            _res.append(_fund_ret)
        self._factor = pd.concat(_res,axis=1)
        self._factor = Calculator.data_reindex_daily_trading_day(self._factor, TradingDay().get())
        self._factor = self._factor.loc[:,~self._factor.columns.duplicated()].copy()

class FundInfoAsset(Factor):

    def __init__(self):
        super().__init__(f_name='FundInfoAsset', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(FundInfo())
        self._deps.add(ActiveFundInfo())
        self._deps.add(FundRetDailyModify())

    def calc(self):
        fund_info = FundInfo().get()
        active_fund_info = ActiveFundInfo().get()
        fund_ret = FundRetDailyModify().get()

        index_list = list(AssetTimeSpan.__dataclass_fields__.keys())
        fund_to_index_dict = fund_info[fund_info.index_id.isin(index_list)][['fund_id', 'index_id']].set_index('fund_id').to_dict()['index_id']
        index_fund = { index_id : [fund_idx for fund_idx, index_idx in fund_to_index_dict.items() if index_idx == index_id] for index_id in index_list}
        if 'active' in index_fund.keys():
            del index_fund['active']
        if 'conv_bond' in index_fund.keys():
            del index_fund['conv_bond']
        for index_id, fund_list in index_fund.items():
            active_list = active_fund_info[active_fund_info.index_id == index_id].fund_id
            fund_list = list(set(active_list).union(set(fund_list)).intersection(fund_ret.columns))
            index_fund[index_id] = fund_list
        fund_to_index = {}
        for index_id, fund_list in index_fund.items():
            for fund_id in fund_list:
                fund_to_index[fund_id] = index_id
        fund_info.loc[:,'bk_index_id'] = fund_info.fund_id.map(lambda x : fund_to_index.get(x))
        self._factor = fund_info

class FundRetWeeklyModify(Factor): # based on FundRetDailyModify

    def __init__(self):
        super().__init__(f_name='FundRetWeeklyModify', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(FundRetDailyModify())

    def calc(self):
        self._factor = FundRetDailyModify().get()
        self._factor = Calculator.data_resample_weekly_ret(self._factor).dropna(axis=0, how='all')

class FundRetMonthlyModify(Factor): # based on FundRetDailyModify

    def __init__(self):
        super().__init__(f_name='FundRetMonthlyModify', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(FundRetDailyModify())

    def calc(self):
        self._factor = FundRetDailyModify().get()
        self._factor = Calculator.data_resample_monthly_ret(self._factor).dropna(axis=0, how='all')

class FundNavDailyModify(Factor): # based on fund_ret_daily_modify

    def __init__(self):
        super().__init__(f_name='FundNavDailyModify', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(TradingDay())
        self._deps.add(FundRetDailyModify())

    def calc(self):
        self._factor = FundRetDailyModify().get()
        self._factor = np.exp(self._factor.cumsum())
        self._factor = Calculator.data_reindex_daily_trading_day(self._factor, TradingDay().get())

class FundNavWeeklyModify(Factor): # based on FundNavDailyModify

    def __init__(self):
        super().__init__(f_name='FundNavWeeklyModify', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(FundNavDailyModify())

    def calc(self):
        self._factor = FundNavDailyModify().get()
        self._factor = Calculator.data_resample_weekly_nav(self._factor).dropna(axis=0, how='all')

class FundNavMonthlyModify(Factor): # based on FundNavDailyModify

    def __init__(self):
        super().__init__(f_name='FundNavMonthlyModify', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(FundNavDailyModify())

    def calc(self):
        self._factor = FundNavDailyModify().get()
        self._factor = Calculator.data_resample_monthly_nav(self._factor).dropna(axis=0, how='all')

class Macroeco(Factor):

    def __init__(self):
        super().__init__(f_name='Macroeco', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(TradingDay())

    def calc(self):
        self._factor = DataManager.raw_data(func_name='get_em_macroeconomic_daily', codes=['EX_DR_RATIO']).drop(columns='_update_time')
        self._factor = self._factor.pivot_table(index='datetime', columns='codes', values='value')
        self._factor = Calculator.data_reindex_daily_trading_day(self._factor, TradingDay().get())

class FundBenchmarkRet(Factor): # based on fund_benchmark_info macroeco index_close_daily fund_info fund_nav_daily fund_info

    def __init__(self):
        super().__init__(f_name='FundBenchmarkRet', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(TradingDay())
        self._deps.add(FundBenchmarkInfo())
        self._deps.add(Macroeco())
        self._deps.add(IndexCloseDaily())
        self._deps.add(FundInfo())
        self._deps.add(FundNavDaily())

    def calc(self):
        fund_benchmark_info = FundBenchmarkInfo().get()
        macroeco = Macroeco().get()
        index_price = IndexCloseDaily().get()
        fund_info = FundInfo().get()
        fund_nav = FundNavDaily().get()
        wind_class_2_dict = fund_info.set_index('fund_id')['wind_class_2'].to_dict()

        benchmark_list: Dict[str, float] = {}
        # 遍历每一只基金的benchmark进行处理
        for row in fund_benchmark_info.itertuples(index=False):
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
                            break
                        else:
                            try:
                                if index == 'nonor':
                                    # 在这里我们用超额存款准备金率替代同业存款利率
                                    ra: pd.Series = macroeco.loc[:, 'EX_DR_RATIO']
                                else:
                                    ra: pd.Series = index_price.loc[:, index]
                            except KeyError:
                                # 表示我们没有该指数的价格数据
                                # print(f'[benchmark_return] Error: Data Missing: {row.fund_id} {index} {index_raw}')
                                break
                            else:
                                values.append(ra.iloc[1:] * 0.01 * weight / Calculator.TRADING_DAYS_PER_YEAR)
                    else:
                        if weight == -1:
                            # 表示我们无法解析公式
                            # print(f'[benchmark_return] Error: Need fix {row.fund_id} {index} {index_raw}')
                            break
                        else:
                            try:
                                ra: pd.Series = index_price.loc[:, index]
                            except KeyError:
                                # 表示我们没有该指数的价格数据
                                # print(f'Error: Data Missing: {row.fund_id} {index} {index_raw}')
                                break
                            else:
                                ra = np.log(ra).diff().iloc[1:]
                                values.append(ra * weight)
                else:
                    if values or cons:
                        the_sum: float = sum(values)
                        if cons:
                            the_sum += np.log(math.pow(1 + cons, 1 / Calculator.TRADING_DAYS_PER_YEAR))
                        benchmark_list[row.fund_id] = the_sum
        self._factor =  pd.DataFrame.from_dict(benchmark_list)
        benchmark_cols = self._factor.columns.tolist()
        fund_nav_cols = fund_nav.columns.tolist()
        _res = []
        for fund_id in fund_nav_cols:
            benchmark_id = fund_id
            if not benchmark_id in benchmark_cols:    
                wind_class_2 = wind_class_2_dict[fund_id]
                if wind_class_2 not in Calculator.WIND_TYPE_DICT:
                    continue
                select_type = Calculator.WIND_TYPE_DICT[wind_class_2]
                index_price_i = index_price[Calculator.REPLACE_DICT[select_type]].rename(benchmark_id)
                benchmark_ret = np.log(index_price_i).diff(1)
                _res.append(benchmark_ret)
        self._factor = self._factor.join(pd.concat(_res,axis=1))
        self._factor = Calculator.data_reindex_daily_trading_day(self._factor, TradingDay().get())
        cols = self._factor.columns.tolist()
        cols = [i for i in cols if isinstance(i, str)]
        self._factor = self._factor[cols]

        # fund nav is null, set benchmark null
        common_columns = list(fund_nav.columns.intersection(self._factor.columns))
        con_df = fund_nav[common_columns].isnull()
        _factor = self._factor[common_columns].copy()
        _factor[con_df] = np.nan
        _cols = self._factor.columns
        _cols_not_in = [ i for i in _cols if i not in common_columns]
        self._factor = _factor.join(self._factor[_cols_not_in])

class FundBenchmarkPrice(Factor): # based on FundBenchmarkRet

    def __init__(self):
        super().__init__(f_name='FundBenchmarkPrice', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(TradingDay())
        self._deps.add(FundBenchmarkRet())

    def calc(self):
        self._factor = FundBenchmarkRet().get()
        self._factor = np.exp(self._factor.cumsum())
        self._factor = Calculator.data_reindex_daily_trading_day(self._factor, TradingDay().get())

class FundPersonalHold(Factor):

    def __init__(self):
        super().__init__(f_name='FundPersonalHold', f_type=FundFactorType.BASIC, f_level='basic')
        self._deps.add(TradingDay())

    def calc(self):
        self._factor = DataManager.basic_data(func_name='get_history_fund_size', start_date=_START_DATE).drop(columns=['_update_time'], errors='ignore')
        self._factor = self._factor.pivot(index='datetime',columns='fund_id',values='personal_holds')
        self._factor = Calculator.data_reindex_daily_trading_day(self._factor, TradingDay().get())

'''
import surfing.data.fund_fac.basic_factors_daily as basic

attr_list = basic.__dir__()
start_idx = attr_list.index('UpdateBasicFactorStart')
update_factor_list = attr_list[start_idx+1:]

for fac in update_factor_list:
    self = eval(fac)()
    self.calc()
    self.save()
'''