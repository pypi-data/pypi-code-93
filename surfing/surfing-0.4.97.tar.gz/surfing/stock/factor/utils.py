
import datetime
from typing import Optional, List, Union

import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset
from sklearn.preprocessing import StandardScaler

from ...constant import StockFactorType
from ...data.manager import DataManager
from .base import Factor


_UTILS_PREFIX = 'utils/'
_START_DATE = '2005-01-01'

_TRADING_DAYS_PER_YEAR = 242


def get_day(num, date_list, last_date):
    value = DateOffset(days=num)
    # 根据时间区间计算出begin date(bd)
    bd = (last_date - value).date()
    # 试图寻找bd及其之前的最近一天
    bd_list = date_list[date_list <= bd]
    return bd_list[-1]


def get_quarterly_tradingday_list() -> List[datetime.date]:
    tradingday = TradingDayList().get()
    tradingday_list: List[datetime.date] = []
    for date in zip(tradingday, tradingday.shift(1)):
        if np.nan in date:
            continue
        today = date[1]
        next_trading_dt = date[0]
        if today.year == next_trading_dt.year and today.month == next_trading_dt.month:
            continue
        if today.month not in (3, 6, 9, 12):
            continue
        tradingday_list.append(today)
    return tradingday_list


def get_factor_from_stock_data(table: str, columns: List[str], index='datetime', processor_after_pivot=None):
    df: Optional[pd.DataFrame] = DataManager.raw_data(table, columns=columns)
    df = df.pivot(index=index, columns='stock_id', values=columns)
    if len(columns) == 1:
        df = df[columns[0]]
    if processor_after_pivot is not None:
        df = processor_after_pivot(df)

    trading_day_list = TradingDayList().get()
    return df.reindex(df.index.union(trading_day_list)).ffill().reindex(trading_day_list)


def calc_growth_rate(x, whole_df):
    date_begin = x.name - DateOffset(years=1)
    date_list = whole_df.index[whole_df.index <= date_begin]
    if date_list.empty:
        return
    return whole_df.loc[x.name, :] / whole_df.loc[date_list.array[-1], :] - 1


def normalize(a: Union[pd.DataFrame, pd.Series]) -> np.ndarray:
    if isinstance(a, pd.Series):
        a = pd.DataFrame(a)
    return StandardScaler().fit_transform(a.replace({np.Inf: np.nan, -np.Inf: np.nan}))


def calc_ttm(x, whole_df):
    date = x.name
    if date.month == 12 and date.day == 31:
        return x
    else:
        try:
            last_annual_report = whole_df.loc[datetime.date(date.year-1, 12, 31), :]
            same_period_last_year = whole_df.loc[datetime.date(date.year-1, date.month, date.day), :]
            return x + last_annual_report - same_period_last_year
        except KeyError:
            return np.nan


class TradingDayList(Factor):

    def __init__(self):
        super().__init__(_UTILS_PREFIX + 'td_list', StockFactorType.BASIC)

    def calc(self):
        trading_day_list: Optional[pd.DataFrame] = DataManager.basic_data('get_trading_day_list', start_date=_START_DATE)

        self._factor = trading_day_list.datetime

    def trim_by_date(self, end_date: str):
        if self._factor is None:
            return
        self._factor = self._factor[self._factor <= pd.to_datetime(end_date).date()]


class FundHoldStockFactor(Factor):

    def __init__(self):
        super().__init__(_UTILS_PREFIX + 'fund_hold_stock', StockFactorType.BASIC)

    def calc(self):
        self._factor = DataManager.basic_data('get_fund_hold_stock_by_id').drop(columns='_update_time')


class StockIndustryInfoFactor(Factor):

    def __init__(self):
        super().__init__(_UTILS_PREFIX + 'stock_ind_info', StockFactorType.BASIC)

    def calc(self):
        df: Optional[pd.DataFrame] = DataManager.raw_data('get_em_stock_info').drop(columns='_update_time')
        self._factor = df.set_index('stock_id').bl_sws_ind_code.str.split(pat='-', expand=True).iloc[:, -1]
