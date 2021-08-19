from datetime import datetime
from typing import Dict, List, Tuple

from ctlml_commons.entity.candle import Candle
from ctlml_commons.entity.lot import Lot
from ctlml_commons.entity.range_window import RangeWindow
from ctlml_commons.util.date_utils import timeoffset_as_str, to_est
from ctlml_commons.util.num_utils import number_to_percentage_str, percent_change


# TODO: add docstrings
class FocusPlugins:
    @classmethod
    def should_buy_percentage_wise(
        cls, symbol: str, current_price: float, candles: Dict[str, Candle], percentage_up: float
    ) -> Tuple[bool, str]:
        if not cls._ensure_buy_prereqs(candle_data=candles):
            return False, "Not enough candle data."

        if not candles.keys():
            return False, f"Not opening price"

        open_price: float = candles[list(candles.keys())[-1]].open
        diff: float = percent_change(num_start=open_price, num_end=current_price)

        diff_as_str: str = number_to_percentage_str(diff)
        threshold_as_str: str = number_to_percentage_str(percentage_up)

        if diff > percentage_up:
            buy_message: str = (
                f"Buy as {symbol} is up over threshold. {diff_as_str} vs {threshold_as_str}. "
                + f"Current and Open prices: ({current_price} vs. {open_price})."
            )

            return True, buy_message

        wait_message: str = (
            f"Wait as {symbol} is not up over threshold {diff_as_str} vs {threshold_as_str}. "
            + f"Current and Open prices: ({current_price} vs. {open_price})."
        )
        return False, wait_message

    @classmethod
    def should_buy_price_wise(cls, current_price: float, candles: Dict[str, Candle], num_periods: int):

        if not cls._ensure_buy_prereqs(candle_data=candles):
            return False, "Not enough data"

        is_up_last_periods, message = cls._up_last(candle_data=candles, a_time=to_est(), periods=num_periods)

        if not is_up_last_periods:
            not_up_message: str = f"Not up: price: {current_price}, open: {candles[list(candles.keys())[-1]].open}"
            return False, not_up_message

        return True, message

    @classmethod
    def should_sell_percentage_wise(
        cls, lot: Lot, current_price: float, percentage_window: RangeWindow
    ) -> Tuple[bool, str]:
        threshold: float = percent_change(num_start=lot.purchase_price, num_end=current_price)
        threshold_as_str: str = number_to_percentage_str(threshold)

        if threshold > percentage_window.ceiling:
            over_sell_message: str = (
                f"{lot.symbol} with purchase price {current_price} is {threshold_as_str} over {lot.purchase_price}. "
                + "Selling"
            )

            return True, over_sell_message
        elif threshold < percentage_window.floor:
            under_sell_message: str = (
                f"{lot.symbol} with purchase price {current_price} is {threshold_as_str} under {lot.purchase_price}. "
                + "Selling"
            )

            return True, under_sell_message

        return False, f"Sell per: {lot.purchase_price} versus {current_price} = {threshold_as_str}"

    @classmethod
    def should_sell_price_wise(
        cls, lot: Lot, current_price: float, total_threshold: float, per_share_price_window: RangeWindow
    ) -> Tuple[bool, str]:
        per_share_diff: float = current_price - lot.purchase_price
        lot_diff: float = per_share_diff * lot.shares

        if lot_diff >= total_threshold:
            message: str = f"Win over threshold by {lot_diff} vs {total_threshold}"
            return True, message

        elif lot_diff <= -total_threshold:
            message: str = f"Loss over threshold by {lot_diff} vs {-total_threshold}"
            return True, message

        elif per_share_diff >= per_share_price_window.ceiling:
            message: str = f"Win over per share price by {per_share_diff} vs {per_share_price_window.ceiling}"
            return True, message

        elif per_share_diff <= per_share_price_window.floor:
            message: str = f"Loss under per share price by {per_share_diff} vs {per_share_price_window.floor}"
            return True, message

        message: str = (
            f"Wait...lot_diff: {lot_diff} vs. {total_threshold}. per_share: "
            + f"{per_share_price_window.floor} < {per_share_diff} < "
            + f"{per_share_price_window.ceiling}"
        )
        return False, message

    @classmethod
    def _ensure_buy_prereqs(cls, candle_data: Dict[str, Candle]) -> bool:
        return candle_data is not None

    @classmethod
    def _up_last(cls, candle_data: Dict[str, Candle], a_time: datetime, periods: int) -> Tuple[bool, str]:

        period_names: List[str] = cls._get_periods(a_time=a_time, periods=periods)
        if not cls._all_exists(periods=period_names, candle_data=candle_data):
            return False, f"Not enough correct periods: {period_names} vs {candle_data.keys()}"

        ups: List[bool] = cls._get_ups(periods=period_names, candle_data=candle_data)
        return all(ups), cls._get_ups_msg(periods=period_names, candle_data=candle_data)

    @classmethod
    def _get_periods(cls, a_time, periods: int) -> List[str]:
        period_names = []

        mins = 0
        for i in range(periods):
            period_names.append(timeoffset_as_str(mins * 60, a_time))
            mins += 1

        period_names.reverse()
        return period_names[:-1]

    @classmethod
    def _all_exists(cls, periods: List[str], candle_data: Dict[str, Candle]) -> bool:
        return set(periods).issubset(candle_data.keys())

    @classmethod
    def _get_ups(cls, periods: List[str], candle_data: Dict[str, Candle]) -> List[bool]:
        return [candle_data[period].close > candle_data[period].open for period in periods]

    @classmethod
    def _get_ups_msg(cls, periods: List[str], candle_data: Dict[str, Candle]) -> str:
        return f"{cls._get_ups(periods, candle_data)} " + "; ".join(
            [f"{period}: {candle_data[period].close} > {candle_data[period].open}" for period in periods]
        )
