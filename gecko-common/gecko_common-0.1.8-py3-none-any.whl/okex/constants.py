from enum import Enum


class TradeMode(Enum):
    # 交易模式
    # 保证金模式
    ISOLATED = "isolated"   # 逐仓
    CROSS = "cross" # 全仓
    # 非保证金模式
    CASH = "cash"


class MgnMode(Enum):
    # 保证金模式
    ISOLATED = "isolated"  # 逐仓
    CROSS = "cross"  # 全仓


class Side(Enum):
    BUY = "buy"
    SELL = "sell"
    NET = "net"


class OrderType(Enum):
    MARKET = "market"   # 市价单
    LIMIT = "limit"     # 限价单
    POST_ONLY = "post_only" # 限价委托，只做maker单，如果该笔订单的任何部分会吃掉当前挂单深度，则该订单将被全部撤销。
    FOK = "fok" # 限价委托，全部成交或立即取消，如果无法全部成交该笔订单，则该订单将被全部撤销
    IOC = "ioc" # 限价委托，立即成交并取消剩余，立即按照委托价格成交，并取消该订单剩余未完成数量，不会再深度列表上展示委托数量
    OPTIMAL_LIMIT_IOC = "optimal_limit_ioc" # 市价委托，立即成交并取消剩余，仅适用于交割合约和永续合约


class InstType(Enum):
    # 产品类型
    SPOT = "SPOT"   # 币币
    MARGIN = "MARGIN"   # 币币杠杆
    SWAP = "SWAP"   # 永续合约
    FUTURES = "FUTURES"     # 交割合约
    OPTION = "OPTION"   # 期权
    ANY = "ANY"     # 全部


class OrderState(Enum):
    # 订单状态
    LIVE = "live"   # 等待成交
    PARTIALLY_FILLED = "partially_filled"   # 部分成交
    FILLED = "filled"   # 完全成交
    CANCELED = "canceled"    # 撤单成功


class OrderCategory(Enum):
    # 订单种类
    TWAP = "twap"   # TWAP自动换币
    ADL = "adl" # ADL自动减仓
    FULL_LIQUIDATION = "full_liquidation"   # 强制平仓
    PARTIAL_LIQUIDATION = "partial_liquidation" # 强制减仓
    DELIVERY = "delivery"   # 交割


class PosMode(Enum):
    # 持仓模式
    NET = "net_mode"   # 单向
    LONG_SHORT = "long_short_mode"  # 双向


class PosSide(Enum):
    LONG = "long"
    SHORT = "short"


class SystemState(Enum):
    # 系统升级状态
    SCHEDULED = "scheduled" # 等待中
    ONGOING = "ongoing" # 进行中
    COMPLETED = "completed" # 已完成
    CANCELED = "canceled"   # 已取消


class WebSocketOp(Enum):
    LOGIN = "login"
    SUB = "subscribe"
    UNSUB = "unsubscribe"


class WebSocketEvent:
    ERROR = "error"
    SUB = "subscribe"
    LOGIN = "login"


class KlineType(Enum):
    candle1Y = "candle1Y"
    candle6M = "candle6M"
    candle3M = "candle3M"
    candle1M = "candle1M"
    candle1W = "candle1W"
    candle1D = "candle1D"
    candle2D = "candle2D"
    candle3D = "candle3D"
    candle5D = "candle5D"
    candle12H = "candle12H"
    candle6H = "candle6H"
    candle4H = "candle4H"
    candle2H = "candle2H"
    candle1H = "candle1H"
    candle30m = "candle30m"
    candle15m = "candle15m"
    candle5m = "candle5m"
    candle3m = "candle3m"
    candle1m = "candle1m"


class BooksType(Enum):
    # 深度类型
    books = "books"
    books5 = "books5"
    books_l2_tbt = "books-l2-tbt"
    books50_l2_tbt = "books50-l2-tbt"
