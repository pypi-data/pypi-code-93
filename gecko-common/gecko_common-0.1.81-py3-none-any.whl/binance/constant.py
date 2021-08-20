class TradeType:
    SPOT = "spot"
    COIN_M = "coin_m"
    USD_M = "usd_m"


class OrderUpdateEvent:
    NEW = "NEW"
    CANCELED = "CANCELED"
    CALCULATED = "CALCULATED"
    EXPIRED = "EXPIRED"
    TRADE = "TRADE"
