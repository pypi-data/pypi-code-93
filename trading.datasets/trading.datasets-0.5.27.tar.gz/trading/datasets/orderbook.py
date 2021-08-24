"""Module containing the OrderBook class."""

from __future__ import annotations

import datetime as dtlib

import pandas as pd

from trading.datasets import dataset_info
from trading.datasets import exchange as exchangelib
from trading.datasets.utils import datetime_utils
from trading.datasets.utils import db_utils
from trading.datasets.utils import generic_utils


__all__ = [
    # Class exports
    'OrderBook',
]


class OrderBookSeries(pd.Series):
    """Slicing an OrderBook should returns a OrderBookSeries."""

    @property
    def _constructor(self):  # pragma: no cover
        return OrderBookSeries

    @property
    def _constructor_expanddim(self):  # pragma: no cover
        return OrderBook


class OrderBook(pd.DataFrame):
    """Order book dataframe."""

    _DEFAULT_DATETIME_COLUMN = 'datetime'
    _DEFAULT_COLUMNS = [
        _DEFAULT_DATETIME_COLUMN,
        'best_ask',
        'worst_ask',
        'average_ask',
        'ask_amount',
        'best_bid',
        'worst_bid',
        'average_bid',
        'bid_amount',
    ]

    @property
    def _constructor(self):
        return OrderBook

    @property
    def _constructor_sliced(self):
        return OrderBookSeries

    @classmethod
    def load(
        cls,
        exchange_name: str,
        symbol: str,
        slippage: float = 0.001,
        start: dtlib.datetime | str | int | None = None,
        end: dtlib.datetime | str | int | None = None,
    ) -> OrderBook:

        """Returns an instance of a DataFrame based on the given parameters.

        Arguments:
            exchange_name: Name of the crypto asset exchange.
            symbol: Ticker symbol of the crypto asset.
            start: Starting datetime of the data to be fetched.
                The input argument can be a string indicating a
                valid datetime-like string or a number indicating the
                timestamp in milliseconds.
            end: Ending timestamp of the data to be fetched.
                The input argument can be a string indicating a
                valid datetime-like string or a number indicating the
                timestamp in milliseconds.

        Returns:
            An instance of a `DataFrame` containing the data of the
            given input parameters.
        """

        # Validate and convert the exchange name into an exchange instance
        exchange = exchangelib.get(exchange_name)()

        # Validate and standardize the symbol before using it
        symbol = exchange.get_valid_symbol(symbol)

        # Make sure that the start and end times are valid
        timeframe = dataset_info.Timeframe('1h')
        start, end = exchange.get_valid_start_end(start, end, timeframe)

        print(f'Downloading {exchange.name} {symbol} orderbooks '
              f'from {start} to {end}...')

        time_diff = end - start
        pbar_target = int(time_diff.days * 24 * 60 / 4)
        pbar_target += int(time_diff.seconds / 60 / 4)
        pbar_target += int(time_diff.microseconds / 1000 / 60 / 4)
        pbar_target *= 2
        pbar = generic_utils.Progbar(pbar_target)

        # Generate query and execute to get the result
        query = cls._generate_db_query(exchange.name, symbol, start, end)
        with db_utils.get_db_connection() as db_cursor:
            db_cursor.execute(query)
            orderbooks = db_cursor.fetchall()

        pbar.update(pbar_target // 2)

        preprocessed_orderbooks = []
        for orderbook in orderbooks:
            _, datetime, asks, bids = orderbook

            preprocessed_orderbooks.append(
                [datetime] +
                cls._preprocess_asks_bids(asks, slippage) +
                cls._preprocess_asks_bids(bids, slippage)
            )

            pbar.add(1)

        # Make sure the index is a datetime type
        orderbooks = cls(preprocessed_orderbooks, columns=cls._DEFAULT_COLUMNS)
        orderbooks[cls._DEFAULT_DATETIME_COLUMN] = (
            datetime_utils.get_datetime(
                orderbooks[cls._DEFAULT_DATETIME_COLUMN]))

        orderbooks = orderbooks.set_index(cls._DEFAULT_DATETIME_COLUMN)

        # Make sure the progressbar ends
        pbar.update(pbar_target)

        return orderbooks

    @staticmethod
    def _preprocess_asks_bids(
        ab_list: list[list[str | float]],
        slippage: float,
    ) -> list[list[str | float]]:

        ab_list = [ab.split(',') for ab in ab_list.split(';')]
        ab_bases = [float(ab[0]) for ab in ab_list]
        ab_quotes = [float(ab[1]) for ab in ab_list]

        best_ab = max(ab_bases)
        worst_ab = best_ab * (1 - slippage)

        ab_bases = [base for base in ab_bases if base >= worst_ab]
        ab_quotes = [
            quote for base, quote in zip(ab_bases, ab_quotes)
            if base >= worst_ab
        ]

        ab_amount = sum(ab_quotes)
        average_ab = sum([
            base * quote for base, quote in zip(ab_bases, ab_quotes)
        ]) / ab_amount

        return [best_ab, worst_ab, average_ab, ab_amount]

    @staticmethod
    def _generate_db_query(
        exchange_name: str,
        symbol: str,
        start: dtlib.datetime,
        end: dtlib.datetime,
    ) -> str:

        query_template = '''
            SELECT *
            FROM orderbook
            WHERE market_id IN (
                SELECT id
                FROM market
                WHERE exchange_id IN (
                    SELECT id
                    FROM exchange
                    WHERE name = '{exchange_name}'
                )
                AND symbol = '{symbol}'
            )
            AND timestamp BETWEEN '{start}'::timestamp
            AND '{end}'::timestamp
            ORDER BY timestamp ASC
        '''

        return query_template.format(
            exchange_name=exchange_name,
            symbol=symbol,
            start=start.strftime("%Y-%m-%d %H:%M:%S"),
            end=end.strftime("%Y-%m-%d %H:%M:%S"),
        )
