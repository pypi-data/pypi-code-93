import pandas as pd
import numpy as np
import datetime
import matplotlib as mpl
import pylab as pl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
mpl.rcParams['font.family'] = ['Heiti TC']

from .manager_fund import FundDataManager
from .score import FundScoreManager
from ..struct import AssetWeight

class FundIndicatorCheck:

    def __init__(self, start_time=None, end_time=None):
        self._dm = FundDataManager(start_time=start_time, end_time=end_time, score_manager=FundScoreManager())
        self.fund_score = FundScoreManager()

    def init(self, asset, check_date):
        self._dm.init()
        self.asset = asset
        self.check_date = check_date
        
        self.tradings_days = self._dm.dts.trading_days
        self.fund_info = self._dm.dts.fund_info
        self.fund_indicator = self._dm.dts.fund_indicator.pivot_table(index=['fund_id','datetime'])
        self.fund_nav = self._dm.dts.fund_nav
        self.index_price = self._dm.dts.index_price
        self.score_equation = self.fund_score.funcs[self.asset].__dict__

        self.check_date = self.tradings_days[self.tradings_days.datetime > self.check_date].datetime.values[0]
        self.fund_list = self.fund_info[self.fund_info['index_id'].isin([self.asset])].fund_id.tolist()
        self.fund_list = [_ for _ in self.fund_nav.columns if _ in self.fund_list]
        self.fund_nav = self.fund_nav[self.fund_list]
        self.index_price = self.index_price[[asset]].loc[:check_date,]
        self.fund_indicator = self.fund_indicator.loc[(self.fund_list,self.check_date),]

    def check_indicator(self):
        res = []
        for fund_id in self.fund_nav.columns:
            dftmp = self.fund_nav[fund_id]
            res.append({'fund_id':fund_id,'begin_nav_date':dftmp.dropna().index[0]})
        res = pd.DataFrame(res).set_index('fund_id')
        df = res.join(self.fund_info.set_index('fund_id'))[['begin_nav_date','desc_name']].join(self.fund_indicator).sort_values('begin_nav_date')
        return df

    def plot_price_ratio(self, select_fund_id:list):
        df = self.fund_nav[select_fund_id].join(self.index_price).dropna()
        df = df / df.iloc[0]
        df.plot.line(figsize=(16,8),legend=False,fontsize = 13)
        l = pl.legend(loc='lower left',fontsize = 10)
        s = pl.title('price ratio', fontsize=20)

if __name__ == "__main__":
    checker = FundIndicatorCheck(start_time = '20100101', end_time = '20160101')
    checker.init(asset='gem', check_date=datetime.date(2015,1,6))
    checker.check_indicator()
    checker.plot_price_ratio(select_fund_id = ['050021!0','159908!0'])