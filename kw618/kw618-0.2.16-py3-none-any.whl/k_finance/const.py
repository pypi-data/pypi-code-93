import json
import pandas as pd


# 导入常用的固定路径(多平台通用)
from kw618._file_path import *
# 本脚本依赖很多 utils_requests的函数和模块, 直接用*  (注意要避免循环导入问题)
from kw618.k_requests.utils_requests import *
from kw618.k_requests.ocr import *
from kw618.k_python.utils_python import *
from kw618.k_pandas.utils_pandas import *
try:
    from kw618.k_finance.secret.secret import *
except:
    print(f"[警告]: 无法导入 secret 密码表模块...")

req = myRequest().req
client = pymongo.MongoClient(f'mongodb://kerwin:kw618@{HOST}:27017/')
db_for_quant = client["quant"]


from vnpy.trader.object import *
from vnpy.trader.constant import *
# 所有的'限价单'的类型
LIMIT_ORDER_TYPES = [
    "LIMIT", "STOP_LOSS_LIMIT", "TAKE_PROFIT_LIMIT",
    "LIMIT_MAKER"
]
# 所有的'市价单'的类型
MARKET_ORDER_TYPES = [
    "MARKET", "STOP_LOSS_MARKET", "TAKE_PROFIT_MARKET"
]
# 所有的'停止单'的类型
STOP_ORDER_TYPES = [
    "STOP_LOSS_LIMIT", "STOP_LOSS_MARKET", "TAKE_PROFIT_LIMIT", "TAKE_PROFIT_MARKET"
]





# 订单类型-命名
# ===================
# kw618 转换至 vnpy
ORDERTYPE_KW2VT = {
    # vnpy中好像没有把 stop单分的那么详细... 之后再研究下为啥vnpy只设置了一个stop,其他几类是怎么实现的
    "LIMIT" : OrderType.LIMIT, # 1.限价单
    "MARKET" : OrderType.MARKET, # 2. 市价单
    "STOP_LOSS_LIMIT" : OrderType.STOP, # 3. 限价-止损单
    "STOP_LOSS_MARKET" : OrderType.STOP, # 4. 市价-止损单
    "TAKE_PROFIT_LIMIT" : OrderType.STOP, # 5. 限价-止盈单
    "TAKE_PROFIT_MARKET" : OrderType.STOP, # 6. 市价-止盈单
}
# kw618 转换至 binance
    # 1.现货的'订单类型'
ORDERTYPE_SPOT_KW2BINANCE = {
    "LIMIT" : "LIMIT", # 1.限价单
    "MARKET" : "MARKET", # 2. 市价单
    "STOP_LOSS_LIMIT" : "STOP_LOSS_LIMIT", # 3. 限价-止损单
    "STOP_LOSS_MARKET" : "STOP_LOSS", # 4. 市价-止损单
    "TAKE_PROFIT_LIMIT" : "TAKE_PROFIT_LIMIT", # 5. 限价-止盈单
    "TAKE_PROFIT_MARKET" : "TAKE_PROFIT", # 6. 市价-止盈单
    "LIMIT_MAKER" : "LIMIT_MAKER", # 7. 只做挂单
}
    # 2.合约的'订单类型'
ORDERTYPE_FUTURES_KW2BINANCE = {
    "LIMIT" : "LIMIT", # 1.限价单
    "MARKET" : "MARKET", # 2. 市价单
    "STOP_LOSS_LIMIT" : "STOP", # 3. 限价-止损单
    "STOP_LOSS_MARKET" : "STOP_MARKET", # 4. 市价-止损单
    "TAKE_PROFIT_LIMIT" : "TAKE_PROFIT", # 5. 限价-止盈单
    "TAKE_PROFIT_MARKET" : "TAKE_PROFIT_MARKET", # 6. 市价-止盈单
    "TRAILING_STOP_MARKET" : "TRAILING_STOP_MARKET", # 7. 暂时还不知道啥意思....
}
ORDERTYPE_DFUTURES_KW2BINANCE = ORDERTYPE_FUTURES_KW2BINANCE

# 交易类型-命名
# ===================
# kw618 转换至 vnpy
OFFSET_KW2VT = {
    "OPEN" : Offset.OPEN,
    "CLOSE" : Offset.CLOSE
}
DIRECTION_KW2VT = {
    "BUY" : Direction.LONG,
    "SELL" : Direction.SHORT,
}
# kw618 转换至 binances (合约)
OFFSET_KW2BINANCES = { # 我已经不想搞懂币安为啥取'long/short'了... 神烦...放弃理解
    ("OPEN", "BUY") : "LONG", # 做多买入
    ("OPEN", "SELL") : "SHORT", # 做空卖出
    ("CLOSE", "BUY") : "SHORT", # 平空买入
    ("CLOSE", "SELL") : "LONG", # 平多卖出
}
DIRECTION_KW2BINANCES = {
    "BUY" : "BUY",
    "SELL" : "SELL"
}

