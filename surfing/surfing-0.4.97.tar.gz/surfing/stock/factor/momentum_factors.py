
from typing import Dict

import numpy as np
import pandas as pd

from .factor_types import MomentumFactor, MixFactorBase
from .basic_factors import StockPostPriceFactor
from .utils import get_day


class AdjMomentumDateFactor(MomentumFactor):
    # 动量（X月）
    def __init__(self, num):
        super().__init__('m'+str(num)+'d')
        self.num = num
        self._deps.add(StockPostPriceFactor())

    def calc(self):
        spp = StockPostPriceFactor().get()
        ls = spp.index  # trading_day_list
        fac = spp.copy()
        for i in range(0, len(spp)):
            try:
                temp = get_day(30, ls, spp.index[i])
                temp2 = get_day(self.num, ls, spp.index[i])
                fac.iloc[i] = spp.loc[temp] / spp.loc[temp2] - 1
            except Exception:
                fac.iloc[i] = np.nan
        self._factor = fac


class AdjMomentum3MFactor(AdjMomentumDateFactor):
    # 动量（3月）
    def __init__(self):
        super().__init__(90)


class AdjMomentum6MFactor(AdjMomentumDateFactor):
    # 动量（6月）
    def __init__(self):
        super().__init__(180)


class AdjMomentum12MFactor(AdjMomentumDateFactor):
    # 动量（12月）
    def __init__(self):
        super().__init__(365)


class MixMomentumFactor(MixFactorBase, MomentumFactor):
    # 合成因子
    def __init__(self):
        super(MixFactorBase, self).__init__('mixm')
        self._factor: Dict[pd.DataFrame] = {}
        self._deps.add(AdjMomentum3MFactor())
        self._deps.add(AdjMomentum6MFactor())
        self._deps.add(AdjMomentum12MFactor())

    def calc(self, universe: str):
        self._factor[universe] = AdjMomentum3MFactor().get_normalized(universe) + AdjMomentum6MFactor().get_normalized(universe) + AdjMomentum12MFactor().get_normalized(universe)
