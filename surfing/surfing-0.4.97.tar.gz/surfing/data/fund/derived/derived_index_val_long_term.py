import datetime
import pandas as pd
import numpy as np
import traceback
from typing import Tuple
from functools import partial
from ....constant import INDEX_VAL_EXTRA_TRADE_DAYS
from ...api.raw import RawDataApi
from ...api.basic import BasicDataApi
from ...api.derived import DerivedDataApi
from ...view.derived_models import IndexValuationLongTerm
from .derived_data_helper import DerivedDataHelper
from ....util.calculator import *


class IndexValProcessLongTerm:

    YEAR = 242
    WINDOW = YEAR * 10
    MIN_PERIOD = YEAR * 5
    _WINDOW_MINOR = YEAR * 5
    _MIN_PERIOD_MINOR = YEAR * 3
    SCORE_METHOD = {
        'PB百分位': 'pb_pct',
        'PE百分位': 'pe_pct',
        'PS百分位': 'ps_pct',
    }
    TAA_INDEX_LIST = ['hs300', 'csi500', 'gem', 'sp500rmb']

    def __init__(self, data_helper):
        self._data_helper = data_helper
        self.raw_api = RawDataApi()
        self.basic_api = BasicDataApi()

    def init(self, start_time, end_time, update_partially_list: Tuple[str] = ()):
        self.start_time = datetime.datetime.strptime(start_time, '%Y%m%d').date()
        self.end_time = datetime.datetime.strptime(end_time, '%Y%m%d').date()
        self.index_info = self.basic_api.get_index_info()
        # 过滤掉em_id是null的情况
        self.index_info = self.index_info[self.index_info.em_id.notna()]
        if update_partially_list:
            self.index_info = self.index_info[self.index_info.em_id.isin(update_partially_list)]
        em_id_to_index_id = self.index_info[['index_id', 'em_id']].set_index('em_id').to_dict()['index_id']
        self.index_val = self.raw_api.get_em_index_val(self.start_time, self.end_time, self.index_info.em_id.to_list())
        self.index_val['index_id'] = self.index_val['em_id'].map(lambda x: em_id_to_index_id[x])
        self.index_val = self.index_val.drop(columns=['em_id', '_update_time']).set_index(['index_id', 'datetime'])
        self.index_id_score_method_dict = self.index_info[self.index_info['tag_method'] != 'none'][['index_id', 'tag_method']].set_index('index_id').to_dict()['tag_method']

    def calculate(self):
        pctrank = lambda x: x.rank(pct=True).iloc[-1]
        self.index_val = self.index_val.rename(columns={'dividend_yield': 'dy'})
        index_list = self.index_val.index.levels[0].tolist()
        self.result = []
        for index_id in index_list:
            df_i = self.index_val.loc[index_id].copy()
            df_long_term = df_i[['pe_ttm', 'pb_mrq', 'ps_ttm', 'roe']].tail(self.WINDOW + 1)
            df_i.loc[:, 'pe_pct'] = df_long_term['pe_ttm'].rolling(window=self.WINDOW, min_periods=self.MIN_PERIOD).apply(pctrank, raw=False)
            df_i.loc[:, 'pb_pct'] = df_long_term['pb_mrq'].rolling(window=self.WINDOW, min_periods=self.MIN_PERIOD).apply(pctrank, raw=False)
            df_i.loc[:, 'ps_pct'] = df_long_term['ps_ttm'].rolling(window=self.WINDOW, min_periods=self.MIN_PERIOD).apply(pctrank, raw=False)
            df_i.loc[:, 'roe_pct'] = df_long_term['roe'].rolling(window=self.WINDOW, min_periods=self.MIN_PERIOD).apply(pctrank, raw=False)

            df_minor = df_i[['pe_ttm', 'pb_mrq', 'ps_ttm', 'roe']].tail(self._WINDOW_MINOR + 1)
            df_i.loc[:, 'pe_pct_5_3'] = df_minor['pe_ttm'].rolling(window=self._WINDOW_MINOR, min_periods=self._MIN_PERIOD_MINOR).apply(pctrank, raw=False)
            df_i.loc[:, 'pb_pct_5_3'] = df_minor['pb_mrq'].rolling(window=self._WINDOW_MINOR, min_periods=self._MIN_PERIOD_MINOR).apply(pctrank, raw=False)
            df_i.loc[:, 'ps_pct_5_3'] = df_minor['ps_ttm'].rolling(window=self._WINDOW_MINOR, min_periods=self._MIN_PERIOD_MINOR).apply(pctrank, raw=False)
            df_i.loc[:, 'roe_pct_5_3'] = df_minor['roe'].rolling(window=self._WINDOW_MINOR, min_periods=self._MIN_PERIOD_MINOR).apply(pctrank, raw=False)

            df_i['peg_ttm'] = df_i['pe_ttm'] / (df_i['dy'] / df_i['dy'].shift(self.YEAR) - 1)
            df_i.loc[:, 'index_id'] = index_id
            self.result.append(df_i)
            # print(f'finish {index_list.index(index_id)} total: {len(index_list)}')
        self.result = pd.concat(self.result).reset_index()
        score_list = []
        for r in self.result.itertuples(index=False):
            tag_method = self.index_id_score_method_dict.get(r.index_id, None)
            score_data = self.SCORE_METHOD.get(tag_method, 'pe_pct')
            score_list.append(getattr(r, score_data))

        self.result['datetime'] = pd.to_datetime(self.result['datetime'])
        self.result['val_score'] = score_list
        self.result = self.result.replace(np.inf, float('nan')).replace(-np.inf, float('nan'))

        index_list = self.result.index_id.unique()
        dic = {'pb_mrq': 'pb_pct', 'pe_ttm': 'pe_pct', 'roe': 'roe_pct'}
        l = list(dic.values())
        pct_list = [0.3, 0.7]
        res = []
        for index_id in index_list:
            _df = self.result[self.result['index_id'] == index_id].set_index('datetime')
            if _df.shape[0] < 242 * 5:
                _df.loc[:,l] = None
                res.append(_df.reset_index())
            else:
                for index_val, index_pct in dic.items():
                    _res = []
                    _df[index_val].dropna().rolling(window=10 * 242, min_periods=5 * 242).apply(partial(Calculator.roll_pct, pct_list=pct_list, res=_res), raw=True)
                    _df_i = pd.DataFrame(_res, index=_df.index.tolist()[-len(_res):]).rename(columns={0: f'{index_pct}_30', 1: f'{index_pct}_70'})
                    _df = _df.join(_df_i)
                res.append(_df.reset_index())
        self.result = pd.concat(res, axis=0)

    def filter_est_peg(self, x):
        if x is None:
            return
        if x > 10000 or x < -10000:
            return
        return x

    def process(self, start_date, end_date):
        failed_tasks = []
        try:
            start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d').date()
            end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d').date()
            start_date = start_date_dt - datetime.timedelta(days=3750)  # 10年历史保险起见，多取几天 10*365=3650
            start_date = datetime.datetime.strftime(start_date, '%Y%m%d')
            self.init(start_date, end_date)
            self.calculate()
            self.result = self.result.dropna(subset=['pe_ttm', 'pb_mrq', 'ps_ttm'], how='all')
            self.result['datetime'] = self.result.datetime.dt.date
            self.result = self.result[self.result['datetime'] >= (pd.to_datetime(start_date_dt).date() - datetime.timedelta(days=INDEX_VAL_EXTRA_TRADE_DAYS))]
            self.result = self.result[self.result['datetime'] <= pd.to_datetime(end_date_dt).date()]
            self.result['est_peg'] = self.result['est_peg'].map(lambda x: self.filter_est_peg(x))

            # 这里将sp500rmb的估值数据直接拷贝给sp500
            sp500rmb_data = self.result.loc[self.result.index_id == 'sp500rmb', :].copy()
            if not sp500rmb_data.empty:
                sp500rmb_data['index_id'] = 'sp500'
                self.result = self.result.append(sp500rmb_data, ignore_index=False)
            for date in self.result.datetime.unique():
                DerivedDataApi().delete_index_valuation(date, self.result[self.result.datetime == date].index_id.to_list())
            self._data_helper._upload_derived(self.result, IndexValuationLongTerm.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('index_val_long_term')
        return failed_tasks


if __name__ == "__main__":
    IndexValProcessLongTerm(DerivedDataHelper()).process('20210314', '20210314')
