import datetime
import traceback
import numpy as np
import pandas as pd
import re
from multiprocessing import Pool
from .basic_data_helper import BasicDataHelper
from ...api.raw import RawDataApi
from ...api.basic import BasicDataApi
from ...view.basic_models import FundIPOStats


class BasicIPOStat():
    '''打新基金'''
    def __init__(self, data_helper: BasicDataHelper):
        self._data_helper = data_helper
        self._raw_data_api = RawDataApi()
        self._basic_data_api = BasicDataApi()

    def init(self):
        self.fund_raw_ipo_status = self._raw_data_api.get_em_fund_ipo_status()
        self.fund_size = self._basic_data_api.get_fund_size_all_data()
        self.fund_info = self._basic_data_api.get_fund_info()
        self.desc_dic = self.fund_info[['fund_id', 'desc_name']].set_index('fund_id').to_dict()['desc_name']
        self.fund_info['trim_name'] = self.fund_info.desc_name.map(lambda x: re.subn(r'[ABCDEFR]{1,2}(\(人民币\)|\(美元现汇\)|\(美元现钞\)|1|2|3)?$', '', x)[0])
        self.fund_info_type = self.fund_info.set_index(['trim_name', 'desc_name'])

        self.fund_size = self.fund_size.pivot_table(index='datetime', columns='fund_id', values='size')
        d1 = self.fund_raw_ipo_status.end_date.unique().tolist()
        d2 = self.fund_size.index.unique().tolist()
        date_list = sorted(list(set(d1).union(d2)))
        self.fund_size = self.fund_size.reindex(date_list).fillna(method='ffill')
        self.fund_size = self.fund_size.stack().reset_index().rename(columns={'datetime': 'end_date', 0: 'size'}).set_index(['fund_id', 'end_date'])
        self.fund_raw_ipo_status['fund_id'] = self.fund_raw_ipo_status.apply(lambda x: self._data_helper._get_fund_id_from_order_book_id(x.em_id.split('.')[0], x.end_date), axis=1)
        self.fund_raw_ipo_status = self.fund_raw_ipo_status.drop(['em_id', '_update_time'], axis=1)
        self.fund_raw_ipo_status = self.fund_raw_ipo_status.dropna(subset=['fund_id'])
        self.fund_raw_ipo_status.loc[:, 'desc_name'] = self.fund_raw_ipo_status.fund_id.map(lambda x: self.desc_dic[x])

    def _loop_item(self, i):
        df_i = pd.DataFrame([i])  #.set_index(['fund_id'])
        desc_name = i['desc_name']
        index_1 = self.fund_info_type.loc[pd.IndexSlice[:, desc_name], :].index.get_level_values(0).values[0]
        fund_info_i = self.fund_info_type.loc[index_1]
        if fund_info_i.shape[0] == 1:
            try:
                df_i['size'] = self.fund_size.loc[i['fund_id'], pd.to_datetime(i['end_date'], infer_datetime_format=True)].values[0]
            except Exception:
                # print(f'[_loop_item] can not find fund size (info){df_i}')
                return
        else:
            df_i = df_i.set_index('fund_id')
            _fund_list = fund_info_i.fund_id.tolist()
            for _fund_id in _fund_list:
                df_i.loc[_fund_id] = df_i.loc[i['fund_id']]
            df_i = df_i.reset_index().set_index(['fund_id', 'end_date']).join(self.fund_size).dropna(subset=['size']).reset_index()
        df_i.loc[:, 'ipo_allocation_weight'] = 10000 * df_i['ipo_allocation_amount'] / df_i['size'].sum()
        return df_i

    def calculate_history(self, end_date: str = ''):
        if end_date:
            self.fund_raw_ipo_status = self.fund_raw_ipo_status[self.fund_raw_ipo_status.end_date == pd.to_datetime(end_date, infer_datetime_format=True).date()]
        dict_list = self.fund_raw_ipo_status.to_dict('records')
        p = Pool()
        res = [i for i in p.imap_unordered(self._loop_item, dict_list, 2000) if i is not None]
        p.close()
        p.join()
        self.result = pd.concat(res).drop('desc_name', axis=1)
        res = []
        for i in self.result.end_date:
            if isinstance(i, pd.Timestamp):
                res.append(i.date())
            else:
                res.append(i)
        self.result['end_date'] = res
        self.result = self.result.drop_duplicates(subset=['fund_id', 'end_date'])
        self._data_helper._upload_basic(self.result, FundIPOStats.__table__.name)


if __name__ == "__main__":
    bipos = BasicIPOStat(BasicDataHelper())
    bipos.init()
    bipos.calculate_history('20210121')
