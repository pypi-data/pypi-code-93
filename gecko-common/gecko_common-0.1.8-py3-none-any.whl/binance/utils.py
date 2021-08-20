from constant import TradeType


def parse_symbol(symbol: str) -> (str, str):
    # 由于u本位永续 btcusdt 和 现货一样 btcusdt，无法分辨，目前忽略u本位永续，就当现货处理

    symbol = symbol.upper()

    if symbol.endswith("PERP"):
        return TradeType.COIN_M, symbol.split('_')[0].replace("USD", "")
    if '_' in symbol:
        if symbol.split('_')[0].endswith("USD"):
            return TradeType.COIN_M, symbol.split('_')[0].replace("USD", "")
        return TradeType.USD_M, symbol.split('_')[0].replace("USDT", "")

    # 现货目前只支持usdt交易对
    return TradeType.SPOT, symbol.replace("USDT", "")
