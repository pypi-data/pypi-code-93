
from .factor_types import ScaleFactor
from .basic_factors import StockPriceFactor, CirculationShareFactor


class MarketValueFloatedFactor(ScaleFactor):
    # A股流通市值
    def __init__(self):
        super().__init__('mv_flo')
        self._deps.add(StockPriceFactor())
        self._deps.add(CirculationShareFactor())

    def calc(self):
        self._factor = StockPriceFactor().get() * CirculationShareFactor().get()
