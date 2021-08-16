#!/usr/bin/env python
# coding: utf-8
import numpy as np
import pandas as pd
import rqdatac as rq
import datetime
import traceback
import json
from ...wrapper.mysql import RawDatabaseConnector
from ...view.raw_models import *
from .constant import STOCK_VALUATION_FACTORS, FUND_INDICATORS
from ...api.basic import BasicDataApi
from .raw_data_helper import RawDataHelper

class RqRawDataDownloader(object):
    def __init__(self, rq_license, data_helper):
        self._data_helper = data_helper
        # Initialize RiceQuant API
        rq.init('license', rq_license, ('rqdatad-pro.ricequant.com', 16011))

        # Get all fund order_book_ids
        # self._fund_order_book_id_list = list(set(rq.fund.all_instruments()['order_book_id'].tolist()))

        # Get stock order_book_ids
        # self._stock_order_book_id_list = rq.all_instruments(type='CS', market='cn')['order_book_id'].tolist()

        # Get index list
        # index_df = BasicDataApi().get_index_info()
        # self._index_list = [order_book_id for order_book_id in index_df['order_book_id'].tolist()
        #     if order_book_id and order_book_id != 'not_available' and '.' in order_book_id]
        # self._future_list = [order_book_id for order_book_id in index_df['order_book_id'].tolist()
        #     if order_book_id and order_book_id != 'not_available' and '.' not in order_book_id]
        # self._order_book_id_2_index_id = {order_book_id : index_id for order_book_id, index_id in
        #     zip(index_df['order_book_id'], index_df['index_id']) if order_book_id != 'not_available'}

    def _get_date_list(self, start_date, end_date):
        start_datetime = datetime.datetime.strptime(start_date, '%Y%m%d')
        end_datetime = datetime.datetime.strptime(end_date, '%Y%m%d')
        date_list = []
        while start_datetime <= end_datetime:
            date_list.append(start_datetime.strftime('%Y%m%d'))
            start_datetime += datetime.timedelta(days=1)
        return date_list

    def rq_fund_indicator(self, start_date, end_date):
        try:
            df = rq.fund.get_indicators(self._fund_order_book_id_list, start_date, end_date,
                fields=FUND_INDICATORS)

            if df is not None:
                df.reset_index(inplace=True)
                self._data_helper._upload_raw(df, RqFundIndicator.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def rq_fund_nav(self, start_date, end_date):
        try:
            df_list = []

            count = 0
            for order_book_id in self._fund_order_book_id_list:
                count += 1
                if count % 100 == 0:
                    print(f'[{RqFundNav.__table__.name}] downloaded {count} out of '
                        f'{len(self._fund_order_book_id_list)} funds')
                df = rq.fund.get_nav(order_book_id, start_date, end_date, expect_df=True)
                if df is None:
                    continue
                df.reset_index(inplace=True)
                df_list.append(df)

            if len(df_list) > 0:
                df_all = pd.concat(df_list)
                self._data_helper._upload_raw(df_all, RqFundNav.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def rq_fund_size(self):
        try:
            instruments = []
            for instrument in rq.fund.instruments(self._fund_order_book_id_list):
                instruments.append({
                    'order_book_id' : instrument.order_book_id,
                    'latest_size' : instrument.latest_size
                })
            df = pd.DataFrame(instruments)
            if df is not None:
                self._data_helper._upload_raw(df, RqFundSize.__table__.name, to_truncate=True)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def rq_index_price(self, start_date, end_date):
        try:
            df = rq.get_price(self._index_list, start_date, end_date, expect_df=True)
            if df is not None:
                df = df.reset_index().drop(['num_trades'], axis = 1)
                df['datetime'] = df['date']
                df = df.drop(['date'], axis = 1)
                self._data_helper._upload_raw(df, RqIndexPrice.__table__.name)

            df = rq.get_price(self._future_list, start_date, end_date, expect_df=True)
            if df is not None:
                df = df.reset_index().drop(['limit_down', 'prev_settlement', 'limit_up', 'open_interest', 'settlement', 
                    'dominant_id'], axis = 1, errors='ignore')
                df['datetime'] = df['date']
                df = df.drop(['date'], axis = 1)
                self._data_helper._upload_raw(df, RqIndexPrice.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def rq_index_weight(self, start_date, end_date):
        try:
            date_list = self._get_date_list(start_date, end_date)
            for i in self._index_list:
                res = []
                for d in date_list:
                    try:
                        df = rq.index_weights(i, date=d)
                        if df is not None:
                            dic = df.to_dict()
                            stock_list = [k for k, v in dic.items()]
                            weight_list = [round(v, 6) for k, v in dic.items()]
                            res.append({
                                'index_id': self._order_book_id_2_index_id[i],
                                'datetime': d,
                                'weight_list': json.dumps(weight_list),
                                'stock_list': json.dumps(stock_list),
                            })
                    except:
                        pass
                if len(res) > 0:
                    df = pd.DataFrame(res)
                    self._data_helper._upload_raw(df, RqIndexWeight.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def rq_stock_fin_fac(self, start_date, end_date):
        try:
            factor = 'return_on_equity_ttm'
            df = rq.get_factor(self._stock_order_book_id_list, factor=factor, start_date=start_date, end_date=end_date)
            if df is not None:
                to_convert_series = type(df) is pd.core.series.Series
                if to_convert_series:
                    df = df.to_frame()
                df = df.stack().reset_index()
                df.columns = ['stock_id', 'datetime', factor] if to_convert_series else ['datetime', 'stock_id', factor]
                self._data_helper._upload_raw(df, RqStockFinFac.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def rq_stock_post_price(self, start_date, end_date):
        try:
            df = rq.get_price(self._stock_order_book_id_list, start_date=start_date, end_date=end_date,
                adjust_type='post', expect_df=True)
            if df is not None:
                df = df.reset_index().rename(columns={'date': 'datetime'})
                self._data_helper._upload_raw(df, RqStockPostPrice.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def rq_stock_price(self, start_date, end_date):
        try:
            df = rq.get_price(self._stock_order_book_id_list, start_date=start_date, end_date=end_date,
                adjust_type='none', expect_df=True)
            if df is not None:
                df = df.reset_index().rename(columns={'date': 'datetime'})
                self._data_helper._upload_raw(df, RqStockPrice.__table__.name)
            return True
        except:
            traceback.print_exc()
            return False

    def rq_stock_valuation(self, start_date, end_date):
        try:
            df = rq.get_factor(self._stock_order_book_id_list, STOCK_VALUATION_FACTORS, start_date=start_date,
                end_date=end_date, expect_df=True)
            if df is not None:
                df = df.reset_index().rename(columns={'order_book_id': 'stock_id', 'date':'datetime'}).replace(
                    [np.inf, -np.inf], np.nan)
                self._data_helper._upload_raw(df, RqStockValuation.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def trading_day_list(self, start_date, end_date):
        try:
            df = pd.DataFrame(rq.get_trading_dates(start_date=start_date, end_date=end_date, market='cn'),
                columns=['datetime'])
            if df is not None:
                self._data_helper._upload_raw(df, TradingDayList.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def stock_info(self):
        try:
            order_book_ids = []
            for stock_order_book_id in self._stock_order_book_id_list:
                order_book_ids.append({
                    'rq_id' : stock_order_book_id,
                    'stock_id' : stock_order_book_id
                })
            df = pd.DataFrame(order_book_ids)
            if df is not None:
                self._data_helper._upload_raw(df, StockInfo.__table__.name, to_truncate=True)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def fund_rating(self, start_date, end_date):
        try:
            fund_order_book_id_list = list(set(rq.fund.all_instruments()['order_book_id'].tolist()))
            df = rq.fund.get_ratings(fund_order_book_id_list)
            # df = rq.fund.get_ratings(self._fund_order_book_id_list)
            if df is not None:
                df.reset_index(inplace=True)
                df = df[(df['datetime'] >= start_date) & (df['datetime'] <= end_date)]
                self._data_helper._upload_raw(df, FundRating.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def stock_minute(self, to_save):
        try:
            stock_order_book_id_list = rq.all_instruments(type='CS', market='cn')['order_book_id'].tolist()
            df = rq.current_minute(stock_order_book_id_list, skip_suspended=True)
            if df is not None:
                today_date = datetime.date.today()
                today = datetime.datetime(today_date.year, today_date.month, today_date.day)
                df.reset_index(inplace=True)
                df = df[df['datetime'] >= today]
                if to_save:
                    try:
                        self._data_helper._upload_raw(df, RqStockMinute.__table__.name)
                    except Exception as e:
                        print(e)
                        traceback.print_exc()
            return df
        except Exception as e:
            print(e)
            traceback.print_exc()
            return None

    def index_minute(self):
        # Get index list
        try:
            index_df = BasicDataApi().get_index_info()
            index_list = [order_book_id for order_book_id in index_df['order_book_id'].tolist()
                if order_book_id and order_book_id != 'not_available' and '.' in order_book_id]
            df = rq.current_minute(index_list, skip_suspended=True)
            if df is not None:
                today = datetime.date.today()
                df.reset_index(inplace=True)
                df = df[df['datetime'] >= today]
                # self._data_helper._upload_raw(df, RqIndexMinute.__table__.name)
            print(df)
            return df
        except Exception as e:
            print(e)
            traceback.print_exc()
            return None

    def download_all(self, start_date, end_date):
        failed_tasks = []
        # # Safe to disable
        # if not self.rq_fund_indicator(start_date, end_date):
        #     failed_tasks.append('rq_fund_indicator')

        # # Safe to disable
        # if not self.rq_fund_nav(start_date, end_date):
        #     failed_tasks.append('rq_fund_nav')

        # # Safe to disable
        # if not self.rq_index_weight(start_date, end_date):
        #     failed_tasks.append('rq_index_weight')

        # # Safe to disable
        # if not self.rq_stock_fin_fac(start_date, end_date):
        #     failed_tasks.append('rq_stock_fin_fac')

        # # Safe to disable
        # if not self.rq_stock_post_price(start_date, end_date):
        #     failed_tasks.append('rq_stock_post_price')

        # # Safe to disable
        # if not self.rq_stock_price(start_date, end_date):
        #     failed_tasks.append('rq_stock_price')

        # # Safe to disable
        # if not self.rq_stock_valuation(start_date, end_date):
        #     failed_tasks.append('rq_stock_valuation')

        # # Safe to disable
        # if not self.stock_info():
        #     failed_tasks.append('stock_info')

        # # Safe to disable
        # if not self.trading_day_list(start_date, end_date):
        #     failed_tasks.append('trading_day_list')

        # # Safe to disable
        # if not self.rq_fund_size():
        #     failed_tasks.append('rq_fund_size')

        # # Safe to disable
        # if not self.rq_index_price(start_date, end_date):
        #     failed_tasks.append('rq_index_price')

        # # Safe to disable
        # if not self.fund_rating(start_date, end_date):
        #     failed_tasks.append('fund_rating')

        return failed_tasks


if __name__ == "__main__":
    from ....util.config import SurfingConfigurator

    rq_license = SurfingConfigurator().get_license_settings('rq')
    raw_data_downloader = RqRawDataDownloader(rq_license, RawDataHelper())
    raw_data_downloader.stock_minute()
    # raw_data_downloader.rq_index_price('20200421', '20200422')
    # raw_data_downloader.rq_index_weight('20200428', '20200428')
    # raw_data_downloader.rq_stock_price('20050101', '20091231')
