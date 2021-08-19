
from typing import List, Dict
import pandas as pd
import numpy as np
import math
import datetime
import traceback
import json
import statsmodels.api as sm
from multiprocessing import Pool
from scipy.optimize import Bounds, minimize
from statsmodels.tsa.ar_model import AutoReg
from ...api.basic import BasicDataApi
from ...api.raw import RawDataApi
from ...view.derived_models import FundAlpha
from .derived_data_helper import DerivedDataHelper


class FundAlphaProcessor:

    _TRADING_DAYS_PER_YEAR = 242
    _NATURAL_DAYS_PER_YEAR = 365
    _RISK_FEE_RATE = 0.011
    _RISK_FEE_RATE_PER_DAY = _RISK_FEE_RATE / _TRADING_DAYS_PER_YEAR
    _REPORT_DATE_LIST = ['0331', '0630', '0930', '1231']
    FUND_CLASSIFIER = {
        'QDII': ['国际(QDII)股票型基金', '国际(QDII)债券型基金', '国际(QDII)另类投资基金', '国际(QDII)混合型基金', ],
        'stock': ['普通股票型基金', '偏股混合型基金',  '被动指数型基金', '增强指数型基金', '平衡混合型基金', '灵活配置型基金', '股票多空'], 
        'bond': ['中长期纯债型基金', '短期纯债型基金', '偏债混合型基金', '增强指数型债券基金', '被动指数型债券基金','混合债券型二级基金', '混合债券型一级基金'],
        'mmf': ['货币市场型基金'],
        'index': ['被动指数型基金', '增强指数型基金', '增强指数型债券基金', '被动指数型债券基金', '商品型基金', 'REITs'],
    }
    REPLACE_DICT = {'stock': 'csi_stockfund',
                     'bond': 'csi_boodfund', 
                     'mmf':  'mmf', 
                     'QDII': 'csi_f_qdii', 
                     'index':'hs300'}
    _W1 = 5
    _M1 = 20
    _M3 = _M1 * 3
    _M6 = _M1 * 6
    _Y1 = _TRADING_DAYS_PER_YEAR
    _Y3 = _Y1 * 3
    _Y5 = _Y1 * 5
    _Y10 = _Y1 * 10
    
    def __init__(self, data_helper: DerivedDataHelper):
        self._data_helper = data_helper
        self._basic_api = BasicDataApi()
        
    def init(self, start_date: str, end_date: str):
        self.wind_type_dict = {}
        for type_i, type_list in self.FUND_CLASSIFIER.items():
            for _ in type_list:
                self.wind_type_dict.update({_:type_i})
        # 向前取12年
        start_date: str = (pd.to_datetime(start_date, infer_datetime_format=True) - datetime.timedelta(days=self._NATURAL_DAYS_PER_YEAR*15+1)).strftime('%Y%m%d')
        print(f'start date for data: {start_date}')
        # 获取区间内交易日列表
        all_trading_days: pd.Series = self._basic_api.get_trading_day_list().drop(columns='_update_time').set_index('datetime')
        self._trading_days: pd.Series = all_trading_days.loc[pd.to_datetime(start_date, infer_datetime_format=True).date():pd.to_datetime(end_date, infer_datetime_format=True).date()]
        # 使用实际trading day的最后一天作为end_date
        self.end_date = self._trading_days.index.array[-1]
        self.begin_of_year = datetime.date(self.end_date.year,1,1)
        self.this_y_lenth = self._trading_days.loc[self.begin_of_year:].shape[0]
        self.fund_info = self._basic_api.get_fund_info().drop(columns='_update_time')
        self._wind_class_2_dict = self.fund_info.set_index('fund_id')['wind_class_2'].to_dict()
        self.fund_info = self.fund_info[(self.fund_info.end_date >= self.end_date) 
                                       & (self.fund_info.structure_type <= 1)
                                       & (~self.fund_info.wind_class_2.isnull())]
        # 基金净值数据、指数价格数据的index对齐到交易日列表
        fund_nav: pd.DataFrame = self._basic_api.get_fund_nav_with_date(start_date=start_date, end_date=end_date)  #, fund_list = f_l)
        self._fund_nav: pd.DataFrame = fund_nav.pivot_table(index='datetime', columns='fund_id', values='adjusted_net_value').reindex(self._trading_days.index).fillna(method='ffill')
        # 排除掉异常净值基金
        res = []
        for fund_id in self._fund_nav:
            _df = self._fund_nav[fund_id].dropna()
            if _df.pct_change(1).abs().max() < 0.2:
                res.append(fund_id)
        self._fund_nav = self._fund_nav[res].copy()

        # 宏观数据
        self._macroeco = RawDataApi().get_em_macroeconomic_daily(codes=['EX_DR_RATIO']).drop(columns='_update_time')
        self._macroeco = self._macroeco.pivot_table(index='datetime', columns='codes', values='value')
        self._macroeco = self._macroeco.reindex(self._trading_days.index.union(self._macroeco.index)).fillna(method='ffill').reindex(self._trading_days.index)

        index_price: pd.DataFrame = self._basic_api.get_index_price_dt(start_date, end_date).drop(columns='_update_time')
        # 有的index最近没有数据，如活期存款利率/各种定期存款利率等，需要先reindex到全部的交易日列表上ffill
        self._index_price: pd.DataFrame = index_price.pivot_table(index='datetime', columns='index_id', values='close').reindex(self._trading_days.index).fillna(method='ffill')
        _bank_rate_df: pd.DataFrame = self._basic_api.get_index_price(index_list=['ddir', 'nonor', 'tmd_1y', 'tmd_2y', 'tmd_3m', 'tmd_3y', 'tmd_5y', 'tmd_6m', 'tmd_7d']).drop(columns='_update_time')
        _bank_rate_df = _bank_rate_df.pivot_table(index='datetime', columns='index_id', values='close').reindex(all_trading_days.index).fillna(method='ffill').reindex(self._trading_days.index)
        drop_list = [i for i in self._index_price if i in _bank_rate_df]
        self._index_price = self._index_price.drop(drop_list, axis=1)
        self._index_price: pd.DataFrame = pd.concat([self._index_price, _bank_rate_df], axis=1)
        # 再reindex到参与计算的交易日列表上
        # self._index_price: pd.DataFrame = index_price.reindex(self._trading_days.index)
        pd.testing.assert_index_equal(self._fund_nav.index, self._index_price.index)
        try:
            # 这个指数有一天的点数是0，特殊处理一下
            self._index_price['spi_spa'] = self._index_price['spi_spa'].where(self._index_price.spi_spa != 0).fillna(method='ffill')
        except KeyError:
            pass

        # 对数净值取差分并且去掉第一个空值，得到基金对数收益率数列
        self._fund_ret: pd.DataFrame = np.log(self._fund_nav).diff().iloc[1:, :]

        # 计算benchmark return，且index对齐到fund_ret
        self.fund_benchmark_df = self._basic_api.get_fund_benchmark().drop(columns='_update_time')
        benchmark_ret: pd.DataFrame = self._get_benchmark_return()
        self._benchmark_ret: pd.DataFrame = benchmark_ret.reindex(self._fund_ret.index)
        self._benchmark_ret = self._benchmark_ret.reindex(self._trading_days.index)
        benchmark_cols = self._benchmark_ret.columns.tolist()
        for fund_id in self._fund_nav.columns:
            benchmark_id = fund_id
            if not benchmark_id in benchmark_cols:    
                wind_class_2 = self._wind_class_2_dict[fund_id]
                if wind_class_2 not in self.wind_type_dict.keys():
                    continue
                select_type = self.wind_type_dict[wind_class_2]
                benchmark_ret = self._index_price[self.REPLACE_DICT[select_type]].pct_change(1).rename(benchmark_id)
                self._benchmark_ret = self._benchmark_ret.join(benchmark_ret)
        self._benchmark_ret = self._benchmark_ret.reindex(self._fund_ret.index).fillna(method='ffill')
        pd.testing.assert_index_equal(self._fund_ret.index, self._benchmark_ret.index)

        # 获取待计算的基金列表
        fund_list: pd.DataFrame = self._basic_api.get_fund_info().drop(columns='_update_time')
        self._fund_list: pd.DataFrame = fund_list[fund_list.structure_type <= 1]
        
        self._hs300 = self._basic_api.get_index_price(tuple(['hs300']))[['datetime','close']].set_index('datetime').rename(columns={'close':'benchmark'})
        self._hs300 = np.log(self._hs300).diff().iloc[1:, :]
        
    def _get_benchmark_return(self) -> pd.DataFrame:
        benchmark_list: Dict[str, float] = {}
        # 遍历每一只基金的benchmark进行处理
        for row in self.fund_benchmark_df.itertuples(index=False):
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

    def get_alpha(self, df, term):
        term = min(df.shape[0], term) 
        ploy_res = np.polyfit(y=df.tail(term).fund, x=df.tail(term).benchmark, deg=1)
        alpha = ploy_res[1] * term
        return alpha
    
    def get_track_err(self, df):
        return (df.fund - df.benchmark).std(ddof=1) * np.sqrt(self._TRADING_DAYS_PER_YEAR)

    def calculate_item(self, fund_id):
        try:
            fund_ret_i = self._fund_ret[[fund_id]].rename(columns={fund_id:'fund'})
            if fund_id in self._benchmark_ret:
                bench_ret_i = self._benchmark_ret[[fund_id]].rename(columns={fund_id:'benchmark'})
            else:
                bench_ret_i = self._hs300
            df_i = fund_ret_i.join(bench_ret_i).dropna()
            
            track_err = self.get_track_err(df_i)
            this_y_alpha = self.get_alpha(df_i, self.this_y_lenth)
            cumulative_alpha = self.get_alpha(df_i, df_i.shape[0])
            w1_alpha = self.get_alpha(df_i, self._W1)
            m1_alpha = self.get_alpha(df_i, self._M1)
            m3_alpha = self.get_alpha(df_i, self._M3)
            m6_alpha = self.get_alpha(df_i, self._M6)
            y1_alpha = self.get_alpha(df_i, self._Y1)
            y3_alpha = self.get_alpha(df_i, self._Y3)
            y5_alpha = self.get_alpha(df_i, self._Y5)
            y10_alpha = self.get_alpha(df_i, self._Y10)

            dic = {
                'track_err' : track_err,
                'this_y_alpha' : this_y_alpha,
                'cumulative_alpha' : cumulative_alpha,
                'w1_alpha' : w1_alpha,
                'm1_alpha' : m1_alpha,
                'm3_alpha' : m3_alpha,
                'm6_alpha' : m6_alpha,
                'y1_alpha' : y1_alpha,
                'y3_alpha' : y3_alpha,
                'y5_alpha' : y5_alpha,
                'y10_alpha' : y10_alpha,
                'fund_id' : fund_id,
                'datetime' : self.end_date
            }
            return dic
        except Exception:
            print('fund_id can not calculate alpha', fund_id)
            return None

    def calculate(self):
        fund_list = self._fund_ret.columns.to_list()
        p = Pool()
        res = [i for i in p.imap_unordered(self.calculate_item, fund_list, 256) if i is not None]
        p.close()
        p.join()
        self.result = pd.DataFrame(res)

    def process(self, start_date, end_date):
        failed_tasks = []
        try:
            self.init(start_date, end_date)
            self.calculate()
            self._data_helper._upload_derived(self.result, FundAlpha.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(FundAlpha.__table__.name)
        return failed_tasks


if __name__ == '__main__':
    fap = FundAlphaProcessor(DerivedDataHelper())
    fap.process('20210624', '20210624')
