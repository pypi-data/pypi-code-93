from multiprocessing import Pool
import traceback
import pandas as pd

from ....util.aip_calc import *
from ...manager.manager_fund import *
from ...struct import AssetTradeParam
from .derived_data_helper import DerivedDataHelper


class AIPProcess:

    YEAR = 242
    INTEL_PARAM = 'ma500'
    MODE = '1m'
    MODE_OFFSET = 0
    AMT_BENCH = 1000
    STOP_PROFIT = 0.15

    def __init__(self, data_helper):
        self._data_helper = data_helper

    def init(self, start_date='20150101', end_date='20200721'):
        self.start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
        self.end_date = datetime.datetime.strptime(end_date, '%Y%m%d').date()
        with BasicDatabaseConnector().managed_session() as quant_session:
            _fund_nav_query = quant_session.query(
                    FundNav.fund_id,
                    FundNav.adjusted_net_value,
                    FundNav.datetime
                ).filter(
                    FundNav.datetime >= self.start_date,
                    FundNav.datetime <= self.end_date,
                )
            _trading_days = quant_session.query(TradingDayList)
            _fund_info = quant_session.query(FundInfo)
        self.fund_info = pd.read_sql(_fund_info.statement, _fund_info.session.bind)
        self.trading_days = pd.read_sql(_trading_days.statement, _trading_days.session.bind)
        self.fund_nav = pd.read_sql(_fund_nav_query.statement, _fund_nav_query.session.bind)
        self.fund_nav = self.fund_nav.pivot_table(index='datetime', columns='fund_id', values='adjusted_net_value')
        _fund_list = self.fund_nav.iloc[-1].dropna().index.tolist()# 只计算当前有净值的基金
        _fund_list = [i for i in _fund_list if i not in ['006279!0','003793!0','006011!0','002091!0']]# 基金净值异常 
        _fund_list = [i for i in _fund_list if i not in ['002091!0']] # 分级基金定投收益过万，去掉
        self.fund_nav = self.fund_nav[_fund_list].fillna(method='ffill')
        self.trade_day_list = self.trading_days.datetime.to_list()
        self.begin_time_1y = self.trade_day_list[-self.YEAR]
        self.begin_time_3y = self.trade_day_list[-3 * self.YEAR]
        self.begin_time_5y = self.trade_day_list[-5 * self.YEAR]
        self.fund_list = self.fund_nav.columns.tolist()
        self.purchase_dict = (self.fund_info[['fund_id','purchase_fee']].set_index('fund_id') * AssetTradeParam.PurchaseDiscount).fillna(0).to_dict()['purchase_fee']
        self.redeem_dict = (self.fund_info[['fund_id','redeem_fee']].set_index('fund_id') * AssetTradeParam.RedeemDiscount).fillna(0).to_dict()['redeem_fee']

    def process(self, start_date, end_date):
        failed_tasks = []
        try:
            start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d').date()
            end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d').date()
            start_date = start_date_dt - datetime.timedelta(days = 2000) #5年历史保险起见，多取几天 5*365=1825
            start_date = datetime.datetime.strftime(start_date, '%Y%m%d')
            self.init(start_date, end_date)
            self.calculate()
            self._data_helper._upload_derived(self.result, FundAIC.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(FundAIC.__table__.name)
        return failed_tasks

    def normal_aip(self, fund_id, start_date, end_date):
        arr = self.fund_nav[fund_id]
        purchase_rate = self.purchase_dict[fund_id]
        redeem_rate = self.redeem_dict[fund_id]
        c = AIPCalculator(arr, start_date, end_date, self.STOP_PROFIT, None, self.AMT_BENCH, self.MODE, self.MODE_OFFSET, purchase_rate, redeem_rate)
        return c.get_irr()

    def intel_aip(self, fund_id, start_date, end_date):
        arr = self.fund_nav[fund_id]
        purchase_rate = self.purchase_dict[fund_id]
        redeem_rate = self.redeem_dict[fund_id]
        c = AIPCalculator(arr, start_date, end_date, self.STOP_PROFIT, self.INTEL_PARAM, self.AMT_BENCH, self.MODE, self.MODE_OFFSET, purchase_rate, redeem_rate)
        return c.get_irr()

    def calculate_item(self, fund_id):
        try:
            dic = {
                'fund_id':fund_id,
                'datetime':self.end_date,
                'y1_ret':self.normal_aip(fund_id,self.begin_time_1y,self.end_date),
                'y3_ret':self.normal_aip(fund_id,self.begin_time_3y,self.end_date),
                'y5_ret':self.normal_aip(fund_id,self.begin_time_5y,self.end_date),
                'intel_y1_ret':self.intel_aip(fund_id,self.begin_time_1y,self.end_date),
                'intel_y3_ret':self.intel_aip(fund_id,self.begin_time_3y,self.end_date),
                'intel_y5_ret':self.intel_aip(fund_id,self.begin_time_5y,self.end_date),
            }
            return dic
        except Exception:
            print('fund_id can not calculate aic', fund_id)
            return None

    def calculate(self):
        # res = [self.calculate_item(fund_id) for fund_id in self.fund_list]
        # res = [i for i in res if i is not None]
        # 不指定processes数量表示使用cpu_count()返回的number
        p = Pool()
        res = [i for i in p.imap_unordered(self.calculate_item, self.fund_list, 256) if i is not None]
        p.close()
        p.join()
        self.result = pd.DataFrame(res)


if __name__ == '__main__':
    aipp = AIPProcess(DerivedDataHelper())
    aipp.process('20210601', '20210601')
