
from typing import Dict

import numpy as np
import pandas as pd

from .factor_types import LeverageFactor, MixFactorBase
from .basic_factors import FloatAssetAvgFactor, FloatDebtAvgFactor, FixAssetAvgFactor, TotalDebtAvgFactor, CashFlowTTMFactor


class FloatRatioFactor(LeverageFactor):
    # 流动比率
    def __init__(self):
        super().__init__('fl_ra')
        self._deps.add(FloatAssetAvgFactor())
        self._deps.add(FloatDebtAvgFactor())

    def calc(self):
        # 企业的流动资产除以流动负债
        self._factor = FloatAssetAvgFactor().get() / FloatDebtAvgFactor().get().replace({0: np.nan})


class StockDebtRatioFactor(LeverageFactor):
    # 股本债务比
    def __init__(self):
        super().__init__('st_de')
        self._deps.add(FixAssetAvgFactor())
        self._deps.add(TotalDebtAvgFactor())

    def calc(self):
        # 企业的净资产除以总债务
        self._factor = FixAssetAvgFactor().get() / TotalDebtAvgFactor().get().replace({0: np.nan})


class CashFlowRatioFactor(LeverageFactor):
    # 营业现金流比率
    def __init__(self):
        super().__init__('cf_r')
        self._deps.add(CashFlowTTMFactor())
        self._deps.add(FloatDebtAvgFactor())

    def calc(self):
        # 过去四个季度的经营现金流除以流动负债
        self._factor = CashFlowTTMFactor().get() / FloatDebtAvgFactor().get().replace({0: np.nan})


class MixLeverageFactor(MixFactorBase, LeverageFactor):
    # 合成因子
    def __init__(self):
        super(MixFactorBase, self).__init__('mixl')
        self._factor: Dict[pd.DataFrame] = {}
        self._deps.add(FloatRatioFactor())
        self._deps.add(StockDebtRatioFactor())
        self._deps.add(CashFlowRatioFactor())

    def calc(self, universe: str):
        self._factor[universe] = FloatRatioFactor().get_normalized(universe) + StockDebtRatioFactor().get_normalized(universe) + CashFlowRatioFactor().get_normalized(universe)
