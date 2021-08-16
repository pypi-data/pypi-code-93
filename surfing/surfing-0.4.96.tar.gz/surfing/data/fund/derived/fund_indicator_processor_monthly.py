
from typing import Dict

import traceback
import math
import datetime
import time
import numpy as np
import pandas as pd

from ...manager.manager_fund import FundDataManager
from ...view.derived_models import FundIndicatorMonthly


class FundIndicatorProcessorMonthly:

    _RF = 0.011

    def __init__(self, data_helper):
        self._data_helper = data_helper

    def init(self, start_date, end_date, dm=None):
        if dm is None:
            self._dm = FundDataManager(start_time=start_date, end_time=end_date)
            self._dm.init(score_pre_calc=False)
        else:
            self._dm = dm
        self.start_date = self._dm.start_date
        self.end_date = self._dm.end_date

        # index price, fund nav 日期对齐至交易日
        self._trading_days = self._dm.dts.trading_days[(self._dm.dts.trading_days.datetime >= self.start_date) & (self._dm.dts.trading_days.datetime <= self.end_date)].datetime
        self._fund_nav: pd.DataFrame = self._dm.dts.fund_nav.reindex(self._trading_days)
        self._index_price: pd.DataFrame = self._dm.dts.index_price.reindex(self._trading_days)
        pd.testing.assert_index_equal(self._fund_nav.index, self._index_price.index)

        # 过滤出来需要用到的fund_info
        self._fund_info: pd.DataFrame = self._dm.dts.fund_info[self._dm.dts.fund_info['fund_id'].isin(self._fund_nav.columns)]

        # 获取fund到index的字典
        fund_to_index: Dict[str, str] = self._fund_info[['fund_id', 'index_id']].set_index('fund_id').to_dict()['index_id']

        # 超过基金终止日的基金净值赋空
        fund_to_end_date_dict = self._fund_info[['fund_id', 'end_date']].set_index('fund_id').to_dict()['end_date']
        for fund_id in self._fund_nav.columns:
            fund_end_date = fund_to_end_date_dict[fund_id]
            if self.end_date >= fund_end_date:
                self._fund_nav.loc[fund_end_date:, fund_id] = np.nan

        self._index_ret: pd.DataFrame = self._get_return(self._index_price)
        self._fund_ret: pd.DataFrame = self._get_return(self._fund_nav)
        index_list: pd.Series = self._fund_ret.columns.map(fund_to_index)
        index_list = index_list[index_list.notna()]
        self._index_list: np.ndarray = index_list.unique()

        # resample
        self._index_ret_resampled: pd.DataFrame = self._get_resample_ret(self._index_ret)
        # self._national_debt_ret_resampled: pd.DataFrame = self._index_ret_resampled.loc[:, 'national_debt']
        self._fund_ret_resampled: pd.DataFrame = self._get_resample_ret(self._fund_ret)

        self._index_fund: pd.DataFrame = self._fund_info.loc[self._fund_info.index_id.isin(self._index_list), ['index_id', 'fund_id']].groupby('index_id').apply(lambda x: x['fund_id'].to_list())
        self._fund_start_date: Dict[str] = self._fund_info[['fund_id', 'start_date']].set_index('fund_id').to_dict()['start_date']

    def _get_return(self, df) -> pd.DataFrame:
        ret = df.applymap(np.log).diff()
        return ret.iloc[1:, :]

    def _get_resample_ret(self, df, rule='1M'):
        return df.set_axis(pd.to_datetime(df.index), inplace=False).resample(rule).sum()

    def _process_fund_indicator_update(self, index_id, index_ret: pd.Series, index_ret_resampled: pd.Series,
                                       fund_list, fund_ret: pd.DataFrame, fund_ret_resampled: pd.DataFrame) -> pd.DataFrame:
        # beta
        beta = fund_ret_resampled.apply(lambda x: index_ret_resampled.cov(x)) / index_ret_resampled.var()

        # sharpe ratio
        annualized_ret_M = fund_ret_resampled.sum() * (12 / len(fund_ret_resampled)) - self._RF
        annualized_vol_M = fund_ret_resampled.std(ddof=0) * math.sqrt(12)
        sharpe_ratio_M = annualized_ret_M / annualized_vol_M

        # treynor ratio
        # ex_ret = fund_ret_resampled.sub(self._national_debt_ret_resampled, axis=0)
        ex_ret = fund_ret_resampled.sub(self._RF / 12, axis=0)
        ex_ret_sum = ex_ret.sum()
        annualized_ret_ex = ex_ret_sum * 12 / len(fund_ret_resampled)
        treynor_ratio = annualized_ret_ex / beta

        # information ratio
        annualized_vol_ex = fund_ret_resampled.std() * math.sqrt(12)
        information_ratio = annualized_ret_ex / annualized_vol_ex

        # jensen alpha
        ri = (fund_ret_resampled.sum()) * 12 / len(fund_ret_resampled)
        rm = (index_ret_resampled.sum()) * 12 / len(index_ret_resampled)

        # rf = (self._national_debt_ret_resampled.sum()) * 12 / len(self._national_debt_ret_resampled)
        jensen_alpha = ri - self._RF - beta * (rm - self._RF)

        # mdd
        net_val = self._fund_nav.loc[:, fund_list]
        peak_series = net_val.rolling(window=len(net_val), min_periods=1).max()
        max_drawdown = (net_val / peak_series - 1.0).min()

        # calmar ratio
        calmar_ratio = annualized_ret_ex / max_drawdown

        return pd.DataFrame({'beta_m': beta, 'sharpe_ratio_m': sharpe_ratio_M,
                             'treynor_ratio_m': treynor_ratio, 'information_ratio_m': information_ratio,
                             'jensen_alpha_m': jensen_alpha, 'calmar_ratio_m': calmar_ratio, })

    def _calculate_update(self):
        result = []
        for index_id in self._index_list:
            _tm_1 = time.time()
            fund_list = self._index_fund[index_id]
            fund_list = list(set(fund_list) & set(self._fund_ret.columns))
            fund_ret = self._fund_ret.loc[:, fund_list]
            fund_ret_resampled = self._fund_ret_resampled.loc[:, fund_list]
            index_ret = self._index_ret.loc[:, index_id]
            index_ret_resampled = self._index_ret_resampled.loc[:, index_id]
            result.append(self._process_fund_indicator_update(index_id, index_ret, index_ret_resampled, fund_list, fund_ret, fund_ret_resampled))
            _tm_2 = time.time()
            print(f'index {index_id} fund number : {len(fund_list)} finish, cost time {_tm_2 - _tm_1}s')
        self.result = pd.concat(result)
        self.result = self.result.replace({-np.Inf:None,np.Inf:None})

    def process(self, start_date: str, end_date: str, end_date_dt: datetime.date):
        # 月更因子, 由于resample出来的日期都是每月最后一天，所以每月最后一天前的最后一个交易日更新
        failed_tasks = []
        try:
            print(f'monthly indicator update on the last day of month {end_date_dt}')
            start_date_dt = pd.to_datetime(start_date, infer_datetime_format=True).date()
            start_date = start_date_dt - datetime.timedelta(days=1150)  # 3年历史保险起见，多取几天 3*365=1095
            start_date = datetime.datetime.strftime(start_date, '%Y%m%d')
            self.init(start_date=start_date, end_date=end_date)
            self._calculate_update()
            self._data_helper._upload_derived(self.result.assign(datetime=end_date_dt).reset_index(), FundIndicatorMonthly.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('fund_indicator_monthly')
        return failed_tasks


if __name__ == '__main__':
    import datetime
    from .derived_data_helper import DerivedDataHelper

    fipa = FundIndicatorProcessorMonthly(DerivedDataHelper())
    fipa.process('20201231', '20201231', datetime.date(2020, 12, 31))
