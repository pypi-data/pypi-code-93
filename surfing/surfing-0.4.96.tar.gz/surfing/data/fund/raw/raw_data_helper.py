
import time
import datetime
from typing import Tuple, Set, Optional, List
from collections import defaultdict

import pandas as pd

from ...api.raw import RawDataApi
from ...wrapper.mysql import RawDatabaseConnector

ALL_CSI_INDEX_INNER_NAME = '_csi_index_all'


class RawDataHelper:
    def __init__(self):
        self._updated_count = defaultdict(int)
        self._timer: float = time.monotonic()

    def _upload_raw(self, df, table_name, to_truncate=False):
        print(table_name)
        # print(df)
        if to_truncate:
            with RawDatabaseConnector().managed_session() as mn_session:
                try:
                    mn_session.execute(f'TRUNCATE TABLE {table_name}')
                    mn_session.commit()
                except Exception as e:
                    print(f'Failed to truncate table {table_name} <err_msg> {e}')

        df = df.drop(columns='_update_time', errors='ignore')
        df.to_sql(table_name, RawDatabaseConnector().get_engine(), index=False, if_exists='append')

        now: float = time.monotonic()
        print(f'{table_name} costs {now - self._timer}s')
        self._timer = now
        self._updated_count[table_name] += df.shape[0]

    @staticmethod
    def get_new_and_delisted_fund_list(date: str) -> Tuple[Set[str], Set[str]]:
        fund_list = RawDataApi().get_em_fund_list(date, limit=2)
        if fund_list is None or fund_list.shape[0] < 2:
            print(f"failed to get two days' fund list, (date){date}")
            return (None, None)

        lastest_list: pd.Series = fund_list.iloc[0, :]
        last_list: pd.Series = fund_list.iloc[1, :]
        print(f"got two days' fund list, (latest){lastest_list.datetime} (prev){last_list.datetime}")
        return (set(lastest_list.all_live_fund_list.split(',')).difference(set(last_list.all_live_fund_list.split(','))),
                set(lastest_list.delisted_fund_list.split(',')).difference(set(last_list.delisted_fund_list.split(','))))

    @staticmethod
    def get_indexes_that_become_invalid(end_date: str) -> Set[str]:
        index_component = RawDataApi().get_em_index_component(end_date=end_date, index_list=[ALL_CSI_INDEX_INNER_NAME])
        if index_component is None or index_component.shape[0] < 2:
            print(f'failed to get em index component, (end_date){end_date}')
            return

        lastest_list: pd.Series = index_component.iloc[-1, :]
        last_list: pd.Series = index_component.iloc[-2, :]
        print(f"got two days' index component, (latest){lastest_list.datetime} (prev){last_list.datetime}")
        return set(last_list.stock_list.split(',')).difference(set(lastest_list.stock_list.split(',')))

    @staticmethod
    def get_all_live_fund_list(end_date: str) -> Optional[List[str]]:
        fund_list_df = RawDataApi().get_em_fund_list(end_date, limit=1)
        if fund_list_df is None or fund_list_df.shape[0] < 1:
            return
        return fund_list_df.all_live_fund_list.array[0].split(',')

    @staticmethod
    def get_all_fund_list(end_date: str) -> Optional[List[str]]:
        fund_list_df = RawDataApi().get_em_fund_list(end_date, limit=1)
        if fund_list_df is None or fund_list_df.shape[0] < 1:
            return
        fund_list = fund_list_df.all_live_fund_list.array[0].split(',')
        fund_list += fund_list_df.delisted_fund_list.array[0].split(',')
        return fund_list

    @staticmethod
    def get_prev_target_date(end_date: str, target_date_list: Tuple[str]) -> datetime.date:
        assert len(target_date_list) > 0, f'target date list should not be empty!!'

        # 寻找离目前最近且没超过当前时间的财报日期，将数据写在这个日期上（先删掉这个日期上的旧数据）
        end_date_dt = pd.to_datetime(end_date, infer_datetime_format=True)
        md = end_date_dt.strftime('%m%d')
        sentry_date = pd.Series(target_date_list)
        sentry = sentry_date[sentry_date <= md]
        if sentry.empty:
            # 这里取前一年的最后一个日期
            return pd.to_datetime(str(end_date_dt.year - 1)+sentry_date.array[-1], infer_datetime_format=True).date()
        else:
            return pd.to_datetime(str(end_date_dt.year)+sentry.array[-1], infer_datetime_format=True).date()

    @staticmethod
    def get_prev_and_aux_target_dates(end_date: str, target_date_list: Tuple[str]) -> (datetime.date, datetime.date):
        assert len(target_date_list) >= 1, f'target date list should have 2 dates at least!!'

        end_date_dt = pd.to_datetime(end_date, infer_datetime_format=True)
        md = end_date_dt.strftime('%m%d')
        sentry_date = pd.Series(target_date_list)
        sentry = sentry_date[sentry_date <= md]
        if sentry.empty:
            return [pd.to_datetime(str(end_date_dt.year - 1)+sentry_date.array[i], infer_datetime_format=True).date() for i in range(-1, -3, -1)]
        elif sentry.size == 1:
            return (pd.to_datetime(str(end_date_dt.year)+sentry.array[-1], infer_datetime_format=True).date(),
                    pd.to_datetime(str(end_date_dt.year - 1)+sentry_date.array[-1], infer_datetime_format=True).date())
        else:
            return [pd.to_datetime(str(end_date_dt.year)+sentry.array[i], infer_datetime_format=True).date() for i in range(-1, -3, -1)]
