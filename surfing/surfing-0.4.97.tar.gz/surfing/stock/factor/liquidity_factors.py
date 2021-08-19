
from typing import Dict

import numpy as np
import pandas as pd

from .factor_types import LiquidityFactor, MixFactorBase
from .basic_factors import TurnoverFactor
from .utils import get_day


class TurnoverDateFactor(LiquidityFactor):
    # 换手率（X日）
    def __init__(self, num):
        super().__init__('t'+str(num)+'d')
        self.num = num
        self._deps.add(TurnoverFactor())

    def calc(self):
        tov = TurnoverFactor().get()
        ls = tov.index  # trading_day_list
        fac = tov.copy()
        for i in range(0, len(tov)):
            try:
                temp = get_day(self.num, ls, tov.index[i])
                temp2 = get_day(0, ls, tov.index[i])
                fac.iloc[i] = tov.loc[temp:temp2].mean()
            except Exception:
                fac.iloc[i] = np.nan
        self._factor = fac


class Turnover30DFactor(TurnoverDateFactor):
    # 换手率（30日）
    def __init__(self):
        super().__init__(30)


class Turnover60DFactor(TurnoverDateFactor):
    # 换手率（60日）
    def __init__(self):
        super().__init__(60)


class Turnover90DFactor(TurnoverDateFactor):
    # 换手率（90日）
    def __init__(self):
        super().__init__(90)


class MixLiquidityFactor(MixFactorBase, LiquidityFactor):
    # 合成因子
    def __init__(self):
        super(MixFactorBase, self).__init__('mixl')
        self._factor: Dict[pd.DataFrame] = {}
        self._deps.add(Turnover30DFactor())
        self._deps.add(Turnover60DFactor())
        self._deps.add(Turnover90DFactor())

    def calc(self, universe: str):
        self._factor[universe] = Turnover30DFactor().get_normalized(universe) + Turnover60DFactor().get_normalized(universe) + Turnover90DFactor().get_normalized(universe)
