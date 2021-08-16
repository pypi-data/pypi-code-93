
import datetime
import json
import traceback

import pandas as pd
import numpy as np
from pandas.tseries.offsets import DateOffset

from ...api.basic import BasicDataApi
from ...view.derived_models import IndexReturn, IndexVolatility


class IndexIndicatorProcessor:

    TRADE_DAY_PER_YEAR = 242
    _DIM_TYPE = {
        'w1_': DateOffset(weeks=1),
        'm1_': DateOffset(months=1),
        'm3_': DateOffset(months=3),
        'm6_': DateOffset(months=6),
        'y1_': DateOffset(years=1),
        'y3_': DateOffset(years=3),
        'y5_': DateOffset(years=5),
        'y10_': DateOffset(years=10),
    }

    def __init__(self, data_helper):
        self._data_helper = data_helper

    def _init(self, start_date: str, end_date: str = ''):
        self.index_price = BasicDataApi().get_index_price_dt(start_date=start_date, end_date=end_date).drop(columns='_update_time')
        index_price_pivoted_table = self.index_price.pivot_table(index='datetime', columns='index_id', values='close')
        begin_d = index_price_pivoted_table.index[0]
        end_d = index_price_pivoted_table.index[-1]
        # 获取区间内的交易日列表
        trade_day_df = BasicDataApi().get_trading_day_list(begin_d, end_d).drop(columns='_update_time')
        # 用交易日列表对index_price做reindex
        index_price_pivoted_table = index_price_pivoted_table.reindex(trade_day_df.datetime)
        # 用于计算return
        self.index_price = index_price_pivoted_table.fillna(method='ffill').fillna(method='bfill')
        # 用于计算volatility
        self.index_price_vol_part = index_price_pivoted_table.pct_change(1)
        self.date_list = self.index_price.index

    def history_init(self):
        self._init(start_date='20050101')

    def init(self, end_date):
        self._init(start_date='20050101', end_date=end_date)
        self.end_date = pd.to_datetime(end_date, infer_datetime_format=True).date()

    def _get_begin_or_end(self, dt, is_begin: bool):
        if is_begin:
            temp = self.date_list[self.date_list < dt]
            if temp.empty:
                return
            return temp.array[-1]
        else:
            return self.date_list[self.date_list >= dt].array[0]

    def _get_year_date(self, dt, is_begin: bool):
        _dt = datetime.date(dt.year, 1, 1)
        return self._get_begin_or_end(_dt, is_begin)

    def _get_season_date(self, dt, is_begin: bool):
        _m = int((dt.month - 1) / 3) * 3 + 1
        _dt = datetime.date(dt.year, _m, 1)
        return self._get_begin_or_end(_dt, is_begin)

    def _term_ret(self, df):
        return df.iloc[-1] / df.iloc[0] - 1

    def _term_vol(self, df):
        return df.std(ddof=1)*np.sqrt(self.TRADE_DAY_PER_YEAR)

    def _this_y_ret(self, x):
        dt2 = x.name
        dt1 = self._get_year_date(dt2, True)
        return self._term_ret(self.index_price.loc[dt1:dt2])

    def _this_s_ret(self, x):
        dt2 = x.name
        dt1 = self._get_season_date(dt2, True)
        return self._term_ret(self.index_price.loc[dt1:dt2])

    def _cumulative_ret(self, x):
        dt = x.name
        return self._term_ret(self.index_price.loc[:dt])

    def _this_y_vol(self, x):
        dt2 = x.name
        dt1 = self._get_year_date(dt2, False)
        return self._term_vol(self.index_price_vol_part.loc[dt1:dt2])

    def _this_s_vol(self, x):
        dt2 = x.name
        dt1 = self._get_season_date(dt2, False)
        return self._term_vol(self.index_price_vol_part.loc[dt1:dt2])

    def _cumulative_vol(self, x):
        dt = x.name
        return self._term_vol(self.index_price_vol_part.loc[:dt])

    def _ret_history(self):
        self.ret_res = {}

        # 遍历每个需要计算的时间区间
        for name, value in self._DIM_TYPE.items():
            # 遍历每一行，根据时间区间计算出begin date(bd)
            temp_ret = []
            for index, row in self.index_price.iterrows():
                bd = (index - value).date()
                # 试图寻找bd及其之前的最近一天
                bd_list = self.date_list[self.date_list <= bd]
                if bd_list.empty:
                    continue
                # 计算区间内的return
                temp_ret.append((row / self.index_price.loc[bd_list.array[-1], :] - 1).rename(row.name))
            self.ret_res[name + 'ret'] = pd.DataFrame(temp_ret).rename_axis(index='datetime')

        self.ret_res['this_s_ret'] = self.index_price.apply(self._this_s_ret, axis=1)
        self.ret_res['this_y_ret'] = self.index_price.apply(self._this_y_ret, axis=1)
        self.ret_res['cumulative_ret'] = self.index_price.apply(self._cumulative_ret, axis=1)

    def _process_result(self, result):
        _res = []
        for k, df in result.items():
            if df.empty:
                continue
            _res.append(pd.DataFrame(df.stack()).rename(columns={0: k}))
        self.result = pd.concat(_res, axis=1, sort=False).reset_index()

    def process_ret_history(self):
        self._ret_history()
        self._process_result(self.ret_res)
        df = self.result[self.result.datetime > '20180101']
        df = df.replace(np.Inf, None).replace(-np.Inf, None)
        df = df.drop_duplicates(subset=['index_id', 'datetime'])
        self._data_helper._upload_derived(df, IndexReturn.__table__.name)

    def _vol_history(self):
        self.ret_vol = {}

        for name, value in self._DIM_TYPE.items():
            temp_vol = []
            for index, row in self.index_price_vol_part.iterrows():
                bd = (index - value).date()
                bd_list = self.date_list[self.date_list <= bd]
                if bd_list.empty:
                    continue
                tem_i = self.index_price_vol_part.loc[bd_list.array[-1]: index, :].std(ddof=1)* np.sqrt(self.TRADE_DAY_PER_YEAR)
                tem_i = tem_i.rename(row.name)
                temp_vol.append(tem_i)
            self.ret_vol[name + 'vol'] = pd.DataFrame(temp_vol).rename_axis(index='datetime')

        self.ret_vol['this_s_vol'] = self.index_price_vol_part.apply(self._this_s_vol, axis=1)
        self.ret_vol['this_y_vol'] = self.index_price_vol_part.apply(self._this_y_vol, axis=1)
        self.ret_vol['cumulative_vol'] = self.index_price_vol_part.apply(self._cumulative_vol, axis=1)

    def process_vol_history(self):
        self._vol_history()
        self._process_result(self.ret_vol)
        df = self.result[self.result.datetime > '20180101']
        df = df.replace(np.Inf, None).replace(-np.Inf, None)
        df = df.drop_duplicates(subset=['index_id', 'datetime'])
        self._data_helper._upload_derived(df, IndexVolatility.__table__.name)

    def _process_update_result(self, result):
        res = []
        for k, s in result.items():
            s.name = k
            res.append(pd.DataFrame(s).rename(columns={0: k}))
        result = pd.concat(res, sort=False, axis=1).reset_index()
        result['datetime'] = self.end_date
        return result

    def _update_ret(self):
        self.ret_res = {}

        # 取最近一天的日期和数据
        last_row = self.index_price.iloc[-1, :]
        last_date = self.index_price.index.array[-1]
        # 遍历每个需要计算的时间区间
        for name, value in self._DIM_TYPE.items():
            # 根据时间区间计算出begin date(bd)
            bd = (last_date - value).date()
            # 试图寻找bd及其之前的最近一天
            bd_list = self.date_list[self.date_list <= bd]
            if bd_list.empty:
                continue
            # 计算区间内的return
            temp_ret = (last_row / self.index_price.loc[bd_list.array[-1], :] - 1).rename(name + 'ret')
            self.ret_res[name + 'ret'] = pd.DataFrame(temp_ret)

        s_date = self._get_season_date(self.end_date, True)
        self.ret_res['this_s_ret'] = self._term_ret(self.index_price.loc[s_date:])

        y_date = self._get_year_date(self.end_date, True)
        self.ret_res['this_y_ret'] = self._term_ret(self.index_price.loc[y_date:])
        self.ret_res['cumulative_ret'] = self._term_ret(self.index_price)
        result_ret = self._process_update_result(self.ret_res)
        return result_ret.replace(np.Inf, None).replace(-np.Inf, None).drop_duplicates(subset=['index_id', 'datetime'])

    def _update_vol(self):
        self.vol_res = {}

        last_date = self.index_price_vol_part.index.array[-1]
        for name, value in self._DIM_TYPE.items():
            bd = (last_date - value).date()
            bd_list = self.date_list[self.date_list <= bd]
            if bd_list.empty:
                continue
            temp_vol = self.index_price_vol_part.loc[bd_list.array[-1]: last_date, :].std(ddof=1) * np.sqrt(self.TRADE_DAY_PER_YEAR)
            temp_vol = temp_vol.rename(name + 'vol')
            self.vol_res[name + 'vol'] = pd.DataFrame(temp_vol)

        s_date = self._get_season_date(self.end_date, False)
        self.vol_res['this_s_vol'] = self._term_vol(self.index_price_vol_part.loc[s_date:])

        y_date = self._get_year_date(self.end_date, False)
        self.vol_res['this_y_vol'] = self._term_vol(self.index_price_vol_part.loc[y_date:])
        self.vol_res['cumulative_vol'] = self._term_vol(self.index_price_vol_part)
        result_vol = self._process_update_result(self.vol_res)
        return result_vol.replace(np.Inf, None).replace(-np.Inf, None).drop_duplicates(subset=['index_id', 'datetime'])

    def process(self, end_date):
        failed_tasks = []
        try:
            # 一次load
            self.init(end_date=end_date)
            result_ret = self._update_ret()
            self._data_helper._upload_derived(result_ret, IndexReturn.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('index_return')

        try:
            result_vol = self._update_vol()
            self._data_helper._upload_derived(result_vol, IndexVolatility.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('index_volatility')
        return failed_tasks


if __name__ == '__main__':
    from .derived_data_helper import DerivedDataHelper
    iip = IndexIndicatorProcessor(DerivedDataHelper())
    iip.process('20200925')

    # iip.history_init()
    # iip.process_ret_history()
    # iip.process_vol_history()
