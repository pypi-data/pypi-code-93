#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
from typing import List, Set, Tuple, Dict, Optional
from operator import itemgetter
from collections import defaultdict

from pandas.core.frame import DataFrame
from .EMQuantAPI_Python.python3.EmQuantAPI import *
import datetime
import time
import json
import os
import traceback
import sys
from sqlalchemy import distinct
from sqlalchemy.orm import sessionmaker
from .constant import FUTURE_SECTOR
from ...wrapper.mysql import RawDatabaseConnector
from ...view.raw_models import *
from ...api.basic import BasicDataApi
from ...api.raw import RawDataApi
from ....constant import SectorType, IndexPriceSource, CodeFeeMode
from ....constant import INDEX_PRICE_EXTRA_TRADE_DAYS, INDEX_VAL_EXTRA_TRADE_DAYS, FUND_NAV_EXTRA_TRADE_DAYS, QUARTER_UPDATE_DATE_LIST, SEMI_UPDATE_DATE_LIST, FUTURE_PRICE_EXTRA_TRADE_DAYS
from .raw_data_helper import RawDataHelper, ALL_CSI_INDEX_INNER_NAME


class EmRawDataDownloader:

    _EM_RETRY_TIMES = 10
    _EM_RETRY_INTERVAL_S = 10
    _MACROECONOMIC_MAP = {
        'E1002041': 'CB_AAA_1Y',
        'E1701048': 'EX_DR_RATIO',
    }
    _MACROECONOMIC_MAP_I = {v: k for k, v in _MACROECONOMIC_MAP.items()}

    def __init__(self, data_helper, dry_run=False):
        # pd.set_option('display.max_rows', None)

        self._data_helper = data_helper
        if not dry_run:
            # ForceLogin
            # 取值0，当线上已存在该账户时，不强制登录
            # 取值1，当线上已存在该账户时，强制登录，将前一位在线用户踢下线
            options = 'TestLatency=1,ForceLogin=1'
            loginResult = c.start(options, mainCallBack=self._main_callback)
            if loginResult.ErrorCode != 0:
                print('EM login failed')
                sys.exit()

        self._index_block_list: Optional[Set[str]] = None

    def __del__(self):
        c.stop()

    def _main_callback(self, quantdata):
        '''
        mainCallback 是主回调函数，可捕捉连接错误
        该函数只有一个为c.EmQuantData类型的参数quantdata
        :param quantdata: c.EmQuantData
        '''
        print(f'MainCallback: {quantdata}')

    def _get_date_list(self, start_date, end_date):
        start_datetime = datetime.datetime.strptime(start_date, '%Y%m%d')
        end_datetime = datetime.datetime.strptime(end_date, '%Y%m%d')
        date_list = []
        while start_datetime <= end_datetime:
            date_list.append(start_datetime.strftime('%Y%m%d'))
            start_datetime += datetime.timedelta(days=1)
        return date_list

    # 使用em wrapper系列的函数可以在失败时自动重试
    def _em_tradedates_wrapper(self, start_date: str, end_date: str, options: str):
        for i in range(self._EM_RETRY_TIMES + 1):
            tradedates_result = c.tradedates(start_date, end_date, options)
            if tradedates_result.ErrorCode == 0:
                return tradedates_result.Data
            print(f'Failed to get tradedates({i}): {tradedates_result.ErrorMsg} (err_code){tradedates_result.ErrorCode}')
            time.sleep(self._EM_RETRY_INTERVAL_S)
        return

    def _em_sector_wrapper(self, sector_code: str, end_date: str):
        for i in range(self._EM_RETRY_TIMES + 1):
            ids_result = c.sector(sector_code, end_date)
            if ids_result.ErrorCode == 0:
                return ids_result.Codes
            print(f'Failed to get sector list({i}): {ids_result.ErrorMsg} (err_code){ids_result.ErrorCode}')
            time.sleep(self._EM_RETRY_INTERVAL_S)
        return

    def _em_css_wrapper(self, codes, indicators: str, options: str):
        if 'ispandas=1' not in options.lower():
            if options:
                options += ','
            options += 'Ispandas=1'
        for i in range(self._EM_RETRY_TIMES + 1):
            data = c.css(codes, indicators, options)
            if isinstance(data, pd.DataFrame):
                return data
            if data.ErrorCode != 0:
                print(f'failed to get css data({i}): {data.ErrorMsg} (err_code){data.ErrorCode}')
            else:
                print('weird, no error but not a df returned')
            time.sleep(self._EM_RETRY_INTERVAL_S)
        return

    def _em_csd_wrapper(self, codes, indicators: str, start_date: str, end_date: str, options: str):
        if 'ispandas=1' not in options.lower():
            if options:
                options += ','
            options += 'Ispandas=1'
        for i in range(self._EM_RETRY_TIMES + 1):
            data = c.csd(codes, indicators, start_date, end_date, options)
            if isinstance(data, pd.DataFrame):
                return data
            if data.ErrorCode != 0:
                print(f'failed to get csd data({i}): {data.ErrorMsg} (err_code){data.ErrorCode}')
            else:
                print('weird, no error but not a df returned')
            time.sleep(self._EM_RETRY_INTERVAL_S)
        return

    def _em_ctr_wrapper(self, ctr_name: str, indicators: str, options: str):
        for i in range(self._EM_RETRY_TIMES + 1):
            data = c.ctr(ctr_name, indicators, options)
            if data.ErrorCode == 0:
                return data.Data
            elif data.ErrorCode == 10000009:
                print(f'no data when get ctr data({i}), return an empty dict')
                return {}
            print(f'failed to get ctr data({i}): {data.ErrorMsg} (err_code){data.ErrorCode}')
            time.sleep(self._EM_RETRY_INTERVAL_S)
        return

    def _em_getdate_wrapper(self, date: str, offday: str):
        for i in range(self._EM_RETRY_TIMES + 1):
            data = c.getdate(date, offday)
            if data.ErrorCode == 0:
                return data.Data
            print(f'Failed to get date data({i}): {data.ErrorMsg} (err_code){data.ErrorCode}')
            time.sleep(self._EM_RETRY_INTERVAL_S)
        return

    def _em_csqsnapshot_wrapper(self, codes: str, indicators: str, options: str):
        if 'ispandas=1' not in options.lower():
            if options:
                options += ','
            options += 'Ispandas=1'
        for i in range(self._EM_RETRY_TIMES + 1):
            data = c.csqsnapshot(codes, indicators, options)
            if isinstance(data, pd.DataFrame):
                return data
            if data.ErrorCode != 0:
                print(f'failed to get csqsnapshot data({i}): {data.ErrorMsg} (err_code){data.ErrorCode}')
            else:
                print('weird, no error but not a df returned')
            time.sleep(self._EM_RETRY_INTERVAL_S)
        return

    def _em_edb_wrapper(self, codes: str, options: str):
        if 'ispandas=1' not in options.lower():
            if options:
                options += ','
            options += 'Ispandas=1'
        for i in range(self._EM_RETRY_TIMES + 1):
            data = c.edb(codes, options)
            if isinstance(data, pd.DataFrame):
                return data
            if data.ErrorCode != 0:
                if data.ErrorCode == 10000009:
                    print(f'no data when get edb data({i}), return an empty df')
                    return pd.DataFrame()
                print(f'failed to get edb data({i}): {data.ErrorMsg} (err_code){data.ErrorCode}')
            else:
                print('weird, no error but not a df returned')
            time.sleep(self._EM_RETRY_INTERVAL_S)
        return

    def em_fund_nav_history(self, nav_file_dir):
        try:
            index = 1
            for filename in os.listdir(nav_file_dir):
                if filename.endswith(".xls"):
                    print(f'{index}: {filename}')
                    index += 1
                    fund_nav = pd.concat(pd.read_excel(os.path.join(nav_file_dir, filename), sheet_name=None),
                                         ignore_index=True)
                    fund_nav = fund_nav.drop(['简称'], axis=1)
                    fund_nav = fund_nav.rename(columns={
                        '代码': 'CODES',
                        '时间': 'DATES',
                        '单位净值(元)': 'ORIGINALUNIT',
                        '累计净值(元)': 'ORIGINALNAVACCUM',
                        '复权净值(元)': 'ADJUSTEDNAV',
                        '万份基金单位收益(元)': 'UNITYIELD10K',
                        '7日年化收益率(%)': 'YIELDOF7DAYS'
                    })

                    fund_nav = fund_nav[(fund_nav['DATES'] != '--')
                                        & (~fund_nav['DATES'].isnull())]
                    fund_nav = fund_nav.replace('--', np.nan)
                    self._data_helper._upload_raw(fund_nav, EmFundNav.__table__.name)
                else:
                    continue
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_index_price_history(self, em_ids, start_date, end_date):
        em_id_str = ','.join(em_ids) if isinstance(em_ids, list) else em_ids
        df = c.csd(em_id_str, "OPEN,HIGH,LOW,VOLUME,CLOSE,AMOUNT", start_date, end_date,
                   "period=1,adjustflag=1,curtype=1,order=1,market=0,Ispandas=1")
        if not isinstance(df, pd.DataFrame):
            if df.ErrorCode != 0:
                print(f'failed to get index price history: {df.ErrorMsg} (index_ids){em_ids}')
            return

        df = df.reset_index().rename(columns={
            'CODES': 'em_id',
            'DATES': 'datetime',
            'CLOSE': 'close',
            'OPEN': 'open',
            'HIGH': 'high',
            'LOW': 'low',
            'VOLUME': 'volume',
            'AMOUNT': 'amount',
        })
        df = df[df['close'].notna()]
        self._data_helper._upload_raw(df, EmIndexPrice.__table__.name)

    def em_fund_scale_history(self):
        with RawDatabaseConnector().managed_session() as db_session:
            try:
                dates = db_session.query(
                    distinct(EmFundNav.DATES)
                ).all()

                dates = [d for d, in dates]
                dates.sort()
                start_date = dates[0]
                for i in range(1, 100):
                    dates.insert(0, start_date - datetime.timedelta(days=i))

                for d in dates:
                    month_day = d.strftime('%m%d')
                    if month_day not in QUARTER_UPDATE_DATE_LIST:
                        continue

                    print(d)

                    fund_ids = db_session.query(
                        distinct(EmFundNav.CODES)
                    ).filter(
                        EmFundNav.DATES >= d,
                        EmFundNav.DATES <= d + datetime.timedelta(days=100)
                    ).all()

                    fund_ids = [f for f, in fund_ids]
                    fund_id_str = ','.join(fund_ids)

                    df = c.css(fund_id_str, "FUNDSCALE",
                               f"EndDate={d},Ispandas=1").reset_index()
                    df['DATES'] = d

                    self._data_helper._upload_raw(df, EmFundScale.__table__.name)
            except Exception as e:
                print('Failed to get data <err_msg> {}'.format(e))
                return None

    def em_fund_holding_rate_history(self, end_date: str):
        fund_list = RawDataHelper.get_all_fund_list(end_date)
        if fund_list is None:
            print('[em_fund_holding_rate_history] failed to get fund list')
            return False
        y_list = [str(y) for y in range(2020, 2021, 1)]
        d_list = []
        for y in y_list:
            for d in SEMI_UPDATE_DATE_LIST:
                d_list.append(y + d)
        for d in d_list:
            data = c.css(fund_list, "HOLDPERSONALHOLDINGPCT,HOLDINSTIHOLDINGPCT,HOLDNUM", f"ReportDate={d},Ispandas=1")
            data = data[data.drop(columns='DATES').notna().any(axis=1)].reset_index()
            data['DATES'] = d
            self._data_helper._upload_raw(data, EmFundHoldingRate.__table__.name)
            print(f'finish {d}')
        return True

    def em_fund_holding_rate(self, end_date: str):
        try:
            fund_list = RawDataHelper.get_all_live_fund_list(end_date)
            if fund_list is None:
                print('[em_fund_holding_rate] failed to get fund list')
                return False

            real_date = RawDataHelper.get_prev_target_date(end_date, SEMI_UPDATE_DATE_LIST)
            df = self._em_css_wrapper(fund_list, "HOLDPERSONALHOLDINGPCT,HOLDINSTIHOLDINGPCT,HOLDNUM", f"ReportDate={real_date},Ispandas=1")
            if df is None:
                print(f'[em_fund_holding_rate] failed to get data')
                return False
            df['DATES'] = real_date
            df = df[df.drop(columns=['DATES']).notna().any(axis=1)].reset_index()
            df['HOLDINSTIHOLDINGPCT'] = df.apply(lambda x: 0 if x.HOLDPERSONALHOLDINGPCT == 100 else x.HOLDINSTIHOLDINGPCT, axis=1)
            df['HOLDPERSONALHOLDINGPCT'] = df.apply(lambda x: 0 if x.HOLDINSTIHOLDINGPCT == 100 else x.HOLDPERSONALHOLDINGPCT, axis=1)
            now_df = RawDataApi().get_em_fund_holding_rate(start_date=real_date, end_date=real_date)
            if now_df is not None:
                df = df.replace({None: np.nan}).infer_objects()
                now_df = now_df.replace({None: np.nan}).infer_objects()
                # 过滤出来新增基金benchmark以及旧基金的benchmark发生变化的情况
                now_df = now_df.drop(columns=['_update_time']).sort_values(by=['CODES', 'DATES']).drop_duplicates(subset='CODES', keep='last')
                # merge on all columns
                df = df.merge(now_df, how='left', indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            # TODO: 最好原子提交下边两步
            RawDataApi().delete_em_fund_hold_rate(real_date, df.CODES.to_list())
            self._data_helper._upload_raw(df, EmFundHoldingRate.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_fund_nav(self, start_date, end_date, fund_list: Tuple[str] = ()):
        try:
            # TODO: 应该使用每一天当天的成分列表, 可能所有的sector都需要这样
            # Get all fund ids, 功能函数-板块成分
            # http://quantapi.eastmoney.com/Cmd/Sector?from=web
            start_date = datetime.datetime.strptime(start_date, '%Y%m%d') - datetime.timedelta(days=FUND_NAV_EXTRA_TRADE_DAYS)
            start_date = start_date.strftime('%Y%m%d')
            if not fund_list:
                # fund_list = self._em_sector_wrapper('507010', end_date)
                fund_list = RawDataHelper.get_all_live_fund_list(end_date)
                if fund_list is None:
                    print('[em_fund_nav] failed to get fund list')
                    return False
            # 基金 单位净值(原始披露) 累计单位净值(原始披露) 复权单位净值 万份基金单位收益 7日年化收益率
            data = self._em_csd_wrapper(fund_list, "ORIGINALUNIT,ORIGINALNAVACCUM,ADJUSTEDNAV,10KUNITYIELD,YIELDOF7DAYS", start_date, end_date, "period=1,adjustflag=1,curtype=1,order=1,market=0,Ispandas=1")
            if data is None:
                print('[em_fund_nav] failed to get fund nav data')
                return False
            df = data[data[['ORIGINALUNIT', 'ORIGINALNAVACCUM', 'ADJUSTEDNAV', '10KUNITYIELD', 'YIELDOF7DAYS']].notna().any(axis=1)]
            df = df.rename(columns={'10KUNITYIELD': 'UNITYIELD10K'}).reset_index()

            # 这里删掉之前几天的数据，然后再重刷一遍
            # TODO: 最好可以原子提交下边两步操作
            self.delete_em_fund_nav(start_date, end_date)
            self._data_helper._upload_raw(df, EmFundNav.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def delete_em_fund_nav(self, start_date, end_date):
        try:
            RawDataApi().delete_em_fund_nav(start_date, end_date)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_fund_status(self, end_date: str, is_history: bool = True):
        try:
            if not is_history:
                fund_list = RawDataHelper.get_all_live_fund_list(end_date)
            else:
                # 获取全量基金列表
                fund_list = self._em_sector_wrapper('507010', end_date)
            if fund_list is None:
                print('[em_fund_status] failed to get fund list')
                return False

            data1 = self._em_css_wrapper(fund_list, 'PCHMINAMT,REDMMINAMT', f'EndDate={end_date},Ispandas=1')
            if data1 is None:
                print('failed to get fund status data1')
                return False
            data2 = self._em_css_wrapper(fund_list, 'PURCHSTATUS,REDEMSTATUS,LPLIMIT,OTCLPLIMITJG,TRADESTATUS', f'TradeDate={end_date},SHAREOBJECT=1,Ispandas=1')
            if data2 is None:
                print('failed to get fund status data2')
                return False
            data3 = self._em_css_wrapper(fund_list, 'OTCLPLIMITJG', f'TradeDate={end_date},SHAREOBJECT=2,Ispandas=1')
            if data3 is None:
                print('failed to get fund status data3')
                return False

            df = data1.drop(columns='DATES').join(data2.drop(columns='DATES'), how='outer').join(data3.drop(columns='DATES').rename(columns={'OTCLPLIMITJG': 'OTCLPLIMITGR'}), how='outer')
            df = df[df.notna().any(axis=1)]
            if df.empty:
                return True
            df = df.reset_index()
            df['DATES'] = end_date
            if not is_history:
                # 获取当前的fund status
                now_df = RawDataApi().get_em_fund_status(end_date=end_date)
                if now_df is not None:
                    df = df.replace({None: np.nan}).infer_objects()
                    now_df = now_df.replace({None: np.nan}).infer_objects()
                    # 过滤出来新增基金status以及旧基金的status发生变化的情况
                    now_df = now_df.drop(columns=['_update_time']).sort_values(by=['CODES', 'DATES']).drop_duplicates(subset='CODES', keep='last')
                    # 这里由于存在未采用当前这种更新方式的历史数据，所以最后的validate需要是one_to_many
                    df = df.merge(now_df, how='left', on=['CODES', 'LPLIMIT', 'OTCLPLIMITJG', 'OTCLPLIMITGR', 'PURCHSTATUS', 'REDEMSTATUS', 'TRADESTATUS', 'PCHMINAMT', 'REDMMINAMT'], indicator=True, validate='one_to_many')
                    df = df[df._merge == 'left_only'].drop(columns=['_merge', 'DATES_y']).rename(columns={'DATES_x': 'DATES'})
            self._data_helper._upload_raw(df, EmFundStatus.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_fund_scale(self, end_date: str) -> bool:
        def _get_data_from_em(the_date, data1):
            # TODO: 这里其实应该用QANALNETSHARE，但目前QANALNETSHARE的值是错的
            data2 = self._em_css_wrapper(fund_list, 'UNITTOTAL', f'TradeDate={the_date},Ispandas=1')
            if data2 is None:
                print('[em_fund_scale] failed to get fund scale data2')
                return False, None
            df = data1.drop(columns='DATES').join(data2.drop(columns='DATES'), how='outer')
            df = df[df.notna().any(axis=1)]
            if df.empty:
                return True, None
            df['DATES'] = the_date
            df = df.reset_index().rename(columns=lambda x: EmFundScale.__getattribute__(EmFundScale, x).name)
            return None, df

        try:
            fund_list = RawDataHelper.get_all_live_fund_list(end_date)
            if fund_list is None:
                print('[em_fund_scale] failed to get fund list')
                return False
            real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
            data1 = self._em_css_wrapper(fund_list, 'QANALNETASSET', f'ReportDate={real_date},Ispandas=1')
            if data1 is None:
                print('[em_fund_scale] failed to get fund scale data1 (real_date)')
                return False
            ret, df = _get_data_from_em(real_date, data1)
            if ret is not None:
                return ret
            now_df = RawDataApi().get_em_fund_scale(start_date=real_date, end_date=real_date)
            if now_df is not None:
                df = df.replace({None: np.nan}).infer_objects()
                now_df = now_df.drop(columns=['_update_time']).replace({None: np.nan}).infer_objects()
                now_df = now_df.sort_values(by=['CODES', 'DATES']).drop_duplicates(subset='CODES', keep='last')
                # merge on all columns
                df = df.merge(now_df, how='left', indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            # TODO: 最好原子提交下边两步
            RawDataApi().delete_em_fund_scale(real_date, df.CODES.to_list())
            self._data_helper._upload_raw(df, EmFundScale.__table__.name)

            # extra data (not from financial report)
            data1 = self._em_css_wrapper(fund_list, 'FUNDSCALE', f'EndDate={end_date},Ispandas=1')
            if data1 is None:
                print('[em_fund_scale] failed to get fund scale data1 (end_date)')
                return False
            ret, df = _get_data_from_em(end_date, data1.rename(columns={'FUNDSCALE': 'QANALNETASSET'}))
            if ret is not None:
                return ret
            now_df = RawDataApi().get_em_fund_scale(start_date=real_date, end_date=end_date)
            if now_df is not None:
                df = df.replace({None: np.nan}).infer_objects()
                now_df = now_df.drop(columns=['_update_time']).replace({None: np.nan}).infer_objects()
                now_df = now_df.sort_values(by=['CODES', 'DATES']).drop_duplicates(subset='CODES', keep='last')
                # merge on all columns
                df = df.merge(now_df, how='left', on=['CODES', 'FUNDSCALE', 'UNITTOTAL'], indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge', 'DATES_y']).rename(columns={'DATES_x': 'DATES'})
            self._data_helper._upload_raw(df, EmFundScale.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def _do_cec(self, em_ids: Tuple[str]) -> Set[str]:
        invalid_ids = set()
        cec_result = c.cec(','.join(em_ids), 'ReturnType=0')
        for one in cec_result.Data.values():
            if not one[2]:
                invalid_ids.add(one[1])
        if invalid_ids:
            print(f'got invalid ids {invalid_ids} in {em_ids}')
        return invalid_ids

    def em_index_price(self, em_ids: Set[str], start_date, end_date):
        try:
            # 每次重刷N个交易日的数据
            tradedate = self._em_getdate_wrapper(start_date, -INDEX_PRICE_EXTRA_TRADE_DAYS)
            if tradedate is None:
                print(f'[em_index_price] failed to get trade dates (date){start_date}')
                return False
            start_date = pd.to_datetime(tradedate[0]).strftime('%Y%m%d')

            # 不支持跨品种的index同时请求，所以需要拆出来分开去做
            df_list = []
            # 利率部分
            ir_index = set()
            c_ir_index = ('LIGBP1M.IR', 'HIBOR3M.IR')
            for one in c_ir_index:
                try:
                    em_ids.remove(one)
                except KeyError:
                    continue
                ir_index.add(one)

            ir_index -= self._do_cec(c_ir_index)
            if ir_index:
                data = self._em_csd_wrapper(','.join(ir_index), "CLOSE", start_date, end_date, "period=1,adjustflag=1,curtype=1,order=1,market=CNSESH,Ispandas=1")
                if data is None:
                    print(f'[em_index_price] failed to get index price (index_id){ir_index}')
                else:
                    df_list.append(data)

            # 期货部分
            future_index = set()
            c_future_index = ('AU9999.SGE', 'AU0.SHF')
            for one in c_future_index:
                try:
                    em_ids.remove(one)
                except KeyError:
                    continue
                future_index.add(one)
            future_index -= self._do_cec(c_future_index)
            if future_index:
                data = self._em_csd_wrapper(','.join(future_index), "OPEN,HIGH,LOW,VOLUME,CLOSE,AMOUNT", start_date, end_date, "period=1,adjustflag=1,curtype=1,order=1,market=CNSESH,Ispandas=1")
                if data is None:
                    print(f'[em_index_price] failed to get index price (index_id){future_index}')
                else:
                    df_list.append(data)

            # 常规指数部分
            em_ids -= self._do_cec(em_ids)
            data = self._em_csd_wrapper(','.join(em_ids), "OPEN,HIGH,LOW,VOLUME,CLOSE,AMOUNT", start_date, end_date, "period=1,adjustflag=1,curtype=1,order=1,market=0,Ispandas=1")
            if data is None:
                print(f'[em_index_price] failed to get index price (index_id){em_ids}')
                return False

            df = pd.concat(df_list + [data]).reset_index().rename(columns={
                'CODES': 'em_id',
                'DATES': 'datetime',
                'CLOSE': 'close',
                'OPEN': 'open',
                'HIGH': 'high',
                'LOW': 'low',
                'VOLUME': 'volume',
                'AMOUNT': 'amount',
            })
            df = df[df['close'].notna()]
            # TODO: 最好可以原子提交下边两步操作
            RawDataApi().delete_em_index_price(list(em_ids | ir_index | future_index), start_date, end_date)
            self._data_helper._upload_raw(df, EmIndexPrice.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_index_info(self, index_ids: List[str]):
        try:
            data = self._em_css_wrapper(','.join(index_ids), 'SHORTNAME,NAME,PUBLISHDATE,MAKERNAME,INDEXPROFILE', 'Ispandas=1')
            if data is None:
                print('failed to get index info')
                return False

            df = data.drop(columns='DATES').reset_index().rename(columns=lambda x: EmIndexInfo.__getattribute__(EmIndexInfo, x).name)
            # 统一设置一个默认值，之后可以按需手工修改
            df['price_source'] = IndexPriceSource.default.name
            # 更新到db
            self._data_helper._upload_raw(df, EmIndexInfo.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_macroeconomic_price(self, start_date, end_date):
        try:
            index_info_df = RawDataApi().get_em_index_info()
            if index_info_df is None:
                print('failed to get index info for macroeconomic price')
                return False
            index_info_df = index_info_df[index_info_df.price_source == IndexPriceSource.macroeconomic]
            me_info = RawDataApi().get_em_macroeconomic_info()
            if me_info is None:
                print('failed to get me info for macroeconomic price')
                return False
            me_map = me_info.set_index('codes')['em_codes'].to_dict()
            me_map.update(self._MACROECONOMIC_MAP_I)
            macroeconomic_list = [me_map[one] for one in index_info_df.em_id.to_list() if one in me_map]
            for i in range(self._EM_RETRY_TIMES + 1):
                data = c.edb(','.join(macroeconomic_list), f'StartDate={start_date},EndDate={end_date},IsLatest=0,RowIndex=2,Ispandas=1')
                if not isinstance(data, pd.DataFrame):
                    if data.ErrorCode != 0:
                        if data.ErrorCode == 10000009:
                            print(f'no macroeconomic price data during {start_date} and {end_date}')
                            return True
                        print(f'failed to get macroeconomic price: {data.ErrorMsg}')
                else:
                    break
            else:
                return False

            df = data.reset_index().rename(columns={
                'CODES': 'em_id',
                'DATES': 'datetime',
                'RESULT': 'close'
            })
            df = df[df.close.notna()]
            me_map_v = me_info.set_index('em_codes')['codes'].to_dict()
            me_map_v.update(self._MACROECONOMIC_MAP)
            df['em_id'] = df['em_id'].map(me_map_v)
            # 更新到db
            self._data_helper._upload_raw(df, EmIndexPrice.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_realtime_index(self, em_ids: Set[str], data_start_time, to_save):
        try:
            # 不支持跨品种的index同时请求，所以需要拆出来分开去做
            df_list = []

            # 利率部分
            ir_index = []
            for one in ('LIGBP1M.IR', 'HIBOR3M.IR'):
                try:
                    em_ids.remove(one)
                except KeyError:
                    continue
                ir_index.append(one)

            # 期货部分
            future_index = []
            for one in ('AU9999.SGE', 'AU0.SHF'):
                try:
                    em_ids.remove(one)
                except KeyError:
                    continue
                future_index.append(one)

            # 常规指数部分
            data = self._em_csqsnapshot_wrapper(','.join(em_ids), 'Date,Time,Now', 'Ispandas=1')
            if data is None:
                print(f'[em_index_price] failed to get index price (index_id){em_ids}')
                return None
            df_list.append(data)

            # # 每两次 csqsnapshot 请求之间必须大于 3000 ms
            # # 暂不实时更新利率指数（需要更新时取消注释）
            # time.sleep(3.1)
            # if ir_index:
            #     data = c.csqsnapshot(','.join(ir_index), 'Date,Time,Now', 'Ispandas=1')
            #     if not isinstance(data, pd.DataFrame):
            #         if data.ErrorCode != 0:
            #             print(f'[em_index_price] failed to get index price: {data.ErrorMsg} (index_id){ir_index}')
            #         return False
            #     df_list.append(data)

            # # 暂不实时更新期货指数（需要更新时取消注释）
            # time.sleep(3.1)
            # if future_index:
            #     data = c.csqsnapshot(','.join(future_index), 'Date,Time,Now', 'Ispandas=1')
            #     if not isinstance(data, pd.DataFrame):
            #         if data.ErrorCode != 0:
            #             print(f'[em_index_price] failed to get index price: {data.ErrorMsg} (index_id){future_index}')
            #         return False
            #     df_list.append(data)

            df = pd.concat(df_list)
            df = df[df['DATE'] != 0]
            df = df[df['TIME'] != 0]
            df['datetime'] = df.apply(
                lambda x: datetime.datetime.strptime(f'{x["DATE"]}{x["TIME"]}', '%Y%m%d%H%M%S'),
                axis=1
            )
            if data_start_time:
                df = df[df['datetime'] > data_start_time]

            df = df.drop(columns=['DATES', 'DATE', 'TIME'])
            df = df.reset_index().rename(columns={
                'CODES': 'em_id',
                'NOW': 'price'
            })
            if to_save:
                try:
                    self._data_helper._upload_raw(df, EmRealtimeIndexPrice.__table__.name)
                except Exception as e:
                    print(e)
                    traceback.print_exc()
            return df

        except Exception as e:
            print(e)
            traceback.print_exc()
            return None

    # 从em客户端导出数据后读取并处理
    def em_stock_price_history(self, stock_price_file_dir: str):
        for index, filename in enumerate(os.listdir(stock_price_file_dir)):
            if not filename.endswith(".xls"):
                continue
            index += 1
            print(f'{index}: {filename}')
            stock_price = pd.concat(pd.read_excel(os.path.join(stock_price_file_dir, filename), sheet_name=None, na_values='--'),
                                    ignore_index=True)
            # 将列名字改为从API获取到数据时的列名字，便于后边统一处理
            stock_price = stock_price.drop(['简称'], axis=1).rename(columns={
                '代码': 'CODES',
                '时间': 'DATES',
                '开盘价(元)': 'OPEN',
                '收盘价(元)': 'CLOSE',
                '最高价(元)': 'HIGH',
                '最低价(元)': 'LOW',
                '前收盘价(元)': 'PRECLOSE',
                '均价(元)': 'AVERAGE',
                '成交量(股)': 'VOLUME',
                '成交金额(元)': 'AMOUNT',
                '换手率(%)': 'TURN',
                '交易状态': 'TRADESTATUS',
                '内盘成交量': 'BUYVOL',
                '外盘成交量': 'SELLVOL',
            })

            # 过滤掉个股未上市以及终止上市时的数据，以及日期为nan的行（表示整行为无效数据）
            stock_price = stock_price.loc[(stock_price['TRADESTATUS'] != '未上市') & (stock_price['TRADESTATUS'] != '终止上市')].loc[~stock_price['DATES'].isna()].rename(columns=lambda x: EmStockPrice.__getattribute__(EmStockPrice, x).name)
            # 更新到db
            self._data_helper._upload_raw(stock_price, EmStockPrice.__table__.name)

    def em_stock_price(self, start_date: str, end_date: str, stock_list: Tuple[str] = ()):
        try:
            # 获取区间内所有交易日
            tradedates = self._em_tradedates_wrapper(start_date, end_date, "period=1,order=1,market=CNSESH")
            if tradedates is None:
                print('[em_stock_price] failed to get trade dates')
                return False
            if len(tradedates) == 0:
                print(f'[em_stock_price] no trade dates, return immediately (start_date){start_date} (end_date){end_date}')
                return False

            df_list = []
            for date in tradedates:
                if not stock_list:
                    # 获取所有A股股票的ID, 功能函数-板块成分
                    # http://quantapi.eastmoney.com/Cmd/Sector?from=web
                    # 全部A股股票
                    stock_list = self._em_sector_wrapper('001004', date)
                    if stock_list is None:
                        print('[em_stock_price] failed to get stock id list')
                        return False
                    extra_stock_list = self._em_sector_wrapper('001020', date)
                    if extra_stock_list is None:
                        print('[em_stock_price] failed to get extra stock id list')
                    else:
                        stock_list += extra_stock_list

                # 获取个股股价信息
                temp_df = self._em_csd_wrapper(stock_list,
                                               'OPEN,CLOSE,HIGH,LOW,PRECLOSE,AVERAGE,VOLUME,AMOUNT,TURN,TRADESTATUS,TNUM,BUYVOL,SELLVOL',
                                               date, date, 'period=1,adjustflag=1,curtype=1,order=1,market=0,Ispandas=1')
                if temp_df is None:
                    print(f'failed to get stock price info (date){date}')
                    return False
                # 过滤掉个股未上市以及终止上市时的数据，以及日期为nan的行（表示整行为无效数据）
                filtered_df = temp_df.loc[(temp_df['TRADESTATUS'] != '未上市') & (temp_df['TRADESTATUS'] != '终止上市')].loc[~temp_df['DATES'].isna()]
                stocks_filtered = set(temp_df.index.unique()) - set(filtered_df.index.unique())
                print(f'[em_stock_price] stocks filtered: {stocks_filtered}')
                print(f'[em_stock_price] info of stocks filtered: {temp_df.loc[stocks_filtered, :]}')
                df_list.append(filtered_df)
                # print(f'{date} done')

            df = pd.concat(df_list).reset_index().rename(columns=lambda x: EmStockPrice.__getattribute__(EmStockPrice, x).name)
            # 更新到db
            self._data_helper._upload_raw(df, EmStockPrice.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    # 从em客户端导出数据后读取并处理
    def em_stock_post_price_history(self, stock_post_price_file_dir: str):
        for index, filename in enumerate(os.listdir(stock_post_price_file_dir)):
            if not filename.endswith(".xls"):
                continue
            index += 1
            print(f'{index}: {filename}')
            stock_price = pd.concat(pd.read_excel(os.path.join(stock_post_price_file_dir, filename), sheet_name=None, na_values='--'),
                                    ignore_index=True)
            # 将列名字改为从API获取到数据时的列名字，便于后边统一处理
            stock_price = stock_price.drop(['简称'], axis=1).rename(columns={
                '代码': 'CODES',
                '时间': 'DATES',
                '开盘价(元)': 'OPEN',
                '收盘价(元)': 'CLOSE',
                '最高价(元)': 'HIGH',
                '最低价(元)': 'LOW',
                '前收盘价(元)': 'PRECLOSE',
                '均价(元)': 'AVERAGE',
                '成交量(股)': 'VOLUME',
                '成交金额(元)': 'AMOUNT',
                '交易状态': 'TRADESTATUS',
            })
            # 过滤掉个股未上市以及终止上市时的数据，以及日期为nan的行（表示整行为无效数据）
            stock_price = stock_price.loc[(stock_price['TRADESTATUS'] != '未上市') & (stock_price['TRADESTATUS'] != '终止上市')].loc[~stock_price['DATES'].isna()].rename(columns=lambda x: EmStockPostPrice.__getattribute__(EmStockPostPrice, x).name)
            # 更新到db
            self._data_helper._upload_raw(stock_price, EmStockPostPrice.__table__.name)

    def em_stock_post_price(self, start_date: str, end_date: str, stock_list: Tuple[str] = ()):
        try:
            # 获取区间内所有交易日
            tradedates = self._em_tradedates_wrapper(start_date, end_date, "period=1,order=1,market=CNSESH")
            if tradedates is None:
                print('[em_stock_post_price] failed to get trade dates')
                return False
            if len(tradedates) == 0:
                print(f'[em_stock_post_price] no trade dates, return immediately (start_date){start_date} (end_date){end_date}')
                return False

            df_list = []
            for date in tradedates:
                if not stock_list:
                    # 获取所有A股股票的ID, 功能函数-板块成分
                    # http://quantapi.eastmoney.com/Cmd/Sector?from=web
                    # 全部A股股票
                    stock_list = self._em_sector_wrapper('001004', date)
                    if stock_list is None:
                        print('[em_stock_post_price] failed to get stock id list')
                        return False
                    extra_stock_list = self._em_sector_wrapper('001020', date)
                    if extra_stock_list is None:
                        print('[em_stock_post_price] failed to get extra stock id list')
                    else:
                        stock_list += extra_stock_list

                # 获取个股股价信息
                temp_df = self._em_csd_wrapper(stock_list,
                                               'OPEN,CLOSE,HIGH,LOW,PRECLOSE,AVERAGE,VOLUME,AMOUNT,TRADESTATUS,TAFACTOR',
                                               date, date, 'period=1,adjustflag=2,curtype=1,order=1,market=0,Ispandas=1')
                if temp_df is None:
                    print(f'failed to get stock price info (date){date}')
                    return False
                print(f'[em_stock_post_price] all stocks with post price {set(temp_df.index.unique())} (count){len(set(temp_df.index.unique()))}')
                stock_price = self._em_csd_wrapper(stock_list,
                                                   'OPEN,CLOSE,HIGH,LOW,PRECLOSE,AVERAGE,VOLUME,AMOUNT,TURN,TRADESTATUS,TNUM,BUYVOL,SELLVOL',
                                                   date, date, 'period=1,adjustflag=1,curtype=1,order=1,market=0,Ispandas=1')
                if stock_price is not None:
                    print(f'[em_stock_post_price] all stocks with price {set(stock_price.index.unique())} (count){len(set(stock_price.index.unique()))}')
                    print(f'[em_stock_post_price] lacked with stock post price {set(stock_price.index.unique()) - set(temp_df.index.unique())}')

                # 过滤掉个股未上市以及终止上市时的数据，以及日期为nan的行（表示整行为无效数据）
                filtered_df = temp_df.loc[(temp_df['TRADESTATUS'] != '未上市') & (temp_df['TRADESTATUS'] != '终止上市')].loc[~temp_df['DATES'].isna()]
                stocks_filtered = set(temp_df.index.unique()) - set(filtered_df.index.unique())
                print(f'[em_stock_post_price] stocks filtered: {stocks_filtered}')
                print(f'[em_stock_post_price] info of stocks filtered: {temp_df.loc[stocks_filtered, :]}')
                df_list.append(filtered_df)
                # print(f'{date} done')

            df = pd.concat(df_list).reset_index().rename(columns=lambda x: EmStockPostPrice.__getattribute__(EmStockPostPrice, x).name)
            # 更新到db
            self._data_helper._upload_raw(df, EmStockPostPrice.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_stock_info(self, end_date: str):
        try:
            # 获取所有A股股票的ID, 功能函数-板块成分
            # http://quantapi.eastmoney.com/Cmd/Sector?from=web
            # 全部A股股票
            stock_list = self._em_sector_wrapper('001004', end_date)
            if stock_list is None:
                print('[em_stock_info] failed to get stock id list')
                return False
            # 已摘牌股票
            delisted_stock_list = self._em_sector_wrapper('001015', end_date)
            if delisted_stock_list is None:
                print('[em_stock_info] failed to get delisted stock id list')
                return False
            new_stock_code = list(set(stock_list) | set(delisted_stock_list))

            # 去掉我们已经有的股票ID
            stock_info_df = RawDataApi().get_em_stock_info()
            if not new_stock_code:
                # 直接返回成功
                return True

            df_list: List[pd.DataFrame] = []
            # 获取无参数指标
            df_no_param = self._em_css_wrapper(new_stock_code,
                                               'NAME,LISTDATE,FINPURCHORNOT,FINSELLORNOT,STOHSTOCKCONNECTEDORNOT,SHENGUTONGTARGET,ENGNAME,COMPNAME,COMPNAMEENG,'
                                               'CAPUNCAPDATE,DELISTDATE,BCODE,BNAME,HCODE,HNAME,BACKDOOR,BACKDOORDATE',
                                               'Ispandas=1')
            if df_no_param is None:
                print('failed to get stock info(no param)')
                return False
            # 将其中'是'/'否'的结果转换为True/False
            columns = ['FINPURCHORNOT', 'FINSELLORNOT', 'STOHSTOCKCONNECTEDORNOT', 'SHENGUTONGTARGET', 'BACKDOOR']
            df_no_param.loc[:, columns] = df_no_param.loc[:, columns].apply(lambda x: x.apply(lambda x: True if x == '是' else False))
            df_list.append(df_no_param)

            # 获取行业分类共有三级的指标
            df_lv4 = self._em_css_wrapper(new_stock_code, "BLEMINDCODE,BLSWSINDCODE,SW2014CODE,EMINDCODE2016,CITICCODE2020", "ClassiFication=4,Ispandas=1")
            if df_lv4 is None:
                print('failed to get stock info(lv4)')
                return False
            df_list.append(df_lv4)

            # 获取行业分类共有二级的指标
            df_lv3 = self._em_css_wrapper(new_stock_code, "BLCSRCINDCODE,CSRCCODENEW", "ClassiFication=3,Ispandas=1")
            if df_lv3 is None:
                print('failed to get stock info(lv3)')
                return False
            df_list.append(df_lv3)

            # 获取行业分类共有四级的指标
            df_lv5 = self._em_css_wrapper(new_stock_code, "CSINDCODE2016,GICSCODE", "ClassiFication=5,Ispandas=1")
            if df_lv5 is None:
                print('failed to get stock info(lv5)')
                return False
            df_list.append(df_lv5)

            if df_list:
                # 将每部分按列粘到一起
                df = pd.concat(df_list, axis=1)
                df.index.name = 'CODES'
                # 不需要存日期的列，去除索引并做列名转换
                df = df.drop(columns='DATES').reset_index().rename(columns=lambda x: EmStockInfo.__getattribute__(EmStockInfo, x).name)
                # 更新新的股票到db
                new_id_df = df[df.stock_id.isin(set(df.stock_id).difference(set(stock_info_df.stock_id)))]
                self._data_helper._upload_raw(new_id_df, EmStockInfo.__table__.name)

            # 对比检查是否有股票名字改变的
            stock_info_old = stock_info_df.set_index('stock_id')['name'].to_dict()
            stock_info_new = df.set_index('stock_id')['name'].to_dict()
            stock_id_list = []
            for stock_id in stock_info_new:
                old_name  = stock_info_old.get(stock_id)
                new_name = stock_info_new.get(stock_id)
                if old_name != new_name:
                    stock_id_list.append(stock_id)

            change_stock_df = df[df.stock_id.isin(stock_id_list)].dropna(subset=['name'])
            if change_stock_df.shape[0] > 0:
                # 删除旧的
                RawDataApi().del_em_stock_info(stock_list=change_stock_df.stock_id.tolist())
                
                # 存新的
                self._data_helper._upload_raw(change_stock_df, EmStockInfo.__table__.name)

            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def add_columns_to_fin_fac(self, end_date: str):
        # 获取所有A股股票的ID, 功能函数-板块成分
        # http://quantapi.eastmoney.com/Cmd/Sector?from=web
        # 全部A股股票
        stock_id_result = c.sector('001004', end_date)
        if stock_id_result.ErrorCode != 0:
            print(f'failed to get stock id list: {stock_id_result.ErrorMsg}')
            return

        # 获取主营收入构成(按产品)
        df = c.css(stock_id_result.Codes, "BALANCESTATEMENT_195", f'ReportDate={end_date},type=1,Ispandas=1')
        if not isinstance(df, pd.DataFrame) and df.ErrorCode != 0:
            print(f'failed to get stock financial factors: {df.ErrorMsg}')
            return

        count = 0
        Session = sessionmaker(RawDatabaseConnector().get_engine())
        db_session = Session()
        for row in db_session.query(EmStockFinFac):
            if row.DATES != datetime.datetime.strptime(end_date, '%Y%m%d').date():
                continue
            if row.CODES in df.index:
                row.BALANCESTATEMENT_195 = df.at[row.CODES, 'BALANCESTATEMENT_195']
                count += 1
        db_session.commit()
        db_session.close()
        print(f'append {count} value(s) to fin fac table')

    def em_stock_fin_fac(self, end_date: str, stock_list: Optional[Tuple[str]] = None):
        try:
            real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
            if stock_list is None:
                # 获取所有A股股票的ID, 功能函数-板块成分
                # http://quantapi.eastmoney.com/Cmd/Sector?from=web
                # 全部A股股票
                # TODO: 每日更新写这个日期没问题，但补历史可能还要特殊处理一下这里
                stock_list = self._em_sector_wrapper('001004', end_date)
                if stock_list is None:
                    print('[em_stock_fin_fac] failed to get stock id list')
                    return False
            df_list: List[pd.DataFrame] = []
            # 获取无参数指标
            df_no_param = self._em_css_wrapper(stock_list,
                                               'EBIT,EBITDA,EXTRAORDINARY,LOWERDIANDNI,GROSSMARGIN,OPERATEINCOME,INVESTINCOME,EBITDRIVE,TOTALCAPITAL,WORKINGCAPITAL,\
                                                NETWORKINGCAPITAL,TANGIBLEASSET,RETAINED,INTERESTLIBILITY,NETLIBILITY,EXINTERESTCL,EXINTERESTNCL,FCFF,FCFE,DA,FCFFDRIVE,\
                                                PERFORMANCEEXPRESSPARENTNI,MBSALESCONS,GPMARGIN,NPMARGIN,EXPENSETOOR,INVTURNRATIO,ARTURNRATIO,ROEAVG,ROEWA,EPSBASIC,EPSDILUTED,\
                                                BPS,MBREVENUE,MBCOST', f'ReportDate={real_date},type=1,Ispandas=1')
            if df_no_param is None:
                print('failed to get stock financial factors (no_param)')
            else:
                df_no_param = df_no_param.drop(columns='DATES')
                df_list.append(df_no_param)

            df_no_param_part2 = self._em_css_wrapper(stock_list,
                                                     'STMTACTDATE,BALANCESTATEMENT_9,BALANCESTATEMENT_25,BALANCESTATEMENT_31,BALANCESTATEMENT_46,BALANCESTATEMENT_74,BALANCESTATEMENT_93,BALANCESTATEMENT_103,\
                                                      BALANCESTATEMENT_128,BALANCESTATEMENT_140,BALANCESTATEMENT_141,BALANCESTATEMENT_195,BALANCESTATEMENT_196,INCOMESTATEMENT_9,INCOMESTATEMENT_14,INCOMESTATEMENT_48,\
                                                      INCOMESTATEMENT_56,INCOMESTATEMENT_60,INCOMESTATEMENT_61,INCOMESTATEMENT_83,INCOMESTATEMENT_85,INCOMESTATEMENT_127,\
                                                      CASHFLOWSTATEMENT_9,CASHFLOWSTATEMENT_39,CASHFLOWSTATEMENT_59,CASHFLOWSTATEMENT_70,CASHFLOWSTATEMENT_77,CASHFLOWSTATEMENT_82,CASHFLOWSTATEMENT_86,CASHFLOWSTATEMENT_87,\
                                                      CASHFLOWSTATEMENT_88,CASHFLOWSTATEMENT_89', f'ReportDate={real_date},type=1,Ispandas=1')
            if df_no_param_part2 is None:
                print('failed to get stock financial factors (no_param part2)')
            else:
                df_no_param_part2 = df_no_param_part2.drop(columns='DATES')
                df_list.append(df_no_param_part2)

            # 获取主营收入构成(按产品)
            df_mb_sales_cons = self._em_css_wrapper(stock_list, "MBSALESCONS", f'ReportDate={real_date},type=2,Ispandas=1')
            if df_mb_sales_cons is None:
                print('failed to get stock financial factors (mb_sales_cons)')
            else:
                df_mb_sales_cons = df_mb_sales_cons.drop(columns='DATES')
                df_list.append(df_mb_sales_cons.rename(columns={'MBSALESCONS': 'MBSALESCONS_P'}))

            # 获取合并报表(调整)数据
            df_combined_with_adj = self._em_css_wrapper(stock_list, "BALANCESTATEMENT_141", f'ReportDate={real_date},type=3,Ispandas=1')
            if df_combined_with_adj is None:
                print('failed to get stock financial factors (combined_with_adj)')
            else:
                df_combined_with_adj = df_combined_with_adj.drop(columns='DATES')
                df_list.append(df_combined_with_adj.rename(columns={'BALANCESTATEMENT_141': 'BALANCESTATEMENT_141_ADJ'}))

            # 获取归属于上市公司股东的扣除非经常性损益后的净利润(调整前)
            df_with_param_1 = self._em_css_wrapper(stock_list, "DEDUCTEDINCOME", f'ReportDate={real_date},DataAdjustType=1,Ispandas=1')
            if df_with_param_1 is None:
                print('failed to get stock financial factors (with_param_1)')
            else:
                df_with_param_1 = df_with_param_1.drop(columns='DATES')
                df_list.append(df_with_param_1.rename(columns={'DEDUCTEDINCOME': 'DEDUCTEDINCOME_BA'}))

            # 获取归属于上市公司股东的扣除非经常性损益后的净利润(调整后)
            df_with_param_2 = self._em_css_wrapper(stock_list, "DEDUCTEDINCOME", f'ReportDate={real_date},DataAdjustType=2,Ispandas=1')
            if df_with_param_2 is None:
                print('failed to get stock financial factors (with_param_2)')
            else:
                df_with_param_2 = df_with_param_2.drop(columns='DATES')
                df_list.append(df_with_param_2.rename(columns={'DEDUCTEDINCOME': 'DEDUCTEDINCOME_AA'}))

            # 获取TTM指标
            df_ttm = self._em_css_wrapper(stock_list, 'GRTTMR,GCTTMR,ORTTMR,OCTTMR,EXPENSETTMR,GROSSMARGINTTMR,OPERATEEXPENSETTMR,ADMINEXPENSETTMR,FINAEXPENSETTMR,IMPAIRMENTTTMR,\
                                                       OPERATEINCOMETTMR,INVESTINCOMETTMR,OPTTMR,NONOPERATEPROFITTTMR,EBITTTMR,EBTTTMR,TAXTTMR,PNITTMR,KCFJCXSYJLRTTMR,\
                                                       NPTTMRP,FVVPALRP,IRTTMRP,IITTMFJVAJVRP,BTAATTMRP,SALESCASHINTTMR,CFOTTMR,CFITTMR,CFFTTMR,CFTTMR,CAPEXR',
                                                       f'ReportDate={real_date},Ispandas=1')
            if df_ttm is None:
                print('failed to get stock financial factors (ttm)')
            else:
                df_ttm = df_ttm.drop(columns='DATES')
                df_list.append(df_ttm)

            if len(df_list) > 0:
                # 将每部分按列粘到一起
                df = pd.concat(df_list, axis=1)
                df = df[df.notna().any(axis=1)]
                if df.empty:
                    return True
                # 日期列修改为real_date
                df.loc[:, 'DATES'] = real_date
                df.loc[:, 'STMTACTDATE'] = pd.to_datetime(df.STMTACTDATE, infer_datetime_format=True).dt.date
                df = df.reset_index().rename(columns=lambda x: EmStockFinFac.__getattribute__(EmStockFinFac, x).name)
                now_df = RawDataApi().get_em_stock_fin_fac(start_date=real_date, end_date=real_date)
                if now_df is not None:
                    now_df = now_df.drop(columns=['_update_time']).sort_values(by=['stock_id', 'datetime']).drop_duplicates(subset='stock_id', keep='last')
                    df = df.astype(now_df.dtypes.to_dict())
                    # merge on all columns
                    df = df.merge(now_df, how='left', indicator=True, validate='one_to_one')
                    df = df[df._merge == 'left_only'].drop(columns=['_merge'])
                # TODO: 最好原子提交下边两步
                RawDataApi().delete_em_stock_fin_fac(real_date, df.stock_id.to_list())
                # 更新到db
                self._data_helper._upload_raw(df, EmStockFinFac.__table__.name)
                return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    # 从em客户端导出数据后读取并处理
    def em_stock_daily_info_history(self, stock_daily_info_file_dir: str):
        for index, filename in enumerate(os.listdir(stock_daily_info_file_dir)):
            if not filename.endswith(".xls"):
                continue
            index += 1
            print(f'{index}: {filename}')
            for stock_daily_info in pd.read_excel(os.path.join(stock_daily_info_file_dir, filename), sheet_name=None, na_values='--').values():
                # 将列名字改为从API获取到数据时的列名字，便于后边统一处理
                stock_daily_info = stock_daily_info.drop(['简称'], axis=1).rename(columns={
                    '代码': 'CODES',
                    '时间': 'DATES',
                    '总股本(股)': 'TOTALSHARE',
                    'A股流通股本(股)': 'LIQSHARE',
                })

                stock_daily_info = stock_daily_info.loc[~stock_daily_info['DATES'].isna()].rename(columns=lambda x: EmStockDailyInfo.__getattribute__(EmStockDailyInfo, x).name)
                # stock_daily_info = stock_daily_info.set_index(['stock_id', 'datetime'])

                # print('done, to commit')
                # Session = sessionmaker(RawDatabaseConnector().get_engine())
                # db_session = Session()
                # for row in db_session.query(EmStockDailyInfo).filter(EmStockDailyInfo.CODES.in_(stock_daily_info.index.get_level_values(0).to_list())).all():
                #     try:
                #         date = row.DATES.isoformat()
                #         row.LIQSHARE = float(stock_daily_info.at[(row.CODES, date), 'liq_share'])
                #     except KeyError:
                #         print(row.CODES, date)
                # db_session.commit()
                # db_session.close()
                # 更新到db
                self._data_helper._upload_raw(stock_daily_info, EmStockDailyInfo.__table__.name)

    def em_stock_daily_info(self, start_date: str, end_date: str, predict_year: int = 0, stock_list: Tuple[str] = ()):
        try:
            # 获取区间内所有交易日
            tradedates = self._em_tradedates_wrapper(start_date, end_date, "period=1,order=1,market=CNSESH")
            if tradedates is None:
                print('[em_stock_daily_info] failed to get trade dates')
                return False
            if len(tradedates) == 0:
                print(f'[em_stock_daily_info] no trade dates, return immediately (start_date){start_date} (end_date){end_date}')
                return False

            if not stock_list:
                # 获取所有A股股票的ID, 功能函数-板块成分
                # http://quantapi.eastmoney.com/Cmd/Sector?from=web
                # 全部A股股票
                stock_list = self._em_sector_wrapper('001004', end_date)
                if stock_list is None:
                    print('[em_stock_daily_info] failed to get stock id list')
                    return False
                extra_stock_list = self._em_sector_wrapper('001020', end_date)
                if extra_stock_list is None:
                    print('[em_stock_price] failed to get extra stock id list')
                else:
                    stock_list += extra_stock_list

            if predict_year == 0:
                predict_year = datetime.datetime.strptime(end_date, '%Y%m%d').date().year

            df_list = []
            for date in tradedates:
                temp_df = self._em_css_wrapper(stock_list,
                                               'TOTALSHARE,LIQSHARE,HOLDFROZENAMTACCUMRATIO,PETTMDEDUCTED,PBLYRN,PSTTM,AHOLDER,ESTPEG,SHAREHDPCT,EVWITHOUTCASH',
                                               f'EndDate={date},TradeDate={date},PREDICTYEAR={predict_year},Ispandas=1')
                if temp_df is None:
                    print(f'failed to get stock daily info (date){date}')
                    return False
                # 日期列修改为end_date
                temp_df.loc[:, 'DATES'] = date
                df_list.append(temp_df)

            df = pd.concat(df_list).reset_index().rename(columns=lambda x: EmStockDailyInfo.__getattribute__(EmStockDailyInfo, x).name)
            # 更新到db
            self._data_helper._upload_raw(df, EmStockDailyInfo.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_stock_refinancing(self, start_date: str, end_date: str):
        try:
            indicators = 'SECURITYCODE,APPROVENOTICEDATE,PLANNOTICEDDATE,NEWPROGRESS,ISSUEOBJECT,SUMFINA_T,PRICEPRINCIPLE,ATTACHNAME,ADDPURPOSE'
            data = self._em_ctr_wrapper("AdditionPlanInfo", indicators,
                                        f"DateType=1,StartDate={start_date},EndDate={end_date},Process=0")
            if data is None:
                print(f'failed to get stock refinancing info')
                return False

            infos: List[List] = []
            for v in data.values():
                # if v[3] in ('董事会批准', '董事会修改', '董事会终止', '股东大会批准', '股东大会修改'):
                #    continue
                infos.append(v)
            df = pd.DataFrame(infos, columns=indicators.split(','))
            df = df[df.SECURITYCODE.notna()]
            self._data_helper._upload_raw(df.rename(columns=lambda x: EmStockRefinancing.__getattribute__(EmStockRefinancing, x).name), EmStockRefinancing.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_stock_refinancing_impl(self, start_date: str, end_date: str):
        try:
            indicators = 'MSECUCODE,DAT_FAXINGRIQI,DAT_SHANGSHIRIQI,NOTICEDATE,PRICEPRINCIPLE,ISSUEOBJECT,ISSUEPRICE,DEC_SHAREISSUED,SUMFINAPLAN,ATTACHNAME,DATE,ZFZZGBBL'
            data = self._em_ctr_wrapper("AddImplementInfo", indicators,
                                        f"DateType=1,StartDate={start_date},EndDate={end_date}")
            if data is None:
                print(f'failed to get stock refinancing impl')
                return False

            infos: List[List] = []
            for v in data.values():
                # if v[3] in ('董事会批准', '董事会修改', '董事会终止', '股东大会批准', '股东大会修改'):
                #    continue
                infos.append(v)
            df = pd.DataFrame(infos, columns=indicators.split(','))
            df = df[df.MSECUCODE.notna()]
            self._data_helper._upload_raw(df.rename(columns=lambda x: EmStockRefinancingImpl.__getattribute__(EmStockRefinancingImpl, x).name), EmStockRefinancingImpl.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_stock_estimate_fac(self, start_date: str, end_date: str, predict_year: int = 0):
        try:
            # 获取区间内所有交易日
            df = RawDataApi().get_em_tradedates(start_date, end_date)
            if df is None or df.shape[0] == 0:
                print(f'[em_stock_estimate_fac] no trade dates, return immediately (start_date){start_date} (end_date){end_date}')
                return False

            # 获取所有A股股票的ID, 功能函数-板块成分
            # http://quantapi.eastmoney.com/Cmd/Sector?from=web
            # 全部A股股票
            stock_list = self._em_sector_wrapper('001004', end_date)
            if stock_list is None:
                print('[em_stock_estimate_fac] failed to get stock id list')
                return False

            if predict_year == 0:
                predict_year = datetime.datetime.strptime(end_date, '%Y%m%d').date().year + 1

            df_list = []
            for date in df.TRADEDATES:
                temp_df = self._em_css_wrapper(stock_list,
                                               'ESTGR,ESTNI',
                                               f'EndDate={date},PREDICTYEAR={predict_year},Ispandas=1')
                if temp_df is None:
                    print(f'failed to get stock estimate fac (date){date}')
                    return False
                # 日期列修改为end_date
                temp_df.loc[:, 'DATES'] = date
                df_list.append(temp_df)

            df = pd.concat(df_list).reset_index().rename(columns=lambda x: EmStockEstimateFac.__getattribute__(EmStockEstimateFac, x).name)
            df = df[df.notna().any(axis=1)]
            df['predict_year'] = predict_year
            # 更新到db
            self._data_helper._upload_raw(df, EmStockEstimateFac.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_index_val_history(self, start_date: str, end_date: str, index_list: Tuple[str] = ()):
        if not index_list:
            index_list_df = RawDataApi().get_em_index_val(start_date, end_date)
            if index_list_df is None:
                print(f'[em_index_val_history] get index list failed (start_date){start_date} (end_date){end_date}')
                return
            index_list = tuple(index_list_df.em_id.unique())
        # 获取区间内所有交易日
        trade_day_df = RawDataApi().get_em_tradedates(start_date, end_date)
        if trade_day_df is None or trade_day_df.shape[0] == 0:
            print(f'[em_index_val_history] no trade dates, return immediately (start_date){start_date} (end_date){end_date}')
            return

        # 这里不直接把start_date, end_date传进去只调一次csd也是有道理的，因为那样的话数据量太大 接口总超时。。
        df_list: List[pd.DataFrame] = []
        # 一天一天地获取
        for date in trade_day_df.TRADEDATES:
            data1 = self._em_csd_wrapper(index_list,
                                         "PETTM,PBMRQ,PSTTM,PCFTTM,ROE,EPSTTM,MV,LIQMV,FREELIQMV",
                                         date, date,
                                         "DelType=1,period=1,adjustflag=1,curtype=1,order=1,market=0,Ispandas=1")
            if data1 is None:
                print(f'failed to get index val history info1 (date){date}')
                break
            data2 = self._em_csd_wrapper(index_list,
                                         "PETTM",
                                         date, date,
                                         "DelType=2,period=1,adjustflag=1,curtype=1,order=1,market=0,Ispandas=1")
            if data2 is None:
                print(f'failed to get index val history info2 (date){date}')
                break
            data2 = data2.rename(columns={'PETTM': 'PETTM_NN'})

            _y = pd.to_datetime(date).date().year + 1
            another_data = self._em_css_wrapper(index_list, "ESTPEG,DIVIDENDRATETTM", f"TradeDate={date},PREDICTYEAR={_y},Ispandas=1")
            if another_data is None:
                break
            another_data['DIVIDENDRATETTM'] /= 100
            df_list.append(data1.join([data2.drop(columns='DATES'), another_data.drop(columns='DATES')], how='outer'))
            print(f'{date} done')

        if df_list:
            if len(df_list) == 1:
                df = df_list[0]
            else:
                df = pd.concat(df_list)
            df = df[df.drop(columns=['DATES']).notna().any(axis=1)]
            df = df.reset_index().rename(columns=lambda x: EmIndexVal.__getattribute__(EmIndexVal, x).name)
            self._data_helper._upload_raw(df, EmIndexVal.__table__.name)

    def em_index_val(self, start_date: str, end_date: str):
        try:
            # 获取区间内所有交易日
            start_date = datetime.datetime.strptime(start_date, '%Y%m%d') - datetime.timedelta(days=INDEX_VAL_EXTRA_TRADE_DAYS)
            start_date = start_date.strftime('%Y%m%d')
            trade_day_df = RawDataApi().get_em_tradedates(start_date, end_date)
            if trade_day_df is None or trade_day_df.shape[0] == 0:
                print(f'[em_index_val] no trade dates, return immediately (start_date){start_date} (end_date){end_date}')
                return False

            # 获取basic table中index_info信息
            index_info_df = BasicDataApi().get_index_info()
            if index_info_df is None:
                print(f'[em_index_val] get index info failed')
                return False
            em_indexes = index_info_df[index_info_df.tag_method.isin(['PE百分位', 'PB百分位', 'PS百分位'])].em_id
            # 过滤掉几个特殊指数
            em_indexes = em_indexes[em_indexes.notna() & ~em_indexes.isin(['LIGBP1M.IR', 'HIBOR3M.IR', 'AU9999.SGE', 'AU0.SHF'])]
            index_list = em_indexes.to_list()
            if self._index_block_list is not None:
                index_list = list(set(index_list) - self._index_block_list)
            if not index_list:
                print(f'[em_index_val] empty index list, return immediately')
                return False

            print(f'[em_index_val] index count: {len(index_list)}')
            # index_split_point = len(index_list) // 2
            STEP_LEN = 100
            df_list: List[pd.DataFrame] = []
            # 一天一天地获取
            for date in trade_day_df.TRADEDATES:
                # 分成两部分去获取，以降低可能因为单条请求数据量较大导致出现超时错误
                for index in range(0, len(index_list), STEP_LEN):
                    index_list_part = index_list[index:index+STEP_LEN]
                    # index_list_part = list(set(index_list_part) - set(['H21573.CSI']))
                    # if not index_list_part:
                    #     continue
                    data1 = self._em_csd_wrapper(index_list_part,
                                                 "PETTM,PBMRQ,PSTTM,PCFTTM,ROE,EPSTTM,MV,LIQMV,FREELIQMV",
                                                 date, date,
                                                 "DelType=1,period=1,adjustflag=1,curtype=1,order=1,market=0,Ispandas=1")
                    if data1 is None:
                        print(f'failed to get index val info1 (date){date}')
                        break
                    data2 = self._em_csd_wrapper(index_list_part,
                                                 "PETTM",
                                                 date, date,
                                                 "DelType=2,period=1,adjustflag=1,curtype=1,order=1,market=0,Ispandas=1")
                    if data2 is None:
                        print(f'failed to get index val info2 (date){date}')
                        break
                    data2 = data2.rename(columns={'PETTM': 'PETTM_NN'})

                    # 实际上更容易出现超时错误的是下边这个css请求
                    _y = pd.to_datetime(date).date().year + 1
                    another_data = self._em_css_wrapper(index_list_part, "DIVIDENDRATETTM,ESTPEG", f"TradeDate={date},PREDICTYEAR={_y},Ispandas=1")
                    if another_data is None:
                        print(f'failed to get index val info part 2 (date){date}')
                        break
                    # 这里除以100与股息率历史数据保持单位一致
                    another_data['DIVIDENDRATETTM'] /= 100
                    df_list.append(data1.join([data2.drop(columns='DATES'), another_data.drop(columns='DATES')], how='outer'))
                print(f'{date} done')

            if df_list:
                if len(df_list) == 1:
                    df = df_list[0]
                else:
                    df = pd.concat(df_list)
                df = df[df.drop(columns='DATES').notna().any(axis=1)]
                df = df.rename_axis(index='CODES').reset_index().rename(columns=lambda x: EmIndexVal.__getattribute__(EmIndexVal, x).name)
                RawDataApi().delete_em_index_val(list(df.em_id.unique()), start_date, end_date)
                self._data_helper._upload_raw(df, EmIndexVal.__table__.name)
                return True
            else:
                return False
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_tradedates(self, start_date, end_date, is_automatic_update=True):
        try:
            if is_automatic_update:
                # 如果是每日自动更新，我们需要去存T+1日的数据，这里保险起见多取30天的
                end_date_dt: datetime.datetime = datetime.datetime.strptime(end_date, '%Y%m%d')
                extra_end_date = (end_date_dt + datetime.timedelta(days=30)).strftime('%Y%m%d')
            else:
                extra_end_date = end_date
            # 这里确保返回结果按日期升序排序
            tradedates = self._em_tradedates_wrapper(start_date, extra_end_date, "period=1,order=1,market=CNSESH")
            if tradedates is None:
                print('[em_tradedates] failed to get trade dates')
                return False

            if is_automatic_update:
                # 如果是每日自动更新，看一下返回的第一个日期是否是start_date，如果不是，表明今天不是交易日
                start_date_dt: datetime.datetime = pd.to_datetime(start_date, infer_datetime_format=True)
                if start_date_dt != pd.to_datetime(tradedates[0], infer_datetime_format=True):
                    print(f'today {start_date} is not a trading day')
                    return False

            df = pd.DataFrame(tradedates, columns=['TRADEDATES'])
            if is_automatic_update:
                # 如果是每日自动更新，向DB中insert T+1日的日期
                df = df.iloc[[1], :]
            self._data_helper._upload_raw(df, EmTradeDates.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_index_component(self, start_date: str, end_date: str):
        try:
            index_info = BasicDataApi().get_index_info()

            date_list = self._get_date_list(start_date, end_date)
            s_list: List[pd.Series] = []
            for row in index_info[~index_info['em_plate_id'].isna()].loc[:, ['index_id', 'em_id', 'em_plate_id']].itertuples(index=False):
                for date in date_list:
                    stock_list = self._em_sector_wrapper(row.em_plate_id, date)
                    if stock_list is None:
                        print(f'[em_index_component] failed to get stock id list (date){date} (em_plate_id){row.em_plate_id}')
                        continue
                    if len(stock_list) != 0:
                        s_list.append(pd.Series(row._asdict()).append(pd.Series({'datetime': date, 'stock_list': ','.join(stock_list)})))
            # 更新到db
            self._data_helper._upload_raw(pd.DataFrame(s_list), EmIndexComponent.__table__.name)

            # 在这里也插一条中证指数的成分数据
            em_id = '905009'
            csi_index_list = self._em_sector_wrapper(em_id, end_date)
            if csi_index_list is None:
                print(f'[em_index_component] failed to get data of sector csi index (em_id){em_id}')
                return False
            prev_index_comp_df = RawDataApi().get_em_index_component(index_list=[ALL_CSI_INDEX_INNER_NAME])
            if prev_index_comp_df is not None:
                prev_index_list = set(prev_index_comp_df.stock_list.array[-1].split(','))
                # 上一天的数据 - 今天的数据 = 失效的指数，但是我们这里只处理了中证指数
                self._index_block_list = prev_index_list - set(csi_index_list)
                if self._index_block_list:
                    print(f'[WARNING]!! these indexes become invalid: {self._index_block_list}')
            self._data_helper._upload_raw(pd.DataFrame([{'index_id': ALL_CSI_INDEX_INNER_NAME, 'datetime': end_date,
                                                         'em_id': em_id, 'em_plate_id': em_id, 'stock_list': ','.join(csi_index_list)}]), EmIndexComponent.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    @staticmethod
    def _lambda_func_index_component_1(x: pd.Series):
        value: List[Dict[str, str]] = json.loads(x)
        new_value = []
        for one in value:
            one = (*one.keys(), float(*one.values()))
            new_value.append(one)
        new_value.sort(key=itemgetter(1), reverse=True)
        return json.dumps(new_value)

    @staticmethod
    def _lambda_func_index_component_2(em_id_map: Dict[str, str], x: pd.Series):
        try:
            return em_id_map[x]
        except KeyError:
            return x

    @staticmethod
    def _lambda_func_index_component_3(x: pd.Series):
        value: List[Dict[str, str]] = json.loads(x)
        new_value = []
        for one in value:
            one = [*one.keys(), float(*one.values())]
            if one[0][0] in ('0', '3'):
                one[0] += '.SZ'
            elif one[0][0] in ('6'):
                one[0] += '.SH'
            new_value.append(one)
        new_value.sort(key=itemgetter(1), reverse=True)
        return json.dumps(new_value)

    @staticmethod
    def _lambda_func_index_component_4(x: pd.Series):
        if pd.isnull(x):
            return x
        return json.dumps([one + '.OF' for one in x.array])

    def cs_index_component(self, date: str):
        try:
            em_id_list = BasicDataApi().get_index_info().em_id.to_list()

            # 中证指数爬下来的部分
            columns_list = ['id', 'name', 'num', 'id_cat', 'sector', 'top10', 'related_funds']
            df_list: List[pd.DataFrame] = []
            for cat in ('industry', 'topic', 'strat', 'cap'):
                raw_df = pd.read_excel(f'./data/Index/{cat}_data.xlsx', na_values='--')
                df_list.append(raw_df[columns_list])

            df = pd.concat(df_list)
            df['id'] = df['id'].transform(lambda x: EmRawDataDownloader._lambda_func_index_component_2({em_id.split('.')[0]: em_id for em_id in em_id_list if em_id is not None}, x))
            df['id_cat'] = df['id_cat'].map({'行业': SectorType.industry.name, '主题': SectorType.topic.name, '策略': SectorType.strategy.name, '规模': SectorType.scale.name})
            df['sector'] = df['sector'].transform(EmRawDataDownloader._lambda_func_index_component_1)
            df['top10'] = df['top10'].transform(EmRawDataDownloader._lambda_func_index_component_3)
            df = df.rename(columns={'id': 'index_id'})
            # Choice中指数的全部成分及权重
            # 该表主要提供指定日期的指数成分股代码及权重等信息
            choice_data = defaultdict(list)
            for em_id in df['index_id'].to_list():
                data = self._em_ctr_wrapper("INDEXCOMPOSITION", "SECUCODE,NAME,WEIGHT", f"IndexCode={em_id},EndDate={date}")
                if data is None:
                    print(f'[cs_index_component] failed to get data (em_id){em_id}')
                    continue
                if data:
                    for constituent in data.values():
                        choice_data[em_id].append((constituent[0], round(constituent[2] * 100, 2)))
                    choice_data[em_id].sort(key=itemgetter(1), reverse=True)
                    choice_data[em_id] = json.dumps(choice_data[em_id])

            df['datetime'] = date
            df = df.set_index('index_id').assign(all_constitu=pd.Series(choice_data))
            # 更新到db
            self._data_helper._upload_raw(df.drop(columns='name').reset_index(), CSIndexComponent.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return

    def em_fund_list(self, start_date: str, end_date: str):
        try:
            # 这两个成分只能取到最新的，所以直接用end_date即可，没必要遍历
            # 获取所有基金列表（不包含未成立、已到期）
            live_fund_list = self._em_sector_wrapper('507013', end_date)
            if live_fund_list is None:
                print('[em_fund_list] failed to get live fund list')
                return False

            # 获取已摘牌基金列表
            delisted_fund_list = self._em_sector_wrapper('507022', end_date)
            if delisted_fund_list is None:
                print('[em_fund_list] failed to get delisted fund list')
                return False

            df = pd.DataFrame({'datetime': [end_date], 'all_live_fund_list': [','.join(live_fund_list)],
                               'delisted_fund_list': [','.join(delisted_fund_list)]})
            # 更新到db
            self._data_helper._upload_raw(df, EmFundList.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return

    def _em_get_all_fund_list(self, date: str):
        # 获取全部基金
        all_fund = c.sector('507013', date)
        if all_fund.ErrorCode != 0:
            print(f'failed to get all fund list: {all_fund.ErrorMsg}')
            return

        # 获取全部基金列表（含未成立、已到期）
        all_fund_extra_full = c.sector('507010', date)
        if all_fund_extra_full.ErrorCode != 0:
            print(f'failed to get all fund list: {all_fund_extra_full.ErrorMsg}')
            return

        # 获取全部基金列表（含未成立）
        all_fund_extra = c.sector('507009', date)
        if all_fund_extra.ErrorCode != 0:
            print(f'failed to get all fund list: {all_fund_extra.ErrorMsg}')
            return

        # 不应该保存未成立基金的数据，这里我们需要(全部 + (含未成立、已到期 - 含未成立))
        all_fund_list = set(all_fund.Codes)
        all_fund_extra_full_list = set(all_fund_extra_full.Codes)
        all_fund_extra_list = set(all_fund_extra.Codes)
        all_fund_list.update(all_fund_extra_full_list.difference(all_fund_extra_list))
        return all_fund_list

    def em_fund_info_history(self, date: str):
        fund_list = self._em_get_all_fund_list(date)
        if fund_list is None:
            return

        # 更新wind_fund_info中没有的数据
        wind_df = RawDataApi().get_wind_fund_info()
        self.em_fund_info(fund_list.difference(wind_df.wind_id))

    def em_fund_info(self, fund_id_list: Set[str]):
        if not fund_id_list:
            return True
        try:
            data = self._em_css_wrapper(','.join(fund_id_list), 'NAME,FNAME,FUNDTYPE,FOUNDDATE,MATURITYDATE,FIRSTINVESTTYPE,SECONDINVESTTYPE,TRADECUR,STRUCFUNDORNOT,GFCODEM,PREDFUNDMANAGER,MGRCOMP,'
                                                                'CUSTODIANBANK,FOREIGNCUSTODIAN,FRONTENDFEECODE,BACKENDFEECODE,ARCODEIN,RISKLEVEL', 'Ispandas=1')
            if data is None:
                print('failed to get fund info')
                return False

            data['FUNDTYPE'] = data['FUNDTYPE'].map(lambda x: True if x == '契约型开放式' else False)
            data['STRUCFUNDORNOT'] = data['STRUCFUNDORNOT'].map(lambda x: True if x == '是' else False)
            df = data.drop(columns='DATES').reset_index().rename(columns=lambda x: EmFundInfo.__getattribute__(EmFundInfo, x).name)
            # 更新到db，先删再添，确保数据不会冲突，且有一个更新的机会
            # TODO: 最好原子提交下边两个操作
            RawDataApi().delete_em_fund_info(df.em_id.to_list())
            self._data_helper._upload_raw(df, EmFundInfo.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_fund_fee_history(self, date: str):
        fund_list = self._em_get_all_fund_list(date)
        if fund_list is None:
            return
        self.em_fund_fee(fund_list)

    def _lambda_fund_fee_1(self, x):
        if x.CODEFEEMODE.array[0] == CodeFeeMode.none:
            fee_type = 1
        else:
            fee_type = x.CODEFEEMODE.array[0].value
        data = self._em_css_wrapper(','.join(x.index.to_list()), 'MANAGFEERATIO,CUSTODIANFEERATIO,PURCHFEERATIO,REDEMFEERATIO,SERVICEFEERATIO,SUBSCRFEERATIO', f'FeeType={fee_type},Ispandas=1')
        if data is None:
            print('failed to get fund code fee')
            return
        return data

    def em_fund_fee(self, fund_id_list: Set[str]):
        if not fund_id_list:
            return True
        try:
            data = self._em_css_wrapper(','.join(fund_id_list), 'CODEFEEMODE', 'Ispandas=1')
            if data is None:
                print('failed to get fund code fee mode')
                return False
            data['CODEFEEMODE'] = data['CODEFEEMODE'].map({'前端': CodeFeeMode.a_type, '后端': CodeFeeMode.b_type, None: CodeFeeMode.none})
            data = data.groupby(by='CODEFEEMODE', sort=False).apply(self._lambda_fund_fee_1).reset_index()
            data['CODEFEEMODE'] = data['CODEFEEMODE'].transform(lambda x: CodeFeeMode(x).name)
            df = data.drop(columns='DATES').rename(columns=lambda x: EmFundFee.__getattribute__(EmFundFee, x).name)
            # 更新到db，先删再添，确保数据不会冲突，且有一个更新的机会
            # TODO: 最好原子提交下边两个操作
            RawDataApi().delete_em_fund_fee(df.em_id.to_list())
            self._data_helper._upload_raw(df, EmFundFee.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_fund_benchmark_history(self, start_date: str, end_date: str):
        # 获取所有基金列表（含未成立、已到期）
        fund_list_result = c.sector('507010', end_date)
        if fund_list_result.ErrorCode != 0:
            print(f'failed to get all fund list: {fund_list_result.ErrorMsg}')
            return

        df = RawDataApi().get_em_tradedates(start_date, end_date)
        for row in df.itertuples(index=False):
            if self.em_fund_benchmark(row.TRADEDATES, fund_list_result.Codes):
                print(f'[em_fund_benchmark_history] {row.TRADEDATES} done')
            else:
                print(f'[em_fund_benchmark_history] {row.TRADEDATES} failed')
                break

    def em_fund_benchmark(self, end_date: str, fund_list=()):
        try:
            if not fund_list:
                fund_list = RawDataHelper.get_all_live_fund_list(end_date)
                if fund_list is None:
                    print(f'[em_fund_benchmark] failed to get fund list')
                    return False
            data = self._em_css_wrapper(fund_list, 'BENCHMARK', f'EndDate={end_date},Ispandas=1')
            if data is None:
                return False
            data = data[data.notna().all(axis=1)]
            if data.empty:
                return True

            df = data.reset_index().rename(columns=lambda x: EmFundBenchmark.__getattribute__(EmFundBenchmark, x).name)
            df['datetime'] = end_date
            df['benchmark'] = df.benchmark.str.rstrip()
            # 获取当前的benchmark
            now_df = RawDataApi().get_em_fund_benchmark(end_date)
            if now_df is not None:
                # 过滤出来新增基金benchmark以及旧基金的benchmark发生变化的情况
                now_df = now_df.drop(columns=['_update_time']).sort_values(by=['em_id', 'datetime']).drop_duplicates(subset='em_id', keep='last')
                df = df.merge(now_df, how='left', on=['em_id', 'benchmark'], indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge', 'datetime_y']).rename(columns={'datetime_x': 'datetime'})
            # 更新到db
            self._data_helper._upload_raw(df, EmFundBenchmark.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_fund_benchmark_of_new_funds(self, last_calc_date):
        last_calc_date: datetime.date = pd.to_datetime(last_calc_date, infer_datetime_format=True).date()
        em_fund_info = RawDataApi().get_em_fund_info()
        em_fund_info = em_fund_info[em_fund_info.start_date > last_calc_date]
        fund_list = em_fund_info.em_id.to_list()
        print(fund_list)
        data = self._em_css_wrapper(fund_list, 'BENCHMARK', f'EndDate={datetime.date.today().isoformat()},Ispandas=1')
        if data is None:
            return
        df_list = [data.drop(columns='DATES')]
        for rank in range(10):
            df = self._em_css_wrapper(fund_list, 'BMINDEXCODE', f'Rank={rank+1},Ispandas=1')
            if df is None:
                return
            df = df.rename(columns={'BMINDEXCODE': f'BMINDEXCODE_{rank+1}'})
            df_list.append(df.drop(columns='DATES'))
        df = pd.concat(df_list, axis=1)
        df.to_csv('./benchmark_of_new_funds.csv', encoding='utf-8-sig')
        return df

    def em_fund_rate(self, end_date: str):
        try:
            fund_list = RawDataHelper.get_all_live_fund_list(end_date)
            if fund_list is None:
                print('[em_fund_rate] failed to get fund list')
                return False
            df = self._em_css_wrapper(fund_list, "MKTCOMPRE3YRAT,MORNSTAR3YRAT,MORNSTAR5YRAT,MERCHANTS3YRAT,TXCOMRATRAT,SHSTOCKSTAR3YCOMRAT,SHSTOCKSTAR3YSTOCKRAT,SHSTOCKSTAR3YTIMERAT,SHSTOCKSTAR3YSHARPERAT,SHSTOCKSTAR5YCOMRATRAT,SHSTOCKSTAR5YSTOCKRAT,SHSTOCKSTAR5YTIMERAT,SHSTOCKSTAR5YSHARPRAT,JAJXCOMRAT,JAJXEARNINGPOWERRAT,JAJXACHIEVESTABILITYRAT,JAJXANTIRISKRAT,JAJXSTOCKSELECTIONRAT,JAJXTIMESELECTIONRAT,JAJXBENCHMARKTRACKINGRAT,JAJXEXCESSEARNINGSRAT,JAJXTOTALFEERAT",
                                      f"EndDate={end_date},Ispandas=1")
            if df is None:
                print('[em_fund_rate] failed to get data')
                return False
            df = df[df.drop(columns='DATES').notna().any(axis=1)]
            df['DATES'] = datetime.datetime.strptime(end_date, '%Y%m%d').date()
            df = df.reset_index()
            self._data_helper._upload_raw(df, EMFundRate.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_fund_asset_history(self, end_date: str):
        # 获取全部基金列表（含未成立、已到期）
        fund_list = self._em_sector_wrapper('507010', end_date)
        if fund_list is None:
            print('[em_fund_asset_history] failed to get fund list')
            return False

        start_year = 2000
        end_year = 2004
        res: List[pd.DataFrame] = []
        for year in range(start_year, end_year+1):
            for date in QUARTER_UPDATE_DATE_LIST:
                dt = str(year) + date
                print(f'doing {dt}')
                data = self._em_css_wrapper(fund_list, "PRTSTOCKTONAV,PRTBONDTONAV,PRTFUNDTONAV,PRTCASHTONAV,PRTOTHERTONAV,MMFFIRSTREPOTONAV,MMFAVGPTM", f"ReportDate={dt},Ispandas=1")
                data['DATES'] = dt
                data['MMFFIRSTREPOTONAV'] = data.apply(lambda x: 0 if not pd.isnull(x.MMFAVGPTM) and pd.isnull(x.MMFFIRSTREPOTONAV) else x.MMFFIRSTREPOTONAV, axis=1)
                res.append(data)
                print(f'{dt} done')
        df = pd.concat(res).reset_index()
        df = df[df.drop(columns=['CODES', 'DATES']).notna().any(axis=1)]
        self._data_helper._upload_raw(df, EMFundHoldAsset.__table__.name)
        return True

    def em_fund_asset(self, end_date: str):
        try:
            fund_list = RawDataHelper.get_all_live_fund_list(end_date)
            if fund_list is None:
                print('[em_fund_asset] failed to get fund list')
                return False

            real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
            df = self._em_css_wrapper(fund_list, "PRTSTOCKTONAV,PRTBONDTONAV,PRTFUNDTONAV,PRTCASHTONAV,PRTOTHERTONAV,MMFFIRSTREPOTONAV,MMFAVGPTM", f"ReportDate={real_date},Ispandas=1")
            if df is None:
                print(f'[em_fund_asset] failed to get data')
                return False
            df['DATES'] = real_date
            df = df[df.drop(columns=['DATES']).notna().any(axis=1)].reset_index()
            df['MMFFIRSTREPOTONAV'] = df.apply(lambda x: 0 if not pd.isnull(x.MMFAVGPTM) and pd.isnull(x.MMFFIRSTREPOTONAV) else x.MMFFIRSTREPOTONAV, axis=1)
            now_df = RawDataApi().get_em_fund_hold_asset(start_date=real_date, end_date=real_date)
            if now_df is not None:
                df = df.replace({None: np.nan}).infer_objects()
                now_df = now_df.replace({None: np.nan}).infer_objects()
                # 过滤出来新增基金benchmark以及旧基金的benchmark发生变化的情况
                now_df = now_df.drop(columns=['_update_time']).sort_values(by=['CODES', 'DATES']).drop_duplicates(subset='CODES', keep='last')
                # merge on all columns
                df = df.merge(now_df, how='left', indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            # TODO: 最好原子提交下边两步
            RawDataApi().delete_em_fund_hold_asset(real_date, df.CODES.to_list())
            self._data_helper._upload_raw(df, EMFundHoldAsset.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_fund_industry(self, end_date: str):
        try:
            fund_list = RawDataHelper.get_all_live_fund_list(end_date)
            if fund_list is None:
                print('[em_fund_industry] failed to get fund list')
                return False

            _res = []
            real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
            for rank in range(1, 4):
                data = self._em_css_wrapper(fund_list, "PRTKEYINDNAME,PRTKEYINDTOASSET", f"ReportDate={real_date},Rank={rank},Ispandas=1")
                if data is None:
                    print(f'[em_fund_industry] failed to get data')
                    return False
                data = data.rename(columns={'PRTKEYINDNAME': f'rank{rank}_indname', 'PRTKEYINDTOASSET': f'rank{rank}_indweight'})
                data = data.drop(columns='DATES')
                _res.append(data)
            df = pd.concat(_res, axis=1)
            df = df[df.notna().any(axis=1)].reset_index()
            df['DATES'] = real_date
            now_df = RawDataApi().get_em_fund_hold_industry(start_date=real_date, end_date=real_date)
            if now_df is not None:
                df = df.replace({None: np.nan}).infer_objects()
                now_df = now_df.replace({None: np.nan}).infer_objects()
                # 过滤出来新增基金benchmark以及旧基金的benchmark发生变化的情况
                now_df = now_df.drop(columns=['_update_time']).sort_values(by=['CODES', 'DATES']).drop_duplicates(subset='CODES', keep='last')
                # merge on all columns
                df = df.merge(now_df, how='left', indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            # TODO: 最好原子提交下边两步
            RawDataApi().delete_em_fund_hold_industry(real_date, df.CODES.to_list())
            self._data_helper._upload_raw(df, EMFundHoldIndustry.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_fund_industry_qdii(self, end_date: str):
        try:
            fund_list=c.sector("507007", end_date).Data
            fund_list = [fund_id for idx, fund_id in enumerate(fund_list) if idx % 2 == 0]
            if fund_list is None:
                print('[em_fund_industry] failed to get fund list')
                return False

            _res = []
            real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
            for rank in range(1, 4):
                data = self._em_css_wrapper(fund_list, "QDIIKEYGICSIND,QDIIKEYGICSINDVALUETONAV", f"ReportDate={real_date},Rank={rank},Ispandas=1")
                if data is None:
                    print(f'[em_fund_industry] failed to get data')
                    return False
                data = data.rename(columns={'QDIIKEYGICSIND': f'rank{rank}_indname', 'QDIIKEYGICSINDVALUETONAV': f'rank{rank}_indweight'})
                data = data.drop(columns='DATES')
                _res.append(data)
            df = pd.concat(_res, axis=1)
            df = df[df.notna().any(axis=1)].reset_index()
            df['DATES'] = real_date
            now_df = RawDataApi().get_em_fund_hold_industry_qdii(start_date=real_date, end_date=real_date)
            if now_df is not None:
                df = df.replace({None: np.nan}).infer_objects()
                now_df = now_df.replace({None: np.nan}).infer_objects()
                # 过滤出来新增基金benchmark以及旧基金的benchmark发生变化的情况
                now_df = now_df.drop(columns=['_update_time']).sort_values(by=['CODES', 'DATES']).drop_duplicates(subset='CODES', keep='last')
                # merge on all columns
                df = df.merge(now_df, how='left', indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            # TODO: 最好原子提交下边两步
            RawDataApi().delete_em_fund_hold_industry_qdii(real_date, df.CODES.to_list())
            self._data_helper._upload_raw(df, EMFundHoldIndustryQDII.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_fund_stock_history(self, fund_stock_path: str, report_date: str):
        df: pd.DataFrame = pd.read_excel(fund_stock_path, na_values='——')
        df = df[df['证券名称'].notna()]
        df = df.drop(columns='证券名称')

        columns_name = ['CODES'] + ['rank'+str(i+1)+'_stock'+suffix for suffix in ('', '_code', 'val', 'weight') for i in range(10)]
        assert len(columns_name) == df.shape[1], 'len of columns name should be equal with columns number of df'
        df = df.set_axis(columns_name, axis=1)
        df['DATES'] = report_date
        em._data_helper._upload_raw(df, EMFundHoldStock.__table__.name)

    def em_us_stock_history(self, start_date, end_date):
        try:
            start_date = datetime.datetime.strptime(start_date, '%Y%m%d') - datetime.timedelta(days=FUND_NAV_EXTRA_TRADE_DAYS)
            start_date = start_date.strftime('%Y%m%d')
            
            end_date = str(datetime.datetime.today().date()).replace('-','')
            stock_list_result = c.sector('202001004', end_date)
            select_data = ['TLH.A'] # 美10年债etf 
            
            stock_list = stock_list_result.Codes
            stock_list += select_data
            data=c.csd(stock_list,"CLOSE",start_date,end_date,"period=1,adjustflag=1,curtype=1,order=1,market=CNSESH,Ispandas=1")
            data = data.reset_index().dropna()
            RawDataApi().delete_em_us_stock_price(start_date, end_date)
            self._data_helper._upload_raw(data, EmOverseaEmStockPriceUS.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_fund_stock(self, end_date: str):
        try:
            fund_list = RawDataHelper.get_all_live_fund_list(end_date)
            if fund_list is None:
                print('[em_fund_stock] failed to get fund list')
                return False

            _res = []
            real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
            for rank in range(1, 11):
                data = self._em_css_wrapper(fund_list, "PRTKEYSTOCKNAME,PRTKEYSTOCKCODE,PRTKEYSTOCKVALUE,PRTKEYSTOCKTONAV", f"ReportDate={real_date},Rank={rank},Ispandas=1")
                if data is None:
                    print(f'[em_fund_stock] failed to get data')
                    return False
                data = data.rename(columns={'PRTKEYSTOCKNAME': f'rank{rank}_stock',
                                            'PRTKEYSTOCKCODE': f'rank{rank}_stock_code',
                                            'PRTKEYSTOCKVALUE': f'rank{rank}_stockval',
                                            'PRTKEYSTOCKTONAV': f'rank{rank}_stockweight'})
                data = data.drop(columns='DATES')
                _res.append(data)
            df = pd.concat(_res, axis=1)
            df = df[df.notna().any(axis=1)].reset_index()
            df['DATES'] = real_date
            now_df = RawDataApi().get_em_fund_hold_stock(start_date=real_date, end_date=real_date)
            if now_df is not None:
                df = df.replace({None: np.nan}).infer_objects()
                now_df = now_df.replace({None: np.nan}).infer_objects()
                # 过滤出来新增基金benchmark以及旧基金的benchmark发生变化的情况
                now_df = now_df.drop(columns=['_update_time']).sort_values(by=['CODES', 'DATES']).drop_duplicates(subset='CODES', keep='last')
                # merge on all columns
                df = df.merge(now_df, how='left', indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            # TODO: 最好原子提交下边两步
            RawDataApi().delete_em_fund_hold_stock(real_date, df.CODES.to_list())
            self._data_helper._upload_raw(df, EMFundHoldStock.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_fund_stock_qdii(self, end_date: str):
        try:
            fund_list=c.sector("507007", end_date).Data
            fund_list = [fund_id for idx, fund_id in enumerate(fund_list) if idx % 2 == 0]
            if fund_list is None:
                print('[em_fund_stock] failed to get fund list')
                return False
            _res = []
            real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
            for rank in range(1, 21):
                data = self._em_css_wrapper(fund_list, "QDIIKEYSECU,QDIIKEYSECUCODE,QDIIKEYSVALUE,QDIIKEYSVALUETONAV,QDIIKEYSECUTYPE", f"ReportDate={real_date},Rank={rank},Ispandas=1")
                if data is None:
                    print(f'[em_fund_stock] failed to get data')
                    return False
                data = data.rename(columns={'QDIIKEYSECU': f'rank{rank}_stock',
                                            'QDIIKEYSECUCODE': f'rank{rank}_stock_code',
                                            'QDIIKEYSVALUE': f'rank{rank}_stockval',
                                            'QDIIKEYSVALUETONAV': f'rank{rank}_stockweight',
                                            'QDIIKEYSECUTYPE': f'rank{rank}_type'})
                data = data.drop(columns='DATES')
                _res.append(data)
            df = pd.concat(_res, axis=1)
            df = df[df.notna().any(axis=1)].reset_index()
            df['DATES'] = real_date
            now_df = RawDataApi().get_em_fund_hold_stock(start_date=real_date, end_date=real_date)
            if now_df is not None:
                df = df.replace({None: np.nan}).infer_objects()
                now_df = now_df.replace({None: np.nan}).infer_objects()
                # 过滤出来新增基金benchmark以及旧基金的benchmark发生变化的情况
                now_df = now_df.drop(columns=['_update_time']).sort_values(by=['CODES', 'DATES']).drop_duplicates(subset='CODES', keep='last')
                # merge on all columns
                df = df.merge(now_df, how='left', indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            # TODO: 最好原子提交下边两步
            RawDataApi().delete_em_fund_hold_stock_qdii(real_date, df.CODES.to_list())
            self._data_helper._upload_raw(df, EMFundHoldStockQDII.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_mng_info_history(self,path):
        col_dic = {'基金经理':'mng_name',
            '代码': 'code',
            '名称':'desc_name',
            '在管基金规模(亿元)':'fund_size',
            '任职日期':'start_date',
            '任职天数':'work_days',
            '任职以来回报(%)':'his_ret',
            '任职以来年化回报(%)':'his_annual_ret',
            '业绩比较基准':'benchmark',
            '基金类型':'fund_type',
            '管理公司':'company_name',
            '共同任职经理':'coworkers',
            '基金经理年限':'mng_work_year',
            '任职基金数':'worked_funds_num',
            '任职基金公司数':'worked_funds_num',
            '任职基金几何总回报(%)':'fund_total_geo_ret',
            '几何平均年化收益率(%)':'geo_annual_ret',
            '算术平均年化收益率(%)':'cal_annual_ret',
            '性别':'gender',
            '出生年份':'birth_year',
            '年龄':'age',
            '学历':'education',
            '国籍':'nationality',
            '简历':'resume',
            '最早任职基金经理日期':'start_mng_date'}
        df = pd.read_excel(path, header=1).dropna(axis=0)
        df = df.rename(columns = col_dic)
        df = df.replace('——',np.NaN)
        em._data_helper._upload_raw(df,EMMngInfo.__table__.name)

    def em_fund_mng_change_history(self, path):
        col_dic = {
            '代码':'code',
            '名称':'desc_name',
            '现任基金经理':'mng_now',
            '现任经理最新任职日期':'mng_now_start_date',
            '最早任职基金经理':'mng_begin',
            '最早任职基金经理日期':'mng_begin_date',
            '现任基金经理年限':'mng_now_work_year',
            '同类型基金现任基金经理年限均值':'same_type_fund_work_year',
            '已离任基金经理':'resign_mngs',
            '历任基金经理人数':'total_mng_num',
            '历任基金经理人均任职年限':'total_mng_avg_work_year',
            '投资类型':'fund_type',
            '管理公司':'company',
            '监管辖区':'region'
        }
        df = pd.read_excel(path, header=0).dropna(axis=0)
        df = df.rename(columns = col_dic)
        df = df.replace('——',np.NaN)
        df = df.drop_duplicates('code') # 发现有重复的数据 比如 codes = 000063.OF
        em._data_helper._upload_raw(df,EMFundMngChange.__table__.name)

    def em_fund_comp_mng_change_history(self, path):
        col_dic = {
            '基金公司':'company',
            '基金经理数':'total_mng_num',
            '基金经理平均年限':'mng_avg_year',
            '基金经理最大年限':'mng_max_year',
            '团队稳定性':'team_stability',
            '新聘基金经理数':'new_mng_num',
            '离职基金经理数':'resign_mng_num',
            '基金经理变动率(%)':'mng_turnover_rate',
            '1年以内':'exp_less_than_1',
            '1-2年':'exp_1_to_2',
            '2-3年':'exp_2_to_3',
            '3-4年':'exp_3_to_4',
            '4年以上':'exp_more_than_4',
        }
        df = pd.read_excel(path, header=1).dropna(axis=0)
        df = df.rename(columns = col_dic)
        df = df.replace('——',np.NaN)
        em._data_helper._upload_raw(df,EMFundCompMngChange.__table__.name)

    def em_fund_com_core_mng_history(self, path):
        col_dic = {
            '基金代码':'code',
            '基金名称':'desc_name',
            '本基金离职基金经理人数':'fund_resign_mng_num',
            '所属基金公司':'company',
            '基金公司基金经理数':'com_mng_num',
            '基金公司离职基金经理数':'com_resign_mng_num',
            '基金公司基金经理离职率(%)':'com_resign_mng_rate',
            '基金公司核心人员人数':'com_core_mng_num',
            '基金公司核心人员离职人数':'com_core_mng_resign_num',
            '基金公司核心人员离职率(%)':'com_core_mng_resign_rate',
            '投资类型':'fund_type',
            '监管区域':'region'
        }
        df = pd.read_excel(path, header=1).dropna(axis=0)
        df = df.rename(columns = col_dic)
        df = df.replace('——',np.NaN)
        df = df.drop_duplicates('code') # 发现有重复的数据 比如 codes = 000424.OF
        em._data_helper._upload_raw(df,EMFundCompCoreMng.__table__.name)

    def em_fund_bond_history(self, fund_bond_path: str, report_date: str):
        df: pd.DataFrame = pd.read_excel(fund_bond_path, na_values='——')
        df = df[df['证券名称'].notna()]
        df = df.drop(columns='证券名称')

        columns_name = ['CODES'] + ['rank'+str(i+1)+'_bond'+suffix for suffix in ('', '_code', 'val', 'weight') for i in range(10)]
        assert len(columns_name) == df.shape[1], 'len of columns name should be equal with columns number of df'
        df = df.set_axis(columns_name, axis=1)
        df['DATES'] = report_date
        em._data_helper._upload_raw(df, EMFundHoldBond.__table__.name)

    def em_fund_bond(self, end_date: str):
        try:
            fund_list = RawDataHelper.get_all_live_fund_list(end_date)
            if fund_list is None:
                print('[em_fund_bond] failed to get fund list')
                return False

            _res = []
            real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
            for rank in range(1, 11):
                data = self._em_css_wrapper(fund_list, "PRTKEYBONDNAME,PRTKEYBONDCODE,PRTKEYBONDVALUE,PRTKEYBONDTONAV", f"ReportDate={real_date},Rank={rank},Ispandas=1")
                if data is None:
                    print(f'[em_fund_bond] failed to get data')
                    return False
                data = data.rename(columns={'PRTKEYBONDNAME': f'rank{rank}_bond', 'PRTKEYBONDCODE': f'rank{rank}_bond_code', 'PRTKEYBONDVALUE': f'rank{rank}_bondval', 'PRTKEYBONDTONAV': f'rank{rank}_bondweight'})
                data = data.drop(columns='DATES')
                _res.append(data)
            df = pd.concat(_res, axis=1)
            df = df[df.notna().any(axis=1)].reset_index()
            df['DATES'] = real_date
            now_df = RawDataApi().get_em_fund_hold_bond(start_date=real_date, end_date=real_date)
            if now_df is not None:
                df = df.replace({None: np.nan}).infer_objects()
                now_df = now_df.replace({None: np.nan}).infer_objects()
                # 过滤出来新增基金benchmark以及旧基金的benchmark发生变化的情况
                now_df = now_df.drop(columns=['_update_time']).sort_values(by=['CODES', 'DATES']).drop_duplicates(subset='CODES', keep='last')
                # merge on all columns
                df = df.merge(now_df, how='left', indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            # TODO: 最好原子提交下边两步
            RawDataApi().delete_em_fund_hold_bond(real_date, df.CODES.to_list())
            self._data_helper._upload_raw(df, EMFundHoldBond.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_macroeconomc_manually(self, file_name: str):
        df = pd.read_csv(f'./{file_name}')
        df = df[df.value.notna()]
        me_map = RawDataApi().get_em_macroeconomic_info().set_index('em_codes')['codes'].to_dict()
        me_map.update(self._MACROECONOMIC_MAP)
        df['codes'] = df.codes.map(me_map)
        self._data_helper._upload_raw(df, EmMacroEconomicDaily.__table__.name)

    def em_macroeconomic_daily_history(self, code_list: List[str], start_date: str, end_date: str):
        data = self._em_edb_wrapper(code_list,
                                   f"IsLatest=0,StartDate={start_date},EndDate={end_date},Ispanads=1")
        if data is None:
            print('[em_macroeconomic_daily_history] failed to get data')
            return

        df = data.reset_index()
        df = df.rename(columns={
            'CODES': 'codes',
            'DATES': 'datetime',
            'RESULT': 'value',
        })
        df = df[df.value.notna()]
        me_map = RawDataApi().get_em_macroeconomic_info().set_index('em_codes')['codes'].to_dict()
        me_map.update(self._MACROECONOMIC_MAP)
        df['codes'] = df.codes.map(me_map)
        self._data_helper._upload_raw(df, EmMacroEconomicDaily.__table__.name)

    def em_macroeconomic_daily(self, start_date: str, end_date: str):
        try:
            data1 = self._em_edb_wrapper("EMM00588712,EMM00588707,EMM00588705,EMM00588703,EMM00622432,EMM00622433,EMM00622434,EMM00622435",
                                        f"IsLatest=0,StartDate={start_date},EndDate={end_date},Ispanads=1")
            if data1 is None:
                print('[em_macroeconomic_daily] failed to get data1')
                return False
            data2 = self._em_edb_wrapper("E1002041,E1701048",
                                        f"IsLatest=0,StartDate={start_date},EndDate={end_date},Ispanads=1")
            if data2 is None:
                print('[em_macroeconomic_daily] failed to get data2')
                return False
            data3 = self._em_edb_wrapper("EMG00001306,EMG00001308,EMG00001310,EMG00001303,EMG00001317,EMG00001318,EMG00001319,EMG00001320,EMG00001321,EMG00001435",
                                        f"IsLatest=0,StartDate={start_date},EndDate={end_date},Ispandas=1")
            if data3 is None:
                print('[em_macroeconomic_daily] failed to get data3')
                return False
            df = pd.concat([data1, data2, data3])
            if not df.empty:
                df = df.reset_index()
                df = df.rename(columns={
                    'CODES': 'codes',
                    'DATES': 'datetime',
                    'RESULT': 'value',
                })
                df = df[df.value.notna()]
            me_map = RawDataApi().get_em_macroeconomic_info()
            if me_map is None:
                print('[em_macroeconomic_daily] failed to get me info')
                return False
            me_map = me_map.set_index('em_codes')['codes'].to_dict()
            me_map.update(self._MACROECONOMIC_MAP)
            
            end_date = str(datetime.date.today())
            begin_date = str(datetime.date.today() - datetime.timedelta(days=10))
            data = self._em_ctr_wrapper('MarginMarketInfo', "TRADEDATE,RZRQYE", f"StartDate={begin_date},EndDate={end_date},Ispanads=1")
            _df = pd.DataFrame(data).T
            _df.columns = ['datetime','value']
            _df.loc[:,'codes'] = 'rzrqye'
            dic = {
                'CODES':'codes',
                'DATES':'datetime',
                'RESULT':'value',
            }
            _df_1 = self._em_edb_wrapper("EMI00227696,EMI00227697,EMI00227698,EMI00227699,EMI00241431,EMI00227700",
                                        f"Ispandas=1,StartDate={begin_date},EndDate={end_date}").reset_index().rename(columns=dic)
            _df = _df.append(_df_1)
            df = df.append(_df)
            df['codes'] = df.codes.map(me_map)
            now_df = RawDataApi().get_em_macroeconomic_daily()
            if now_df is not None:
                df['datetime'] = pd.to_datetime(df.datetime, infer_datetime_format=True).dt.date
                now_df = now_df.drop(columns=['_update_time'])
                df = df.astype(now_df.dtypes.to_dict())
                df = df.merge(now_df, how='left', on=['codes', 'datetime', 'value'], indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            print(df)
            for code in df.codes.unique():
                RawDataApi().delete_em_macroeconomic_daily(code, df[df.codes == code].datetime.to_list())
            self._data_helper._upload_raw(df, EmMacroEconomicDaily.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_macroeconomic_monthly_history(self, code_list: List[str], start_date: str, end_date: str):
        data = self._em_edb_wrapper(code_list,
                                   f"IsLatest=0,StartDate={start_date},EndDate={end_date},Ispanads=1")
        if data is None:
            print('[em_macroeconomic_monthly_history] failed to get data')
            return
        df = data.reset_index().rename(columns={
            'CODES': 'codes',
            'DATES': 'datetime',
            'RESULT': 'value',
        })
        df = df[df.value.notna()]
        me_map = RawDataApi().get_em_macroeconomic_info().set_index('em_codes')['codes'].to_dict()
        me_map.update(self._MACROECONOMIC_MAP)
        df['codes'] = df.codes.map(me_map)
        self._data_helper._upload_raw(df, EmMacroEconomicMonthly.__table__.name)

    def em_macroeconomic_monthly(self):
        try:
            data1 = self._em_edb_wrapper("EMM00072301,EMM00073348,EMM00087084,EMM00087086,EMM00634721,EMM00008445,EMM00121996,EMM00122023,EMI00135328,EMM00122009,EMM00000008,EMM00000009,EMM01014626,EMM00000010,EMM01014628,EMM00000011,EMM01014630,EMM00000012,EMM00072324,EMM00072343,EMM00072385,EMM00588948,EMM00588952",
                                        "IsLatest=1,Ispanads=1")
            if data1 is None:
                print('[em_macroeconomic_monthly] failed to get data')
                return False
            data2 = self._em_edb_wrapper("EMI01476152,EMI01476160,EMI00120309,EMI00120291",
                                        f"IsLatest=1,Ispandas=1")
            if data2 is None:
                print('[em_macroeconomic_monthly] failed to get data2')
                return False
            df = pd.concat([data1, data2])
            df = df.reset_index().rename(columns={
                'CODES': 'codes',
                'DATES': 'datetime',
                'RESULT': 'value',
            })
            df = df[df.value.notna()]
            me_map = RawDataApi().get_em_macroeconomic_info()
            if me_map is None:
                print('[em_macroeconomic_monthly] failed to get me info')
                return False
            me_map = me_map.set_index('em_codes')['codes'].to_dict()
            me_map.update(self._MACROECONOMIC_MAP)
            df['codes'] = df.codes.map(me_map)

            now_df = RawDataApi().get_em_macroeconomic_monthly()
            if now_df is not None:
                df['datetime'] = pd.to_datetime(df.datetime, infer_datetime_format=True).dt.date
                now_df = now_df.drop(columns=['_update_time']).sort_values(by=['codes', 'datetime']).drop_duplicates(subset='codes', keep='last')
                df = df.round(6).merge(now_df.round(6), how='left', on=['codes', 'datetime', 'value'], indicator=True, validate='one_to_one')
                df = df[df._merge == 'left_only'].drop(columns=['_merge'])
            print(df)
            for date in df.datetime.unique():
                RawDataApi().delete_em_macroeconomic_monthly(date, df[df.datetime == date].codes.to_list())
            self._data_helper._upload_raw(df, EmMacroEconomicMonthly.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_fund_ipo_stats_from_file(self, csv_path, start_date, end_date):
        df_i = pd.read_excel(csv_path, encoding='utf_8_sig', na_values='——').dropna(subset=['基金全称'])
        df_i = df_i.drop(['打新年化收益率(%)','最新净值','净值日期','基金类型','基金全称','基金所属公司'], axis=1)
        start_date = pd.to_datetime(start_date, infer_datetime_format=True).date()
        end_date = pd.to_datetime(end_date, infer_datetime_format=True).date()
        col_name = {
            '基金代码':'em_id',
            '打中新股数量': 'ipo_allocation_num',
            '累计获配股数(万股)': 'ipo_allocation_share_num',
            '累计获配金额(万元)': 'ipo_allocation_amount',
            '打新收益率(%)': 'ipo_allocation_ret',
        }
        df_i = df_i.rename(columns=col_name)
        df_i.loc[:, 'start_date'] = start_date
        df_i.loc[:, 'end_date'] = end_date
        self._data_helper._upload_raw(df_i, EmFundIPOStats.__table__.name)

    # FIXME 这张表暂时没法用API来下数据(Choice不支持)
    # def em_fund_ipo_stats(self):
    #     try:
    #         fund_list = RawDataHelper.get_all_live_fund_list(end_date)
    #         if fund_list is None:
    #             print('[em_fund_ipo_stats] failed to get fund list')
    #             return False

    #         real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
    #         df = self._em_css_wrapper(fund_list, "PRTSTOCKTONAV,PRTBONDTONAV,PRTFUNDTONAV,PRTCASHTONAV,PRTOTHERTONAV,MMFFIRSTREPOTONAV,MMFAVGPTM", f"ReportDate={real_date},Ispandas=1")
    #         if df is None:
    #             print(f'[em_fund_ipo_stats] failed to get data')
    #             return False
    #         df['DATES'] = real_date
    #         df = df[df.drop(columns=['DATES']).notna().any(axis=1)].reset_index()
    #         df['MMFFIRSTREPOTONAV'] = df.apply(lambda x: 0 if not pd.isnull(x.MMFAVGPTM) and pd.isnull(x.MMFFIRSTREPOTONAV) else x.MMFFIRSTREPOTONAV, axis=1)
    #         now_df = RawDataApi().get_em_fund_hold_asset(start_date=real_date, end_date=real_date)
    #         if now_df is not None:
    #             df = df.replace({None: np.nan}).infer_objects()
    #             now_df = now_df.replace({None: np.nan}).infer_objects()
    #             # 过滤出来新增基金benchmark以及旧基金的benchmark发生变化的情况
    #             now_df = now_df.drop(columns=['_update_time']).sort_values(by=['CODES', 'DATES']).drop_duplicates(subset='CODES', keep='last')
    #             # merge on all columns
    #             df = df.merge(now_df, how='left', indicator=True, validate='one_to_one')
    #             df = df[df._merge == 'left_only'].drop(columns=['_merge'])
    #         # TODO: 最好原子提交下边两步
    #         RawDataApi().delete_em_fund_hold_asset(real_date, df.CODES.to_list())
    #         self._data_helper._upload_raw(df, EMFundHoldAsset.__table__.name)
    #         return True
    #     except Exception as e:
    #         print(e)
    #         traceback.print_exc()
    #         return False

    def em_fund_conr_info(self, csv_path):
        df = pd.read_excel(csv_path, encoding='utf_8_sig', na_values='——').dropna(subset=['转债名称'])
        col_dic = {
            '代码':'em_id',
            '名称':'desc_name',
            '转债代码':'conv_bond_id',
            '转债名称':'bond_name',
            '发行方式':'ipo_method',
            '发行规模(亿元)':'ipo_size',
            '发行期限(年)':'duration',
            '信用评级':'rating',
            '票面利率(%)':'coupon_rate',
            '补偿利率(%)':'compensation_rate',
            '利率类型':'rate_type',
            '最新余额(万元)':'latest_balance',
            '付息频率':'payment_frequency',
            '付息说明':'payment_doc',
            '发行日期':'issue_date',
            '上市日期':'listing_date',
            '起息日期':'value_date',
            '到期日期':'date_of_expiry',
            '转股起始日':'conv_start_date',
            '初始转股价':'init_conv_price',
            '最新转股价':'latest_conv_price',
            '利率说明':'rate_doc',
            '赎回条款':'redemption_clause',
            '回售条款':'resale_clause',
            '特别向下修正条款':'downward_amendment',
            '转股条款':'conv_clause',
            '担保人':'warrent',
            '担保方式':'warrent_method',
            '担保范围':'warrent_scope',
            '信用等级':'credit_rating',
            '评估机构':'evaluation_agency',
            '主承销商':'lead_underwriter',
            '证监会行业(2012)':'industry',
            '东财行业':'em_industry'
            }
        df = df.rename(columns=col_dic)
        df = df.drop_duplicates(subset=['issue_date','conv_bond_id','bond_name'])
        self._data_helper._upload_raw(df_i, EmFundConvInfo.__table__.name)

    def em_fund_ipo_detail(self, csv_path, em_id):
        df_i = pd.read_excel(csv_path, encoding='utf_8_sig', na_values='——').dropna(subset=['名称'])
        df_i['em_id'] = em_id
        dic = {'代码':'stock_id',
            '名称':'desc_name',
            '配售日期':'placedate',
            '有效申购数量(万股)':'effective_volume',
            '实际配售数量(万股)':'actual_volume',
            '获配比例(%)':'place_rate',
            '获配金额(万元)':'place_amt',
            '锁定期限':'lock_up_period',
            '发行价格(元)':'issue_price',
            '首个开板日涨跌幅(%)':'first_open_d_ret',
            '上市以来最高涨幅(%)':'historcal_ret',
            '打新收益率(%)':'ipo_allocation_ret',
            '年化打新收益率(%)':'annual_allocation_ret',
            '证监会行业(2012)':'industry',
            '东财行业':'em_industry'
            }
        df_i = df_i.rename(columns = dic)
        self._data_helper._upload_raw(df_i, EmFundIPODetail.__table__.name)

    def em_fund_stock_portfolio_history(self, data_file_path: str):
        with os.scandir(data_file_path) as it:
            for entry in it:
                if entry.name.endswith('.xls') and entry.is_file():
                    print(f'doing {entry.path}')
                    df = pd.concat(pd.read_excel(entry.path, sheet_name=None, na_values='——', skipfooter=6))
                    column_names_dict = {
                        '代码': 'em_id',
                        '报告期': 'report_date',
                        '股票代码': 'stock_id',
                        '持股数量(万股)': 'hold_number',
                        '半年度持股变动(万股)': 'semi_change',
                        '持股市值(万元)': 'stock_mv',
                        '占净值比(%)': 'net_asset_ratio',
                        '占股票投资市值比(%)': 'mv_ratio',
                    }
                    df = df.loc[:, list(column_names_dict.keys())].rename(columns=column_names_dict)
                    # 这里需要相应修改
                    df['report_date'] = df.report_date.map({'2020年中报': '2020-06-30'})
                    self._data_helper._upload_raw(df, EmFundStockPortfolio.__table__.name)
                    print(f'{entry.path} done')

    def em_fund_stock_portfolio(self):
        pass

    def em_stock_industrial_capital(self, end_date: str, is_history: bool = True) -> bool:
        def transform_columns_name(x: str) -> str:
            if x in ('EMM00593994', 'EMM00594026', 'EMM00594058', 'EMM00594090'):
                return 'inc_amt_all'
            elif x in ('EMM00594001', 'EMM00594033', 'EMM00594065', 'EMM00594097'):
                return 'inc_amt_gem'
            elif x in ('EMM00594010', 'EMM00594042', 'EMM00594074', 'EMM00594106'):
                return 'dec_amt_all'
            elif x in ('EMM00594017', 'EMM00594049', 'EMM00594081', 'EMM00594113'):
                return 'dec_amt_gem'
            assert False, f'got an unknown column name {x}'

        try:
            if not is_history:
                now_df = RawDataApi().get_em_stock_industrial_capital()
                options = 'IsLatest=1,Ispanads=1'
            else:
                options = f'IsLatest=0,StartDate=1990-01-01,EndDate={end_date},Ispanads=1'

            data = self._em_edb_wrapper("EMM00593994,EMM00594001,EMM00594010,EMM00594017,EMM00594026,EMM00594033,EMM00594042,EMM00594049,EMM00594058,EMM00594065,EMM00594074,EMM00594081,EMM00594090,EMM00594097,EMM00594106,EMM00594113", options)
            if data is None:
                print('[em_stock_industrial_capital] failed to get data')
                return False
            df = data.reset_index().rename(columns={
                'CODES': 'codes',
                'DATES': 'datetime',
                'RESULT': 'value',
            })
            df = df[df.value.notna()]
            df_dict: Dict[str, pd.DataFrame] = {}
            df_dict['D'] = df[df.codes.isin(['EMM00593994','EMM00594001','EMM00594010','EMM00594017'])]
            df_dict['W'] = df[df.codes.isin(['EMM00594026','EMM00594033','EMM00594042','EMM00594049'])]
            df_dict['M'] = df[df.codes.isin(['EMM00594058','EMM00594065','EMM00594074','EMM00594081'])]
            df_dict['Y'] = df[df.codes.isin(['EMM00594090','EMM00594097','EMM00594106','EMM00594113'])]
            df_list: List[pd.DataFrame] = []
            for period, one in df_dict.items():
                pivoted_one = one.pivot(index='datetime', columns='codes', values='value')
                pivoted_one = pivoted_one.rename(columns=transform_columns_name)
                pivoted_one['period'] = period
                df_list.append(pivoted_one.reset_index())

            df_all = pd.concat(df_list)
            if not is_history and now_df is not None:
                df_all['datetime'] = pd.to_datetime(df_all.datetime, infer_datetime_format=True).dt.date
                now_df = now_df.drop(columns=['_update_time']).sort_values(by=['period', 'datetime']).drop_duplicates(subset='period', keep='last')
                df_all = df_all.merge(now_df, how='left', on=['datetime', 'period', 'inc_amt_all', 'inc_amt_gem', 'dec_amt_all', 'dec_amt_gem'], indicator=True, validate='one_to_one')
                df_all = df_all[df_all._merge == 'left_only'].drop(columns=['_merge'])

                # 删掉旧的之后再插新的
                df_all.apply(lambda x: RawDataApi().delete_em_stock_industrial_capital(x.datetime, x.period), axis=1)
            self._data_helper._upload_raw(df_all, EmStockIndustrialCapital.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_stock_to_hk_connect(self, end_date: str) -> bool:
        ret = True
        try:
            data_list: List[pd.Series] = []
            for ctr_name in (('SH', 'ActiveStockTOP10SHInfo'), ('SZ', 'ActiveStockTOP10SZInfo')):
                data = self._em_ctr_wrapper(ctr_name[1], "TRADEDATE,DEC_RANK,MSECUCODE,BMONEY,SMONEY,TVAL,ZTVAL,ZSZ,CNT,STR_PUBLISHNAMEDC3",f"period=1,TradeDate={end_date}")
                if data is None:
                    ret = False
                    print(f'[em_stock_to_hk_connect] failed to get data of {ctr_name[0]}')
                    continue
                for v in data.values():
                    data_list.append(pd.Series(v + [ctr_name[0]], index=['datetime', 'dec_rank', 'msecu_code', 'bmoney', 'smoney', 'tval', 'ztval', 'zsz', 'cnt', 'publish_name_dc3', 'market']))
            if data_list:
                df = pd.DataFrame(data_list)
                df['period'] = 'D'
                self._data_helper._upload_raw(df, EmSHSZToHKStockConnect.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
        return ret

    def em_stock_to_hk_connect_history(self, start_date: str, end_date: str):
        trading_day_df = BasicDataApi().get_trading_day_list(start_date, end_date)
        for date in trading_day_df.datetime:
            print(f'do {date}')
            self.em_stock_to_hk_connect(date.strftime('%Y%m%d'))
            print(f'{date} done')

    def em_stock_industrial_capital_trade_detail(self, start_date: str, end_date: str) -> bool:
        try:
            data_list: List[pd.Series] = []
            data = self._em_ctr_wrapper('HoldTradeDetailInfo', 'SECURITYCODE,NOTICEDATE,SHAREHDNAME,SHAREHDTYPE,IS_controller,POSITION1,FX,CHANGENUM,BDSLZLTB,TGDZJYPTZR,'
                                                               'BDHCYLTGSL,BDHCYLTSLZLTGB,BDHCGZS,BDHCGBL,JYPJJ,NEW,DEC_JYPJJ_RATE,BDQJGPJJ,BDBFCKSZ,BDQSRQ,BDJZRQ,'
                                                               'CLB_REMARK,STR_PUBLISHNAMEDC3,TYPE',
                                                               f'StartDate={start_date},EndDate={end_date},secucode=,HoldType=0')
            if data is None:
                print(f'[em_stock_industrial_capital_trade_detail] failed to get data')
                return False
            for v in data.values():
                data_list.append(pd.Series(v, index=['sec_code', 'notice_date', 'share_hd_name', 'share_hd_type', 'is_ctrl', 'position1', 'fx', 'change_num', 'bdsl_zltb',
                                                     'tg_dzjy_ptzr', 'bdh_cyltgsl', 'bdh_cyltslzltgb', 'bdh_cgzs', 'bdh_cgbl', 'jyp_jj', 'latest_price', 'dec_jypjj_rate',
                                                     'bdqj_gpjj', 'bdbf_cksz', 'bd_qsrq', 'bd_jzrq', 'clb_remark', 'publish_name_dc3', 'trade_type']))
            if data_list:
                df = pd.DataFrame(data_list)
                self._data_helper._upload_raw(df, EmStockIndustrialCapitalTradeDetail.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_stock_research_info(self, end_date: str) -> bool:
        try:
            stock_list = self._em_sector_wrapper('001004', end_date)
            if stock_list is None:
                print('[em_stock_research_info] failed to get stock id list')
                return False
            data = self._em_css_wrapper(stock_list, "RESERCHNUM,RESERCHOTHERNUM,RESERCHINSTITUTENUM,RESERCHSECUNUM,RESERCHSECUNAME,RESERCHSECUFREQUENCY1", f"StartDate={end_date},EndDate={end_date}")
            if data is None:
                print(f'[em_stock_research_info] failed to get data')
                return False
            data['DATES'] = end_date
            df = data[data.drop(columns='DATES').notna().any(axis=1)]
            df = df.reset_index().rename(columns=lambda x: EmStockResearchInfo.__getattribute__(EmStockResearchInfo, x).name)
            self._data_helper._upload_raw(df, EmStockResearchInfo.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_stock_research_info_history(self, start_date: str, end_date: str):
        trading_day_df = BasicDataApi().get_trading_day_list(start_date, end_date)
        for date in trading_day_df.datetime:
            print(f'do {date}')
            self.em_stock_research_info(date.strftime('%Y%m%d'))
            print(f'{date} done')

    def em_stock_yearly(self):
        for year in range(2004, 2021):
            if year != 2020:
                end_date = str(year+1)+'0110'
            else:
                end_date = '20201023'
            stock_list = self._em_sector_wrapper('001004', end_date)
            if stock_list is None:
                print('[em_stock_yearly] failed to get stock id list')
                return False
            data = self._em_css_wrapper(stock_list, "DIVANNUACCUM", f"Payyear={year},Ispandas=1")
            if data is None:
                print(f'[em_stock_yearly] failed to get data')
                return False
            df = data.drop(columns='DATES')
            df['year'] = year
            df = df.reset_index().rename(columns=lambda x: EmStockYearly.__getattribute__(EmStockYearly, x).name)
            self._data_helper._upload_raw(df, EmStockYearly.__table__.name)

    def em_stock_fs_balance_sheet_from_file(self):
            # 全部A股股票
            stock_list = self._em_sector_wrapper('001004', end_date)
            if stock_list is None:
                print('[em_stock_fs_balance_sheet] failed to get stock id list')
                return False

            for indicator in (
                # 资产负债表-流动资产
                "BALANCESTATEMENT_9,BALANCESTATEMENT_67,BALANCESTATEMENT_181,BALANCESTATEMENT_50,BALANCESTATEMENT_224,BALANCESTATEMENT_163,BALANCESTATEMENT_10,BALANCESTATEMENT_164,BALANCESTATEMENT_51,BALANCESTATEMENT_216,BALANCESTATEMENT_11,BALANCESTATEMENT_12,BALANCESTATEMENT_223,BALANCESTATEMENT_14,BALANCESTATEMENT_55,BALANCESTATEMENT_57,BALANCESTATEMENT_152,BALANCESTATEMENT_222,BALANCESTATEMENT_16,BALANCESTATEMENT_15,BALANCESTATEMENT_13,BALANCESTATEMENT_156,BALANCESTATEMENT_157,BALANCESTATEMENT_158,BALANCESTATEMENT_52,BALANCESTATEMENT_206,BALANCESTATEMENT_17,BALANCESTATEMENT_207,BALANCESTATEMENT_209,BALANCESTATEMENT_202,BALANCESTATEMENT_20,BALANCESTATEMENT_190,BALANCESTATEMENT_21,BALANCESTATEMENT_22,BALANCESTATEMENT_23,BALANCESTATEMENT_25",
                # 资产负债表-非流动资产
                "BALANCESTATEMENT_53,BALANCESTATEMENT_217,BALANCESTATEMENT_218,BALANCESTATEMENT_211,BALANCESTATEMENT_212,BALANCESTATEMENT_26,BALANCESTATEMENT_27,BALANCESTATEMENT_30,BALANCESTATEMENT_29,BALANCESTATEMENT_28,BALANCESTATEMENT_31,BALANCESTATEMENT_33,BALANCESTATEMENT_32,BALANCESTATEMENT_219,BALANCESTATEMENT_220,BALANCESTATEMENT_34,BALANCESTATEMENT_35,BALANCESTATEMENT_36,BALANCESTATEMENT_225,BALANCESTATEMENT_37,BALANCESTATEMENT_44,BALANCESTATEMENT_38,BALANCESTATEMENT_39,BALANCESTATEMENT_40,BALANCESTATEMENT_41,BALANCESTATEMENT_42,BALANCESTATEMENT_43,BALANCESTATEMENT_46,BALANCESTATEMENT_71,BALANCESTATEMENT_72,BALANCESTATEMENT_74",
                # 资产负债表-流动负债
                "BALANCESTATEMENT_75,BALANCESTATEMENT_105,BALANCESTATEMENT_153,BALANCESTATEMENT_106,BALANCESTATEMENT_226,BALANCESTATEMENT_170,BALANCESTATEMENT_76,BALANCESTATEMENT_171,BALANCESTATEMENT_107,BALANCESTATEMENT_221,BALANCESTATEMENT_77,BALANCESTATEMENT_78,BALANCESTATEMENT_79,BALANCESTATEMENT_213,BALANCESTATEMENT_108,BALANCESTATEMENT_113,BALANCESTATEMENT_80,BALANCESTATEMENT_81,BALANCESTATEMENT_227,BALANCESTATEMENT_82,BALANCESTATEMENT_83,BALANCESTATEMENT_84,BALANCESTATEMENT_114,BALANCESTATEMENT_188,BALANCESTATEMENT_189,BALANCESTATEMENT_154,BALANCESTATEMENT_123,BALANCESTATEMENT_124,BALANCESTATEMENT_87,BALANCESTATEMENT_208,BALANCESTATEMENT_147,BALANCESTATEMENT_203,BALANCESTATEMENT_88,BALANCESTATEMENT_191,BALANCESTATEMENT_89,BALANCESTATEMENT_90,BALANCESTATEMENT_91,BALANCESTATEMENT_93",
                # 资产负债表-非流动负债
                "BALANCESTATEMENT_94,BALANCESTATEMENT_215,BALANCESTATEMENT_95,BALANCESTATEMENT_193,BALANCESTATEMENT_194,BALANCESTATEMENT_228,BALANCESTATEMENT_96,BALANCESTATEMENT_201,BALANCESTATEMENT_97,BALANCESTATEMENT_86,BALANCESTATEMENT_148,BALANCESTATEMENT_98,BALANCESTATEMENT_99,BALANCESTATEMENT_100,BALANCESTATEMENT_101,BALANCESTATEMENT_103,BALANCESTATEMENT_125,BALANCESTATEMENT_126,BALANCESTATEMENT_128",
                # 资产负债表-所有者权益
                "BALANCESTATEMENT_129,BALANCESTATEMENT_195,BALANCESTATEMENT_196,BALANCESTATEMENT_197,BALANCESTATEMENT_198,BALANCESTATEMENT_130,BALANCESTATEMENT_199,BALANCESTATEMENT_133,BALANCESTATEMENT_159,BALANCESTATEMENT_131,BALANCESTATEMENT_134,BALANCESTATEMENT_151,BALANCESTATEMENT_132,BALANCESTATEMENT_160,BALANCESTATEMENT_135,BALANCESTATEMENT_161,BALANCESTATEMENT_162,BALANCESTATEMENT_140,BALANCESTATEMENT_136,BALANCESTATEMENT_137,BALANCESTATEMENT_138,BALANCESTATEMENT_141,BALANCESTATEMENT_142,BALANCESTATEMENT_143,BALANCESTATEMENT_145",
            ):
                real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
                df = self._em_css_wrapper(stock_list, indicator, f"ReportDate={real_date},type=1,Ispandas=1")
                if df is None:
                    print('[em_stock_fs_balance_sheet] failed to get data part1')
                    return False
                df = df.drop(columns='DATES')
                df_list.append(df)
            whole_data = pd.concat(df_list, axis=1)
            whole_data['DATES'] = real_date
            whole_data = whole_data.reset_index()
            self._data_helper._upload_raw(whole_data, EmStockFSBalanceSheet.__table__.name)

    def em_stock_fs_balance_sheet(self, end_date: str):
        df_list: List[pd.DataFrame] = []
        try:
            # 全部A股股票
            stock_list = self._em_sector_wrapper('001004', end_date)
            if stock_list is None:
                print('[em_stock_fs_balance_sheet] failed to get stock id list')
                return False

            for indicator in (
                # 资产负债表-流动资产
                "BALANCESTATEMENT_9,BALANCESTATEMENT_67,BALANCESTATEMENT_181,BALANCESTATEMENT_50,BALANCESTATEMENT_224,BALANCESTATEMENT_163,BALANCESTATEMENT_10,BALANCESTATEMENT_164,BALANCESTATEMENT_51,BALANCESTATEMENT_216,BALANCESTATEMENT_11,BALANCESTATEMENT_12,BALANCESTATEMENT_223,BALANCESTATEMENT_14,BALANCESTATEMENT_55,BALANCESTATEMENT_57,BALANCESTATEMENT_152,BALANCESTATEMENT_222,BALANCESTATEMENT_16,BALANCESTATEMENT_15,BALANCESTATEMENT_13,BALANCESTATEMENT_156,BALANCESTATEMENT_157,BALANCESTATEMENT_158,BALANCESTATEMENT_52,BALANCESTATEMENT_206,BALANCESTATEMENT_17,BALANCESTATEMENT_207,BALANCESTATEMENT_209,BALANCESTATEMENT_202,BALANCESTATEMENT_20,BALANCESTATEMENT_190,BALANCESTATEMENT_21,BALANCESTATEMENT_22,BALANCESTATEMENT_23,BALANCESTATEMENT_25",
                # 资产负债表-非流动资产
                "BALANCESTATEMENT_53,BALANCESTATEMENT_217,BALANCESTATEMENT_218,BALANCESTATEMENT_211,BALANCESTATEMENT_212,BALANCESTATEMENT_26,BALANCESTATEMENT_27,BALANCESTATEMENT_30,BALANCESTATEMENT_29,BALANCESTATEMENT_28,BALANCESTATEMENT_31,BALANCESTATEMENT_33,BALANCESTATEMENT_32,BALANCESTATEMENT_219,BALANCESTATEMENT_220,BALANCESTATEMENT_34,BALANCESTATEMENT_35,BALANCESTATEMENT_36,BALANCESTATEMENT_225,BALANCESTATEMENT_37,BALANCESTATEMENT_44,BALANCESTATEMENT_38,BALANCESTATEMENT_39,BALANCESTATEMENT_40,BALANCESTATEMENT_41,BALANCESTATEMENT_42,BALANCESTATEMENT_43,BALANCESTATEMENT_46,BALANCESTATEMENT_71,BALANCESTATEMENT_72,BALANCESTATEMENT_74",
                # 资产负债表-流动负债
                "BALANCESTATEMENT_75,BALANCESTATEMENT_105,BALANCESTATEMENT_153,BALANCESTATEMENT_106,BALANCESTATEMENT_226,BALANCESTATEMENT_170,BALANCESTATEMENT_76,BALANCESTATEMENT_171,BALANCESTATEMENT_107,BALANCESTATEMENT_221,BALANCESTATEMENT_77,BALANCESTATEMENT_78,BALANCESTATEMENT_79,BALANCESTATEMENT_213,BALANCESTATEMENT_108,BALANCESTATEMENT_113,BALANCESTATEMENT_80,BALANCESTATEMENT_81,BALANCESTATEMENT_227,BALANCESTATEMENT_82,BALANCESTATEMENT_83,BALANCESTATEMENT_84,BALANCESTATEMENT_114,BALANCESTATEMENT_188,BALANCESTATEMENT_189,BALANCESTATEMENT_154,BALANCESTATEMENT_123,BALANCESTATEMENT_124,BALANCESTATEMENT_87,BALANCESTATEMENT_208,BALANCESTATEMENT_147,BALANCESTATEMENT_203,BALANCESTATEMENT_88,BALANCESTATEMENT_191,BALANCESTATEMENT_89,BALANCESTATEMENT_90,BALANCESTATEMENT_91,BALANCESTATEMENT_93",
                # 资产负债表-非流动负债
                "BALANCESTATEMENT_94,BALANCESTATEMENT_215,BALANCESTATEMENT_95,BALANCESTATEMENT_193,BALANCESTATEMENT_194,BALANCESTATEMENT_228,BALANCESTATEMENT_96,BALANCESTATEMENT_201,BALANCESTATEMENT_97,BALANCESTATEMENT_86,BALANCESTATEMENT_148,BALANCESTATEMENT_98,BALANCESTATEMENT_99,BALANCESTATEMENT_100,BALANCESTATEMENT_101,BALANCESTATEMENT_103,BALANCESTATEMENT_125,BALANCESTATEMENT_126,BALANCESTATEMENT_128",
                # 资产负债表-所有者权益
                "BALANCESTATEMENT_129,BALANCESTATEMENT_195,BALANCESTATEMENT_196,BALANCESTATEMENT_197,BALANCESTATEMENT_198,BALANCESTATEMENT_130,BALANCESTATEMENT_199,BALANCESTATEMENT_133,BALANCESTATEMENT_159,BALANCESTATEMENT_131,BALANCESTATEMENT_134,BALANCESTATEMENT_151,BALANCESTATEMENT_132,BALANCESTATEMENT_160,BALANCESTATEMENT_135,BALANCESTATEMENT_161,BALANCESTATEMENT_162,BALANCESTATEMENT_140,BALANCESTATEMENT_136,BALANCESTATEMENT_137,BALANCESTATEMENT_138,BALANCESTATEMENT_141,BALANCESTATEMENT_142,BALANCESTATEMENT_143,BALANCESTATEMENT_145",
            ):
                real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
                df = self._em_css_wrapper(stock_list, indicator, f"ReportDate={real_date},type=1,Ispandas=1")
                if df is None:
                    print('[em_stock_fs_balance_sheet] failed to get data part1')
                    return False
                df = df.drop(columns='DATES')
                df_list.append(df)
            whole_data = pd.concat(df_list, axis=1)
            whole_data['DATES'] = real_date
            whole_data = whole_data.reset_index()
            self._data_helper._upload_raw(whole_data, EmStockFSBalanceSheet.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_stock_fs_income_statement(self, end_date: str):
        df_list: List[pd.DataFrame] = []
        try:
            # 全部A股股票
            stock_list = self._em_sector_wrapper('001004', end_date)
            if stock_list is None:
                print('[em_stock_fs_income_statement] failed to get stock id list')
                return False

            for indicator in (
                # 利润表part1
                "INCOMESTATEMENT_83,INCOMESTATEMENT_9,INCOMESTATEMENT_19,INCOMESTATEMENT_28,INCOMESTATEMENT_22,INCOMESTATEMENT_85,INCOMESTATEMENT_88,INCOMESTATEMENT_84,INCOMESTATEMENT_10,INCOMESTATEMENT_20,INCOMESTATEMENT_23,INCOMESTATEMENT_89,INCOMESTATEMENT_39,INCOMESTATEMENT_33,INCOMESTATEMENT_35,INCOMESTATEMENT_40,INCOMESTATEMENT_38,INCOMESTATEMENT_86,INCOMESTATEMENT_11,INCOMESTATEMENT_12,INCOMESTATEMENT_13,INCOMESTATEMENT_14,INCOMESTATEMENT_127,INCOMESTATEMENT_128,INCOMESTATEMENT_15,INCOMESTATEMENT_129,INCOMESTATEMENT_90,INCOMESTATEMENT_16,INCOMESTATEMENT_17,INCOMESTATEMENT_82,INCOMESTATEMENT_130,INCOMESTATEMENT_25,INCOMESTATEMENT_180,INCOMESTATEMENT_182,INCOMESTATEMENT_123,INCOMESTATEMENT_124,INCOMESTATEMENT_45,INCOMESTATEMENT_46,INCOMESTATEMENT_48,INCOMESTATEMENT_49,INCOMESTATEMENT_118,INCOMESTATEMENT_50,INCOMESTATEMENT_51,INCOMESTATEMENT_52,INCOMESTATEMENT_53,INCOMESTATEMENT_55,INCOMESTATEMENT_56,INCOMESTATEMENT_87,INCOMESTATEMENT_57,INCOMESTATEMENT_120,INCOMESTATEMENT_60,INCOMESTATEMENT_125,INCOMESTATEMENT_126,INCOMESTATEMENT_91,INCOMESTATEMENT_61,INCOMESTATEMENT_62,INCOMESTATEMENT_92,INCOMESTATEMENT_58,INCOMESTATEMENT_80,INCOMESTATEMENT_81,INCOMESTATEMENT_114,INCOMESTATEMENT_116,INCOMESTATEMENT_115,INCOMESTATEMENT_113",
                # 利润表part2
                "INCOMESTATEMENT_93,INCOMESTATEMENT_94,INCOMESTATEMENT_139",
            ):
                real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
                df = self._em_css_wrapper(stock_list, indicator, f"ReportDate={real_date},type=1,Ispandas=1")
                if df is None:
                    print('[em_stock_fs_income_statement] failed to get data part1')
                    return False
                df = df.drop(columns='DATES')
                df_list.append(df)
            whole_data = pd.concat(df_list, axis=1)
            whole_data['DATES'] = real_date
            whole_data = whole_data.reset_index()
            self._data_helper._upload_raw(whole_data, EmStockFSIncomeStatement.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_stock_fs_cashflow_statement(self, end_date: str):
        df_list: List[pd.DataFrame] = []
        try:
            # 全部A股股票
            stock_list = self._em_sector_wrapper('001004', end_date)
            if stock_list is None:
                print('[em_stock_fs_cashflow_statement] failed to get stock id list')
                return False

            for indicator in (
                # 现金流量表-经营活动产生的现金流量
                "CASHFLOWSTATEMENT_9,CASHFLOWSTATEMENT_12,CASHFLOWSTATEMENT_13,CASHFLOWSTATEMENT_14,CASHFLOWSTATEMENT_16,CASHFLOWSTATEMENT_17,CASHFLOWSTATEMENT_64,CASHFLOWSTATEMENT_18,CASHFLOWSTATEMENT_186,CASHFLOWSTATEMENT_20,CASHFLOWSTATEMENT_120,CASHFLOWSTATEMENT_21,CASHFLOWSTATEMENT_10,CASHFLOWSTATEMENT_11,CASHFLOWSTATEMENT_22,CASHFLOWSTATEMENT_23,CASHFLOWSTATEMENT_25,CASHFLOWSTATEMENT_26,CASHFLOWSTATEMENT_30,CASHFLOWSTATEMENT_31,CASHFLOWSTATEMENT_32,CASHFLOWSTATEMENT_33,CASHFLOWSTATEMENT_195,CASHFLOWSTATEMENT_27,CASHFLOWSTATEMENT_28,CASHFLOWSTATEMENT_29,CASHFLOWSTATEMENT_34,CASHFLOWSTATEMENT_35,CASHFLOWSTATEMENT_37,CASHFLOWSTATEMENT_121,CASHFLOWSTATEMENT_38,CASHFLOWSTATEMENT_39",
                # 现金流量表-投资活动产生的现金流量
                "CASHFLOWSTATEMENT_40,CASHFLOWSTATEMENT_41,CASHFLOWSTATEMENT_42,CASHFLOWSTATEMENT_43,CASHFLOWSTATEMENT_232,CASHFLOWSTATEMENT_44,CASHFLOWSTATEMENT_45,CASHFLOWSTATEMENT_46,CASHFLOWSTATEMENT_48,CASHFLOWSTATEMENT_49,CASHFLOWSTATEMENT_50,CASHFLOWSTATEMENT_53,CASHFLOWSTATEMENT_51,CASHFLOWSTATEMENT_233,CASHFLOWSTATEMENT_52,CASHFLOWSTATEMENT_54,CASHFLOWSTATEMENT_55,CASHFLOWSTATEMENT_57,CASHFLOWSTATEMENT_122,CASHFLOWSTATEMENT_58,CASHFLOWSTATEMENT_59",
                # 现金流量表-筹资活动产生的现金流量
                "CASHFLOWSTATEMENT_60,CASHFLOWSTATEMENT_118,CASHFLOWSTATEMENT_61,CASHFLOWSTATEMENT_63,CASHFLOWSTATEMENT_62,CASHFLOWSTATEMENT_65,CASHFLOWSTATEMENT_66,CASHFLOWSTATEMENT_68,CASHFLOWSTATEMENT_69,CASHFLOWSTATEMENT_70,CASHFLOWSTATEMENT_119,CASHFLOWSTATEMENT_123,CASHFLOWSTATEMENT_71,CASHFLOWSTATEMENT_124,CASHFLOWSTATEMENT_72,CASHFLOWSTATEMENT_73,CASHFLOWSTATEMENT_75,CASHFLOWSTATEMENT_125,CASHFLOWSTATEMENT_76,CASHFLOWSTATEMENT_77",
                # 现金流量表-现金及现金等价物净增加
                "CASHFLOWSTATEMENT_78,CASHFLOWSTATEMENT_79,CASHFLOWSTATEMENT_80,CASHFLOWSTATEMENT_82,CASHFLOWSTATEMENT_83,CASHFLOWSTATEMENT_126,CASHFLOWSTATEMENT_127,CASHFLOWSTATEMENT_84",
                # 现金流量表-补充资料
                "CASHFLOWSTATEMENT_85,CASHFLOWSTATEMENT_86,CASHFLOWSTATEMENT_206,CASHFLOWSTATEMENT_87,CASHFLOWSTATEMENT_207,CASHFLOWSTATEMENT_88,CASHFLOWSTATEMENT_89,CASHFLOWSTATEMENT_208,CASHFLOWSTATEMENT_90,CASHFLOWSTATEMENT_91,CASHFLOWSTATEMENT_92,CASHFLOWSTATEMENT_93,CASHFLOWSTATEMENT_94,CASHFLOWSTATEMENT_95,CASHFLOWSTATEMENT_96,CASHFLOWSTATEMENT_209,CASHFLOWSTATEMENT_97,CASHFLOWSTATEMENT_98,CASHFLOWSTATEMENT_210,CASHFLOWSTATEMENT_99,CASHFLOWSTATEMENT_100,CASHFLOWSTATEMENT_101,CASHFLOWSTATEMENT_117,CASHFLOWSTATEMENT_102,CASHFLOWSTATEMENT_103,CASHFLOWSTATEMENT_105,CASHFLOWSTATEMENT_106,CASHFLOWSTATEMENT_107,CASHFLOWSTATEMENT_108,CASHFLOWSTATEMENT_212,CASHFLOWSTATEMENT_109,CASHFLOWSTATEMENT_110,CASHFLOWSTATEMENT_111,CASHFLOWSTATEMENT_112,CASHFLOWSTATEMENT_113,CASHFLOWSTATEMENT_114,CASHFLOWSTATEMENT_116",
            ):
                real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
                df = self._em_css_wrapper(stock_list, indicator, f"ReportDate={real_date},type=1,Ispandas=1")
                if df is None:
                    print('[em_stock_fs_cashflow_statement] failed to get data part1')
                    return False
                df = df.drop(columns='DATES')
                df_list.append(df)
            whole_data = pd.concat(df_list, axis=1)
            whole_data['DATES'] = real_date
            whole_data = whole_data.reset_index()
            self._data_helper._upload_raw(whole_data, EmStockFSCashflowStatement.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_stock_fs_income_statement_q(self, end_date: str):
        df_list: List[pd.DataFrame] = []
        try:
            # 全部A股股票
            stock_list = self._em_sector_wrapper('001004', end_date)
            if stock_list is None:
                print('[em_stock_fs_income_statement_q] failed to get stock id list')
                return False

            for indicator in (
                # 利润表(单季度)1
                "INCOMESTATEMENTQ_83,INCOMESTATEMENTQ_9,INCOMESTATEMENTQ_19,INCOMESTATEMENTQ_28,INCOMESTATEMENTQ_22,INCOMESTATEMENTQ_85,INCOMESTATEMENTQ_88,INCOMESTATEMENTQ_84,INCOMESTATEMENTQ_10,INCOMESTATEMENTQ_20,INCOMESTATEMENTQ_23,INCOMESTATEMENTQ_89,INCOMESTATEMENTQ_39,INCOMESTATEMENTQ_33,INCOMESTATEMENTQ_35,INCOMESTATEMENTQ_40,INCOMESTATEMENTQ_38,INCOMESTATEMENTQ_86,INCOMESTATEMENTQ_11,INCOMESTATEMENTQ_12,INCOMESTATEMENTQ_13,INCOMESTATEMENTQ_14,INCOMESTATEMENTQ_127,INCOMESTATEMENTQ_128,INCOMESTATEMENTQ_15,INCOMESTATEMENTQ_129,INCOMESTATEMENTQ_90,INCOMESTATEMENTQ_16,INCOMESTATEMENTQ_17,INCOMESTATEMENTQ_82,INCOMESTATEMENTQ_130,INCOMESTATEMENTQ_25,INCOMESTATEMENTQ_123,INCOMESTATEMENTQ_124,INCOMESTATEMENTQ_45,INCOMESTATEMENTQ_46,INCOMESTATEMENTQ_48,INCOMESTATEMENTQ_49,INCOMESTATEMENTQ_118,INCOMESTATEMENTQ_50,INCOMESTATEMENTQ_51,INCOMESTATEMENTQ_52,INCOMESTATEMENTQ_53,INCOMESTATEMENTQ_55,INCOMESTATEMENTQ_56,INCOMESTATEMENTQ_87,INCOMESTATEMENTQ_57,INCOMESTATEMENTQ_120,INCOMESTATEMENTQ_60,INCOMESTATEMENTQ_125,INCOMESTATEMENTQ_126,INCOMESTATEMENTQ_91,INCOMESTATEMENTQ_61,INCOMESTATEMENTQ_62,INCOMESTATEMENTQ_92,INCOMESTATEMENTQ_80,INCOMESTATEMENTQ_81,INCOMESTATEMENTQ_114,INCOMESTATEMENTQ_116,INCOMESTATEMENTQ_115,INCOMESTATEMENTQ_113,INCOMESTATEMENTQ_93,INCOMESTATEMENTQ_94,INCOMESTATEMENTQ_182",
                # 利润表(单季度)2
                "INCOMESTATEMENTQ_180",
            ):
                real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
                df = self._em_css_wrapper(stock_list, indicator, f"ReportDate={real_date},type=1,Ispandas=1")
                if df is None:
                    print('[em_stock_fs_income_statement_q] failed to get data part1')
                    return False
                df = df.drop(columns='DATES')
                df_list.append(df)
            whole_data = pd.concat(df_list, axis=1)
            whole_data['DATES'] = real_date
            whole_data = whole_data.reset_index()
            self._data_helper._upload_raw(whole_data, EmStockFSIncomeStatementQ.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_stock_fs_cashflow_statement_q(self, end_date: str):
        df_list: List[pd.DataFrame] = []
        try:
            # 全部A股股票
            stock_list = self._em_sector_wrapper('001004', end_date)
            if stock_list is None:
                print('[em_stock_fs_cashflow_statement_q] failed to get stock id list')
                return False

            for indicator in (
                # 现金流量表(单季度)-经营活动产生的现金流量
                "CASHFLOWSTATEMENTQ_9,CASHFLOWSTATEMENTQ_12,CASHFLOWSTATEMENTQ_13,CASHFLOWSTATEMENTQ_14,CASHFLOWSTATEMENTQ_16,CASHFLOWSTATEMENTQ_17,CASHFLOWSTATEMENTQ_64,CASHFLOWSTATEMENTQ_18,CASHFLOWSTATEMENTQ_186,CASHFLOWSTATEMENTQ_20,CASHFLOWSTATEMENTQ_120,CASHFLOWSTATEMENTQ_21,CASHFLOWSTATEMENTQ_10,CASHFLOWSTATEMENTQ_11,CASHFLOWSTATEMENTQ_22,CASHFLOWSTATEMENTQ_23,CASHFLOWSTATEMENTQ_25,CASHFLOWSTATEMENTQ_26,CASHFLOWSTATEMENTQ_30,CASHFLOWSTATEMENTQ_31,CASHFLOWSTATEMENTQ_32,CASHFLOWSTATEMENTQ_33,CASHFLOWSTATEMENTQ_195,CASHFLOWSTATEMENTQ_27,CASHFLOWSTATEMENTQ_28,CASHFLOWSTATEMENTQ_29,CASHFLOWSTATEMENTQ_34,CASHFLOWSTATEMENTQ_35,CASHFLOWSTATEMENTQ_37,CASHFLOWSTATEMENTQ_121,CASHFLOWSTATEMENTQ_38,CASHFLOWSTATEMENTQ_39,CASHFLOWSTATEMENTQ_192",
                # 现金流量表(单季度)-投资活动产生的现金流量
                "CASHFLOWSTATEMENTQ_40,CASHFLOWSTATEMENTQ_41,CASHFLOWSTATEMENTQ_42,CASHFLOWSTATEMENTQ_43,CASHFLOWSTATEMENTQ_232,CASHFLOWSTATEMENTQ_44,CASHFLOWSTATEMENTQ_45,CASHFLOWSTATEMENTQ_46,CASHFLOWSTATEMENTQ_48,CASHFLOWSTATEMENTQ_49,CASHFLOWSTATEMENTQ_50,CASHFLOWSTATEMENTQ_53,CASHFLOWSTATEMENTQ_51,CASHFLOWSTATEMENTQ_233,CASHFLOWSTATEMENTQ_52,CASHFLOWSTATEMENTQ_54,CASHFLOWSTATEMENTQ_57,CASHFLOWSTATEMENTQ_55,CASHFLOWSTATEMENTQ_122,CASHFLOWSTATEMENTQ_59,CASHFLOWSTATEMENTQ_58",
                # 现金流量表(单季度)-筹资活动产生的现金流量
                "CASHFLOWSTATEMENTQ_60,CASHFLOWSTATEMENTQ_118,CASHFLOWSTATEMENTQ_61,CASHFLOWSTATEMENTQ_63,CASHFLOWSTATEMENTQ_62,CASHFLOWSTATEMENTQ_65,CASHFLOWSTATEMENTQ_66,CASHFLOWSTATEMENTQ_68,CASHFLOWSTATEMENTQ_69,CASHFLOWSTATEMENTQ_70,CASHFLOWSTATEMENTQ_119,CASHFLOWSTATEMENTQ_123,CASHFLOWSTATEMENTQ_71,CASHFLOWSTATEMENTQ_124,CASHFLOWSTATEMENTQ_72,CASHFLOWSTATEMENTQ_73,CASHFLOWSTATEMENTQ_75,CASHFLOWSTATEMENTQ_125,CASHFLOWSTATEMENTQ_76,CASHFLOWSTATEMENTQ_77",
                # 现金流量表(单季度)-现金及现金等价物净增加
                "CASHFLOWSTATEMENTQ_78,CASHFLOWSTATEMENTQ_79,CASHFLOWSTATEMENTQ_80,CASHFLOWSTATEMENTQ_82,CASHFLOWSTATEMENTQ_83,CASHFLOWSTATEMENTQ_126,CASHFLOWSTATEMENTQ_127,CASHFLOWSTATEMENTQ_84",
            ):
                real_date = RawDataHelper.get_prev_target_date(end_date, QUARTER_UPDATE_DATE_LIST)
                df = self._em_css_wrapper(stock_list, indicator, f"ReportDate={real_date},type=1,Ispandas=1")
                if df is None:
                    print('[em_stock_fs_cashflow_statement_q] failed to get data part1')
                    return False
                df = df.drop(columns='DATES')
                df_list.append(df)
            whole_data = pd.concat(df_list, axis=1)
            whole_data['DATES'] = real_date
            whole_data = whole_data.reset_index()
            self._data_helper._upload_raw(whole_data, EmStockFSCashflowStatementQ.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_stock_ipo_info(self, today):
        try:
            with RawDatabaseConnector().managed_session() as db_session:
                query = db_session.query(EmStockIpoInfo) #EmStockIpoInfo  #EmConvBondIpoInfo
                existed_df = pd.read_sql(query.statement, query.session.bind)

            _update_code = existed_df[ (existed_df.LISTDATE.isnull())
                | (existed_df.SUCRATIOONL.isnull())
                | (existed_df.IPOPE.isnull())
                | (existed_df.IPOPRICE.isnull()) ].CODES.tolist()
            data = c.sector("001019", today)
            codes = [i for i in data.Data if '.' in i]
            code_list = list(set(codes + _update_code))
            data = c.css(code_list,"IPOPRICE,IPOISSUEDATE,IPOSHARESVOL,IPOPE,PURCHACODEONL,SUCRATIOONL,NAME,CEILINGONL,EMIND2016,TRADEMARKET,IPOPURCHDATEONL,IPOANNCDATE,WSZQJGGGDATE,LISTDATE,ISSUEAMTONL,LOTNUM,COMPROFILE,BUSINESS","ClassiFication=1,Ispandas=1")
            data = data.reset_index().drop(columns=['DATES'])
            total_data = existed_df[~existed_df.CODES.isin(data.CODES)].append(data)
            self._data_helper._upload_raw(total_data, EmStockIpoInfo.__table__.name, to_truncate=True)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_conv_bond_ipo_info(self, today):
        try:
            with RawDatabaseConnector().managed_session() as db_session:
                query = db_session.query(EmConvBondIpoInfo)
                existed_df = pd.read_sql(query.statement, query.session.bind)
            data_1 = self._em_sector_wrapper('620002005',today) # 正在发行可转债
            if data_1 is not None:
                codes_1 = [i for i in data_1 if '.' in i]
            else:
                codes_1 = []
            data_2 = c.sector('620001005',today) # 待发行可转债
            if data_2.ErrorCode == 0:
                codes_2 = [i for i in data_2.Codes if '.' in i]
            else:
                codes_2 = []
            data_3 = self._em_sector_wrapper('620003005', today) # 待上市可转债
            if data_3 is not None:
                codes_3 = [i for i in data_3 if '.' in i]
            else:
                codes_3 = []
            code_list = list(set(codes_1 + codes_2 + codes_3))
            data = self._em_css_wrapper(code_list, "CBCODE,CBNAME,CBSTOCKCODE,CBSTOCKNAME,CBISSUEAMT,IPOANNCDATE,CBIPOTYPE,CBPURCODEONL,ISSRATE,CBTERM,CBISSUEPRICE,ISSUEONLEDATE,CBCONVPRICE,CBDATEONL,CBLISTDATE,CBRESULTDATE,CBSUCRATEONL,QUANTLIMITINTRO,CBMATURITYDATE,CBREDEMPRICETM,CBRATIONCODE,CBSUCCESS,CBPUTBACKPRICEEXPLAIN,CBREDEMMEMO", "Ispandas=1")
            data = data.reset_index().drop(columns=['DATES'])
            total_data = existed_df[~existed_df.CODES.isin(data.CODES)].append(data)
            self._data_helper._upload_raw(total_data, EmConvBondIpoInfo.__table__.name, to_truncate=True)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_bond_clean_price(self, start_date: str, end_date: str, bond_list: Tuple[str] = ()):
        BLACK_SHEET = ['175449.SH', '175471.SH', 'n16042138.SH', 'n20110693.SZ', 'n20102723.SH', 'n20102361.SH',
                       'n20111636.SZ', 'n20111657.SZ', 'n20111659.SZ', 'n20111675.SZ', 'n20111676.SZ', 'n20111677.SZ', 'n20111960.SZ',
                       'n20112000.SZ', 'n20112011.SZ', 'n20112078.SZ', 'n20112209.SH', 'n20112210.SH', 'n20112503.SZ', 'n20112504.SZ',
                       'n20112507.SZ', 'n20112615.SH', 'n20112700.SZ', 'n20112805.SH', 'n20113015.SH', 'n20113027.SZ', 'n20113071.SH']

        try:
            # 获取区间内所有交易日
            tradedates = self._em_tradedates_wrapper(start_date, end_date, "period=1,order=1,market=CNSESH")
            if tradedates is None:
                print('[em_bond_clean_price] failed to get trade dates')
                return False
            if len(tradedates) == 0:
                print(f'[em_bond_clean_price] no trade dates, return immediately (start_date){start_date} (end_date){end_date}')
                return False

            if not bond_list:
                # 从bond info获取bond list
                bond_info = RawDataApi().get_em_bond_info()
                if bond_info is None:
                    print('[em_bond_clean_price] failed to get bond id list')
                    return False
                bond_info = bond_info[bond_info.bond_id.str.endswith('.SH', na=False) | bond_info.bond_id.str.endswith('.SZ', na=False)]
                bond_info = bond_info[~bond_info.bond_id.isin(BLACK_SHEET)]
                bond_list = list(bond_info.bond_id.unique())

            split_num = 1
            while (len(bond_list) / split_num) > 1000:
                split_num *= 10
            print(f'[em_bond_clean_price] (split num){split_num} (total){len(bond_list)}')

            df_list: List[pd.DataFrame] = []
            for date in tradedates:
                # for i in range(0, len(bond_list), split_num):
                    # bond_list_part = bond_list[i:i+split_num]
                    # print(bond_list_part)
                # 获取债券价格信息
                part_df = self._em_css_wrapper(bond_list,
                                                'PRECLOSE,OPEN,HIGH,LOW,CLOSE',
                                                f'TradeDate={date},type=1,Ispandas=1')
                if part_df is None:
                    print(f'[em_bond_clean_price] failed to get bond price info (start_date){start_date} (end_date){end_date}')
                    return False
                part_df['DATES'] = date
                df_list.append(part_df)
                print(f'[em_bond_clean_price] {date} done')
            df = pd.concat(df_list)
            df = df[df.CLOSE.notna()]
            df['DATES'] = pd.to_datetime(df.DATES, infer_datetime_format=True).dt.date
            # 只保留trading day的数据
            df = df.reset_index().pivot(index='DATES', columns='CODES').reindex(tradedates)
            df = df.stack().reset_index().rename(columns=lambda x: EmBondCleanPrice.__getattribute__(EmBondCleanPrice, x).name)
            # 更新到db
            self._data_helper._upload_raw(df, EmBondCleanPrice.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_bond_dirty_price(self, start_date: str, end_date: str, bond_list: Tuple[str] = ()):
        BLACK_SHEET = ['175449.SH', '175471.SH', 'n16042138.SH', 'n20110693.SZ', 'n20102723.SH', 'n20102361.SH',
                       'n20111636.SZ', 'n20111657.SZ', 'n20111659.SZ', 'n20111675.SZ', 'n20111676.SZ', 'n20111677.SZ', 'n20111960.SZ',
                       'n20112000.SZ', 'n20112011.SZ', 'n20112078.SZ', 'n20112209.SH', 'n20112210.SH', 'n20112503.SZ', 'n20112504.SZ',
                       'n20112507.SZ', 'n20112615.SH', 'n20112700.SZ', 'n20112805.SH', 'n20113015.SH', 'n20113027.SZ', 'n20113071.SH']

        try:
            # 获取区间内所有交易日
            tradedates = self._em_tradedates_wrapper(start_date, end_date, "period=1,order=1,market=CNSESH")
            if tradedates is None:
                print('[em_bond_dirty_price] failed to get trade dates')
                return False
            if len(tradedates) == 0:
                print(f'[em_bond_dirty_price] no trade dates, return immediately (start_date){start_date} (end_date){end_date}')
                return False

            if not bond_list:
                # 从bond info获取bond list
                bond_info = RawDataApi().get_em_bond_info()
                if bond_info is None:
                    print('[em_bond_dirty_price] failed to get bond id list')
                    return False
                bond_info = bond_info[bond_info.bond_id.str.endswith('.SH', na=False) | bond_info.bond_id.str.endswith('.SZ', na=False)]
                bond_info = bond_info[~bond_info.bond_id.isin(BLACK_SHEET)]
                bond_list = list(bond_info.bond_id.unique())

            df_list: List[pd.DataFrame] = []
            for date in tradedates:
                # for i in range(0, len(bond_list), split_num):
                    # bond_list_part = bond_list[i:i+split_num]
                    # print(bond_list_part)
                # 获取债券价格信息
                part_df = self._em_css_wrapper(bond_list,
                                               'PRECLOSE,OPEN,HIGH,LOW,CLOSE,VOLUME,AMOUNT',
                                               f'TradeDate={date},type=2,Ispandas=1')
                if part_df is None:
                    print(f'[em_bond_dirty_price] failed to get bond price info (start_date){start_date} (end_date){end_date}')
                    return False
                part_df['DATES'] = date
                df_list.append(part_df)
                print(f'[em_bond_dirty_price] {date} done')
            df = pd.concat(df_list)
            df = df[df.CLOSE.notna()]
            df['DATES'] = pd.to_datetime(df.DATES, infer_datetime_format=True).dt.date
            # 只保留trading day的数据
            df = df.reset_index().pivot(index='DATES', columns='CODES').reindex(tradedates)
            df = df.stack().reset_index().rename(columns=lambda x: EmBondDirtyPrice.__getattribute__(EmBondDirtyPrice, x).name)
            # 更新到db
            self._data_helper._upload_raw(df, EmBondDirtyPrice.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_conv_bond_clean_price(self, start_date: str, end_date: str, bond_list: Tuple[str] = ()):
        try:
            # 获取区间内所有交易日
            tradedates = self._em_tradedates_wrapper(start_date, end_date, "period=1,order=1,market=CNSESH")
            if tradedates is None:
                print('[em_conv_bond_clean_price] failed to get trade dates')
                return False
            if len(tradedates) == 0:
                print(f'[em_conv_bond_clean_price] no trade dates, return immediately (start_date){start_date} (end_date){end_date}')
                return False

            if not bond_list:
                # 东财分类(含到期) 可转换债券
                bond_list = self._em_sector_wrapper('617012', end_date)
                if bond_list is None:
                    print('[em_conv_bond_clean_price] failed to get bond id list')
                    return False

            # 获取债券价格信息
            df = self._em_csd_wrapper(bond_list,
                                      'OPEN,CLOSE,HIGH,LOW,PRECLOSE,AVERAGE,VOLUME,AMOUNT',
                                      start_date, end_date, "type=1,period=1,adjustflag=1,curtype=1,order=1,market=0,Ispandas=1")
            if df is None:
                print(f'[em_conv_bond_clean_price] failed to get bond price info (start_date){start_date} (end_date){end_date}')
                return False
            df = df[df.CLOSE.notna()]
            df['DATES'] = pd.to_datetime(df.DATES, infer_datetime_format=True).dt.date
            # 只保留trading day的数据
            df = df.reset_index().pivot(index='DATES', columns='CODES').reindex(tradedates)
            df = df.stack().reset_index().rename(columns=lambda x: EmConvBondCleanPrice.__getattribute__(EmConvBondCleanPrice, x).name)
            # 更新到db
            self._data_helper._upload_raw(df, EmConvBondCleanPrice.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_conv_bond_dirty_price(self, start_date: str, end_date: str, bond_list: Tuple[str] = ()):
        try:
            # 获取区间内所有交易日
            tradedates = self._em_tradedates_wrapper(start_date, end_date, "period=1,order=1,market=CNSESH")
            if tradedates is None:
                print('[em_conv_bond_dirty_price] failed to get trade dates')
                return False
            if len(tradedates) == 0:
                print(f'[em_conv_bond_dirty_price] no trade dates, return immediately (start_date){start_date} (end_date){end_date}')
                return False

            if not bond_list:
                # 东财分类(含到期) 可转换债券
                bond_list = self._em_sector_wrapper('617012', end_date)
                if bond_list is None:
                    print('[em_conv_bond_dirty_price] failed to get bond id list')
                    return False

            # 获取债券价格信息
            df = self._em_csd_wrapper(bond_list,
                                      'OPEN,CLOSE,HIGH,LOW,PRECLOSE,AVERAGE',
                                      start_date, end_date, "type=2,period=1,adjustflag=1,curtype=1,order=1,market=0,Ispandas=1")
            if df is None:
                print(f'[em_conv_bond_dirty_price] failed to get bond price info (start_date){start_date} (end_date){end_date}')
                return False
            df = df[df.CLOSE.notna()]
            df['DATES'] = pd.to_datetime(df.DATES, infer_datetime_format=True).dt.date
            # 只保留trading day的数据
            df = df.reset_index().pivot(index='DATES', columns='CODES').reindex(tradedates)
            df = df.stack().reset_index().rename(columns=lambda x: EmConvBondDirtyPrice.__getattribute__(EmConvBondDirtyPrice, x).name)
            # 更新到db
            self._data_helper._upload_raw(df, EmConvBondDirtyPrice.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_future_price(self, start_date, end_date):
        # 目前没有future info 先在这里hard code the list of futures
        future_list = ['CN00Y.SG','TY00Y.CBT','SI00Y.CMX','CL00Y.NYM','GC00Y.CMX','CPRC.LME','HG00Y.CMX','A0.DCE','AG0.SHF',
                       'AL0.SHF','AP0.CZC','AU0.SHF','B0.DCE','BB0.DCE','BCM.INE','BU0.SHF','C0.DCE','CF0.CZC','CJ0.CZC','CS0.DCE',
                       'CU0.SHF','CY0.CZC','EB0.DCE','EG0.DCE','FB0.DCE','FG0.CZC','FU0.SHF','HC0.SHF','I0.DCE','J0.DCE','JD0.DCE','JM0.DCE',
                       'JR0.CZC','L0.DCE','LH0.DCE','LR0.CZC','LUM.INE','M0.DCE','MA0.CZC','NI0.SHF','NRM.INE','OI0.CZC','P0.DCE','PB0.SHF','PF0.CZC',
                       'PG0.DCE','PK0.CZC','PM0.CZC','PP0.DCE','RB0.SHF','RI0.CZC','RM0.CZC','RR0.DCE','RS0.CZC','RU0.SHF','SA0.CZC','SCM.INE',
                       'SF0.CZC','SM0.CZC','SN0.SHF','SP0.SHF','SR0.CZC','SS0.SHF','TA0.CZC','UR0.CZC','V0.DCE','WH0.CZC','WR0.SHF','Y0.DCE','ZC0.CZC','ZN0.SHF']
        l = "A0.DCE,AG0.SHF,AL0.SHF,AP0.CZC,AU0.SHF,B0.DCE,BB0.DCE,BCM.INE,BU0.SHF,C0.DCE,CF0.CZC,CJ0.CZC,CS0.DCE,CU0.SHF,CY0.CZC,EB0.DCE,EG0.DCE,FB0.DCE,FG0.CZC,FU0.SHF,HC0.SHF,I0.DCE,J0.DCE,JD0.DCE,JM0.DCE,JR0.CZC,L0.DCE,LH0.DCE,LR0.CZC,LUM.INE,M0.DCE,MA0.CZC,NI0.SHF,NRM.INE,OI0.CZC,P0.DCE,PB0.SHF,PF0.CZC,PG0.DCE,PK0.CZC,PM0.CZC,PP0.DCE,RB0.SHF,RI0.CZC,RM0.CZC,RR0.DCE,RS0.CZC,RU0.SHF,SA0.CZC,SCM.INE,SF0.CZC,SM0.CZC,SN0.SHF,SP0.SHF,SR0.CZC,SS0.SHF,TA0.CZC,UR0.CZC,V0.DCE,WH0.CZC,WR0.SHF,Y0.DCE,ZC0.CZC,ZN0.SHF"
        future_list = list(set(l.split(',') + future_list))
        try:
            start_date = pd.to_datetime(start_date, infer_datetime_format=True) - datetime.timedelta(days=FUTURE_PRICE_EXTRA_TRADE_DAYS)
            start_date = start_date.strftime('%Y%m%d')
            # 获取期货价格信息
            df = self._em_csd_wrapper(future_list, "CLOSE,OPEN,HIGH,LOW,CLEAR,PRECLOSE,PRECLEAR,UNIHQOI,UNIVOLUME,UNIAMOUNT,SPREAD,MAINFORCE",
                                        start_date, end_date, "period=1,adjustflag=1,curtype=1,order=1,market=0,Ispandas=1")
            if df is None:
                print(f'[em_future_price] failed to get future price info (start_date){start_date} (end_date){end_date}')
                return False
            df = df[df.CLOSE.notna()]
            df['DATES'] = pd.to_datetime(df.DATES, infer_datetime_format=True).dt.date
            df = df.reset_index().rename(columns=lambda x: EmFuturePrice.__getattribute__(EmFuturePrice, x).name)
            # TODO: 原子执行下边两行
            RawDataApi().delete_em_future_price(start_date, end_date, df.future_id.to_list())
            self._data_helper._upload_raw(df, EmFuturePrice.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_stock_future_diff(self, start_date, end_date):
        try:
            start_date = datetime.datetime.strptime(start_date, '%Y%m%d') - datetime.timedelta(days=FUND_NAV_EXTRA_TRADE_DAYS)
            start_date = start_date.strftime('%Y%m%d')
            data=c.edb("EMM00597133,EMM00597134,EMM00597135,EMM00597136,EMM00597137,EMM00597138,EMM00597139,EMM00597140,EMM00597141,EMM00597142,EMM00597143,EMM00597144,EMM00599973,EMM00599974,EMM00599975,EMM00599976,EMM00599977,EMM00599978,EMM00599979,EMM00599980,EMM00599981,EMM00599982,EMM00599983,EMM00599984,EMM00599985,EMM00599986,EMM00599987,EMM00599988,EMM00599989,EMM00599990", f"IsLatest=0,StartDate={start_date},EndDate={end_date},Ispandas=1")
            data = data.dropna().reset_index()
            RawDataApi().delete_em_stock_future_diff(start_date, end_date)
            self._data_helper._upload_raw(data, EmStockFutureDiff.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_north_capital(self, start_date, end_date):
        try:
            data_north_SH = self._em_ctr_wrapper("TransactionSHHKInfo","TRADEDATE,NETIF_SH",f"period=1,StartDate={start_date},EndDate={end_date},Ispandas=1")
            data_north_SH = pd.DataFrame(data_north_SH).T.rename(columns={0:'datetime',1:'sh_hk_sc'})
            data_north_SZ = self._em_ctr_wrapper("TransactionSZHKInfo","TRADEDATE,NETIF_SZ",f"period=1,StartDate={start_date},EndDate={end_date},Ispandas=1")
            data_north_SZ = pd.DataFrame(data_north_SZ).T.rename(columns={0:'datetime',1:'sz_hk_sc'})
            if not data_north_SZ.empty or not data_north_SH.empty:
                df = pd.merge(data_north_SH,data_north_SZ,on='datetime',how='outer')
                df.loc[:,'north_cap'] = df['sh_hk_sc'].add(df['sz_hk_sc'],fill_value=0)
                df = df.sort_values('datetime')
                self._data_helper._upload_raw(df, EMNorthCapital.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_south_capital(self, start_date, end_date):
        try:
            data_north_SH=c.ctr("TransactionSHHKInfo","TRADEDATE,NETIF_H",f"period=1,StartDate={start_date},EndDate={end_date},Ispandas=1")
            data_north_SH=pd.DataFrame(data_north_SH.Data).T.rename(columns={0:'datetime',1:'hk_sh_sc'})

            data_north_SZ=c.ctr("TransactionSZHKInfo","TRADEDATE,NETIF_H",f"period=1,StartDate={start_date},EndDate={end_date},Ispandas=1")
            data_north_SZ=pd.DataFrame(data_north_SZ.Data).T.rename(columns={0:'datetime',1:'hk_sz_sc'})
            df = pd.merge(data_north_SH,data_north_SZ,on='datetime',how='outer')
            df.loc[:,'south_cap'] = df['hk_sh_sc'].add(df['hk_sz_sc'],fill_value=0)
            df.loc[:,'south_cap'] = df['hk_sh_sc'].add(df['hk_sz_sc'],fill_value=0)
            df = df.sort_values('datetime')
            self._data_helper._upload_raw(df, EMSouthCapital.__table__.name)
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_future_info_detail(self, start_date):
        try:
            future_info_dic={
                'CODES':'em_id',
                'NAME':'desc_name',               
                'TRADINGCODE':'trading_code',
                'FTMKTSNAME':'mkt_name',
                'FTPRICELIMIT':'price_limit',
                'FTTRANSMARGIN':'trans_margin',
                'FTDELIVMONTH':'deliv_month',
                'FTQUTOBPRICE':'quote_price',
                'FTCONTRAENGSNAME':'short_eng_name',
                'FTCONTRAENGNAME':'eng_name',
                'DELIVERYDATE':'deliver_date',
                'STARTTRADEDATE':'start_trade_date',
                'LASTTRADEDATE':'last_trade_date',
                'LONGMARGIN':'long_margin',
                'SHORTMARGIN':'short_margin',
                'PRICELIMITRANGE':'price_limit_range',
                'FTTRANSTYPE':'trans_type',
                'FTTRANSUNIT':'trans_unit',
                'CONTRACTMUL':'contract_mul',
                'FTPRICEUNIT':'price_unit',
                'FTMINPRICECHG':'min_price_change',
                'LISTDATE':'list_standard_date',
                'FTCONTRADATEINTRO':'contract_date_info',
                'FTTRANSDATEINSTRO':'trans_date_info',
                'FTLTRANSDATE':'last_trans_date',
                'FTDELIVDATEINTRO':'deliver_date_info',
                'FTFIRSTTRANSMARGIN':'first_trans_margin',
                }
            code_list = []
            for exchange_i, detail1 in FUTURE_SECTOR.items():
                for product_i, detail2 in detail1.items():
                    for run_stat, sector_id in detail2.items():
                        if run_stat == '运作':                            
                            try:
                                code_list.extend(c.sector(sector_id,start_date).Codes)
                            except:
                                print(exchange_i, product_i, run_stat, sector_id,'failed')

            # 去除所有中金所合约
            tickers = [i for i in code_list if 'CFE' not in i]
            tickers = list(set(tickers))
            # 获取期货合约信息
            exsited_fund_info = RawDataApi().get_em_future_info()
            info=c.css(tickers,"NAME,EMCODE,TRADINGCODE,FTMKTSNAME,FTPRICELIMIT,FTTRANSMARGIN,FTDELIVMONTH,FTQUTOBPRICE,FTCONTRAENGSNAME,FTCONTRAENGNAME,DELIVERYDATE,STARTTRADEDATE,LASTTRADEDATE,LONGMARGIN,SHORTMARGIN,PRICELIMITRANGE,FTTRANSTYPE,FTTRANSUNIT,CONTRACTMUL,FTPRICEUNIT,FTMINPRICECHG,LISTDATE,FTCONTRADATEINTRO,FTTRANSDATEINSTRO,FTLTRANSDATE,FTDELIVDATEINTRO,FTFIRSTTRANSMARGIN",f"TradeDate={start_date}, Ispandas=1")
            info = info.reset_index()[future_info_dic.keys()].rename(columns=future_info_dic)
            new_info = info[~info.em_id.isin(exsited_fund_info.em_id)]
            self._data_helper._upload_raw(new_info, EmFutureInfoDetail.__table__.name)
            return True

        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def em_future_price_detail(self, start_date):
        try:
            future_price_dic_dev = {
                "CODES":"em_id",
                "DATES" :"datetime",
                "OPEN":"open",
                "CLOSE":"close", 
                "HIGH":"high",                                          
                "LOW":"low", 
                "PRECLOSE":"pre_close", 
                "AVERAGE":"average_price", 
                "SPREAD":"spread", 
                "CLEAR":"clear", 
                "PRECLEAR":"pre_clear",  
                "MAINFORCE":"mainforce", 
                "UNIVOLUME":"uni_volume", 
                "UNIAMOUNT":"uni_amount", 
                "UNIHQOI":"uni_oi", 
                "UNICHANGEOI":"uni_change_oi", 
            }
            fund_info = RawDataApi().get_em_future_info()
            tickers = fund_info[fund_info.deliver_date >= pd.to_datetime(start_date).date()].em_id.tolist()
            tickers = [i for i in tickers if 'CFE' not in i]
            data = self._em_csd_wrapper(tickers, "OPEN,CLOSE,HIGH,LOW,PRECLOSE,AVERAGE,CHANGE,PCTCHANGE,VOLUME,AMOUNT,SPREAD,CLEAR,PRECLEAR,PCTCHANGECLEAR,CHANGECLEAR,UNIHQOI,UNICHANGEOI,AMPLITUDE,MAINFORCE,UNIVOLUME,UNIAMOUNT",
                            start_date, start_date, "period=1,adjustflag=1,curtype=1,order=1,market=0,Ispandas=1")
            if data is None:
                return True
            data = data.reset_index()[future_price_dic_dev.keys()].rename(columns=future_price_dic_dev)
            data = data.dropna(subset=['close'])
            self._data_helper._upload_raw(data, EmFuturePriceDetail.__table__.name)
            return True

        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def download_all(self, start_date, end_date):
        failed_tasks = []
        # If em_tradedates fails, there is no trading day between start_date and end_date
        # Stop and return

        # 这里先更新，更新完之后可以看一下中证指数的列表
        if not self.em_index_component(start_date, end_date):
            failed_tasks.append('em_index_component')

        index_info_df = BasicDataApi().get_index_info()
        if index_info_df is None:
            failed_tasks.append('retrieve data for em_index_price')
        else:
            index_info_df = index_info_df[index_info_df.price_source == IndexPriceSource.default]
            index_ids = set(index_info_df.em_id.to_list())
            index_ids.discard(None)
            if self._index_block_list is not None:
                index_ids -= self._index_block_list
            if not self.em_index_price(index_ids, start_date, end_date):
                failed_tasks.append('em_index_price')

        if not self.em_index_val(start_date, end_date):
            failed_tasks.append('em_index_val')

        # 必须作为fund数据更新的第一个
        if not self.em_fund_list(start_date, end_date):
            failed_tasks.append('em_fund_list')

        if not self.em_fund_nav(start_date, end_date):
            failed_tasks.append('em_fund_nav')

        if not self.em_macroeconomic_daily(start_date, end_date):
            failed_tasks.append('em_macroeconomic_daily')

        if not self.em_tradedates(start_date, end_date):
            failed_tasks.append('em_tradedates')
            return failed_tasks

        if not self.em_stock_info(end_date):
            failed_tasks.append('em_stock_info')

        if not self.em_stock_price(start_date, end_date):
            failed_tasks.append('em_stock_price')

        if not self.em_stock_post_price(start_date, end_date):
            failed_tasks.append('em_stock_post_price')

        if not self.em_stock_daily_info(start_date, end_date):
            failed_tasks.append('em_stock_daily_info')

        if 'em_fund_list' not in failed_tasks:
            new_fund_list, delisted_fund_list = RawDataHelper.get_new_and_delisted_fund_list(end_date)
            if new_fund_list is None and delisted_fund_list is None:
                failed_tasks.append('get_new_and_delisted_fund_list')
            else:
                # 摘牌基金在这里也强制更新下以更新end_date
                if not self.em_fund_info(new_fund_list | delisted_fund_list):
                    failed_tasks.append('em_fund_info')
                if not self.em_fund_fee(new_fund_list):
                    failed_tasks.append('em_fund_fee')

        if not self.em_fund_status(end_date, is_history=False):
            failed_tasks.append('em_fund_status')

        if not self.em_macroeconomic_price(start_date, end_date):
            failed_tasks.append('em_macroeconomic_price')

        if not self.em_fund_rate(end_date):
            failed_tasks.append('em_fund_rate')

        if not self.em_fund_benchmark(end_date):
            failed_task.append('em_fund_benchmark')

        if not self.em_macroeconomic_monthly():
            failed_tasks.append('em_macroeconomic_monthly')

        if not self.em_stock_industrial_capital(end_date, is_history=False):
            failed_tasks.append('em_stock_industrial_capital')

        if not self.em_stock_to_hk_connect(end_date):
            failed_tasks.append('em_stock_to_hk_connect')

        if not self.em_stock_industrial_capital_trade_detail(start_date, end_date):
            failed_tasks.append('em_stock_industrial_capital_trade_detail')

        if not self.em_stock_research_info(end_date):
            failed_tasks.append('em_stock_research_info')

        if not self.em_stock_refinancing(start_date, end_date):
            failed_tasks.append('em_stock_refinancing')

        if not self.em_stock_refinancing_impl(start_date, end_date):
            failed_tasks.append('em_stock_refinancing_impl')

        if not self.em_conv_bond_clean_price(start_date, end_date):
            failed_tasks.append('em_conv_bond_clean_price')

        if not self.em_conv_bond_dirty_price(start_date, end_date):
            failed_tasks.append('em_conv_bond_dirty_price')

        if not self.em_bond_clean_price(start_date, end_date):
            failed_tasks.append('em_bond_clean_price')

        if not self.em_bond_dirty_price(start_date, end_date):
            failed_tasks.append('em_bond_dirty_price')

        if not self.em_future_price(start_date, end_date):
            failed_tasks.append('em_future_price')

        if not self.em_us_stock_history(start_date, end_date):
            failed_tasks.append('em_us_stock_price')

        if not self.em_stock_future_diff(start_date, end_date):
            failed_tasks.append('em_stock_future_diff')

        if not self.em_north_capital(start_date, end_date):
            failed_tasks.append('em_north_capital')

        if not self.em_south_capital(start_date, end_date):
            failed_tasks.append('em_south_capital')

        if not self.em_future_info_detail(start_date):
            failed_tasks.append('em_future_info_detail')

        if not self.em_future_price_detail(start_date):
            failed_tasks.append('em_future_price_detail')

        # 获取下一个交易日
        trading_day_df = RawDataApi().get_em_tradedates(start_date=end_date)
        if trading_day_df.shape[0] <= 1:
            print(f'get trading days start with {end_date} failed')
            failed_tasks.append('get_em_tradedates for weekly update in raw')
        else:
            next_trading_day = trading_day_df.iloc[1, :].TRADEDATES
            print(f'got next trading day {next_trading_day}')
            end_date_dt = pd.to_datetime(end_date, infer_datetime_format=True).date()
            next_trading_dt = pd.to_datetime(next_trading_day, infer_datetime_format=True).date()

            next_trading_dt_str = str(next_trading_dt)
            if not self.em_stock_ipo_info(next_trading_dt_str):
                failed_tasks.append('em_stock_ipo_info')

            if not self.em_conv_bond_ipo_info(next_trading_dt_str):
                failed_tasks.append('em_conv_bond_ipo_info')

            if end_date_dt.weekday() < next_trading_dt.weekday() and next_trading_dt < end_date_dt + datetime.timedelta(weeks=1):
                # 表明本周后边还有交易日，今天不需要更新
                print(f'weekly data only update on the last day of week, not today {end_date_dt}')
            else:
                if not self.em_fund_scale(end_date):
                    failed_tasks.append('em_fund_scale')

                if not self.em_fund_asset(end_date):
                    failed_tasks.append('em_fund_asset')

                if not self.em_fund_holding_rate(end_date):
                    failed_tasks.append('em_fund_holding_rate')

                if not self.em_fund_stock(end_date):
                    failed_tasks.append('em_fund_stock')

                if not self.em_fund_stock_qdii(end_date):
                    failed_tasks.append('em_fund_stock_qdii')

                if not self.em_fund_bond(end_date):
                    failed_tasks.append('em_fund_bond')

                if not self.em_fund_industry(end_date):
                    failed_tasks.append('em_fund_industry')

                if not self.em_fund_industry_qdii(end_date):
                    failed_tasks.append('em_fund_industry_qdii')

                if not self.em_stock_fin_fac(end_date):
                    failed_tasks.append('em_stock_fin_fac')

        return failed_tasks


if __name__ == '__main__':
    em = EmRawDataDownloader(RawDataHelper())
    # em.em_tradedates('20000101', '20091231')
    # em.em_index_val('20210512', '20210512')
    # em.em_fund_nav('20110201', '20110323')
    # em.em_index_price_history('H00140.SH', '20050101', '20200419')
    # em.em_fund_scale_history()
    # em.em_fund_scale('20210219')
    # em.em_stock_fin_fac('20201231')
    # em.em_stock_info('20200424')
    # em.em_stock_price('20210112', '20210112')
    # em.em_stock_post_price('20210125', '20210125')
    # em.em_stock_daily_info('20041231', '20041231')
    # em.em_stock_price_history('./')
    # em.em_stock_post_price_history('./')
    # em.em_stock_daily_info_history('./')
    # em.em_stock_refinancing('20100101', '20141231')
    # em.em_stock_refinancing_impl('20000101', '20091231')
    # em.add_columns_to_fin_fac('20190930')
    # em.em_fund_status('20200513')
    # em.em_index_component('20200528', '20200529')
    # em.em_fund_list('20200702', '20200702')
    # em.em_fund_info_history('20200707')
    # em.em_fund_benchmark_history('20200929', '20201004')
    # em.em_index_info(['399972.SZ'])
    # em.em_fund_info({'010000.OF', '010051.OF', '010150.OF', '970009.OF', '970010.OF'})
    # em.em_stock_estimate_fac('20200101', '20200709', 2020)
    # em.cs_index_component('20200713')
    # em.em_macroeconomic_price('20210319', '20210319')
    # em.em_fund_fee_history('20200715')
    # em.em_fund_asset('20200819')
    # em.em_fund_holding_rate_history('20200819')
    # em.em_macroeconomic_monthly_history(['EMI00120309', 'EMI00120291'], '19920201', '20210518')
    # em.em_macroeconomic_monthly()
    # em.em_macroeconomic_daily_history('20210307')
    # em.em_macroeconomic_daily('20210703', '20210704')
    # em.em_stock_research_info_history('20080101', '20081231')
    # end_date = '20000330'
    # em.em_stock_fs_balance_sheet(end_date)
    # em.em_stock_fs_income_statement(end_date)
    # em.em_stock_fs_cashflow_statement(end_date)
    # em.em_stock_fs_income_statement_q(end_date)
    # em.em_stock_fs_cashflow_statement_q(end_date)
    # em.em_conv_bond_clean_price('20000101', '20001231')
    # em.em_conv_bond_dirty_price('20000101', '20001231')
    # em.em_fund_asset_history('20201231')
    # em.em_bond_clean_price('20210323', '20210323')
    # em.em_bond_dirty_price('20210323', '20210323')
    # em.em_fund_ipo_stats_from_file('../基金打新收益率统计2020Q3.xls', '20200701', '20200930')
    # em.em_future_price('20210723', '20210723')
    # em.em_fund_benchmark_of_new_funds('20210126')
    # em.em_north_capital('20210701', '20210701')
    # em.em_index_val_history('20121203', '20121203', ['SPX.GI'])
