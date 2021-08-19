
import inspect
import enum

INDEX_PRICE_EXTRA_TRADE_DAYS = 8
INDEX_VAL_EXTRA_TRADE_DAYS = 8
FUND_NAV_EXTRA_TRADE_DAYS = 8
FUTURE_PRICE_EXTRA_TRADE_DAYS = 4
QUARTER_UPDATE_DATE_LIST = ('0331', '0630', '0930', '1231')
SEMI_UPDATE_DATE_LIST = ('0630', '1231')


class ReadableEnum(object):
    _code_name_cache = None

    @classmethod
    def init_cache(cls):
        cls._code_name_cache = ({}, {})
        for name in dir(cls):
            attr = getattr(cls, name)
            if name.startswith('_') or inspect.ismethod(attr):
                continue
            # assert attr not in cls._code_name_cache[0], f'failed to register {name}, {attr} is a registed value'
            # assert name not in cls._code_name_cache[1], f'failed to register {attr}, {name} is a registed enum'
            cls._code_name_cache[0][attr] = name
            cls._code_name_cache[1][name] = attr

    @classmethod
    def read(cls, code):
        if cls._code_name_cache is None:
            cls.init_cache()
        return cls._code_name_cache[0].get(code, code)

    @classmethod
    def parse(cls, code):
        if cls._code_name_cache is None:
            cls.init_cache()
        return cls._code_name_cache[1].get(code, code)


class SourceType(enum.IntEnum):
    qieman = 1  # 且慢
    danjuan = 2  # 蛋卷
    em = 3  # 天天基金
    gf_sec = 4  # 广发基金

    # 以下为手工爬取部分
    bcm = 8192  # 交通银行
    ccb = 8193  # 建设银行
    cgb = 8194  # 广发银行
    citics = 8195  # 中信证券
    citicb = 8196  # 中信银行
    cmbc = 8197  # 民生银行
    gtjas = 8198  # 国泰君安
    guosens = 8199  # 国信证券
    icbc = 8200  # 工商银行
    pinganb = 8201  # 平安银行
    spdb = 8202  # 浦发银行

    @staticmethod
    def get_names_of_type():
        return {
            SourceType.qieman: '且慢',
            SourceType.danjuan: '蛋卷',
            SourceType.em: '天天基金',
            SourceType.gf_sec: '广发基金',
            SourceType.bcm: '交通银行',
            SourceType.ccb: '建设银行',
            SourceType.cgb: '广发银行',
            SourceType.citics: '中信证券',
            SourceType.citicb: '中信银行',
            SourceType.cmbc: '民生银行',
            SourceType.gtjas: '国泰君安',
            SourceType.guosens: '国信证券',
            SourceType.icbc: '工商银行',
            SourceType.pinganb: '平安银行',
            SourceType.spdb: '浦发银行',
        }


# 板块类型
class SectorType(enum.IntEnum):
    industry = 1
    topic = 2
    strategy = 3
    scale = 4


# 指数价格数据来源类型
class IndexPriceSource(enum.IntEnum):
    default = 1
    none = 2
    macroeconomic = 3


# 基金收费模式
class CodeFeeMode(enum.IntEnum):
    none = 0
    a_type = 1  # 前端收费
    b_type = 2  # 后端收费


# 股票因子类型
class StockFactorType(enum.IntEnum):
    BASIC = 1  # 基础
    VALUE = 2  # 价值
    GROWTH = 3  # 成长
    FIN_QUALITY = 4  # 财务质量
    LEVERAGE = 5  # 杠杆
    SCALE = 6  # 规模
    MOMENTUM = 7  # 动量
    VOLATILITY = 8  # 波动率
    LIQUIDITY = 9  # 流动性
    ANALYST = 10  # 分析师
    TECH = 11  # 技术
    ALPHA101 = 12  # WorldQuant alpha101
    SPEC = 13  # 一些特殊因子


# 基金因子类型
class FundFactorType(enum.IntEnum):
    BASIC = 1  # 基础
    DERIVED = 2 # 高级
    SCORE = 3 # 分数


# 行业分类类型
class IndClassType(enum.IntEnum):
    SWI1 = 1  # 申万一级行业指数
    SWI2 = 2  # 申万二级行业指数
    SWI3 = 3  # 申万三级行业指数


# 持仓资产类型
class HoldingAssetType(enum.IntEnum):
    MUTUAL = 1  # 公募基金
    HEDGE = 2  # 私募基金


# 资金状态
class FundStatus(enum.IntEnum):
    IN_TRANSIT = 1  # 在途
    DONE = 2  # 完成
    INSENTIVE_DONE = 3  # 业绩计提扣除份额完成


class ExchangeID(ReadableEnum):
    NOT_AVAILABLE = 0
    SSE = 1
    SZE = 2
    HK = 3
    CFFEX = 4
    DCE = 5
    SHFE = 6
    CZCE = 7

    CRYPTO = 100
    HUOBI = 101
    OKEX = 102
    BINANCE = 103
    BITMEX = 104


class Direction(ReadableEnum):
    NOT_AVAILABLE = 0
    BUY = 1
    SELL = 2


