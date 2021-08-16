
from ...structure import Tick
from .wrapper import DataWrapper
import pandas as pd
import numpy as np
import os
import json
import datetime

class RQDataWrapper(DataWrapper):

    TICK_COLUMNS = [
        'open', 'last', 'high', 'low', 'prev_close', 'volume', 'total_turnover',
        'limit_up', 'limit_down', 'a1', 'a2', 'a3', 'a4', 'a5', 'b1', 'b2',
        'b3', 'b4', 'b5', 'a1_v', 'a2_v', 'a3_v', 'a4_v', 'a5_v', 'b1_v',
        'b2_v', 'b3_v', 'b4_v', 'b5_v', 'change_rate', 'time'
    ]

    def __init__(self, base_path):
        super().__init__(base_path)

    def load_data(self, month, ticker):
        folder = os.path.join(self.base_path, month)
        return DataWrapper.base_load_data(folder, ticker, 'time', self.TICK_COLUMNS)

    def parse(self, index, row):
        return Tick(ticker=row.ticker, mkt_time= pd.to_datetime(index, format='%Y-%m-%dT%H:%M:%S.%fZ'),
                    bid_price1=row.b1, ask_price1=row.a1, bid_volume1=row.b1_v, ask_volume1=row.a1_v,
                    bid_price2=row.b2, ask_price2=row.a2, bid_volume2=row.b2_v, ask_volume2=row.a2_v,
                    bid_price3=row.b3, ask_price3=row.a3, bid_volume3=row.b3_v, ask_volume3=row.a3_v,
                    bid_price4=row.b4, ask_price4=row.a4, bid_volume4=row.b4_v, ask_volume4=row.a4_v,
                    bid_price5=row.b5, ask_price5=row.a5, bid_volume5=row.b5_v, ask_volume5=row.a5_v,
                    up_limit=row.limit_up, down_limit=row.limit_down,
                    last_price=row['last']
        )


class OTTicksWrapper(DataWrapper):

    TICK_COLUMNS = [
        'ask_price_1', 'ask_volume_1', 'ask_price_2', 'ask_volume_2', 'ask_price_3', 'ask_volume_3',
        'ask_price_4', 'ask_volume_4', 'ask_price_5', 'ask_volume_5', 'bid_price_1', 'bid_volume_1',
        'bid_price_2', 'bid_volume_2', 'bid_price_3', 'bid_volume_3', 'bid_price_4', 'bid_volume_4',
        'bid_price_5', 'bid_volume_5', 'last_price',  'mkt_time', 'volume',
    ]

    def __init__(self, base_path):
        super().__init__(base_path)

    def load_data(self, month, ticker):
        folder = os.path.join(self.base_path, month)
        df = DataWrapper.base_load_data(folder, ticker, 'mkt_time', self.TICK_COLUMNS)
        df.index = pd.to_datetime(df.index, unit='ns')
        return df

    def parse(self, index, row):
        return Tick(ticker=row.ticker, mkt_time= pd.to_datetime(index, format='%Y-%m-%dT%H:%M:%S.%fZ'),
                    last_price=row.last_price,
                    ask_price1=row.ask_price_1, ask_volume1=row.ask_volume_1, bid_price1=row.bid_price_1, bid_volume1=row.bid_volume_1,
                    ask_price2=row.ask_price_2, ask_volume2=row.ask_volume_2, bid_price2=row.bid_price_2, bid_volume2=row.bid_volume_2,
                    ask_price3=row.ask_price_3, ask_volume3=row.ask_volume_3, bid_price3=row.bid_price_3, bid_volume3=row.bid_volume_3,
                    ask_price4=row.ask_price_4, ask_volume4=row.ask_volume_4, bid_price4=row.bid_price_4, bid_volume4=row.bid_volume_4,
                    ask_price5=row.ask_price_5, ask_volume5=row.ask_volume_5, bid_price5=row.bid_price_5, bid_volume5=row.bid_volume_5
        )


