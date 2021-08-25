from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from logging import Logger
from typing import Any, Dict, List, Optional, Tuple

from ctlml_commons.entity.candle import Candle
from ctlml_commons.entity.focus.focus import Focus
from ctlml_commons.entity.focus.focus_plugins import FocusPlugins
from ctlml_commons.entity.lot import Lot
from ctlml_commons.entity.news import News
from ctlml_commons.entity.range_window import RangeWindow


@dataclass(frozen=True)
class PercentageFocus(Focus):
    """Percentage up/down based investment strategy."""

    """Percentage based per share to consider purchasing"""
    percentage_up: float

    """Percentage up per share total to decide to sell"""
    percentage_window: RangeWindow

    """If should sell at the end of day"""
    sell_at_end_of_day: bool

    def evaluate_buy(
        self,
        symbol: str,
        news: List[News],
        current_price: float,
        candles: Dict[str, Candle],
        logger: Optional[Logger] = None,
    ) -> Tuple[bool, str]:
        return FocusPlugins.should_buy_percentage_wise(
            symbol=symbol, current_price=current_price, candles=candles, percentage_up=self.percentage_up
        )

    def evaluate_sell(
        self, lot: Lot, news: List[News], current_price: float, candles: Dict[str, Candle], logger: Logger
    ) -> Tuple[bool, str]:
        return FocusPlugins.should_sell_percentage_wise(
            lot=lot, current_price=current_price, percentage_window=self.percentage_window
        )

    def serialize(self) -> Dict[str, Any]:
        data = deepcopy(self.__dict__)
        data["percentage_window"] = self.percentage_window.serialize()
        data["focus_type"] = self.__class__.__name__
        return data

    @classmethod
    def deserialize(cls, input_data: Dict[str, Any]) -> PercentageFocus:
        data = deepcopy(input_data)

        del data["focus_type"]
        data["percentage_window"] = RangeWindow.deserialize(data["percentage_window"])

        return cls(**data)
