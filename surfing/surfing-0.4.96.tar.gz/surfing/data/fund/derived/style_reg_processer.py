import traceback
from typing import List

import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler

from ...api.basic import BasicDataApi
from ...view.derived_models import StyleReg
from .derived_data_helper import DerivedDataHelper

class StyleBoxReg:
    
    def __init__(self,_data_helper: DerivedDataHelper):
        self._data_helper: DerivedDataHelper = _data_helper
        self._basic_api = BasicDataApi()
        
    def init(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        #从db读取六个指数的数据
        self._large_v_price = self._basic_api.get_index_price(['cni_largec_v'])
        self._large_g_price = self._basic_api.get_index_price(['cni_largec_g'])
        self._mid_v_price = self._basic_api.get_index_price(['cni_midc_v'])
        self._mid_g_price = self._basic_api.get_index_price(['cni_midc_g'])
        self._small_v_price = self._basic_api.get_index_price(['cni_smallc_v'])
        self._small_g_price = self._basic_api.get_index_price(['cni_smallc_g'])
        #db表格转收益率序列
        def get_return(test, start_date, end_date):
            start_date_dt = pd.to_datetime(start_date, infer_datetime_format=True)
            end_date_dt = pd.to_datetime(end_date, infer_datetime_format=True)
            test = test[['datetime','close']]
            test = test.set_index(test.datetime)
            temp = test.close
            temp = temp.apply(np.log).diff()[1:]
            temp = temp[np.logical_and(temp.index>=start_date_dt, temp.index<=end_date_dt)]
            return temp
        self.large_v_return = get_return(self._large_v_price, start_date, end_date)
        self.large_g_return = get_return(self._large_g_price, start_date, end_date)
        self.mid_v_return = get_return(self._mid_v_price, start_date, end_date)
        self.mid_g_return = get_return(self._mid_g_price, start_date, end_date)
        self.small_v_return = get_return(self._small_v_price, start_date, end_date)
        self.small_g_return = get_return(self._small_g_price, start_date, end_date)
        self.x = pd.concat([self.large_g_return, self.large_v_return, self.mid_g_return, self.mid_v_return, self.small_g_return, self.small_v_return], axis = 1)
        self.x.columns = ['large_g','large_v','mid_g','mid_v','small_g','small_v']
    
    def process(self, start_date, end_date):
        failed_tasks: List[str] = []
        try:
            self.init(start_date=start_date, end_date=end_date)
            self._data_helper._upload_derived(self.x.reset_index(), StyleReg.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(StyleReg.__table__.name)
        return failed_tasks
        
    
    @staticmethod
    def cal_fund(factor_return: pd.DataFrame, fund_nav:pd.Series):
        fund_ret = np.log(fund_nav).diff().iloc[1:].rename('fund_ret')
        whole_data = factor_return.join(fund_ret)
        whole_data = whole_data[whole_data.notna().all(axis=1)]
        X = sm.add_constant(whole_data.drop(columns='fund_ret'))
        Y = whole_data.fund_ret
        model = sm.OLS(Y, X)
        resu = model.fit()
        rets = (resu.params[1:] * whole_data.drop(columns='fund_ret'))
        summation = rets.sum(axis=1)
        return (resu.params, whole_data.loc[:, 'fund_ret'] - summation, whole_data.fund_ret, rets)
    
    @staticmethod
    def fund_analysis_plot(fund_ret: pd.Series, factor_ret_contri: pd.DataFrame):
        import matplotlib.pyplot as plt

        total_data = pd.concat([factor_ret_contri, fund_ret], axis=1)
        summation = total_data.drop(columns='fund_ret').sum(axis=1)
        total_data['spec'] = total_data.fund_ret - summation
        total_data.cumsum().plot(figsize=(18, 12), grid=True, title='基金收益率分解', colormap=plt.cm.get_cmap('nipy_spectral'))
        plt.legend(fontsize=15)


if __name__ == '__main__':
    sbg = StyleBoxReg(DerivedDataHelper())
    sbg.process('20200922', '20200922')
