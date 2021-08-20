"""
常量
"""


KLINE_INTERVAL_1MINUTE = '1min'
KLINE_INTERVAL_5MINUTE = '5min'
KLINE_INTERVAL_15MINUTE = '15min'
KLINE_INTERVAL_30MINUTE = '30min'
KLINE_INTERVAL_60MINUTE = '60min'
KLINE_INTERVAL_1HOUR = '1hour'
KLINE_INTERVAL_4HOUR = '4hour'
KLINE_INTERVAL_1DAY = '1day'
KLINE_INTERVAL_1WEEK = '1week'
KLINE_INTERVAL_1MONTH = '1mon'

WS_DEPTH_0 = "step0"
WS_DEPTH_1 = "step1"
WS_DEPTH_2 = "step2"
WS_DEPTH_3 = "step3"
WS_DEPTH_4 = "step4"
WS_DEPTH_5 = "step5"
WS_DEPTH_6 = "step6"
WS_DEPTH_7 = "step7"
WS_DEPTH_8 = "step8"
WS_DEPTH_9 = "step9"
WS_DEPTH_10 = "step10"
WS_DEPTH_11 = "step11"
WS_DEPTH_12 = "step12"
WS_DEPTH_13 = "step13"
WS_DEPTH_14 = "step14"
WS_DEPTH_15 = "step15"
WS_DEPTH_16 = "step16"
WS_DEPTH_17 = "step17"
WS_DEPTH_18 = "step18"
WS_DEPTH_19 = "step19"


class DataType:
    INCREMENTAL = "incremental"
    SNAPSHOT = "snapshot"


class WebSocketOP:
    SUB = "sub"
    REQ = "req"
    UNSUB = "unsub"
    AUTH = "auth"
    PING = "ping"
    PONG = "pong"
    NOTIFY = "notify"
    ERROR = "error"
    CLOSE = "close"


class BasisPriceType:
    OPEN = "open"
    CLOSE = "close"
    HIGH = "high"
    LOW = "low"
    AVERAGE = "average"


class AssetChangeEvent:
    """
    资产变化通知相关事件说明，比如订单创建开仓(order.open) 、订单成交(order.match)（除开强平和结算交割）、结算交割(settlement)、
    订单强平成交(order.liquidation)（对钆和接管仓位）、订单撤销(order.cancel) 、合约账户划转（contract.transfer)（包括外部划转）、
    系统（contract.system)、其他资产变化(other)、切换杠杆（switch_lever_rate）、初始资金（init）
    """
    OPEN = "order.open"
    MATCH = "order.match"
    SETTLEMENT = "settlement"
    LIQUIDATION = "order.liquidation"
    CANCEL = "order.cancel"
    TRANSFER = "contract.transfer"
    SYSTEM = "contract.system"
    OTHER = "other"
    SWITCH_LEVER_RATE = "switch_lever_rate"
    INIT = "init"


class ContractType:
    THIS_WEEK = "this_week"
    NEXT_WEEK = "next_week"
    QUARTER = "quarter"
    NEXT_QUARTER = "next_quarter"


class TradeType:
    SPOT = "spot"
    FUTURE = "future"
    COIN_M = "coin_margined"
    USD_M = "usdt_margined"


class WSMsgFormat:
    SIMPLE = 'simple'   # {'sub': 'xxx'}
    STANDARD = 'standard'   # {'op': 'sub', 'topic': 'xxx'}


class OrderStatus:
    ReadyToSubmit1 = 1  # 准备提交
    ReadyToSubmit2 = 2  # 2准备提交
    Submitted = 3   # 已提交
    PartiallyMatched = 4    # 部分成交
    CancelledWithPartiallyMatched = 5   # 部分成交已撤单
    FullyMatched = 6    # 全部成交
    Cancelled = 7   # 已撤单
    Cancelling = 11  # 撤单中


class OrderPriceType:
    LIGHTNING = 'lightning'
    LIMIT = 'limit'
    POST_ONLY = 'post_only'     # 只做maker单
    OPPONENT = 'opponent'   # 对手价
    FOK = 'fok'


class Side:
    BUY = "buy"
    SELL = "sell"




