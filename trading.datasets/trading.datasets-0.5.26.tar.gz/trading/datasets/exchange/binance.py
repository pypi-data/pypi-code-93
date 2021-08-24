"""Module containing the Binance Exchange class."""

from __future__ import annotations

import datetime as dtlib

import ccxt

from trading.datasets import dataset_info
from trading.datasets import exchange
from trading.datasets.utils import datetime_utils


__all__ = [
    # Class exports
    'BinanceExchange',
]


class BinanceExchange(exchange.Exchange, ccxt.binance):
    """Improved class implementation of the CCXT Binance Exchange."""

    FETCH_OHLCV_LIMIT = 999

    def _generate_fetch_ohlcv_params(
        self,
        timeframe: dataset_info.Timeframe,
        start: dtlib.datetime,
        end: dtlib.datetime,
        limit: int,
    ) -> dict:

        # Binance accepts the ending timestamp in milliseconds
        end_ms = datetime_utils.get_milliseconds(end)

        return {
            'endTime': int(end_ms),
            'limit': limit,
        }
