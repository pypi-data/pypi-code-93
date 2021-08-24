"""Tests for exchange.ftx."""
# pylint: disable=missing-class-docstring,missing-function-docstring,line-too-long

import ccxt
import pytest

from trading.datasets import dataset_info
from trading.datasets import errors
from trading.datasets import exchange as exchange_lib
from trading.datasets.utils import datetime_utils


@pytest.fixture(name='exchange', scope="class")
def fixture_exchange():
    return exchange_lib.FTXExchange()


class TestExchangeFTX:

    def test_initialization(self, exchange):
        assert issubclass(type(exchange), exchange_lib.Exchange)
        assert isinstance(exchange, exchange_lib.FTXExchange)

    def test_generate_fetch_ohlcv_params(self, exchange):
        expected_output = {
            'start_time': 1609455600,
            'end_time': 1609459200,
            'limit': 1
        }

        assert exchange._generate_fetch_ohlcv_params(
            timeframe=dataset_info.Timeframe('1h'),
            start=datetime_utils.get_datetime('2011'),
            end=datetime_utils.get_datetime('2021'),
            limit=1) == expected_output

        expected_output = {
            'start_time': 1100082400,
            'end_time': 1101119200,
            'limit': 12
        }

        assert exchange._generate_fetch_ohlcv_params(
            timeframe=dataset_info.Timeframe('1d'),
            start=datetime_utils.get_datetime('2000'),
            end=datetime_utils.get_datetime('2004-11-22 10:26:40+00:00'),
            limit=12) == expected_output

    def test_validating_symbol(self, exchange):
        with pytest.raises(errors.UnknownSymbolError):
            exchange.get_valid_symbol('BKAHDBLAJDHunknwonExchange')

    def test_unsuccessful_get_ohlcv(self, exchange, mocker):
        """Separate unsuccessful case so it can be mock patched."""
        mocker.patch('ccxt.ftx.fetch_ohlcv', side_effect=ccxt.ExchangeError)
        mocker.patch('time.sleep', return_value=None)
        with pytest.raises(errors.OHLCVFetchError):
            exchange.get_ohlcv(
                symbol='btcusd',
                timeframe='1d',
                start='JAN 1 2021',
                end='JAN 4 2021')

    def test_successful_get_ohlcv(self, exchange):
        expected_output = [
            [1609459200000, 28965.0, 29691.5, 28700.0, 29399.0, 172186059.13855],
            [1609545600000, 29399.0, 33349.5, 29023.5, 32201.5, 254401802.10525],
            [1609632000000, 32201.5, 34809.5, 31978.0, 33045.5, 147019465.64805],
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
