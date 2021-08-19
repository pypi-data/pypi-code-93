
import traceback
from typing import List

import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler

from ...api.basic import BasicDataApi
from ...view.derived_models import BarraCNE5FactorReturn
from .derived_data_helper import DerivedDataHelper


class BarraCNE5FactorProcessor:

    def __init__(self, _data_helper: DerivedDataHelper):
        self._data_helper: DerivedDataHelper = _data_helper
        self._columns: List[str] = BarraCNE5FactorReturn.__table__.columns.keys()
        for c in ('datetime', '_update_time'):
            self._columns.remove(c)

    def init(self, start_date: str, end_date: str):
        self._start_date: str = start_date
        self._end_date: str = end_date

    def _linear_regression(self, x: pd.DataFrame) -> pd.Series:
        x = x[x.notna().all(axis=1)]
        if x.empty:
            return
        scaler = StandardScaler()
        X = sm.add_constant(scaler.fit_transform(x.drop(columns=['stock_id', 'datetime', 'ret'])))
        Y = x.ret.to_numpy()
        model = sm.OLS(Y, X)
        resu = model.fit()
        return pd.Series(resu.params, index=self._columns)

    def _calculate_update(self):
        factor_data: pd.DataFrame = BasicDataApi().get_barra_cne5_risk_factor(self._start_date, self._end_date).drop(columns='_update_time')
        self._result_df: pd.DataFrame = factor_data.groupby(by='datetime', sort=False).apply(self._linear_regression)
        self._result_df = self._result_df[self._result_df.notna().any(axis=1)]

    def process(self, start_date: str, end_date: str):
        failed_tasks: List[str] = []
        try:
            self.init(start_date=start_date, end_date=end_date)
            self._calculate_update()
            self._data_helper._upload_derived(self._result_df.reset_index(), BarraCNE5FactorReturn.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append(BarraCNE5FactorReturn.__table__.name)
        return failed_tasks

    @staticmethod
    def fund_analysis(factor_return: pd.DataFrame, fund_nav: pd.Series):
        fund_ret = np.log(fund_nav).diff().iloc[1:].rename('fund_ret')
        whole_data = factor_return.set_index('datetime').join(fund_ret)
        whole_data = whole_data[whole_data.notna().all(axis=1)]
        X = sm.add_constant(whole_data.drop(columns='fund_ret'))
        Y = whole_data.fund_ret
        model = sm.OLS(Y, X)
        resu = model.fit()
        # print(resu.summary())
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
    bcfp = BarraCNE5FactorProcessor(DerivedDataHelper())
    bcfp.process('20201026', '20201026')
