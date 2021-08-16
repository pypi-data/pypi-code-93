
import datetime
import traceback
from typing import List, Dict

import pandas as pd
import numpy as np
from dateutil.relativedelta import relativedelta

from ...api.raw import RawDataApi
from ...api.basic import BasicDataApi
from ...view.basic_models import BarraCNE5RiskFactor
from .basic_data_helper import BasicDataHelper


class BarraCNE5FactorData:

    _EXTRA_DAYS = 240

    def __init__(self, _data_helper: BasicDataHelper):
        self._data_helper: BasicDataHelper = _data_helper
        self._factors: Dict[str, pd.DataFrame] = {}
        self._raw_api = RawDataApi()

    def init(self, start_date: str, end_date: str):
        self._start_date: str = start_date
        self._end_date: str = end_date

        # 由于有rolling, 所以需要从start_date往前多取一些数据
        trading_day: pd.DataFrame = BasicDataApi().get_trading_day_list().set_index('datetime')
        start_date_loc = trading_day.index.get_loc(pd.to_datetime(self._start_date, infer_datetime_format=True).date(), method='ffill')
        assert isinstance(start_date_loc, int), 'start date is not a valid trading day'

        assert start_date_loc >= self._EXTRA_DAYS, 'there is no enough extra days before start date'
        start_date_with_extra_days = trading_day.index.array[start_date_loc - self._EXTRA_DAYS]
        print(f'start date with extra days: {start_date_with_extra_days}')
        self._last_trading_day = pd.to_datetime(trading_day.index.array[start_date_loc - 1])

        # 获取未复权收盘价
        stock_price: pd.DataFrame = self._raw_api.get_em_stock_price(start_date_with_extra_days, self._end_date, columns=['close', 'turn']).set_index(['stock_id', 'datetime'])
        self._stock_price: pd.DataFrame = stock_price.drop(columns='turn')
        # 干掉当天没有进行交易的股票, 但这样的话往前取的数据可能不够rolling窗口使用了
        # self._stock_price[~self._stock_price['trade_status'].isin(('停牌一天', '暂停上市', '连续停牌'))]
        print('load stock price done')

        # 获取后复权收盘价及前收
        self._stock_post_price = self._raw_api.get_em_stock_post_price(start_date_with_extra_days, self._end_date, columns=['close', 'pre_close']).set_index(['stock_id', 'datetime'])
        # 按道理索引应该与未复权df完全一致，但可能值是一样的但顺序不同，这里reindex一下
        self._stock_post_price = self._stock_post_price.reindex(index=self._stock_price.index)
        # 干掉当天没有进行交易的股票, 但这样的话往前取的数据可能不够rolling窗口使用了
        # self._stock_post_price[~self._stock_post_price['trade_status'].isin(('停牌一天', '暂停上市', '连续停牌'))]
        print('load stock post price done')

        pd.testing.assert_index_equal(self._stock_post_price.index, self._stock_price.index)
        # reindex可能掩盖了不一致，这里看一下是否有某一行除了索引之外全为null
        assert not self._stock_post_price.isnull().all(axis=1).any(), 'stock post price df should not have any NaN!!'

        # 获取换手率
        self._stock_turnover: pd.DataFrame = stock_price.drop(columns='close')
        print('load stock turnover done')

        # 获取每日更新的总股本
        self._stock_daily_info: pd.DataFrame = self._raw_api.get_em_daily_info(start_date_with_extra_days, self._end_date, columns=['total_share']).set_index(['stock_id', 'datetime'])
        # 与未复权股价的索引对齐(空值保持为nan)
        self._stock_daily_info = self._stock_daily_info.reindex(index=self._stock_price.index)
        # 对齐后将每只个股时间序列上总股本为nan的值ffill, TODO: 再做bfill了，这样对吗
        self._stock_daily_info['total_share'] = self._stock_daily_info.reset_index().pivot_table(index='stock_id', columns='datetime', values='total_share', dropna=False).fillna(method='ffill', axis=1).fillna(method='bfill', axis=1).stack()
        print('load stock daily info done')
        pd.testing.assert_index_equal(self._stock_daily_info.index, self._stock_price.index)
        assert not self._stock_daily_info.isnull().to_numpy().any(), 'stock daily info df should not have any NaN!!'

        # 获取个股财务数据
        equity_start: datetime.date() = (pd.to_datetime(self._start_date, infer_datetime_format=True) - relativedelta(years=5)).date()
        self._fin_fac = self._raw_api.get_em_stock_fin_fac(start_date=equity_start, end_date=self._end_date)
        print('load fin_fac info done')

    # 5%-95%
    @staticmethod
    def winsorize_quantile(x: pd.DataFrame, flag=0.05) -> pd.DataFrame:
        x = x.stack()
        x = x[x.notna().all(axis=1)]
        if x.empty:
            return
        high_low_quantile = x.quantile([1 - flag, flag])
        anew = x.droplevel(0)
        anew = anew.where(anew <= high_low_quantile.loc[1 - flag, :], high_low_quantile.loc[1 - flag, :], axis=1)
        anew = anew.where(anew >= high_low_quantile.loc[flag, :], high_low_quantile.loc[flag, :], axis=1)
        return anew

    def calculate_factors(self):
        # 日对数收益率
        temp_return: pd.Series = np.log(self._stock_post_price.loc[:, 'close'] / self._stock_post_price.loc[:, 'pre_close'])
        self._factors['ret'] = temp_return.unstack(level=0)
        self._factors['momentum'] = self._factors['ret'].rolling(20).sum()

        # 市值因子：size取对数
        temp_shareweight: pd.DataFrame = (self._stock_daily_info.loc[:, 'total_share'] * self._stock_price.loc[:, 'close']).unstack(level=0)
        self._factors['logsize'] = -np.log(temp_shareweight)

        fin_fac_pivoted_df: pd.DataFrame = self._fin_fac.pivot_table(index='datetime', columns='stock_id', values=['balance_statement_140', 'income_statement_61', 'income_statement_83', 'cashflow_statement_39', 'balance_statement_74', 'balance_statement_128'], dropna=False)
        total_equity: pd.DataFrame = fin_fac_pivoted_df['balance_statement_140']
        # fin_fac(财务数据)有一部分数据的日期可能是非交易日，这里取并fill一下，然后再回到交易日的index上来
        total_equity = total_equity.reindex(index=self._factors['ret'].index.union(total_equity.index)).fillna(method='ffill').reindex(index=self._factors['ret'].index)

        # 计算有效股票列表
        effective_col: pd.Index = temp_shareweight.columns.intersection(total_equity.columns)
        self._factors['ret'] = self._factors['ret'].loc[:, effective_col]
        temp_shareweight = temp_shareweight.loc[:, effective_col]

        self._factors['book_price'] = total_equity.loc[:, effective_col] / temp_shareweight

        # index: datetime, value: float
        temp_rm: pd.Series = (self._factors['ret'] * temp_shareweight / temp_shareweight.sum()).sum(axis=1)
        beta = self._factors['ret'].rolling(20).cov(temp_rm).div(temp_rm.rolling(20).var(), axis=0)
        DASTD = self._factors['ret'].rolling(20).std()
        CMRA = self._factors['ret'].rolling(20).max() - self._factors['ret'].rolling(20).min()
        HSIGMA = (self._factors['ret'] - beta.mul(temp_rm, axis=0)).rolling(20).std()
        self._factors['resvol'] = 0.74 * DASTD + 0.16 * CMRA + 0.1 * HSIGMA

        net_earnings: pd.DataFrame = fin_fac_pivoted_df['income_statement_61'].loc[:, effective_col]
        EGRO = net_earnings.rolling(5).apply(lambda x: (x[-1] - x[0]) / x[0], raw=True)
        net_sales: pd.DataFrame = fin_fac_pivoted_df['income_statement_83'].loc[:, effective_col]
        SGRO = net_sales.rolling(5).apply(lambda x: (x[-1] - x[0]) / x[0], raw=True)
        growth = 0.34 * EGRO + 0.66 * SGRO
        self._factors['growth'] = growth.reindex(index=self._factors['resvol'].index.union(growth.index)).fillna(method='ffill').reindex(index=self._factors['resvol'].index)

        temp_turnover = self._stock_turnover.pivot_table(index='datetime', columns='stock_id', values='turn', dropna=False).fillna(method='ffill')
        STOM = temp_turnover.rolling(20).sum()
        # 这里rolling.apply很慢，可以考虑用注释中的近似算法，不过目前engine用numba且每日更新数据量较小，耗时可以接受
        STOQ = temp_turnover.rolling(60).apply(lambda x: (x * (1 / np.arange(60//20, 0, -1)).repeat(20)).sum(), engine='numba', raw=True)
        # STOQ = temp_turnover.rolling(60).sum() / 3
        STOA = temp_turnover.rolling(240).apply(lambda x: (x * (1 / np.arange(240//20, 0, -1)).repeat(20)).sum(), engine='numba', raw=True)
        # STOA = temp_turnover.rolling(240).sum() / 12
        self._factors['liquidity'] = 0.35 * np.log(STOM) + 0.35 * np.log(STOQ) / 3 + 0.3 * np.log(STOA) / 12

        ETOP: pd.DataFrame = net_earnings.reindex(index=self._factors['resvol'].index.union(net_earnings.index)).fillna(method='ffill').div(temp_shareweight).reindex(index=self._factors['resvol'].index)
        net_cash: pd.DataFrame = fin_fac_pivoted_df['cashflow_statement_39']
        CETOP: pd.DataFrame = net_cash.reindex(index=self._factors['resvol'].index.union(net_cash.index)).fillna(method='ffill').div(temp_shareweight).reindex(index=self._factors['resvol'].index)
        self._factors['earning_yields'] = 0.66 * ETOP + 0.34 * CETOP

        leverage: pd.DataFrame = fin_fac_pivoted_df['balance_statement_128'] / fin_fac_pivoted_df['balance_statement_74']
        self._factors['leverage'] = leverage.reindex(self._factors['resvol'].index.union(leverage.index)).fillna(method='ffill').reindex(self._factors['resvol'].index)
        print(f'all factors are calculated successfully')

        # 将所有因子放到一个df里
        concat_keys: List[str] = []
        df_list: List[pd.Series] = []
        for name, factor in self._factors.items():
            # ret这里先不放进来
            if name != 'ret':
                factor = factor.loc[:, effective_col]
                factor = factor[factor.index >= self._last_trading_day]
                df_list.append(factor)
                concat_keys.append(name)
        whole_df: pd.DataFrame = pd.concat(df_list, axis=1, keys=concat_keys)
        whole_df = whole_df.shift(1).groupby(by='datetime', sort=False).apply(BarraCNE5FactorData.winsorize_quantile, flag=0.01)
        ret = self._factors['ret']
        ret = ret[ret.index >= self._last_trading_day]
        self._whole_factors = whole_df.join(ret.stack().rename('ret'), how='outer')

    def process_all(self, start_date: str, end_date: str):
        start_date = pd.to_datetime(start_date, infer_datetime_format=True).date().isoformat()
        end_date = pd.to_datetime(end_date, infer_datetime_format=True).date().isoformat()
        failed_tasks: List[str] = []
        try:
            self.init(start_date, end_date)
            self.calculate_factors()
            self._data_helper._upload_basic(self._whole_factors.loc[start_date:end_date, :].reset_index(), BarraCNE5RiskFactor.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(BarraCNE5RiskFactor.__table__.name)
        return failed_tasks


if __name__ == '__main__':
    barra_cne5 = BarraCNE5FactorData(BasicDataHelper())
    barra_cne5.process_all('20201026', '20201026')
