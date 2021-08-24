"""Tests for exchange.bitstamp."""
# pylint: disable=missing-class-docstring,missing-function-docstring,line-too-long

import ccxt
import pytest

from trading.datasets import dataset_info
from trading.datasets import errors
from trading.datasets import exchange as exchange_lib
from trading.datasets.utils import datetime_utils


@pytest.fixture(name='exchange', scope="class")
def fixture_exchange():
    return exchange_lib.BitstampExchange()


class TestExchangeBitstamp:

    def test_initialization(self, exchange):
        assert issubclass(type(exchange), exchange_lib.Exchange)
        assert isinstance(exchange, exchange_lib.BitstampExchange)

    def test_generate_fetch_ohlcv_params(self, exchange):
        expected_output = {'start': 1609455600, 'end': 1609459200, 'limit': 1}
        assert exchange._generate_fetch_ohlcv_params(
            dataset_info.Timeframe('1h'),
            datetime_utils.get_datetime('2011'),
            datetime_utils.get_datetime('2021'),
            1) == expected_output

        expected_output = {'start': 1100082400, 'end': 1101119200, 'limit': 12}
        assert exchange._generate_fetch_ohlcv_params(
            dataset_info.Timeframe('1d'),
            datetime_utils.get_datetime('2000'),
            datetime_utils.get_datetime('2004-11-22 10:26:40+00:00'),
            12) == expected_output

    def test_validating_symbol(self, exchange):
        with pytest.raises(errors.UnknownSymbolError):
            exchange.get_valid_symbol('BKAHDBLAJDHunknwonExchange')

    def test_unsuccessful_get_ohlcv(self, exchange, mocker):
        """Separate unsuccessful case so it can be mock patched."""
        mocker.patch('ccxt.bitstamp.fetch_ohlcv', side_effect=ccxt.ExchangeError)
        mocker.patch('time.sleep', return_value=None)
        with pytest.raises(errors.OHLCVFetchError):
            exchange.get_ohlcv(
                symbol='btcusd',
                timeframe='1d',
                start='JAN 1 2021',
                end='JAN 4 2021')

    def test_successful_get_ohlcv(self, exchange):
        expected_output = [
            [1609459200000, 28999.63, 29700.0, 28720.0, 29402.64, 8781.46555456],
            [1609545600000, 29410.77, 33333.0, 29050.0, 32216.53, 17867.8788985],
            [1609632000000, 32216.51, 34800.0, 31977.45, 33097.83, 14160.5812801],
            [1609718400000, 33068.83, 33669.76, 27734.0, 32005.88, 22446.94000548],
        ]
        assert exchange.get_ohlcv(
            symbol='btcusd',
            timeframe='1d',
            start='JAN 1 2021',
            end='JAN 4 2021') == expected_output

        assert exchange.get_ohlcv(
            symbol='btcusd',
            timeframe='1d',
            start='JAN 1 2000',
            end='JAN 4 2000') == []