# 币本位合约的所有币种
DFUTURES_ASSETS = [
    "BTC", "ETH", "LINK", "BNB", "DOT", "ADA", "LTC", "BCH", "XRP",
    "TRX", "EOS", "ETC", "EGLD", "DOGE", "UNI", "THETA", "XLM",
]

# 币本位有季度合约的币种
DFUTURES_QUARTER_ASSETS = [
    "BTC", "ETH", "LINK", "BNB", "DOT", "ADA", "LTC", "BCH", "XRP",
]


# 币安所有计价资产
QUOTE_ASSETS = [
    "BNB", "BTC", "ETH", "TRX", "XRP",
    "USDT", "BUSD", "AUD", "BRL", "EUR", "GBP", "RUB", "TRY", "TUSD", "USDC", "PAX", "BIDR", # 稳定币
    "DAI", "IDRT", "UAH", "NGN", "VAI", "BVND", # 稳定币
    "USD"
]

# 所有-U本位合约的asset
ALL_FUTURES_ASSETS = ['SUSHI', 'CVC', 'BTS', 'HOT', 'ZRX', 'QTUM', 'IOTA', 'BTC', 'WAVES', 'ADA', 'LIT', 'XTZ',
 'BNB', 'AKRO', 'HNT', 'ETC', 'XMR', 'YFI', 'ETH', 'ALICE', 'ALPHA', 'SFP', 'REEF', 'BAT', 'DOGE',
 'RLC', 'TRX', 'BTCST', 'STORJ', 'SNX', 'ETH', 'XLM', 'NEO', 'UNFI', 'SAND', 'DASH', 'KAVA', 'RUNE',
 'CTK', 'LINK', 'CELR', 'RSR', 'DGB', 'SKL', 'REN', 'TOMO', 'MTL', 'LTC', 'DODO', 'KSM', 'EGLD', 'BNB',
 'BTC', 'VET', 'ONT', 'TRB', 'MANA', 'COTI', 'CHR', 'BAKE', 'GRT', 'FLM', 'EOS', 'OGN', 'SC', 'BAL', 'STMX',
 'BTT', 'LUNA', 'DENT', 'KNC', 'SRM', 'ENJ', 'ZEN', 'ATOM', 'NEAR', 'BCH', 'IOST', 'HBAR', 'ZEC', '1000SHIB',
 'BZRX', 'AAVE', 'ALGO', 'ICP', 'LRC', 'AVAX', 'MATIC', '1INCH', 'MKR', 'THETA', 'UNI', 'LINA', 'RVN', 'FIL',
 'NKN', 'DEFI', 'COMP', 'SOL', 'BTC', 'OMG', 'ICX', 'BLZ', 'FTM', 'YFII', 'BAND', 'XRP', 'SXP', 'CRV', 'BEL',
 'DOT', 'XEM', 'ONE', 'ZIL', 'AXS', 'OCEAN', 'CHZ', 'ANKR']

# 核心-U本位合约的asset (为了减少不必要的计算资源开销...) (每个ws都是实时推送, 一百多个币*4个接口, 造成延迟比较严重!)
KEY_FUTURES_ASSETS = [
    'SUSHI', 'CVC', 'HOT', 'IOTA', 'BTC', 'ADA', 'LIT', # 7
    'BNB', 'HNT', 'ETC', 'XMR', 'ETH', 'ALICE', 'ALPHA', 'BAT', 'DOGE', # 9
    'TRX', 'STORJ', 'XLM', 'CTK', 'LINK', 'RSR', 'DGB', 'REN', 'LTC', 'DODO', 'EGLD', # 11
    'VET', 'COTI', 'BAKE', 'GRT', 'FLM', 'EOS', 'SC', 'BAL', 'STMX', # 9
    'BTT', 'LUNA', 'DENT', 'ENJ', 'ZEN', 'ATOM', 'BCH', 'HBAR', # 8
    'AAVE', 'ICP', 'AVAX', 'MATIC', '1INCH', 'MKR', 'THETA', 'UNI', 'LINA', 'FIL', # 10
    'SOL', 'OMG', 'FTM', 'BAND', 'XRP', 'SXP', 'CRV', 'BEL', # 8
    'DOT', 'XEM', 'ONE', 'ZIL', 'AXS', 'CHZ', 'ANKR' # 7
    ] # 共 69个asset

# ASSET_SUFFIXS = [ # 所有的后缀名... // 季度合约就比较麻烦,要经常更新, 暂不用
#     "USDT", "BNB", "BUSD",
#     "USDT_PERP", "USD_PERP", "USDT_210625", "USDT_210625", "USD_210625"
# ]































def main():
    pass


if __name__ == '__main__':
    print("Start test!\n\n")
    main()
    print("\n\n\nIt's over!")
