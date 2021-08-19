import traceback
import json
import datetime
import pandas as pd

from ...manager.manager_fund import *
from ...view.derived_models import *
from .derived_data_helper import DerivedDataHelper


class TopManagerFundProcessor:

    def __init__(self, data_helper):
        self._data_helper = data_helper

    def init(self, start_date='20100101', end_date='20200930'):
        self.start_date = start_date
        self.end_date = end_date
        self.white_list = pd.read_csv('../rpm/etc/chuang_jin_modify.csv').fund_id.tolist()

        with BasicDatabaseConnector().managed_session() as quant_session:
            query = quant_session.query(
                TradingDayList
            )
            trading_days = pd.read_sql(query.statement, query.session.bind)
            self.trading_dates = trading_days[trading_days['datetime'] >= self.start_date].datetime

        with DerivedDatabaseConnector().managed_session() as session:
            query = session.query(
                FundManagerScore
            ).filter(
                FundManagerScore.fund_type == 'stock',
                FundManagerScore.datetime >= self.start_date,
                FundManagerScore.datetime <= self.end_date,
            )
            self.mng_score_df = pd.read_sql(query.statement, query.session.bind)
            self.mng_score_df = self.mng_score_df.set_index(['datetime', 'manager_id']).drop(columns='fund_type')
            query = session.query(
                FundManagerFundRank
            ).filter(
                FundManagerFundRank.datetime >= self.start_date,
                FundManagerFundRank.datetime <= self.end_date,
            )
            self.mng_fund_list = pd.read_sql(query.statement, query.session.bind)
            self.mng_fund_list = self.mng_fund_list.set_index(['datetime', 'mng_id'])

    def calculate_update(self):
        res = []
        for dt in self.trading_dates:
            try:
                pd_dt = pd.to_datetime(dt, infer_datetime_format=True)
                top_mng_list = self.mng_score_df.loc[pd_dt].sort_values('score', ascending=False).index.tolist()
                mng_fund_dt = self.mng_fund_list.loc[pd_dt]
                mng_fund_dt_list = mng_fund_dt.index.tolist()
                top_mng_list = [_ for _ in top_mng_list if (_ in mng_fund_dt_list)]
                top_funds = [json.loads(_)[0] for _ in mng_fund_dt.loc[top_mng_list].fund_list.values]
                top_funds = [ _ for _ in top_funds if _ in self.white_list][:10]
                dic = {
                    'datetime':dt,
                }
                for idx, i in enumerate(top_funds):
                    dic.update({f'top_{idx+1}':i})
                res.append(dic)
            except Exception:
                continue
        self.result = pd.DataFrame(res)

    def process(self, start_date, end_date):
        failed_tasks = []
        try:
            start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d').date()
            end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d').date()
            start_date_dt = start_date_dt - datetime.timedelta(days = 20)
            self.init(start_date=start_date_dt, end_date=end_date_dt)
            self.calculate_update()
            df = self.result[self.result['datetime'] == end_date_dt]
            self._data_helper._upload_derived(df, TopManagerFunds.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('top_manager_funds')

        return failed_tasks


if __name__ == "__main__":
    the_date = '20210111'
    tmfp = TopManagerFundProcessor(DerivedDataHelper())
    tmfp.process(the_date, the_date)
