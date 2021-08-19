
from typing import Dict

import numpy as np
import pandas as pd

from .factor_types import ValueFactor, MixFactorBase
from .basic_factors import MarketValueFactor, AdjNetAssetAvgFactor, NetProfitTTMFactor, TotalRevenueTTMFactor
from .basic_factors import EBITDATTMFactor, EntValueFactor, DividendYearlyFactor
from .utils import normalize


class NAToMVFactor(ValueFactor):
    # 净市率
    def __init__(self):
        super().__init__('na_mv')
        self._deps.add(AdjNetAssetAvgFactor())
        self._deps.add(MarketValueFactor())

    def calc(self):
        # 净资产 / 总市值，即市净率倒数
        self._factor = AdjNetAssetAvgFactor().get() / MarketValueFactor().get().replace({0: np.nan})


class NPToMVFactor(ValueFactor):
    # 盈利收益比
    def __init__(self):
        super().__init__('np_mv')
        self._deps.add(NetProfitTTMFactor())
        self._deps.add(MarketValueFactor())

    def calc(self):
        # 净利润 / 总市值，即市盈率倒数
        self._factor = NetProfitTTMFactor().get() / MarketValueFactor().get().replace({0: np.nan})


class SPSToPFactor(ValueFactor):
    # 营收股价比
    def __init__(self):
        super().__init__('sps_p')
        self._deps.add(TotalRevenueTTMFactor())
        self._deps.add(MarketValueFactor())

    def calc(self):
        # 每股销售额 / 股价，即市销率倒数
        self._factor = TotalRevenueTTMFactor().get() / MarketValueFactor().get().replace({0: np.nan})


class DividendYieldFactor(ValueFactor):
    # 股息率
    def __init__(self):
        super().__init__('dys')
        self._deps.add(DividendYearlyFactor())
        self._deps.add(MarketValueFactor())

    def calc(self):
        # 过去12个月总派息额 / 总市值
        self._factor = DividendYearlyFactor().get() / MarketValueFactor().get().replace({0: np.nan})


class EBITDAToMVFactor(ValueFactor):
    # EBITDA股价比
    def __init__(self):
        super().__init__('eb_mv')
        self._deps.add(EBITDATTMFactor())
        self._deps.add(MarketValueFactor())

    def calc(self):
        # EBITDA（税息折旧及摊销前利润） / 总市值
        self._factor = EBITDATTMFactor().get() / MarketValueFactor().get().replace({0: np.nan})


class EBITDAToEVFactor(ValueFactor):
    # EBITDA企业价值比
    def __init__(self):
        super().__init__('eb_ev')
        self._deps.add(EBITDATTMFactor())
        self._deps.add(EntValueFactor())

    def calc(self):
        # EBITDA（税息折旧及摊销前利润） / 企业价值, 即企业倍数的倒数
        self._factor = EBITDATTMFactor().get() / EntValueFactor().get().replace({0: np.nan})


class MixValueFactor(MixFactorBase, ValueFactor):
    # 合成因子
    def __init__(self):
        super(MixFactorBase, self).__init__('mixv')
        self._factor: Dict[pd.DataFrame] = {}
        self._deps.add(NAToMVFactor())
        self._deps.add(NPToMVFactor())
        self._deps.add(SPSToPFactor())
        self._deps.add(DividendYieldFactor())
        self._deps.add(EBITDAToMVFactor())
        self._deps.add(EBITDAToEVFactor())

    def calc(self, universe: str):
        index = NAToMVFactor().get(universe).index
        columns = NAToMVFactor().get(universe).columns
        self._factor[universe] = pd.DataFrame((normalize(NAToMVFactor().get(universe).T) + normalize(NPToMVFactor().get(universe).T) + normalize(SPSToPFactor().get(universe).T) +
                                               normalize(DividendYieldFactor().get(universe).T) + normalize(EBITDAToMVFactor().get(universe).T) + normalize(EBITDAToEVFactor().get(universe).T)).T, index=index, columns=columns)
