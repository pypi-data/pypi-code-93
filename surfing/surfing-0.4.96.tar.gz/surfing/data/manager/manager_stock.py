
from typing import Tuple, Optional

import datetime
import pandas as pd
from . import DataManager
from ..wrapper.wrapper_stock import StockDailyWrapper
from ...structure import TickerInfo
from ...stock.factor.api import StockFactorApi


class StockDataManager(DataManager):

    def __init__(self,data_path=None,start_time=None,end_time=None,universe=None,datatype=None,stock_pool=None,price_type=None,factor_path=None,factor_name=None,vwap_limit=None):
        self.wrapper = datatype(data_path,price_type,stock_pool,start_time,end_time,factor_path,factor_name,vwap_limit) if datatype == StockDailyWrapper else datatype(data_path)
        self.universe = universe
        self.frames = None
        self.start_time = start_time if isinstance(start_time, datetime.datetime) else datetime.datetime.strptime(start_time,'%Y%m%d')
        self.end_time = end_time if isinstance(end_time, datetime.datetime) else datetime.datetime.strptime(end_time,'%Y%m%d')
        self.t_info = 0 if datatype == StockDailyWrapper else self.init_t_info()
        self.modify_df()
        self.stock_pool=stock_pool

    def init(self):
        pass

    def get_data(self):
        return self._get_frames(self.start_time, self.end_time, self.universe)

    def parse_row(self, index, row):
        return self.wrapper.parse(index, row)

    def find_start_file(self, ticker):
        start_day_str = self.start_time.strftime('%Y%m%d')
        for i in self.wrapper.meta_info[ticker]['data_list'][:-1]:
            next_file_index = self.wrapper.meta_info[ticker]['data_list'].index(i)+1
            if start_day_str >= i and start_day_str < self.wrapper.meta_info[ticker]['data_list'][next_file_index]:
                return i
        assert False, 'data not exist'

    def _get_months(self, start_dt, end_dt):
        months = set([])
        dt = start_dt
        while dt <= end_dt:
            months.add(dt.strftime('%Y%m'))
            dt += datetime.timedelta(days=1)
        months = sorted(months)
        return months

    def init_t_info(self):
        dic = {}
        if not self.universe:
            return None
        for ticker in self.universe:
            dic[ticker] = TickerInfo()
            dic[ticker].loc = 0
            dic[ticker].file = self.find_start_file(ticker)
            dic[ticker].file_reader_time = self.start_time
            dic[ticker].data_list = self.wrapper.meta_info[ticker]['data_list']
            dic[ticker].data_bite = int(self.wrapper.meta_info[ticker]['data_bite'])
        return dic

    def modify_df(self):
        if not self.universe:
            return None

        for ticker in self.universe:
            self.t_info[ticker].df   = self.load_df_bite(ticker)
            if self.t_info[ticker].df.empty:
                self.t_info[ticker].len  = 0
                self.t_info[ticker].file_end_time  = 0
            else:
                self.t_info[ticker].len  = self.t_info[ticker].df.shape[0]
                self.t_info[ticker].file_end_time  = self.t_info[ticker].df.index[-1]

    def get_current_time(self):
        return  [self.t_info[i].df.index[self.t_info[i].loc] for i in self.universe]

    def load_df_bite(self, ticker):
        df_item = self.wrapper.load_data(self.t_info[ticker].file, ticker)
        df_item['ticker'] = ticker
        df_item.sort_index(inplace=True)
        if df_item.empty:
            self.t_info[ticker].file_end_time  = 0
        else:
            self.t_info[ticker].file_end_time = df_item.index[-1]
        begin_time = max(self.t_info[ticker].file_reader_time, df_item.index[0])
        finish_time = begin_time + pd.offsets.Day(self.t_info[ticker].data_bite)
        self.t_info[ticker].file_reader_time = finish_time
        if self.t_info[ticker].file_reader_time > self.t_info[ticker].file_end_time:
            self.t_info[ticker].file_reader_time = self.start_time
            idx = self.t_info[ticker].data_list.index(self.t_info[ticker].file) + 1
            self.t_info[ticker].file = self.t_info[ticker].data_list[idx]
        begin_time  = begin_time.strftime('%Y-%m-%d') + ' 00:00:00'
        finish_time = finish_time + pd.offsets.Day(1)
        finish_time = finish_time.strftime('%Y-%m-%d') + ' 00:00:00'
        df_item = df_item[df_item.index >= begin_time]
        df_item = df_item[df_item.index <= finish_time]
        return df_item

    def reload(self):
        for ticker in self.universe:
            if self.t_info[ticker].loc == self.t_info[ticker].len:
                df_item = pd.DataFrame()
                while df_item.empty:
                    df_item = self.load_df_bite(ticker)
                    if not df_item.empty:
                        self.t_info[ticker].df = df_item
                        self.t_info[ticker].loc = 0
                        self.t_info[ticker].len = df_item.shape[0]
                        self.t_info[ticker].file_end_time = df_item.index[-1]
                    elif df_item.empty:
                        if self.t_info[ticker].file_reader_time >  self.t_info[ticker].file_end_time:
                            idx = self.t_info[ticker].data_list.index(self.t_info[ticker].file) + 1
                            try:
                                self.t_info[ticker].file = self.t_info[ticker].data_list[idx]
                                self.t_info[ticker].file_reader_time = self.start_time
                            except:
                                print('download more data')
                                break
                        df_item = self.load_df_bite(ticker)

    def get_next_tick(self):
        self.reload()
        # if time > end_time,  stop
        time_list = self.get_current_time()
        current_time = min(time_list)
        if current_time > self.end_time:
            return
        # normal send and renew loc_list
        i = time_list.index(current_time)
        ticker = self.universe[i]
        row = self.t_info[ticker].df.iloc[self.t_info[ticker].loc]
        self.t_info[ticker].loc += 1
        self.current_index = row.name
        return self.parse_row(row.name, row)

    def get_next_day(self):
        # remove st and suspended from pool_today
        # build today factor filter by pool_today
        try:
            date = self.wrapper.date_list[self.t_info]
            self.stock_pool_today = self.wrapper.stock_pool_data[date]
            self.st_today = self.wrapper.st_data[date]
            self.suspended_today = self.wrapper.suspended_data[date]
            ban_list = list(set(self.st_today + self.suspended_today))
            self.stock_pool_today = [item for item in self.stock_pool_today if item not in ban_list]
            self.factor_today = self.wrapper.factor_data[date]
            self.t_info += 1
            self.factor_today = {k: v for k, v in self.factor_today.items() if k in self.stock_pool_today}
            self.rm_l_today = self.wrapper.remove_limit_vwap_stock(date)
            return self.wrapper.price_data[date]
        except:
            return None

    def _get_frames(self, start_time=None, end_time=None, universe=None):
        months = self._get_months(start_time, end_time)
        dfs = []
        for ticker in universe:
            for month in months:
                df_item = self.wrapper.load_data(month, ticker)
                df_item['ticker'] = ticker
                dfs.append(df_item)
        dfs = pd.concat(dfs)
        dfs.sort_index(inplace=True)
        dfs = dfs[dfs.index >= start_time.strftime('%Y-%m-%d') + ' 00:00:00']
        dfs = dfs[dfs.index <= end_time.strftime('%Y-%m-%d') + ' 23:59:59']
        return dfs

    def terminate(self):
        pass

    @staticmethod
    def get_stock_factor_ret(factor_names: Tuple[str], universe: str = 'default') -> Optional[pd.DataFrame]:
        return StockFactorApi.get_stock_factor_ret(factor_names, universe)
