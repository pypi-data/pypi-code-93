"""Module containing the BitMEX Exchange class."""

from __future__ import annotations

import datetime as dtlib

import ccxt

from trading.datasets import dataset_info
from trading.datasets import exchange
from trading.datasets.utils import datetime_utils


__all__ = [
    # Class exports
    'BitMEXExchange',
]


class BitMEXExchange(exchange.Exchange, ccxt.bitmex):
    """Improved class implementation of the CCXT BitMEX Exchange."""

    FETCH_OHLCV_LIMIT = 999

    def _generate_fetch_ohlcv_params(
        self,
        timeframe: dataset_info.Timeframe,
        start: dtlib.datetime,
        end: dtlib.datetime,
        limit: int,
    ) -> dict:

        # BitMEX accepts the ending timestamp in ISO-8601 format
        # the reason why we add 1-timeframe worth of time to the
        # ending is because BitMEX uses closing time as reference
        end = end + timeframe.to_timedelta()
        end_iso8601 = datetime_utils.get_iso8601(end)

        return {
            'endTime': end_iso8601,
            'count': limit,
        }
