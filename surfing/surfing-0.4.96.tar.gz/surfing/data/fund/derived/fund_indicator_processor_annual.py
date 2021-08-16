
from typing import List, Dict
import pandas as pd
import numpy as np
import datetime
import traceback
import time
from .derived_data_helper import DerivedDataHelper
from ...manager.manager_fund import FundDataManager
from ...view.derived_models import FundIndicatorAnnual


class FundIndicatorProcessorAnnual:

    _MONTHS_A_YEAR = 12

    def __init__(self, data_helper):
        self._data_helper: DerivedDataHelper = data_helper
        self._res: List[pd.DataFrame] = []
        self._res2: List[pd.DataFrame] = []
        self._result = None
        self._result2 = None

    def init(self, start_date: str, end_date: str, dm=None, resample_day='1M'):
        # DM作为基础数据
        if dm is None:
            self._dm = FundDataManager(start_time=start_date, end_time=end_date)
            self._dm.init(score_pre_calc=False)
        else:
            self._dm = dm
        self._resample_day = resample_day

        # index price, fund nav 日期对齐至交易日
        self._trading_days = self._dm.dts.trading_days[self._dm.dts.trading_days.datetime >= self._dm.start_date].datetime
        self._fund_nav = self._dm.dts.fund_nav.reindex(self._trading_days)
        index_price = self._dm.dts.index_price.reindex(self._trading_days)
        pd.testing.assert_index_equal(self._fund_nav.index, index_price.index)

        # fund id到index id的字典
        self._fund_id_to_index_id: Dict[str, str] = self._dm.dts.fund_info[['fund_id', 'index_id']].set_index('fund_id').to_dict()['index_id']

        # 超过基金终止日的基金净值赋空
        fund_to_enddate_dict = self._dm.dts.fund_info[['fund_id', 'end_date']].set_index('fund_id').to_dict()['end_date']
        for fund_id in self._fund_nav.columns:
            fund_end_date = fund_to_enddate_dict[fund_id]
            if self._dm.end_date > fund_end_date:
                self._fund_nav.loc[fund_end_date:, fund_id] = np.nan

        # resample and datetime convert
        self._fund_ret = self._df_resample(np.log(self._fund_nav / self._fund_nav.shift(1)))
        self._index_ret = self._df_resample(np.log(index_price / index_price.shift(1)))

        # fund ret上加一列index id
        self._fund_ret = self._fund_ret.stack().reset_index().rename(columns={0: 'ret'})
        self._fund_ret['index_id'] = self._fund_ret.fund_id.map(self._fund_id_to_index_id)
        # 过滤掉没有index_id的基金
        self._fund_ret = self._fund_ret[self._fund_ret.index_id.notna()]

    def _df_resample(self, df):
        # resample前需要转成datetime索引
        df = df.set_axis(pd.to_datetime(df.index), inplace=False)
        # min_count=1，使得全NA的列最后的和也为NA(否则为0)
        df = df.resample(self._resample_day).sum(min_count=1)
        return df

    def _lambda_1(self, x: pd.Series, fund: pd.DataFrame, benchmark: pd.Series):
        fund: pd.DataFrame = fund.loc[x, :]
        benchmark: pd.Series = benchmark.loc[x]
        # shape[0]与benchmark的基金才可以回归
        fund = fund.loc[:, fund.count() == benchmark.size]
        # 每一列是一只基金，一起回归计算alpha
        ploy_res = np.polyfit(x=benchmark, y=fund, deg=1)
        result = pd.DataFrame({'datetime': x.array[-1], 'alpha_annual': ploy_res[1, :] * self._MONTHS_A_YEAR, 'beta_annual': ploy_res[0, :]}, index=fund.columns)
        # 计算超额收益
        er = fund.sum() - benchmark.sum()
        self._res.append(result.assign(excess_return_annual=er.T))

        # # 另一种方法算的alpha和beta，可作验证用
        # beta = fund.apply(lambda x: benchmark.cov(x)) / benchmark.var()
        # # jensen alpha
        # ri = (fund.sum()) * 12 / len(fund)
        # rm = (benchmark.sum()) * 12 / len(benchmark)
        # jensen_alpha = ri - beta * rm
        # self._res2.append(pd.DataFrame({'date': fund.index[-1], 'alpha': jensen_alpha, 'beta': beta}))

    def _process_fund_indicator_item(self, fund_ret, index_id, index_ret):
        # resample的apply每次只能操作一个Series，所以这里我们只对索引做resample+apply，同时将df作为参数传进去
        # 另外因为在func参数中只有一个函数时只会返回Series，我们需要在里边自己存储计算结果
        fund_ret.index.to_series().resample('1Y').apply(self._lambda_1, fund=fund_ret, benchmark=index_ret)

    def calculate_history(self, index_id_list: List[str] = None):
        # 支持传进来一个index list，所以这里没有直接group by index id
        # 获得index list
        index_list = self._fund_ret.index_id.unique() if index_id_list is None else index_id_list
        for index_id in index_list:
            _tm_1 = time.time()
            # 获取对应该index的所有fund
            fund_ret = self._fund_ret[self._fund_ret.index_id == index_id].drop(columns='index_id')
            fund_ret = fund_ret.pivot_table(index='datetime', columns='fund_id', values='ret')
            # 获取benchmark
            index_ret = self._index_ret.loc[:, index_id]
            self._process_fund_indicator_item(fund_ret, index_id, index_ret)
            _tm_2 = time.time()
            print(f'index {index_id} fund number: {fund_ret.shape[1]} finished, cost time {_tm_2 - _tm_1}s')
        self._result = pd.concat(self._res).replace({-np.Inf:None,np.Inf:None})
        # self._result2 = pd.concat(self._res2)

    def process(self, year=3):
        failed_tasks = []
        try:
            now_date: datetime.date = datetime.datetime.now().date()
            # 起始时间为第一年的1月1日
            start_date = datetime.date(now_date.year - year + 1, 1, 1)
            start_date = start_date.strftime('%Y%m%d')
            if (now_date + datetime.timedelta(days=1)).month != now_date.month:
                # 如果是本月最后一天，直接使用这个日期
                end_date = now_date
            else:
                # 如果不是，取上月最后一天
                end_date = datetime.date(now_date.year, now_date.month, 1) - datetime.timedelta(days=1)
            end_date = end_date.strftime('%Y%m%d')
            print(start_date, end_date)
            self.init(start_date=start_date, end_date=end_date)
            self.calculate_history()
            self._data_helper._upload_derived(self._result.reset_index(), FundIndicatorAnnual.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('fund_indicator_annual')
        return failed_tasks


if __name__ == '__main__':
    fipa = FundIndicatorProcessorAnnual(DerivedDataHelper())
    fipa.process()