class StockDailyWrapper():

    def __init__(self,base_path=None,price_type=None,stock_pool=None,start_time=None,end_time=None,factor_path=None,factor_name=None,vwap_limit=None):
        self.base_path       = base_path
        self.price_type      = price_type
        self.stock_pool      = stock_pool
        self.factor_path     = factor_path
        self.factor_name     = factor_name
        self.vwap_limit      = vwap_limit
        self.start_time      = self.change_date_time(start_time)
        self.end_time        = self.change_date_time(end_time)
        self.stock_pool_data = self.load_stock_pool()
        self.common_pool     = self.load_common_pool()
        self.price_data      = self.load_price()
        self.st_data         = self.load_st()
        self.suspended_data  = self.load_suspended()
        self.stock_info      = self.load_stock_info()
        self.date_list       = sorted(list(self.price_data.keys()))
        self.factor_data     = self.load_factor()
        self.vwap_diff_limit_stock = self.load_vwap_diff_limit_stock()

    def change_date_time(self, str_date):
        if len(str_date) == 8:
            return str_date[:4]+'-'+str_date[4:6]+'-'+str_date[6:8]
        else:
            return str_date

    def load_json(self, paths):
        with open(paths,'r') as load_f:
            json_data = json.load(load_f)
        return json_data

    def load_stock_pool(self):
        paths = os.path.join(self.base_path, 'stock_pool', f'{self.stock_pool}.json')
        dic = self.load_json(paths)
        return self.filter_dict_by_key(dic)

    def load_common_pool(self):
        common_pool = set()
        for i in list(self.stock_pool_data.values()):
            common_pool.update(i)
        return list(common_pool)

    def load_stock_info(self):
        paths = os.path.join(self.base_path, 'stock_info', 'stock_info.json')
        return self.load_json(paths)

    def load_price(self):
        paths = os.path.join(self.base_path, self.price_type)
        meta_info = DataWrapper(paths).meta_info
        columns = meta_info['tickers']+['time']
        df = DataWrapper.base_load_npz(paths, self.price_type, columns)
        df = df.fillna(method='ffill')
        df.index = df.time.dt.strftime('%Y-%m-%d')
        df.drop(columns=['time'],inplace=True)
        df = df[self.common_pool]
        df = df.astype(float).round(3).copy()
        df['time'] = df.index
        data_dic = df.to_dict('index')
        return self.filter_dict_by_key(data_dic)

    def load_st(self):
        paths = os.path.join(self.base_path, 'st', 'st.json')
        dic = self.load_json(paths)
        return self.filter_dict_by_key(dic)

    def load_suspended(self):
        paths = os.path.join(self.base_path, 'suspended', 'suspended.json')
        dic = self.load_json(paths)
        return self.filter_dict_by_key(dic)

    def load_factor(self):
        factor_path = os.path.join(self.factor_path, f'{self.factor_name}.npz')
        factor_meta_path = os.path.join(self.factor_path, '.meta_data.json')
        meta_info = self.load_json(factor_meta_path)
        value = np.load(factor_path, allow_pickle=True)
        df = pd.DataFrame(data=value['arr_0'], columns=meta_info['tickers']+['time'])
        df.index = df.time.dt.strftime('%Y-%m-%d')
        df.drop(columns=['time'],inplace=True)
        try:
            df = df[self.common_pool]
        except:
            pass
        df = df.astype(float).round(4).copy()
        df['time'] = df.index
        data_dic = df.to_dict('index')
        return self.filter_dict_by_key(data_dic)

    def load_black_list(self):
        pass

    def load_vwap_diff_limit_stock(self):
        paths = os.path.join(self.base_path, 'post_vwap_preclose_diff')
        meta_info = DataWrapper(paths).meta_info
        columns = meta_info['tickers']+['time']
        df = DataWrapper.base_load_npz(paths, 'post_vwap_preclose_diff', columns)
        df.index = df.time.dt.strftime('%Y-%m-%d')
        df.drop(columns=['time'],inplace=True)
        df = df[self.common_pool]
        df = df.astype(float).round(2).abs().copy()
        df['time'] = df.index
        data_dic = df.to_dict('index')
        return self.filter_dict_by_key(data_dic)

    def remove_limit_vwap_stock(self, date):
        dic = self.vwap_diff_limit_stock[date]
        del dic['time']
        rm_l = [k for k, v in  dic.items() if v > self.vwap_limit]
        return rm_l

    def filter_dict_by_key(self, dic):
        dic = dict(filter(lambda elem: (elem[0] >= self.start_time and elem[0] <= self.end_time), dic.items()))
        return dic

    def find_beginday_yesterday(self):
        paths = os.path.join(self.base_path, self.price_type)
        meta_info = DataWrapper(paths).meta_info
        start_time = [ _ for _ in meta_info['dates'] if self.start_time < _][0]
        d = meta_info['dates'][meta_info['dates'].index(start_time) - 1]
        return d
