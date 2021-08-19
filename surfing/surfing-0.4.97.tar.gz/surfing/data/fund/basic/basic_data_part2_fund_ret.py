
import datetime
import traceback

import numpy as np
import pandas as pd
from pandas.tseries.offsets import DateOffset

from ...api.basic import BasicDataApi
from ...view.basic_models import FundRet
from .basic_data_part1 import BasicDataPart1
from .basic_data_helper import BasicDataHelper


class BasicFundRet(BasicDataPart1):

    _DIM_TYPE = {
        'w1_': DateOffset(weeks=1),
        'm1_': DateOffset(months=1),
        'm3_': DateOffset(months=3),
        'm6_': DateOffset(months=6),
        'y1_': DateOffset(years=1),
        'y3_': DateOffset(years=3),
        'y5_': DateOffset(years=5),
    }

    Y_1 = 242
    RISK_FEE_RATE = 0.025

    def __init__(self, data_helper: BasicDataHelper):
        self._data_helper = data_helper
        self.basic_api = BasicDataApi()
        BasicDataPart1.__init__(self, self._data_helper)
        self.ret_res = {}

    def init(self, start_date, end_date):
        self.start_date: datetime.date = start_date if isinstance(start_date, datetime.date) else pd.to_datetime(start_date, infer_datetime_format=True).date()
        self.end_date: datetime.date = end_date if isinstance(end_date, datetime.date) else pd.to_datetime(end_date, infer_datetime_format=True).date()

        # 获取区间内的交易日列表
        dts = BasicDataApi().get_trading_day_list(start_date, end_date).drop(columns='_update_time').datetime
        fund_list = self._fund_info_df.fund_id.tolist()
        self.fund_nav = self.basic_api.get_fund_nav_with_date(start_date=self.start_date, end_date=self.end_date, fund_list=fund_list)
        self.fund_nav = self.fund_nav.pivot_table(index='datetime', columns='fund_id', values='adjusted_net_value').reindex(dts).fillna(method='ffill')
        self.fund_nav_fill = self.fund_nav.fillna(method='bfill').copy()
        _fund_to_enddate_dict = self._fund_info_df[['fund_id', 'end_date']].set_index('fund_id').to_dict()['end_date']
        # 超过基金终止日的基金净值赋空
        for fund_id in self.fund_nav.columns:
            fund_end_date = _fund_to_enddate_dict[fund_id]
            if self.end_date > fund_end_date:
                self.fund_nav.loc[fund_end_date:, fund_id] = np.nan
        # 直接使用basic的最新fund scale
        fund_scale = self.basic_api.get_fund_size()
        fund_scale = fund_scale[fund_scale.fund_id.isin(fund_list)]
        fund_scale['datetime'] = self.fund_nav.index.array[-1]
        self.ret_res['avg_size'] = fund_scale.pivot_table(index='datetime', columns='fund_id', values='latest_size').iloc[0, :]
        # 基金天数
        self.days = self.fund_nav.count() - 1
        self.date_list = self.fund_nav_fill.index

    def get_annual_ret(self, total_ret):
        '''
        累计年化收益
        exp(log(p[-1] / p[0]) / (trade_days / 242)) - 1
        '''
        log_total_ret = np.log(total_ret)
        ret_yearly = self.days / self.Y_1
        return np.exp(log_total_ret / ret_yearly) - 1

    def get_annual_vol(self):
        '''
        累计年化波动率
        (p.shift(1) / p).std(ddof=1) * np.sqrt((days - 1) / year)
        '''
        diff = self.fund_nav.shift(1) / self.fund_nav
        std = diff.std(ddof=1)
        std_yearly = np.sqrt((self.days - 1) / (self.days / self.Y_1))
        return std * std_yearly

    @staticmethod
    def get_mdd(fund_nav):
        '''
        累计最大回撤
        1 - (p / p.cummax()).min()
        '''
        return 1 - (fund_nav / fund_nav.cummax()).min()

    def calculate_one_date(self):
        # 取最近一天的日期和数据
        last_row = self.fund_nav_fill.iloc[-1, :]
        last_date = self.fund_nav_fill.index.array[-1]
        # 遍历每个需要计算的时间区间
        for name, value in self._DIM_TYPE.items():
            # 根据时间区间计算出begin date(bd)
            bd = (last_date - value).date()
            # 试图寻找bd及其之前的最近一天
            bd_list = self.date_list[self.date_list <= bd]
            if bd_list.empty:
                continue
            # 计算区间内的return
            temp_ret = (last_row / self.fund_nav_fill.loc[bd_list.array[-1], :] - 1)
            self.ret_res[name + 'ret'] = temp_ret

        total_ret = self.fund_nav_fill.iloc[-1] / self.fund_nav_fill.iloc[0]
        self.ret_res['to_date_ret'] = (total_ret - 1)
        self.ret_res['annual_ret'] = self.get_annual_ret(total_ret)
        self.ret_res['vol'] = self.fund_nav.pct_change(1).std(ddof=1) * np.sqrt(242)
        annual_vol = self.get_annual_vol()
        self.ret_res['sharpe_ratio'] = ((self.ret_res['annual_ret'] - self.RISK_FEE_RATE) / annual_vol)
        self.ret_res['mdd'] = BasicFundRet.get_mdd(self.fund_nav)
        self.ret_res['recent_y_ret'] = (self.fund_nav_fill.iloc[-1] / self.fund_nav_fill[self.fund_nav_fill.index < datetime.date(self.end_date.year, 1, 1)].iloc[-1] - 1)

        self.result = pd.DataFrame.from_dict(self.ret_res).rename_axis(index='fund_id').reset_index()
        self.result['datetime'] = self.fund_nav.index[-1]
        self.result['info_ratio'] = None  # TODO
        self.result = self.result.replace({np.inf: None, -np.inf: None})
        self.result = self.result[self.result.drop(columns=['fund_id', 'datetime']).notna().any(axis=1)]

    def process_all(self, end_date):
        failed_tasks = []
        try:
            default_begin_date = '20050101'  # 算累计指标用较久的起始日
            self.init(default_begin_date, end_date)
            self.calculate_one_date()
            self._data_helper._upload_basic(self.result, FundRet.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('fund_score')
        return failed_tasks


if __name__ == '__main__':
    bfr = BasicFundRet(BasicDataHelper())
    bfr.process_all('20210601')
