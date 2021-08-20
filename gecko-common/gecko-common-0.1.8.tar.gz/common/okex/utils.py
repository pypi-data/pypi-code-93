from constants import InstType


def parse_symbol(symbol: str) -> (InstType, str):
    symbol = symbol.upper()
    s = symbol.split('-')[0]

    if symbol.endswith("SWAP"):
        return InstType.SWAP, s
    if symbol.split('-')[-1].isdigit():
        return InstType.FUTURES, s
    return InstType.SPOT, s
