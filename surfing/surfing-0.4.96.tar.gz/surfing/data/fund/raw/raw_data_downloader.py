
import traceback
import pandas as pd
import datetime
# from .rq_raw_data_downloader import RqRawDataDownloader
from .em_raw_data_downloader import EmRawDataDownloader
from .web_raw_data_downloader import WebRawDataDownloader
from .oversea_data_downloader import OverseaDataUpdate
from .raw_data_helper import RawDataHelper
from .other_raw_data_downloader import OtherRawDataDownloader
from ...api.raw import RawDataApi


class RawDataDownloader:
    def __init__(self, rq_license=None, dry_run=False):
        self._data_helper = RawDataHelper()
        # self.rq_downloader = RqRawDataDownloader(rq_license, self._data_helper)
        self.web_downloader = WebRawDataDownloader(self._data_helper)
        self.em_downloader = EmRawDataDownloader(self._data_helper, dry_run)
        self.oversea_download = OverseaDataUpdate(update_period=10, data_per_page=5, data_helper=self._data_helper)
        self.oversea_download_long_term = OverseaDataUpdate(update_period=400, data_per_page=600, data_helper=self._data_helper)
        self.other_raw_data_downloader = OtherRawDataDownloader(data_helper=self._data_helper)

    def download(self, start_date, end_date):
        failed_tasks = []

        try:
            failed_tasks.extend(self.em_downloader.download_all(start_date, end_date))
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('unknown in em_downloader')

        # If 'em_tradedates' in failed_tasks, there is no trading day between start_date and end_date
        # Stop and return
        # try:
        #     failed_tasks.extend(self.rq_downloader.download_all(start_date, end_date))
        # except Exception as e:
        #     print(e)
        #     traceback.print_exc()
        #     failed_tasks.append('unknown in rq_downloader')
        try:
            failed_tasks.extend(self.oversea_download.update_fund_nav())
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('oversea fund nav')

        try:
            failed_tasks.extend(self.other_raw_data_downloader.hf_fund_nav_miss())
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('hf_fund_nav_miss')

        if 'em_tradedates' in failed_tasks:
            return failed_tasks
        else:

            try:
                failed_tasks.extend(self.web_downloader.download_all(start_date, end_date))
            except Exception as e:
                print(e)
                traceback.print_exc()
                failed_tasks.append('unknown in web_downloader')

            # 获取下一个交易日
            trading_day_df = RawDataApi().get_em_tradedates(start_date=end_date)
            if trading_day_df.shape[0] <= 1:
                print(f'get trading days start with {end_date} failed')
                failed_tasks.append('get_trading_day for weekly/monthly indicator in raw')
            else:
                next_trading_day = trading_day_df.iloc[1, :].TRADEDATES
                print(f'got next trading day {next_trading_day}')
                next_trading_dt = pd.to_datetime(next_trading_day, infer_datetime_format=True).date()
                end_date_dt = pd.to_datetime(end_date, infer_datetime_format=True).date()
                if end_date_dt.weekday() < next_trading_dt.weekday() and next_trading_dt < end_date_dt + datetime.timedelta(weeks=1):
                    # 表明本非周末，今天不需要更新
                    print(f'monthly indicator update on every weekend, not today {end_date_dt}')
                else:
                    if not self.oversea_download_long_term.update_fund_adj_factor():
                        failed_tasks.append('oversea_fund_adj_factor')
                    if not self.other_raw_data_downloader.fund_nav_adj_process():
                        failed_tasks.append('oversea_fund_nav_adj_process')
        return failed_tasks

    def get_updated_count(self):
        return self._data_helper._updated_count
