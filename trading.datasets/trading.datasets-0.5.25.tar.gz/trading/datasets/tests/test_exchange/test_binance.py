"""Tests for exchange.binance."""
# pylint: disable=missing-class-docstring,missing-function-docstring

import ccxt
import pytest

from trading.datasets import dataset_info
from trading.datasets import errors
from trading.datasets import exchange as exchange_lib
from trading.datasets.utils import datetime_utils


@pytest.fixture(name='exchange', scope="class")
def fixture_exchange():
    return exchange_lib.BinanceExchange()


class TestExchangeBinance:

    def test_initialization(self, exchange):
        assert issubclass(type(exchange), exchange_lib.Exchange)
        assert isinstance(exchange, exchange_lib.BinanceExchange)

    def test_generate_fetch_ohlcv_params(self, exchange):
        expected_output = {'endTime': 1609459200000, 'limit': 1000}
        assert exchange._generate_fetch_ohlcv_params(
            dataset_info.Timeframe('1h'),
            datetime_utils.get_datetime('2011'),
            datetime_utils.get_datetime('2021'),
            1000) == expected_output

        expected_output = {'endTime': 1101119200000, 'limit': 12}
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
        mocker.patch(
            'ccxt.binance.fetch_ohlcv', side_effect=ccxt.ExchangeError)
        mocker.patch('time.sleep', return_value=None)

        with pytest.raises(errors.OHLCVFetchError):
            exchange.get_ohlcv(
                symbol='btcusd',
                timeframe='1d',
                start='JAN 1 2021',
                end='JAN 4 2021')

    def test_successful_get_ohlcv(self, exchange):
        expected_output = [
            [1609459200000, 28923.63, 28961.66, 28913.12, 28961.66, 27.457032],
            [1609459260000, 28961.67, 29017.5, 28961.01, 29009.91, 58.477501],
            [1609459320000, 29009.54, 29016.71, 28973.58, 28989.3, 42.470329],
        ]
        assert exchange.get_ohlcv(
            symbol='btcusd',
            timeframe='1m',
            start='JAN 1 2021 00:00:00+00:00',
            end='JAN 1 2021 00:02:00+00:00') == expected_output

        assert exchange.get_ohlcv(
            symbol='btcusd',
            timeframe='1d',
            start='JAN 1 2000',
            end='JAN 4 2000') == []
