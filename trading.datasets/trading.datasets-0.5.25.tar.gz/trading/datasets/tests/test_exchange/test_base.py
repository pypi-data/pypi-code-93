"""Tests for exchange.base."""
# pylint: disable=missing-class-docstring,missing-function-docstring

import ccxt
import pandas as pd
import pytest
import pytz

from trading.datasets import dataset_info
from trading.datasets import exchange as exchange_lib


@pytest.fixture(name='exchange', scope="class")
def fixture_exchange():
    return exchange_lib.Exchange()


class TestExchangeBase:

    def test_initialization(self, exchange):
        assert issubclass(type(exchange), ccxt.Exchange)
        assert isinstance(exchange, exchange_lib.Exchange)

    def test_unimplemented_generate_fetch_ohlcv_params(self, exchange):
        with pytest.raises(NotImplementedError):
            # We don't really valid params, this is not implemented yet
            exchange._generate_fetch_ohlcv_params(None, None, None, None)

    def test_validating_fetch_limit(self, exchange):
        assert exchange._get_valid_limit(9999999) == exchange.FETCH_OHLCV_LIMIT
        assert exchange._get_valid_limit(None) == exchange.FETCH_OHLCV_LIMIT
        assert exchange._get_valid_limit(9.41) == 10
        assert exchange._get_valid_limit(9.71) == 10
        assert exchange._get_valid_limit(-123) == 0

    def test_validating_start_and_end_datetimes(self, exchange, mocker):
        timeframe = dataset_info.Timeframe(interval=1, unit='d')
        expected_start = pd.to_datetime('2020-09-23').replace(tzinfo=pytz.utc)
        expected_end = pd.to_datetime('2021-01-01').replace(tzinfo=pytz.utc)

        assert exchange.get_valid_start_end(
            None, '2021-01-01', timeframe) == (expected_start, expected_end)
        assert exchange.get_valid_start_end(
            '2020-09-23', None, timeframe) == (expected_start, expected_end)
