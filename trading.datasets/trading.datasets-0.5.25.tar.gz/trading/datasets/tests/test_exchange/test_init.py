"""Tests for trading.datasets.exchange."""
# pylint: disable=missing-class-docstring,missing-function-docstring

import pytest

from trading.datasets import errors
from trading.datasets import exchange


class TestExchange:

    def test_getting_exchange_object(self):
        assert exchange.get(exchange.BINANCE) == exchange.BinanceExchange
        assert exchange.get(exchange.BITMEX) == exchange.BitMEXExchange
        assert exchange.get(exchange.FTX) == exchange.FTXExchange

        with pytest.raises(errors.UnknownExchangeError):
            exchange.get('SomeCompletelyUnknownExchange')