class PosiDirection(ReadableEnum):
    NOT_AVAILABLE = 0
    NET = 1
    LONG = 2
    SHORT = 3


class OrderType(ReadableEnum):
    NOT_AVAILABLE = 0
    PLAIN_ORDER_PREFIX = 1
    BASKET_ORDER_PREFIX = 2
    ALGO_ORDER_PREFIX = 3
    # PLAIN
    PLAIN_ORDER = 10
    LIMIT = 11
    MARKET = 12
    FAK = 13
    FOK = 14
    # BASKET
    BASKET_ORDER = 20
    # ALGO
    ALGO_ORDER = 30
    TWAP = 31


class OffsetFlag(ReadableEnum):
    NOT_AVAILABLE = 0
    OPEN = 1
    CLOSE = 2
    FORCE_CLOSE = 3
    CLOSE_TODAY = 4
    CLOSE_YESTERDAY = 5


class OrderStatus(ReadableEnum):
    NOT_AVAILABLE = 0
    UNKNOWN = 1
    PROPOSED = 10
    RESPONDED = 20
    QUEUEING = 30
    NO_TRADE_QUEUEING = 31
    PART_TRADE_QUEUEING = 32
    PENDING_MAX = 39
    # // if status >= 40, it is not pending
    REJECTED = 40  # // router / gateway / exchange reject
    REJECT_BY_ROUTER = 41
    REJECT_BY_GATEWAY = 42
    REJECT_BY_EXCHANGE = 43
    CANCELLED = 50  # // cancelled, no mater all traded or partly traded
    NO_TRADE_CANCELED = 51
    PART_TRADE_CANCELED = 52
    ALL_TRADED = 60
    # // some other middle status...
    TO_CANCEL = 70


class TradingStyle(ReadableEnum):
    NOT_AVAILABLE = 0
    AGGRESSIVE = 1
    NEUTRAL = 2
    CONSERVATIVE = 3


class BarType(ReadableEnum):
    NOT_AVAILABLE = 0
    MIN_1 = 1
    MIN_3 = 2
    MIN_5 = 3
    MIN_15 = 4
    MIN_30 = 5
    HOUR_1 = 10
    HOUR_2 = 11
    HOUR_4 = 12
    HOUR_6 = 13
    HOUR_12 = 14
    DAY_1 = 20
    WEEK_1 = 30
    MONTH_1 = 40
    YEAR_1 = 50

    _type_secs_cache = None

    @classmethod
    def get_seconds(cls, bar_type):
        if cls._type_secs_cache is None:
            cls._type_secs_cache = {
                cls.MIN_1: 1 * 60,
                cls.MIN_3: 3 * 60,
                cls.MIN_5: 5 * 60,
                cls.MIN_15: 15 * 60,
                cls.MIN_30: 30 * 60,
                cls.HOUR_1: 1 * 60 * 60,
                cls.HOUR_2: 2 * 60 * 60,
                cls.HOUR_4: 4 * 60 * 60,
                cls.HOUR_6: 6 * 60 * 60,
                cls.HOUR_12: 12 * 60 * 60,
                cls.DAY_1: 1 * 24 * 60 * 60,
                cls.WEEK_1: 1 * 7 * 24 * 60 * 60,
                cls.MONTH_1: 1 * 30 * 24 * 60 * 60,  # not accurate
                cls.YEAR_1: 1 * 365 * 24 * 60 * 60,  # not accurate
            }
        return cls._type_secs_cache.get(bar_type, -1)


class AssetType(ReadableEnum):
    NOT_AVAILABLE = 0
    #
    TRADITIONAL_ASSET = 10
    STOCK = 11
    FUTURES = 12
    OPTION = 13
    FUND = 14
    #
    CRYPTO_ASSET = 20
    CRYPTO_SPOT = 21
    CRYPTO_CONTRACT = 22
    CRYPTO_MARGIN = 23
    CRYPTO_PERPETUAL = 24
    CRYPTO_CONTRACT_MARGIN = 25  # 为CRYPTO_COIN_MARGIN_CONTRACT对应的margin
    CRYPTO_COIN_MARGIN_CONTRACT = 26  # 这里特指以币计价的合约,确定了为这类asset需再额外确定对应的margin(体现在posItem里)


class ExecRole(ReadableEnum):
    NOT_AVAILABLE = 0
    MAKER = 1
    TAKER = 2


class MarginMode(ReadableEnum):
    NOT_AVAILABLE = 0
    CROSSED = 1
    FIXED = 2

class LongShort():
    # [long, short] +1 top, -1 bottom, 0 None
    Lt      = [1,   0,  'Longtop']
    Lb      = [-1,  0,  'Longbottom']
    St      = [0,   1,  'Shorttop']
    Sb      = [0,   -1, 'Shortbottom']
    Long    = [1,   0,  'Long']
    Short   = [0,   1,  'Short']
    LtSb    = [1,   -1, 'LongtopShortbottom']
    LbSt    = [-1,  1,  'LongbottomShorttop']

    def find_strategy(self, code):
        self._code_name_cache = ({}, {})
        for name in dir(self):
            attr = getattr(self, name)
            if name.startswith('_') or inspect.ismethod(attr):
                continue
            self._code_name_cache[0][attr[2]] = name
            self._code_name_cache[1][name] = attr

        return self._code_name_cache[1][self._code_name_cache[0].get(code, code)]


