"""Package for exchange-related components in Trading Datasets."""

import re

from fuzzywuzzy import process as fuzzy_match

from trading.datasets import errors

from trading.datasets.exchange.base import Exchange
from trading.datasets.exchange.binance import BinanceExchange
from trading.datasets.exchange.bitmex import BitMEXExchange
from trading.datasets.exchange.bitstamp import BitstampExchange
from trading.datasets.exchange.ftx import FTXExchange


__all__ = [
    # Class exports
    'Exchange',
    'BinanceExchange',
    'BitMEXExchange',
    'BitstampExchange',
    'FTXExchange',

    # Function exports
    'get',
]

_EXCHANGE_NAME_CLASS_MAPPING = {
    'Binance': BinanceExchange,
    'BitMEX': BitMEXExchange,
    'Bitstamp': BitstampExchange,
    'FTX': FTXExchange,
}


def get(exchange_name: str) -> Exchange:  # pylint: disable=redefined-outer-name
    """Returns the proper exchange class given its name."""
    valid_exchange_name, match_score = fuzzy_match.extractOne(
        str(exchange_name), _EXCHANGE_NAME_CLASS_MAPPING.keys())

    # Raise an error if the exchange name is unrecognized or invalid
    if not exchange_name or match_score < 55:
        raise errors.UnknownExchangeError(exchange_name)

    return _EXCHANGE_NAME_CLASS_MAPPING.get(valid_exchange_name, Exchange)


# Dynamic export of exchange name constants
for exchange_name in _EXCHANGE_NAME_CLASS_MAPPING.keys():  # pylint: disable=consider-iterating-dictionary
    # Replace any special character with underscore
    # and convert exchange names to uppercase
    constant_name = re.sub('[^A-Za-z0-9]+', '_', exchange_name).upper()
    globals()[constant_name] = exchange_name

__all__ += [key.upper() for key in _EXCHANGE_NAME_CLASS_MAPPING.keys()]
