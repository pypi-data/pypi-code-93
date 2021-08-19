import datetime
import pandas as pd
import numpy as np
import traceback
from ...api.raw import RawDataApi
from ...api.basic import BasicDataApi
from ...view.derived_models import IndexValuation
from .derived_data_helper import DerivedDataHelper


class IndexValProcess:

    YEAR = 242
    WINDOW = YEAR * 5
    MIN_PERIOD = YEAR * 3
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

    def init(self, start_time, end_time):
        self.start_time = datetime.datetime.strptime(start_time, '%Y%m%d').date()
        self.end_time = datetime.datetime.strptime(end_time, '%Y%m%d').date()
        self.index_info = self.basic_api.get_index_info()
        # 过滤掉em_id是null的情况
        self.index_info = self.index_info[self.index_info.em_id.notna()]
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
            if index_id in self.TAA_INDEX_LIST:
                mins_periods = self.MIN_PERIOD
            else:
                mins_periods = 3 * self.YEAR
            df_i = self.index_val.loc[index_id].copy()
            df_i.loc[:, 'pe_pct'] = df_i['pe_ttm'].tail(self.WINDOW+1).rolling(window=self.WINDOW, min_periods=mins_periods).apply(pctrank)
            df_i.loc[:, 'pb_pct'] = df_i['pb_mrq'].tail(self.WINDOW+1).rolling(window=self.WINDOW, min_periods=mins_periods).apply(pctrank)
            df_i.loc[:, 'ps_pct'] = df_i['ps_ttm'].tail(self.WINDOW+1).rolling(window=self.WINDOW, min_periods=mins_periods).apply(pctrank)
            df_i.loc[:, 'roe_pct'] = df_i['roe'].tail(self.WINDOW+1).rolling(window=self.WINDOW, min_periods=mins_periods).apply(pctrank)

            df_i['peg_ttm'] = df_i['pe_ttm'] / (df_i['dy'] / df_i['dy'].shift(self.YEAR)-1)
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

    def filter_est_peg(self, x):
        if x > 10000 or x < -10000:
            return None
        return x

    def process(self, start_date, end_date):
        failed_tasks = []
        try:
            start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d').date()
            end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d').date()
            start_date = start_date_dt - datetime.timedelta(days = 2000) #5年历史保险起见，多取几天 5*365=1825
            start_date = datetime.datetime.strftime(start_date, '%Y%m%d')
            self.init(start_date, end_date)
            self.calculate()
            self.result = self.result.dropna(subset=['pe_ttm','pb_mrq','ps_ttm'], how='all')
            self.result = self.result[self.result['datetime'] >= pd.to_datetime(start_date_dt)]
            self.result = self.result[self.result['datetime'] <= pd.to_datetime(end_date_dt)]
            self.result['est_peg'] = self.result['est_peg'].map(lambda x : self.filter_est_peg(x))
            self._data_helper._upload_derived(self.result, IndexValuation.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('index_val')

        return failed_tasks


if __name__ == "__main__":
    IndexValProcess(DerivedDataHelper()).process('20200727', '20200727')
