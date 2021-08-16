
import pickle
import os
import gzip
import datetime
import time
from ..fund.engine.backtest import *


class DataStore:

    REPORT_PATH = 'report_data.pkz'
    DATA_MANAGER_PATH = 'data_manager.pkz'
    CURR_FILE_DIR = os.path.split(os.path.realpath(__file__))[0]

    def __init__(self):
        pass

    @staticmethod
    def store(data, f_path):
        f_path = os.path.join(DataStore.CURR_FILE_DIR, f_path)
        with gzip.GzipFile(f_path, 'wb') as f:
            pickle.dump(data, f, -1)
        print(f'store data successfully to {f_path}')

    @staticmethod
    def load(f_path):
        f_path = os.path.join(DataStore.CURR_FILE_DIR, f_path)
        with gzip.GzipFile(f_path, 'rb') as f:
            data = pickle.load(f)
        print(f'load data successfully from {f_path}')
        return data

    @staticmethod
    def refresh_dm(score_pre_calc=True,start_time='20110101',end_time=None,score_manager=None,print_time=False,use_weekly_monthly_indicators=False,s3_retriever_activation=None):
        print(f'start load at {datetime.datetime.now()}')
        t1 = time.time()
        if end_time is None:
            end_time = datetime.datetime.now().strftime('%Y%m%d')
        dm = FundDataManager(start_time=start_time, end_time=end_time, score_manager=score_manager, s3_retriever_activation=s3_retriever_activation)
        dm.init(score_pre_calc=score_pre_calc, print_time=print_time, use_weekly_monthly_indicators=use_weekly_monthly_indicators)
        DataStore.store(dm, DataStore.DATA_MANAGER_PATH)
        t2 = time.time()
        print(f'refresh dm cost time {t2 - t1}s')

    @staticmethod
    def load_dm():
        return DataStore.load(DataStore.DATA_MANAGER_PATH)

    @staticmethod
    def save_reporter(reporter):
        DataStore.store(reporter, DataStore.REPORT_PATH)

    @staticmethod
    def load_reporter():
        return DataStore.load(DataStore.REPORT_PATH)

if __name__ == "__main__":
    # save fm
    DataStore.refresh_dm()
    # load dm
    m = DataStore.load_dm()
    taa_detail_item_mmf = TAAParam(HighThreshold = 0.95,
                   HighStop = 0.5,
                   HighMinus = 0.03,
                   LowStop = -1,
                   LowThreshold = -1,
                   LowPlus = 0,
                   ToMmf=True)

    taa_detail= {
        'hs300': taa_detail_item_mmf,
        'csi500': taa_detail_item_mmf,
        'gem': taa_detail_item_mmf,
        'sp500rmb': taa_detail_item_mmf,
    }
    asset_param = AssetTradeParam()
    fund_param = FundTradeParam()
    t = FundTrader(asset_param, fund_param)
    fa_param = FAParam()
    taa_default = TAAParam()
    saa = AssetWeight(
        hs300=18/100,
        csi500=14/100,
        gem=9/100,
        sp500rmb=4/100,
        national_debt=44/100,
        gold=10/100,
        cash=1/100
    )
    b = FundBacktestEngine(data_manager=m, trader=t, taa_params=taa_default, fa_params=fa_param, taa_param_details=taa_detail)
    b.init()
    b.run(saa=saa, start_date=datetime.date(2020,1,3), end_date=datetime.date(2020,6,4))
    # save reporter
    DataStore.save_reporter(b._report_helper)

    # load reporter
    reporter = DataStore.load_reporter()
