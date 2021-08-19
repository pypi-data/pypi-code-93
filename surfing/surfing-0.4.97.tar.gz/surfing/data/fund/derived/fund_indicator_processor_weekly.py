import pandas as pd
import numpy as np
import datetime
import traceback
from functools import partial
from sklearn.metrics import r2_score
import time
import concurrent.futures
from ...manager.manager_fund import FundDataManager
from ...manager.score import FundScoreManager
from ...wrapper.mysql import DerivedDatabaseConnector
from ...view.derived_models import *


class FundIndicatorProcessorWeekly(object):

    TRADING_DAYS_PER_YEAR = 242
    NATURAL_DAYS_PER_YEAR = 365
    SHORT_TIME_SPAN = TRADING_DAYS_PER_YEAR
    LONG_TIME_SPAN = TRADING_DAYS_PER_YEAR * 3
    LONG_TERM_INDEX = ['hs300', 'csi500', 'mmf']
    MIN_TIME_SPAN = 10 #最小回归单位
    RESAMPLE_WORK_DAY_DIC = {'1W':5}

    def __init__(self, data_helper):
        self._data_helper = data_helper

    def init(self, start_date='20040101', end_date='20200626', dm=None, resample_day='1W'):
        if dm is None:
            self._dm = FundDataManager(start_time=start_date, end_time=end_date, score_manager=FundScoreManager())
            self._dm.init(score_pre_calc=False)
        else:
            self._dm = dm
        self.start_date = self._dm.start_date
        self.end_date = self._dm.end_date
        self.resample_day = resample_day

        # index price, fund nav 日期对齐至交易日
        self.trading_days = self._dm.dts.trading_days.datetime
        self.fund_nav = self._dm.dts.fund_nav.copy()
        self.fund_info = self._dm.dts.fund_info.copy()
        self.fund_to_index_dict = self.fund_info[['fund_id', 'index_id']].set_index('fund_id').to_dict()['index_id']
        self.index_price = self._dm.dts.index_price.copy()
        self.fund_nav = self.fund_nav.reindex(self.trading_days).loc[:self.end_date]
        self.index_price = self.index_price.reindex(self.trading_days)[:self.end_date]
        l1 = self.fund_nav.index.to_list().sort()
        l2 = self.index_price.index.to_list().sort()
        assert l1 == l2, f'date index of index price and fund nav are not identical, l1 {l1} lens {len(l1)}, l2 {l2} lens {len(l2)}'

        # 超过基金终止日的基金净值赋空
        fund_to_enddate_dict = self.fund_info[['fund_id', 'end_date']].set_index('fund_id').to_dict()['end_date']
        for fund_id in self.fund_nav.columns:
            fund_end_date = fund_to_enddate_dict[fund_id]
            if self.end_date > fund_end_date:
                self.fund_nav.loc[fund_end_date:,fund_id] = np.nan

        # resample and datetime convert
        self.fund_ret = np.log(self.fund_nav / self.fund_nav.shift(1))
        self.index_ret = np.log(self.index_price / self.index_price.shift(1))
        self.fund_ret = self.df_resample(self.fund_ret)
        self.index_ret = self.df_resample(self.index_ret)

        self.fund_ret = self.fund_ret.stack().reset_index(level=[0,1]).rename(columns={0:'ret'})
        self.fund_ret['index_id'] = self.fund_ret.fund_id.apply(lambda x: self.fund_to_index_dict[x])
        self.fund_ret = self.fund_ret.pivot_table(index = ['index_id','datetime'],columns='fund_id',values='ret')

        self.index_list = self.fund_ret.index.levels[0]
        self.index_fund = { index_id : [fund_idx for fund_idx, index_idx in self.fund_to_index_dict.items() if index_idx == index_id] for index_id in self.index_list}
        self.start_date_dic = self.fund_info[['fund_id','start_date']].set_index('fund_id').to_dict()['start_date']

    def df_resample(self, df):
        df.index = pd.to_datetime(df.index)
        df = df.resample(self.resample_day).sum()
        df.index = pd.Series(df.index).dt.date
        return df

    def get_time_range(self, index_id):
        if index_id in self.LONG_TERM_INDEX:
            return self.LONG_TIME_SPAN
        else:
            return self.SHORT_TIME_SPAN

    def _rolling_alpha_beta_time_ret_r2(self, x, res, df):
        # 回归相关的都在这里
        df_i = df.loc[x[0]:x[-1],]
        return self._rolling_alpha_beta_time_ret_r2_base(res,df_i)

    def _rolling_alpha_beta_time_ret_r2_base(self, res, df_i):
        if sum(df_i.fund) == 0:
            res.append({'alpha_w':np.Inf,'beta_w':np.Inf})
            return 1
        else:
            ploy_res = np.polyfit(y=df_i.fund, x=df_i.benchmark,deg=1)
            p = np.poly1d(ploy_res)
            beta = ploy_res[0]
            # 根据resample 日子做回归  比如当前是 1w 对应 5天
            alpha = ploy_res[1] * self.TRADING_DAYS_PER_YEAR / self.RESAMPLE_WORK_DAY_DIC[self.resample_day]
            res.append({'alpha_w': alpha,
                        'beta_w': beta})
            return 1

    def _process_fund_indicator_item(self, fund_id, time_range, fund_ret, index_id, index_ret):
        df = fund_ret[[fund_id]].join(index_ret).dropna()
        b_day = self.fund_nav[[fund_id]].dropna().index[0]
        df = df.loc[b_day:].rename(columns={index_id:'benchmark',fund_id:'fund'}).reset_index()
        res = []
        pd.Series(df.index).rolling(
            window=time_range,min_periods=self.MIN_TIME_SPAN).apply(
                partial(self._rolling_alpha_beta_time_ret_r2, res=res, df=df), raw=True)
        df = df.set_index('datetime')
        df = df.join(pd.DataFrame(res,index=df.index[-len(res):]))
        if 'alpha_w' not in df.columns:
            return None
        df['track_err_w'] = (df.fund - df.benchmark).rolling(window=time_range, min_periods=self.MIN_TIME_SPAN).std(ddof=1) * np.sqrt(self.TRADING_DAYS_PER_YEAR / self.RESAMPLE_WORK_DAY_DIC[self.resample_day])
        df['fund_id'] = fund_id
        df = df.drop(['fund','benchmark'], axis=1)
        df = df.replace({-np.Inf:None,np.Inf:None}).dropna(subset=['beta_w', 'alpha_w','track_err_w']).reset_index()
        if df.empty:
            return None
        return df

    def calculate_history(self, index_id_list:list=None):
        result = []
        index_list = self.index_list if index_id_list is None else index_id_list
        for index_id in index_list:
            _tm_1 = time.time()
            time_range = int(self.get_time_range(index_id) / self.RESAMPLE_WORK_DAY_DIC[self.resample_day])
            fund_list = self.index_fund[index_id]
            fund_list_calculate = self.fund_ret.loc[index_id].columns
            fund_list = list(set(fund_list) & set(fund_list_calculate))
            fund_ret = self.fund_ret.loc[index_id][fund_list].copy()
            index_ret = self.index_ret[[index_id]]
            for fund_id in fund_list:
                df_i = self._process_fund_indicator_item(fund_id, time_range, fund_ret, index_id, index_ret)
                result.append(df_i)
            _tm_2 = time.time()
            print(f'index {index_id} fund number : {len(fund_list)} finish, cost time {_tm_2 - _tm_1} s')
        result = [_ for _ in result if not _ is None]
        self.result = pd.concat(result, axis=0, sort=True)

    def save_db(self):
        self._data_helper._upload_derived(self.result, FundIndicatorWeekly.__table__.name)

    def process(self, start_date: str, end_date: str, end_date_dt: datetime.date):
        # 周更因子, resample出来的日期都是周日，在周日前的最后一个交易日更新
        failed_tasks = []
        try:
            print(f'weekly indicator update on the last day of week {end_date_dt}')
            start_date_dt = pd.to_datetime(start_date, infer_datetime_format=True).date()
            start_date = start_date_dt - datetime.timedelta(days=1150)  # 3年历史保险起见，多取几天 3*365=1095
            start_date = datetime.datetime.strftime(start_date, '%Y%m%d')
            self.init(start_date=start_date, end_date=end_date)
            self.calculate_history()
            end_date_dt = end_date_dt + datetime.timedelta(days=2)
            df = self.result[self.result['datetime'] == end_date_dt]
            self._data_helper._upload_derived(df, FundIndicatorWeekly.__table__.name)

        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('fund_indicator_weekly')
        return failed_tasks
