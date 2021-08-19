
from typing import Dict

import pandas as pd

from .factor_types import GrowthFactor, MixFactorBase
from .basic_factors import IncomeFactor, AdjNetProfitFactor, CashFlowFactor
from .utils import calc_growth_rate, normalize


class IncomeGrowthFactor(GrowthFactor):
    # 收入增长
    def __init__(self):
        super().__init__('inc_gr')
        self._deps.add(IncomeFactor())

    def calc(self):
        # 过去四个季度的营业收入增长率
        income = IncomeFactor().get()
        self._factor = income.apply(calc_growth_rate, axis=1, result_type='broadcast', whole_df=income)


class NetProfitOfNonRecurringGoLFactor(GrowthFactor):
    # 扣非后盈利增长
    def __init__(self):
        super().__init__('np_nrgol')
        self._deps.add(AdjNetProfitFactor())

    def calc(self):
        # 过去四个季度扣除非经常性损益后的净利润的增长率
        adj_net_profit = AdjNetProfitFactor().get()
        self._factor = adj_net_profit.apply(calc_growth_rate, axis=1, result_type='broadcast', whole_df=adj_net_profit)


class OperationalCashFlowFactor(GrowthFactor):
    # 经营性现金流增长
    def __init__(self):
        super().__init__('op_cf')
        self._deps.add(CashFlowFactor())

    def calc(self):
        # 企业过去四个季度经营性现金流的增长率
        cash_flow = CashFlowFactor().get()
        self._factor = cash_flow.apply(calc_growth_rate, axis=1, result_type='broadcast', whole_df=cash_flow)


class MixGrowthFactor(MixFactorBase, GrowthFactor):
    # 合成因子
    def __init__(self):
        super(MixFactorBase, self).__init__('mixg')
        self._factor: Dict[pd.DataFrame] = {}
        self._deps.add(IncomeGrowthFactor())
        self._deps.add(NetProfitOfNonRecurringGoLFactor())
        self._deps.add(OperationalCashFlowFactor())

    def calc(self, universe: str):
        index = IncomeGrowthFactor().get(universe).index
        columns = IncomeGrowthFactor().get(universe).columns
        self._factor[universe] = pd.DataFrame((normalize(IncomeGrowthFactor().get(universe).T) + normalize(NetProfitOfNonRecurringGoLFactor().get(universe).T) +
                                               normalize(OperationalCashFlowFactor().get(universe).T)).T, index=index, columns=columns)
