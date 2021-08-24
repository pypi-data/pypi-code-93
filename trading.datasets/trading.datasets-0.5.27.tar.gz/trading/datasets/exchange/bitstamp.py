"""Module containing the Bitstamp Exchange class."""

from __future__ import annotations

import datetime as dtlib

import ccxt

from trading.datasets import dataset_info
from trading.datasets import exchange
from trading.datasets.utils import datetime_utils


__all__ = [
    # Class exports
    'BitstampExchange',
]


class BitstampExchange(exchange.Exchange, ccxt.bitstamp):
    """Improved class implementation of the CCXT Bitstamp Exchange."""

    FETCH_OHLCV_LIMIT = 999

    def _generate_fetch_ohlcv_params(
        self,
        timeframe: dataset_info.Timeframe,
        start: dtlib.datetime,
        end: dtlib.datetime,
        limit: int,
    ) -> dict:

        # Bitstamp accepts the starting and ending timestamp in seconds
        end_seconds = datetime_utils.get_seconds(end)
        start_seconds = end_seconds
        start_seconds -= timeframe.get_duration(
            unit=dataset_info.TimeframeUnit.SECOND) * limit

        return {
            'start': int(start_seconds),
            'end': int(end_seconds),
            'limit': limit,
        }
