
from typing import Optional

import pandas as pd

from .derived import DerivedFactor
from ...constant import StockFactorType


class MixFactorBase(DerivedFactor):

    def get(self, universe: str = 'default') -> Optional[pd.DataFrame]:
        if universe not in self._factor:
            try:
                self._factor[universe]: pd.DataFrame = pd.read_parquet(self._get_s3_factor_uri_with_universe(universe))
            except Exception as e:
                print(f'retrieve data from s3 failed, (err_msg){e}; try to re-calc')
                self.calc(universe)
        return self._factor[universe]

    def save(self, universe: str = 'default') -> bool:
        if self._factor is None or universe not in self._factor:
            return False
        self._factor[universe].to_parquet(self._get_s3_factor_uri_with_universe(universe), compression='gzip')
        return True


class ValueFactor(DerivedFactor):
    # 所有价值因子的基类
    def __init__(self, name):
        super().__init__(f'val/{name}', StockFactorType.VALUE)


class GrowthFactor(DerivedFactor):
    # 所有成长因子的基类
    def __init__(self, name):
        super().__init__(f'gro/{name}', StockFactorType.GROWTH)


class FinQualityFactor(DerivedFactor):
    # 所有财务质量因子的基类
    def __init__(self, name):
        super().__init__(f'fin/{name}', StockFactorType.FIN_QUALITY)


class VolatilityFactor(DerivedFactor):
    # 所有波动率因子的基类
    def __init__(self, name):
        super().__init__(f'vol/{name}', StockFactorType.VOLATILITY)


class ScaleFactor(DerivedFactor):
    # 所有规模因子的基类
    def __init__(self, name):
        super().__init__(f'sca/{name}', StockFactorType.SCALE)


class LeverageFactor(DerivedFactor):
    # 所有杠杆因子的基类
    def __init__(self, name):
        super().__init__(f'lev/{name}', StockFactorType.LEVERAGE)


class MomentumFactor(DerivedFactor):
    # 所有动量因子的基类
    def __init__(self, name):
        super().__init__(f'mom/{name}', StockFactorType.MOMENTUM)


class LiquidityFactor(DerivedFactor):
    # 所有流动性因子的基类
    def __init__(self, name):
        super().__init__(f'liq/{name}', StockFactorType.LIQUIDITY)


class TechFactor(DerivedFactor):
    # 所有技术因子的基类
    def __init__(self, name):
        super().__init__(f'tech/{name}', StockFactorType.TECH)


class Alpha101Factor(DerivedFactor):
    # 所有alpha101因子的基类
    def __init__(self, name):
        super().__init__(f'alpha101/{name}', StockFactorType.ALPHA101)
