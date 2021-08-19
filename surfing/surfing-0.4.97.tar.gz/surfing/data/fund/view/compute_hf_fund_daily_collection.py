import pandas as pd
import numpy as np
import traceback
import json
import math
from ...api.raw import *
from ....util.calculator import *
from ...view.view_models import HFFundDailyCollection
from ...wrapper.mysql import ViewDatabaseConnector


class HFFundDailyCollectionProcessor(object):
    
    def __init__(self):
        self.raw_api = RawDataApi()
        self.fund_info = self.raw_api.get_hf_fund_info()
        self.fund_nav = self.raw_api.get_hf_fund_nav_dt()
        self.fund_nav = self.fund_nav.pivot_table(index='datetime',values='nav',columns='fund_id')
    
    def get_fund_price_start_and_end(self):
        result = []
        for fund_id in self.fund_nav:
            _df = self.fund_nav[[fund_id]].dropna()
            dic = {
                'fund_id':fund_id,
                'price_begin_date':_df.index[0],
                'price_end_date':_df.index[-1]
            }
            result.append(dic)
        df = pd.DataFrame(result)
        return df

    def get_fund_indicator(self):
        dic = {
            'annualized_ret':'annual_ret',
            'annualized_vol':'annual_vol',
            'sharpe':'sharpe_ratio',
            'fund_id':'fund_id',
        }
        result = []
        for fund_id in self.fund_nav:
            _df = self.fund_nav[fund_id].dropna()
            stats = Calculator.get_stat_result(dates=_df.index,values=_df.values,frequency='1D',risk_free_rate=0.025).__dict__
            stats['fund_id'] = fund_id
            result.append(stats)
        df = pd.DataFrame(result)
        df = df[dic.keys()].rename(columns=dic)
        return df

    def append_data(self, table_name, data_append_directly_data_df):
        if not data_append_directly_data_df.empty:
            with ViewDatabaseConnector().managed_session() as mn_session:
                try:
                    mn_session.execute(f'TRUNCATE TABLE {table_name}')
                    mn_session.commit()
                except Exception as e:
                    print(f'Failed to truncate table {table_name} <err_msg> {e}')
            data_append_directly_data_df.to_sql(table_name, ViewDatabaseConnector().get_engine(), index = False, if_exists = 'append')
            print('新数据已插入')
        else:
            print('没有需要插入的新数据')

    def _process(self):
        try:
            fund_info = self.fund_info.set_index('fund_id')
            fund_start_end_date_df = self.get_fund_price_start_and_end().set_index('fund_id')
            fund_indicator = self.get_fund_indicator().set_index('fund_id')

            df = pd.concat([fund_info, fund_start_end_date_df, fund_indicator], axis=1, sort=False)
            df = df.reset_index().rename(columns={'index':'fund_id'}).replace({np.inf: np.nan, -np.inf: np.nan})
            self.append_data(HFFundDailyCollection.__tablename__, df)
            return True
        
        except Exception as e:
            print(e)
            traceback.print_exc()
            return False

    def process(self):
        failed_tasks = []
        if not self._process():
            failed_tasks.append('hf_fund_daily_collection')
        return failed_tasks


if __name__ == '__main__':
    HFFundDailyCollectionProcessor().process()
