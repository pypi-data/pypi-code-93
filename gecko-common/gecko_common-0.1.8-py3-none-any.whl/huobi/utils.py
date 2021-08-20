import re

from .constants import TradeType


def reverse_direction(direction):
    return "buy" if direction == 'sell' else 'sell'


def parse_symbol(symbol: str) -> (str, str):
    symbol = symbol.upper()

    if '-' in symbol:
        s = symbol.split('-')[0]
        if symbol.endswith("USD"):
            return TradeType.COIN_M, s
        return TradeType.USD_M, s
    if any(map(str.isdigit, symbol)):
        s = re.match(r"^([A-Z]+)\d+$", symbol).groups()[0]
        return TradeType.FUTURE, s

    # 现货目前只支持usdt对
    return TradeType.SPOT, symbol.replace("USDT", "")