class ExchangeStatus(ReadableEnum):
    """交易状态指标"""
    OPEN = 0
    SUSPENDED = 1
    LIMITED = 2
    CLOSE = 3


class FOFTradeStatus(ReadableEnum):
    PURCHASE = 1  # 认购
    SUBSCRIBE = 2  # 申购
    REDEEM = 3  # 赎回
    DIVIDEND_CASH = 4  # 现金分红
    DIVIDEND_VOLUME = 5  # 红利再投
    DEDUCT_REWARD = 6  # 划扣业绩报酬
    DEDUCT_REWARD_AND_DIVIDEND_VOLUME = 7  # 划扣业绩报酬且红利再投
    DEDUCT_REWARD_AND_DIVIDEND_CASH = 8  # 划扣业绩报酬且现金分红
    FORCE_PLUS = 9
    FORCE_MINUS = 10


class FOFStatementStatus(ReadableEnum):
    """FOF资产状态"""
    IN_INVESTOR = 1             # 投资者投入
    OUT_INVESTOR = 2            # 投资者取出
    IN_HEDGE = 3                # 底层资产卖出
    OUT_HEDGE = 4               # 底层资产买入
    IN_HEDGE_DIVIDEND = 5       # 底层资产分红
    OUT_FOF_DIVIDEND = 6        # 产品分红
    IN_INTEREST = 7             # 利息入账
    OUT_MANAGEMENT = 8          # 管理费出账
    OUT_CUSTODIAN = 9           # 托管费出账
    OUT_ADMINISTRATIVE = 10     # 行政管理费出账
    IN_OTHER_IN = 11            # 其他入账
    OUT_OTHER_OUT = 12          # 其他出账
    OUT_OTHER_DEBT = 13         # 其他负债
    IN_OTHER_DEBT_OFFSET = 14   # 其他负债冲抵


class FOFTransitStatus(ReadableEnum):
    """FOF在途资金状态"""
    PENDING = 1
    DONE = 2


class FOFOtherRecordStatus(ReadableEnum):
    """FOF其他记录状态"""
    IN = 1
    OUT = 2


class FOFSaleStatue(ReadableEnum):
    """FOF产品状态"""
    COLLECTION = 1          # 募集期
    OPEN = 2                # 开放期
    LOCK = 3                # 锁定期
    CLEAR = 4               # 已清算


class FOFStrategyType(ReadableEnum):
    """FOF产品 策略类型"""
    S1 = 1                  # 主观多头
    S2 = 2                  # 指数增强
    S3 = 3                  # 市场中性
    S4 = 4                  # 管理期货
    S5 = 5                  # 事件驱动
    S6 = 6                  # 宏观对冲
    S7 = 7                  # 高频套利
    S8 = 8                  # 债券策略
    S10 = 10                # 组合策略
    S11 = 11                # 股票多空
    S12 = 12                # 其他（期权等）

    @staticmethod
    def get_type_of_names():
        return {
            '主观多头': FOFStrategyType.S1,
            '指数增强': FOFStrategyType.S2,
            '市场中性': FOFStrategyType.S3,
            '管理期货': FOFStrategyType.S4,
            '事件驱动': FOFStrategyType.S5,
            '宏观对冲': FOFStrategyType.S6,
            '高频套利': FOFStrategyType.S7,
            '债券策略': FOFStrategyType.S8,
            '组合策略': FOFStrategyType.S10,
            '股票多空': FOFStrategyType.S11,
            '其他（期权等）': FOFStrategyType.S12,
        }


FOFStrategyTypeDic = {
    1:'主观多头',
    2:'指数增强',
    3:'市场中性',
    4:'管理期货',
    5:'事件驱动',
    6:'宏观对冲',
    7:'高频套利',
    8:'债券策略',
    10:'组合策略',
    11:'股票多空',
    12:'其他（期权等)',
}
    
class FOFRiskType(ReadableEnum):
    """FOF产品 风险等级"""
    R1 = 1
    R2 = 2
    R3 = 3
    R4 = 4
    R5 = 5


class DividendCalcMethod(ReadableEnum):
    '''分红计算方式'''

    BY_TOTAL_AMOUNT = 1  # 红利总额
    BY_PER_UNIT = 2  # 每单位红利


class FOFIncentiveFeeMode(ReadableEnum):
    ''' 业绩计提方式 '''

    SCST_HIGH_WL_S = 1  # 单人单笔高水位法（扣减份额）
    SCST_HIGH_WL_N = 2  # 单人单笔高水位法（扣减净值）
    INTE_HIGH_WL = 3  # 整体高水位法
    INTE_HIGH_WL_WITH_SCST_R = 4  # 整体高水位配合单人单笔赎回时计提法


class EMailParserType(ReadableEnum):
    ''' 电子邮件 parser 类型'''

    E_PARSER_NAV = 1  # 净值邮件
    E_PARSER_VALUATION = 2  # 估值表邮件
