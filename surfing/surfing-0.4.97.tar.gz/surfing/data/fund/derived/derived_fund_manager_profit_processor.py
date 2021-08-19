
import datetime
from typing import List, Tuple, Optional, Dict
import pandas as pd
import traceback
import numpy as np

from ...api.basic import BasicDataApi, BasicDatabaseConnector, FundNav
from ...api.derived import DerivedDataApi, DerivedDatabaseConnector
from ...view.derived_models import FundManagerInfo
from .derived_data_helper import DerivedDataHelper


class FundManagerProfitProcess:

    def __init__(self, data_helper: DerivedDataHelper):
        self._data_helper = data_helper

    def init(self, start_date: str, end_date: str):
        self._end_date = end_date
        self._end_date_dt = pd.to_datetime(end_date).date()
        self._fund_info: pd.DataFrame = DerivedDataApi().get_fund_manager_info()
        self._result = pd.DataFrame([])

    def calc_fund_profit(self, start_date, end_date, fund_id):
        with BasicDatabaseConnector().managed_session() as db_session:
            start_nav = db_session.query(FundNav.adjusted_net_value).filter(
                FundNav.fund_id == fund_id,
                FundNav.datetime >= start_date,
            ).order_by(FundNav.datetime.asc()).first()
            end_nav = db_session.query(FundNav.adjusted_net_value).filter(
                FundNav.fund_id == fund_id,
                FundNav.datetime <= end_date,
            ).order_by(FundNav.datetime.desc()).first()
            if not start_nav or not end_nav:
                return None
            
            try:
                profit = end_nav[0] / start_nav[0] - 1
            except Exception as e:
                print(start_nav, end_nav)
                print(traceback.format_exc())
                return None
            return profit

    def calc(self):
        print(self._fund_info)
        with DerivedDatabaseConnector().managed_session() as db_session:
            for i in self._fund_info.index:
                profit = self.calc_fund_profit(
                    self._fund_info.loc[i, 'start_date'],
                    self._fund_info.loc[i, 'end_date'],
                    self._fund_info.loc[i, 'fund_id'],
                )
                db_session.query(FundManagerInfo).filter(
                    FundManagerInfo.fund_id == self._fund_info.loc[i, 'fund_id'],
                    FundManagerInfo.start_date == self._fund_info.loc[i, 'start_date'],
                    FundManagerInfo.mng_id == self._fund_info.loc[i, 'mng_id'],
                ).update(
                    {'profit': profit}
                )
                db_session.commit()
                print(i, self._fund_info.loc[i, 'fund_id'])
        print(self._result)

    def process(self, start_date: str, end_date: str, end_date_dt: datetime.date) -> List[str]:
        print(f'fund manager profit update on the last day of week {end_date_dt}')
        failed_tasks = []
        try:
            self.init(start_date, end_date)
            self.calc()
            # self._data_helper._upload_derived(self._result, FundManagerInfo.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('FundManagerProfitProcess')
        return failed_tasks


if __name__ == '__main__':
    date = '20200930'
    fsg = FundManagerProfitProcess(DerivedDataHelper())
    fsg.process(date, date, pd.to_datetime(date).date())
    # FundScoreGroupProcess.update_history('20201010', 5)
