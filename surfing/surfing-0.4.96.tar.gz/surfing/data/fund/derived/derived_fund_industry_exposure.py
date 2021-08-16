
import datetime
from typing import List, Optional
import traceback

import numpy as np
import pandas as pd

from ....constant import IndClassType, SEMI_UPDATE_DATE_LIST
from ...api.raw import RawDataApi
from ...api.basic import BasicDataApi
from ...view.derived_models import FundIndustryExposure
from ..raw.raw_data_helper import RawDataHelper
from .derived_data_helper import DerivedDataHelper


class FundIndustryExposureProcess:

    def __init__(self, data_helper: DerivedDataHelper):
        self._data_helper = data_helper
        self._result: Optional[pd.DataFrame] = None

    def init(self, start_date: str, end_date: str):
        self._end_date: str = end_date

        # 计算过去离目前最近的数据公布日期
        real_date, aux_date = RawDataHelper.get_prev_and_aux_target_dates(end_date, SEMI_UPDATE_DATE_LIST)
        # 基金的股票持仓明细
        fund_stock_portfolio = BasicDataApi().get_fund_stock_portfolio(dt=real_date).drop(columns=['datetime', '_update_time'])
        fund_stock_portfolio_aux = BasicDataApi().get_fund_stock_portfolio(dt=aux_date).drop(columns=['datetime', '_update_time'])
        fund_stock_portfolio_aux = fund_stock_portfolio_aux[~fund_stock_portfolio_aux.fund_id.isin(set(fund_stock_portfolio.fund_id.array))]
        self._fund_stock_portfolio = pd.concat([fund_stock_portfolio, fund_stock_portfolio_aux])
        stock_list: List[str] = list(self._fund_stock_portfolio.stock_id.unique())
        # 获取涉及到的这些股票的信息
        stock_infos = RawDataApi().get_em_stock_info(stock_list=stock_list)
        # 目前只需要申万一级行业分类ID
        sws_ind_code = stock_infos.set_index('stock_id')['bl_sws_ind_code']
        self._sws_ind_code = sws_ind_code.transform(lambda x: x.split('-')[0] if not pd.isnull(x) else np.nan)
        # 获取股票未复权价格
        stock_price = RawDataApi().get_em_stock_price(start_date=(pd.to_datetime(start_date).date() - datetime.timedelta(days=30)).isoformat(), end_date=end_date, stock_list=stock_list, columns=['close'])
        stock_price = stock_price.pivot(index='datetime', columns='stock_id', values='close').sort_index().ffill().iloc[[-1], :]
        self._stock_prices = stock_price.stack().droplevel('datetime').rename('close')

    def calc(self):
        def _aggregate_data(x):
            # valid_code = self._sws_ind_code.index.intersection(x.index).intersection(self._stock_prices.index)
            # return x[x.index.isin(valid_code)].loc[:, ['hold_number']].join(self._stock_prices.loc[valid_code]).join(self._sws_ind_code.loc[valid_code])
            return x.set_index('stock_id').loc[:, ['hold_number']].join([self._stock_prices, self._sws_ind_code], how='left')

        def _calc_ratio(x):
            x['value'] = x.mv / x.mv.sum()
            return x.value.droplevel('fund_id').to_json()

        # 把计算所需数据聚合在一起
        agg_result: pd.DataFrame = self._fund_stock_portfolio.groupby(by='fund_id', sort=False).apply(_aggregate_data)
        # 计算各持仓最新市值
        before_next_calc = agg_result.reset_index().drop(columns='stock_id')
        before_next_calc['mv'] = before_next_calc.hold_number * before_next_calc.close
        before_next_calc = before_next_calc.drop(columns=['hold_number', 'close'])
        # 计算每只基金各行业市值总和
        industry_sum = before_next_calc.groupby(by=['fund_id', 'bl_sws_ind_code'], sort=False).sum(min_count=1)
        # 计算每只基金各行业持仓比例
        self._result = industry_sum.groupby(level='fund_id', sort=False).apply(_calc_ratio).to_frame('value')
        # 这里先直接填成SWI
        self._result['ind_class_type'] = IndClassType.SWI1
        self._result['datetime'] = self._end_date

    def process(self, start_date: str, end_date: str, end_date_dt: datetime.date) -> List[str]:
        print(f'fund industry exposure update on the last day of week {end_date_dt}')
        failed_tasks: List[str] = []
        try:
            self.init(start_date, end_date)
            self.calc()
            self._data_helper._upload_derived(self._result.reset_index(), FundIndustryExposure.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(f'fund_industry_exposure')
        return failed_tasks


if __name__ == '__main__':
    date = '20201231'
    fsg = FundIndustryExposureProcess(DerivedDataHelper())
    fsg.process(date, date, pd.to_datetime(date).date())
