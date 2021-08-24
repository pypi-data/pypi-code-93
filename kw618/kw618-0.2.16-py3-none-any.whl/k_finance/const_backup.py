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
# 所有的'限价单'的类型
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








































# 待删
# ======================================================================================================
# ======================================================================================================

# [tips]: 仅挑选需要的'field'即可
    # [注意]: 这里的 field 对应关系仅用于: 多股列表中获取最新数据 (个股的详细数据中,field的对应关系就不是这样了)
    # 两种change_name_dic:
        # 1. /api/qt/ulist/sse: "多股列表"接口
        # 2. /api/qt/stock/get: "个股详情"接口
ulist_change_name_dict = {
    "f2":"最新股价(分)",
    "f3":"涨跌幅(万分制)",
    "f4":"涨跌额(分)",
    "f5":"成交总手(手)",
    "f6":"成交总额(元)",
    "f7":"振幅(万分制)",
    "f8":"换手率(万分制)",
    "f9":"市盈率(百分制)",
    "f10":"量比(百分制)",
    "f12":"Zqdm",
    "f13":"SecSe", # 0:深市; 1:上市; 116:香港; 105:纳斯达克; 90:板块; 106:NYSE; 119:外汇;
    "f14":"Zqmc",
    "f15":"最高股价(分)",
    "f16":"最低股价(分)",
    "f18":"昨收股价(分)",
    "f22":"涨速(万分制)",
    "f26":"上市日期",
    "f30":"当前手(正负+手)",
    "f31":"买一价(分)",
    "f32":"卖一价(分)",

    "f38":"总股本(股)",
    "f39":"流通股本(股)",
    "f40":"营业收入(元)",
    "f41":"营业收入同比(百分制)",
    "f42":"营业利润(元)",
    "f44":"利润总额(元)",
    "f45":"净利润(元)", # 营业收入>营业利润>利润总额>净利润
    "f46":"净利润同比(百分制)",
    "f49":"毛利率(百分制)",

    "f50":"总资产(元)",
    "f51":"流动资产(元)",
    "f52":"固定资产(元)",
    "f53":"无形资产(元)",
    "f54":"总负债(元)",
    "f55":"流动负债(元)",
    "f56":"长期负债(元)",
    "f57":"资产负债比率(百分制)",

    "f100":"行业板块",
    "f102":"区域板块",
    "f103":"概念板块",
    "f112":"每股收益(元)",
    "f113":"每股净资产(元)",
}







# 自选的股票集
# 重点关注: 回测一般都只选这些"zx"股票回测就行
# ===========================================
A_Zqmc_lst = [
    "海康威视", "科大讯飞", "惠城科技",
    "宁波银行", "中国平安", "格力电器", "牧原股份", "三一重工",
    "长江电力",
    "大康农业", "好想你",
    "欧菲光", "复星医药", "海螺水泥",
    "贵州茅台", "五粮液", "美的集团", "招商银行",
]


ETF_Zqmc_lst = [
    "芯片ETF", "生物医药ETF", "主要消费ETF", "军工行业ETF", "酒ETF", "新能源车ETF",
    "创业板", "沪深300ETF", "中证500ETF",
    "深价值", "深红利", "深F60",
]













def main():
    pass


if __name__ == '__main__':
    print("Start test!\n\n")
    main()
    print("\n\n\nIt's over!")
