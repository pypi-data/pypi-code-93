
from typing import Dict

import pandas as pd
import numpy as np

from ...data.manager import DataManager
from .factor_types import VolatilityFactor, MixFactorBase
from .basic_factors import StockPostPriceFactor
from .utils import _TRADING_DAYS_PER_YEAR, normalize


class BetaSSEIFactor(VolatilityFactor):

    _WINDOW = 30

    # 上证指数beta
    def __init__(self):
        super().__init__('b_ssei')
        self._deps.add(StockPostPriceFactor())

    def calc(self):
        def _rolling_regression(x: np.ndarray):
            data = combined.iloc[x, :]
            self._factor.iloc[int(x[-1]), :] = np.polyfit(x=data.sse, y=data.drop(columns='sse'), deg=1)[0]
            return np.nan

        # 股票对上证指数回归得到的贝塔
        stock_ret = StockPostPriceFactor().get().pct_change()
        index_price = DataManager.basic_data('get_index_price_dt', index_list=['sse', 'tmd_1y'], columns=['close'])
        index_price = index_price.pivot(index='datetime', columns='index_id', values='close')
        index_price = index_price.reindex(index_price.index.union(stock_ret.index)).ffill().reindex(stock_ret.index)

        # 日化一年整存整取利率
        tmd_1y = index_price.tmd_1y * 0.01 / _TRADING_DAYS_PER_YEAR
        pd.testing.assert_index_equal(stock_ret.index, index_price.index)

        combined = stock_ret.join(index_price.sse.pct_change())
        combined = combined.sub(tmd_1y, axis=0).iloc[1:, :]

        self._factor = pd.DataFrame(index=combined.index, columns=stock_ret.columns)
        pd.Series(range(combined.shape[0])).rolling(window=self._WINDOW).apply(_rolling_regression, raw=True)
        self._factor = self._factor.reindex(stock_ret.index)


class Vol250DFactor(VolatilityFactor):

    _WINDOW = 250

    # 波动率（250日）
    def __init__(self):
        super().__init__('v_250d')
        self._deps.add(StockPostPriceFactor())

    def calc(self):
        # 股票收益率的标准差，选取过去250日的收益率进行计算
        stock_ret = StockPostPriceFactor().get().pct_change()
        self._factor = stock_ret.rolling(window=self._WINDOW).std()


class ResidualVolSSEIFactor(VolatilityFactor):

    _WINDOW = 30

    # 上证指数残差波动率
    def __init__(self):
        super().__init__('rv_ssei')
        self._deps.add(StockPostPriceFactor())

    def calc(self):
        def _rolling_regression(x: np.ndarray):
            data = combined.iloc[x, :]
            # 计算残差的标准差
            self._factor.iloc[int(x[-1]), :] = np.sqrt(np.polyfit(x=data.sse, y=data.drop(columns='sse'), deg=1, full=True)[1] / (self._WINDOW - 1))
            return np.nan

        # 股票对上证指数回归得到的贝塔
        stock_ret = StockPostPriceFactor().get().pct_change()
        index_price = DataManager.basic_data('get_index_price_dt', index_list=['sse', 'tmd_1y'], columns=['close'])
        index_price = index_price.pivot(index='datetime', columns='index_id', values='close')
        index_price = index_price.reindex(index_price.index.union(stock_ret.index)).ffill().reindex(stock_ret.index)

        # 日化一年整存整取利率
        tmd_1y = index_price.tmd_1y * 0.01 / _TRADING_DAYS_PER_YEAR
        pd.testing.assert_index_equal(stock_ret.index, index_price.index)

        combined = stock_ret.join(index_price.sse.pct_change())
        combined = combined.sub(tmd_1y, axis=0).iloc[1:, :]

        self._factor = pd.DataFrame(index=combined.index, columns=stock_ret.columns)
        pd.Series(range(combined.shape[0])).rolling(window=self._WINDOW).apply(_rolling_regression, raw=True)
        self._factor = self._factor.reindex(stock_ret.index)


class MixVolatilityFactor(MixFactorBase, VolatilityFactor):
    # 合成因子
    def __init__(self):
        super(MixFactorBase, self).__init__('mixv')
        self._factor: Dict[pd.DataFrame] = {}
        self._deps.add(BetaSSEIFactor())
        self._deps.add(Vol250DFactor())
        self._deps.add(ResidualVolSSEIFactor())

    def calc(self, universe: str):
        index = BetaSSEIFactor().get(universe).index
        columns = BetaSSEIFactor().get(universe).columns
        self._factor[universe] = pd.DataFrame((normalize(BetaSSEIFactor().get(universe).T) + normalize(Vol250DFactor().get(universe).T) +
                                               normalize(ResidualVolSSEIFactor().get(universe).T)).T, index=index, columns=columns)
