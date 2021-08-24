"""Tests for exchange.bitmex."""
# pylint: disable=missing-class-docstring,missing-function-docstring

import ccxt
import pytest

from trading.datasets import dataset_info
from trading.datasets import errors
from trading.datasets import exchange as exchange_lib
from trading.datasets.utils import datetime_utils


@pytest.fixture(name='exchange', scope="class")
def fixture_exchange():
    return exchange_lib.BitMEXExchange()


class TestExchangeBitMEX:

    def test_initialization(self, exchange):
        assert issubclass(type(exchange), exchange_lib.Exchange)
        assert isinstance(exchange, exchange_lib.BitMEXExchange)

    def test_generate_fetch_ohlcv_params(self, exchange):
        expected_output = {'endTime': '2021-01-01T01:00:00.000Z', 'count': 1}
        assert exchange._generate_fetch_ohlcv_params(
            dataset_info.Timeframe('1h'),
            datetime_utils.get_datetime('2011'),
            datetime_utils.get_datetime('2021'),
            1) == expected_output

        expected_output = {'endTime': '2004-11-23T10:26:40.000Z', 'count': 12}
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
        mocker.patch('ccxt.bitmex.fetch_ohlcv', side_effect=ccxt.ExchangeError)
        mocker.patch('time.sleep', return_value=None)
        with pytest.raises(errors.OHLCVFetchError):
            exchange.get_ohlcv(
                symbol='btcusd',
                timeframe='1d',
                start='JAN 1 2021',
                end='JAN 4 2021')

    def test_successful_get_ohlcv(self, exchange):
        expected_output = [
            [1609459200000, 28951.0, 29065.0, 28727.0, 29039.0, 84364703.0],
            [1609462800000, 29039.0, 29561.0, 29012.0, 29460.0, 214017760.0],
            [1609466400000, 29460.0, 29517.5, 29215.0, 29267.0, 84059857.0],
        ]
        assert exchange.get_ohlcv(
            symbol='btcusd',
            timeframe='1h',
            start='JAN 1 2021 00:00:00+00:00',
            end='JAN 1 2021 02:00:00+00:00') == expected_output

        assert exchange.get_ohlcv(
            symbol='btcusd',
            timeframe='1d',
            start='JAN 1 2000',
            end='JAN 4 2000') == []
