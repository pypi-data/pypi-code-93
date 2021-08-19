
from sqlalchemy import CHAR, Column, Integer, TEXT, BOOLEAN, text, Index, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import DOUBLE, DATE, TINYINT, DATETIME, MEDIUMTEXT, YEAR, SMALLINT, BIGINT, DECIMAL, VARCHAR

from ...constant import SectorType, IndexPriceSource, CodeFeeMode, IndClassType


class Base():
    _update_time = Column('_update_time', DATETIME, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  # 更新时间


# make this column at the end of every derived table
Base._update_time._creation_order = 9999
Base = declarative_base(cls=Base)


class WindFundInfo(Base):
    '''万徳基金信息表'''

    __tablename__ = 'wind_fund_info'

    wind_id = Column(CHAR(20), primary_key=True) # 基金代码
    desc_name = Column(CHAR(64)) # 基金名称
    full_name = Column(CHAR(255)) #基金全称
    start_date = Column(DATE) # 成立日期
    end_date = Column(DATE) # 结束日期
    benchmark = Column(CHAR(255)) # 业绩比较基准
    wind_class_1 = Column(CHAR(64)) # wind投资分类一级
    wind_class_2 = Column(CHAR(64)) # wind投资分类二级
    currency = Column(CHAR(20)) # 交易币种
    base_fund_id = Column(CHAR(20)) # 分级基金母基金代码
    is_structured = Column(TINYINT(1)) # 是否分级基金
    is_open = Column(TINYINT(1)) # 是否定期开放基金
    manager_id = Column(CHAR(255)) # 基金经理(历任)
    company_id = Column(CHAR(64)) # 基金公司


class RqStockPrice(Base):
    '''米筐股票不复权数据表'''

    __tablename__ = 'rq_stock_price'

    order_book_id = Column(CHAR(20), primary_key=True) # 股票ID
    datetime = Column(DATE, primary_key=True) # 日期

    open = Column(DOUBLE(asdecimal=False)) # 开盘价
    close = Column(DOUBLE(asdecimal=False)) # 收盘价
    high = Column(DOUBLE(asdecimal=False)) # 最高价
    low = Column(DOUBLE(asdecimal=False)) # 最低价
    limit_up = Column(DOUBLE(asdecimal=False)) # 涨停价
    limit_down = Column(DOUBLE(asdecimal=False)) # 跌停价
    total_turnover = Column(DOUBLE(asdecimal=False)) # 成交额
    volume = Column(DOUBLE(asdecimal=False)) # 成交量  不复权和后复权的交易量不同
    num_trades = Column(DOUBLE(asdecimal=False)) # 成交笔数

    __table_args__ = (
        Index('idx_rq_stock_price_datetime', 'datetime'),
    )


class RqStockPostPrice(Base):
    '''米筐股票后复权数据表'''

    __tablename__ = 'rq_stock_post_price'

    order_book_id = Column(CHAR(20), primary_key=True) # 股票ID
    datetime = Column(DATE, primary_key=True) # 日期

    open = Column(DOUBLE(asdecimal=False)) # 开盘价
    close = Column(DOUBLE(asdecimal=False)) # 收盘价
    high = Column(DOUBLE(asdecimal=False)) # 最高价
    low = Column(DOUBLE(asdecimal=False)) # 最低价
    limit_up = Column(DOUBLE(asdecimal=False)) # 涨停价
    limit_down = Column(DOUBLE(asdecimal=False)) # 跌停价
    total_turnover = Column(DOUBLE(asdecimal=False)) # 成交额
    volume = Column(DOUBLE(asdecimal=False)) # 成交量  不复权和后复权的交易量不同
    num_trades = Column(DOUBLE(asdecimal=False)) # 成交笔数

    __table_args__ = (
        Index('idx_rq_stock_post_price_datetime', 'datetime'),
    )


class RqStockMinute(Base):
    '''米筐股票分钟线数据表'''

    __tablename__ = 'rq_stock_minute'

    order_book_id = Column(CHAR(20), primary_key=True) # 股票ID
    datetime = Column(DATETIME, primary_key=True) # 日期

    open = Column(DOUBLE(asdecimal=False)) # 开盘价
    close = Column(DOUBLE(asdecimal=False)) # 收盘价
    high = Column(DOUBLE(asdecimal=False)) # 最高价
    low = Column(DOUBLE(asdecimal=False)) # 最低价
    total_turnover = Column(DOUBLE(asdecimal=False)) # 成交额
    volume = Column(DOUBLE(asdecimal=False)) # 成交量  不复权和后复权的交易量不同

    __table_args__ = (
        Index('idx_rq_stock_minute_datetime', 'datetime'),
    )


class RqIndexMinute(Base):
    '''米筐指数分钟线数据表'''

    __tablename__ = 'rq_index_minute'

    order_book_id = Column(CHAR(20), primary_key=True) # 指数ID
    datetime = Column(DATETIME, primary_key=True) # 日期

    open = Column(DOUBLE(asdecimal=False)) # 开盘价
    close = Column(DOUBLE(asdecimal=False)) # 收盘价
    high = Column(DOUBLE(asdecimal=False)) # 最高价
    low = Column(DOUBLE(asdecimal=False)) # 最低价
    total_turnover = Column(DOUBLE(asdecimal=False)) # 成交额
    volume = Column(DOUBLE(asdecimal=False)) # 成交量  不复权和后复权的交易量不同

    __table_args__ = (
        Index('idx_rq_index_minute_datetime', 'datetime'),
    )


class RqFundNav(Base):
    '''米筐基金净值表'''

    __tablename__ = 'rq_fund_nav'

    order_book_id = Column(CHAR(10), primary_key=True) # 合约代码
    datetime = Column(DATE, primary_key=True) # 日期

    unit_net_value = Column(DOUBLE(asdecimal=False)) # 单位净值
    acc_net_value = Column(DOUBLE(asdecimal=False)) # 累计单位净值
    adjusted_net_value = Column(DOUBLE(asdecimal=False)) # 复权净值
    change_rate = Column(DOUBLE(asdecimal=False)) # 涨跌幅
    daily_profit = Column(DOUBLE(asdecimal=False)) # 每万元收益（日结型货币基金专用）
    weekly_yield = Column(DOUBLE(asdecimal=False)) # 7日年化收益率（日结型货币基金专用）
    subscribe_status = Column(CHAR(10)) # 申购状态，开放 - Open, 暂停 - Suspended, 限制大额申赎 - Limited, 封闭期 - Close
    redeem_status = Column(CHAR(10)) # 赎回状态，开放 - Open, 暂停 - Suspended, 限制大额申赎 - Limited, 封闭期 - Close

    __table_args__ = (
        Index('idx_rq_fund_nav_datetime', 'datetime'),
    )


class RqStockValuation(Base):
    '''
    股票每日估值
    LF, Last File 时效性最好
    LYR, Last Year Ratio 上市公司年报有审计要求，数据可靠性最高
    TTM, Trailing Twelve Months 时效性较好，滚动4个报告期计算，可避免某一期财报数据的偶然性
    '''

    __tablename__ = 'rq_stock_valuation'

    stock_id = Column(CHAR(20), primary_key=True) # 股票id
    datetime = Column(DATE, primary_key=True) # 日期

    pe_ratio_lyr = Column(DOUBLE(asdecimal=False)) # 市盈率lyr
    pe_ratio_ttm = Column(DOUBLE(asdecimal=False)) # 市盈率ttm
    ep_ratio_lyr = Column(DOUBLE(asdecimal=False)) # 盈市率lyr
    ep_ratio_ttm = Column(DOUBLE(asdecimal=False)) # 盈市率ttm
    pcf_ratio_total_lyr = Column(DOUBLE(asdecimal=False)) # 市现率_总现金流lyr
    pcf_ratio_total_ttm = Column(DOUBLE(asdecimal=False)) # 市现率_总现金流ttm
    pcf_ratio_lyr = Column(DOUBLE(asdecimal=False)) # 市现率_经营lyr
    pcf_ratio_ttm = Column(DOUBLE(asdecimal=False)) # 市现率_经营ttm
    cfp_ratio_lyr = Column(DOUBLE(asdecimal=False)) # 现金收益率lyr
    cfp_ratio_ttm = Column(DOUBLE(asdecimal=False)) # 现金收益率ttm
    pb_ratio_lyr = Column(DOUBLE(asdecimal=False)) # 市净率lyr
    pb_ratio_ttm = Column(DOUBLE(asdecimal=False)) # 市净率ttm
    pb_ratio_lf = Column(DOUBLE(asdecimal=False)) # 市净率lf
    book_to_market_ratio_lyr = Column(DOUBLE(asdecimal=False)) # 账面市值比lyr
    book_to_market_ratio_ttm = Column(DOUBLE(asdecimal=False)) # 账面市值比ttm
    book_to_market_ratio_lf = Column(DOUBLE(asdecimal=False)) # 账面市值比lf
    dividend_yield_ttm = Column(DOUBLE(asdecimal=False)) # 股息率ttm
    peg_ratio_lyr = Column(DOUBLE(asdecimal=False)) # PEG值lyr
    peg_ratio_ttm = Column(DOUBLE(asdecimal=False)) # PEG值ttm
    ps_ratio_lyr = Column(DOUBLE(asdecimal=False)) # 市销率lyr
    ps_ratio_ttm = Column(DOUBLE(asdecimal=False)) # 市销率ttm
    sp_ratio_lyr = Column(DOUBLE(asdecimal=False)) # 销售收益率lyr
    sp_ratio_ttm = Column(DOUBLE(asdecimal=False)) # 销售收益率ttm
    market_cap = Column(DOUBLE(asdecimal=False)) # 总市值1
    market_cap_2 = Column(DOUBLE(asdecimal=False)) # 流通股总市值
    market_cap_3 = Column(DOUBLE(asdecimal=False)) # 总市值3
    a_share_market_val = Column(DOUBLE(asdecimal=False)) # A股市值
    a_share_market_val_in_circulation = Column(DOUBLE(asdecimal=False)) # 流通A股市值
    ev_lyr = Column(DOUBLE(asdecimal=False)) # 企业价值lyr
    ev_ttm = Column(DOUBLE(asdecimal=False)) # 企业价值ttm
    ev_lf = Column(DOUBLE(asdecimal=False)) # 企业价值lf
    ev_no_cash_lyr = Column(DOUBLE(asdecimal=False)) # 企业价值(不含货币资金)lyr
    ev_no_cash_ttm = Column(DOUBLE(asdecimal=False)) # 企业价值(不含货币资金)ttm
    ev_no_cash_lf = Column(DOUBLE(asdecimal=False)) # 企业价值(不含货币资金)lf
    ev_to_ebitda_lyr = Column(DOUBLE(asdecimal=False)) # 企业倍数lyr
    ev_to_ebitda_ttm = Column(DOUBLE(asdecimal=False)) # 企业倍数ttm
    ev_no_cash_to_ebit_lyr = Column(DOUBLE(asdecimal=False)) # 企业倍数(不含货币资金)lyr
    ev_no_cash_to_ebit_ttm = Column(DOUBLE(asdecimal=False)) # 企业倍数(不含货币资金)ttm

    __table_args__ = (
        Index('idx_rq_stock_valuation_datetime', 'datetime'),
    )


class RqFundIndicator(Base):
    '''米筐基金指标'''

    __tablename__ = 'rq_fund_indicator'

    order_book_id = Column(CHAR(10), primary_key=True) # 原始基金ID
    datetime = Column(DATE, primary_key=True) # 日期

    last_week_return = Column(DOUBLE(asdecimal=False)) # 近一周收益率
    last_month_return = Column(DOUBLE(asdecimal=False)) # 近一月收益率
    last_three_month_return = Column(DOUBLE(asdecimal=False)) # 近一季度收益率
    last_six_month_return = Column(DOUBLE(asdecimal=False)) # 近半年收益率
    last_twelve_month_return = Column(DOUBLE(asdecimal=False)) # 近一年收益率
    year_to_date_return = Column(DOUBLE(asdecimal=False)) # 今年以来收益率
    to_date_return = Column(DOUBLE(asdecimal=False)) # 成立至今收益率
    average_size = Column(DOUBLE(asdecimal=False)) # 平均规模
    annualized_returns = Column(DOUBLE(asdecimal=False)) # 成立以来年化收益率
    annualized_risk = Column(DOUBLE(asdecimal=False)) # 成立以来年化风险
    sharp_ratio = Column(DOUBLE(asdecimal=False)) # 成立以来夏普比率
    max_drop_down = Column(DOUBLE(asdecimal=False)) # 成立以来最大回撤
    information_ratio = Column(DOUBLE(asdecimal=False)) # 成立以来信息比率

    __table_args__ = (
        Index('idx_rq_fund_indicator_datetime', 'datetime'),
    )


class RqIndexPrice(Base):
    '''米筐指数数据'''

    __tablename__ = 'rq_index_price'

    order_book_id = Column(CHAR(20), primary_key=True) # 米筐代码
    datetime = Column(DATE, primary_key=True) # 日期

    high = Column(DOUBLE(asdecimal=False)) # 最高价
    open = Column(DOUBLE(asdecimal=False)) # 开盘价
    total_turnover = Column(DOUBLE(asdecimal=False)) # 交易额
    low = Column(DOUBLE(asdecimal=False)) # 最低价
    close = Column(DOUBLE(asdecimal=False)) # 收盘价
    volume = Column(DOUBLE(asdecimal=False)) # 交易量

    __table_args__ = (
        Index('idx_rq_index_price_datetime', 'datetime'),
    )


class RqIndexComponent(Base):
    '''米筐指数成分'''

    __tablename__ = 'rq_index_component'

    index_id = Column(CHAR(20), primary_key=True) # 米筐代码
    datetime = Column(DATE, primary_key=True) # 日期
    stock_list = Column(TEXT) # 股票列表


class SinaStockMinute(Base):
    '''米筐股票分钟线数据表'''

    __tablename__ = 'sina_stock_minute'

    stock_id = Column(CHAR(20), primary_key=True) # 股票ID
    datetime = Column(DATETIME, primary_key=True) # 日期

    close = Column(DOUBLE(asdecimal=False)) # 收盘价

    __table_args__ = (
        Index('idx_sina_stock_minute_datetime', 'datetime'),
    )


class EmIndexPrice(Base):
    '''Choice指数数据'''

    __tablename__ = 'em_index_price'

    em_id = Column(CHAR(20), primary_key=True) # Choice代码
    datetime = Column(DATE, primary_key=True) # 日期
    open = Column(DOUBLE(asdecimal=False)) # 开盘价
    high = Column(DOUBLE(asdecimal=False)) # 最高价
    low = Column(DOUBLE(asdecimal=False)) # 最低价
    close = Column(DOUBLE(asdecimal=False)) # 收盘价
    volume = Column(DOUBLE(asdecimal=False)) # 交易量
    amount = Column(DOUBLE(asdecimal=False)) # 交易额


class EmRealtimeIndexPrice(Base):
    '''Choice实时指数数据'''

    __tablename__ = 'em_realtime_index_price'
    em_id = Column(CHAR(20), primary_key=True) # Choice代码
    datetime = Column(DATETIME, primary_key=True) # 数据时间
    price = Column(DOUBLE(asdecimal=False)) # 指数点位


class EmIndexInfo(Base):
    '''Choice指数信息'''

    __tablename__ = 'em_index_info'

    CODES = Column('em_id', CHAR(20), primary_key=True)  # Choice代码

    NAME = Column('name', CHAR(64), nullable=False)  # 指数名称
    SHORTNAME = Column('short_name', CHAR(64), nullable=False)  # 指数简称
    PUBLISHDATE = Column('publish_date', DATE)  # 发布日期
    MAKERNAME = Column('maker_name', CHAR(32), nullable=False)  # 编制机构
    INDEXPROFILE = Column('index_profile', TEXT)  # 指数概况
    price_source = Column(Enum(IndexPriceSource), nullable=False)  # 指数价格来源标记

class FundFee(Base):
    '''基金费率'''

    __tablename__ = 'fund_fee'
    id = Column(Integer, primary_key=True)

    desc_name = Column(CHAR(32)) # 基金名称
    manage_fee = Column(DOUBLE(asdecimal=False)) # 管理费
    trustee_fee = Column(DOUBLE(asdecimal=False)) # 托管费
    purchase_fee = Column(DOUBLE(asdecimal=False)) # 申购费
    redeem_fee = Column(DOUBLE(asdecimal=False)) # 赎回费
    note = Column(CHAR(64)) # 附加信息
    fund_id = Column(CHAR(20)) # 基金id


class CxindexIndexPrice(Base):
    '''中证指数数据'''

    __tablename__ = 'cxindex_index_price'

    index_id = Column(CHAR(20), primary_key=True) # 指数名称
    datetime = Column(DATE, primary_key=True) # 日期

    open = Column(DOUBLE(asdecimal=False)) # 开盘价
    close = Column(DOUBLE(asdecimal=False)) # 收盘价
    high = Column(DOUBLE(asdecimal=False)) # 最高价
    low = Column(DOUBLE(asdecimal=False)) # 最低价
    volume = Column(DOUBLE(asdecimal=False)) # 交易量
    total_turnover = Column(DOUBLE(asdecimal=False)) # 交易额
    ret = Column(DOUBLE(asdecimal=False)) # 收益率

    __table_args__ = (
        Index('idx_cxindex_index_price_datetime', 'datetime'),
    )

class YahooIndexPrice(Base):
    '''雅虎指数数据'''

    __tablename__ = 'yahoo_index_price'

    index_id = Column(CHAR(20), primary_key=True) # 指数名称
    datetime = Column(DATE, primary_key=True) # 日期

    open = Column(DOUBLE(asdecimal=False)) # 开盘价
    close = Column(DOUBLE(asdecimal=False)) # 收盘价
    high = Column(DOUBLE(asdecimal=False)) # 最高价
    low = Column(DOUBLE(asdecimal=False)) # 最低价
    volume = Column(DOUBLE(asdecimal=False)) # 交易量
    total_turnover = Column(DOUBLE(asdecimal=False)) # 交易额
    ret = Column(DOUBLE(asdecimal=False)) # 收益率

    __table_args__ = (
        Index('idx_yahoo_index_price_datetime', 'datetime'),
    )

class CmIndexPrice(Base):
    '''汇率数据'''

    __tablename__ = 'cm_index_price'
    datetime = Column(DATE, primary_key=True) # 日期

    usd_central_parity_rate = Column(DOUBLE(asdecimal=False)) # 美元人民币汇率中间价
    eur_central_parity_rate = Column(DOUBLE(asdecimal=False)) # 欧元人民币汇率中间价
    jpy_central_parity_rate = Column(DOUBLE(asdecimal=False)) # 日元人民币汇率中间价
    usd_cfets = Column(DOUBLE(asdecimal=False)) # 美元人民币市询价
    eur_cfets = Column(DOUBLE(asdecimal=False)) # 欧元人民币市询价
    jpy_cfets = Column(DOUBLE(asdecimal=False)) # 日元人民币市询价


class FundRating(Base):
    '''基金评级'''

    __tablename__ = 'fund_rating'

    order_book_id = Column(CHAR(10), primary_key=True) # 米筐基金id
    datetime = Column(DATE, primary_key=True) # 日期

    zs = Column(DOUBLE(asdecimal=False)) # 招商评级
    sh3 = Column(DOUBLE(asdecimal=False)) # 上海证券评级三年期
    sh5 = Column(DOUBLE(asdecimal=False)) # 上海证券评级五年期
    jajx = Column(DOUBLE(asdecimal=False)) # 济安金信评级


class RqIndexWeight(Base):
    '''指数成分权重'''

    __tablename__ = 'rq_index_weight'

    index_id = Column(CHAR(20), primary_key=True) # 指数ID
    datetime = Column(DATE, primary_key=True) # 日期

    weight_list = Column(TEXT) # 权重列表 json 格式str 两者顺位对应
    stock_list = Column(TEXT) # 股票列表 json 格式str 两者顺位对应

    __table_args__ = (
        Index('idx_rq_index_weight_datetime', 'datetime'),
    )


class RqStockFinFac(Base):
    '''米筐股票财务因子'''

    __tablename__ = 'rq_stock_fin_fac'

    stock_id = Column(CHAR(20), primary_key=True) # 股票
    datetime = Column(DATE, primary_key=True) # 日期

    return_on_equity_ttm = Column(DOUBLE(asdecimal=False))  # 净资产收益率ttm
    market_cap_3 = Column(DOUBLE(asdecimal=False))  # 总市值
    net_profit_parent_company_ttm_0 = Column(DOUBLE(asdecimal=False))  # 归母公司净利润TTM
    net_profit_ttm_0 = Column(DOUBLE(asdecimal=False))  # 最近一期净利润TTM
    net_profit_ttm_1 = Column(DOUBLE(asdecimal=False))  # 最近一期上一期的净利润TTM
    basic_earnings_per_share_lyr_0 = Column(DOUBLE(asdecimal=False))  # 最近一期年报基本每股收益LYR
    basic_earnings_per_share_lyr_1 = Column(DOUBLE(asdecimal=False))  # 最近一期上一期年报基本每股收益LYR
    basic_earnings_per_share_lyr_2 = Column(DOUBLE(asdecimal=False))  # 最近一期上上期年报基本每股收益LYR
    equity_parent_company_mrq_0 = Column(DOUBLE(asdecimal=False))  # 最近一期单季度归母公司所有者权益合计


class RqFundSize(Base):
    '''米筐基金最新规模'''

    __tablename__ = 'rq_fund_size'

    order_book_id = Column(CHAR(10), primary_key=True) # 米筐基金id
    latest_size = Column(DOUBLE(asdecimal=False)) # 最新规模


class StockInfo(Base):
    '''股票信息表'''

    __tablename__ = 'rq_stock_info'

    stock_id = Column(CHAR(20), primary_key=True) # 股票ID
    rq_id = Column(CHAR(20)) # 米筐ID


class TradingDayList(Base):
    '''交易日列表'''

    __tablename__ = 'rq_trading_day_list'
    datetime = Column(DATE, primary_key=True)


class IndexValPct(Base):
    '''指数估值'''

    __tablename__ = 'index_valpct'

    index_id = Column(CHAR(20), primary_key=True) # 指数
    datetime = Column(DATE, primary_key=True) # 日期

    pe_ttm  = Column(DOUBLE(asdecimal=False)) # pe
    pe_pct = Column(DOUBLE(asdecimal=False)) # pe 百分位
    pb =  Column(DOUBLE(asdecimal=False)) # pb
    pb_pct =  Column(DOUBLE(asdecimal=False)) # pb pct


class EmFundNav(Base):
    '''Choice基金净值表'''

    __tablename__ = 'em_fund_nav'
    CODES = Column(CHAR(10), primary_key=True) # 合约代码
    DATES = Column(DATE, primary_key=True) # 日期

    ORIGINALUNIT = Column(DOUBLE(asdecimal=False)) # 单位净值
    ORIGINALNAVACCUM = Column(DOUBLE(asdecimal=False)) # 累计单位净值
    ADJUSTEDNAV = Column(DOUBLE(asdecimal=False)) # 复权净值
    UNITYIELD10K = Column(DOUBLE(asdecimal=False)) # 每万元收益（日结型货币基金专用）
    YIELDOF7DAYS = Column(DOUBLE(asdecimal=False)) # 7日年化收益率（日结型货币基金专用）

    __table_args__ = (
        Index('idx_em_fund_nav_datetime', 'DATES'),
    )


class EmFundScale(Base):
    '''Choice基金规模表'''

    __tablename__ = 'em_fund_scale'

    CODES = Column(CHAR(10), primary_key=True)  # Choice基金ID
    DATES = Column(DATE, primary_key=True)  # 日期

    QANALNETASSET = Column('FUNDSCALE', DOUBLE(asdecimal=False))  # 基金规模
    UNITTOTAL = Column(DOUBLE(asdecimal=False))  # 基金份额


class EmFundStatus(Base):
    '''Choice基金状态表'''

    __tablename__ = 'em_fund_status'

    CODES = Column(CHAR(10), primary_key=True)  # Choice基金ID
    DATES = Column(DATE, primary_key=True)  # 日期

    PURCHSTATUS = Column(CHAR(16))  # 申购状态
    REDEMSTATUS = Column(CHAR(16))  # 赎回状态
    LPLIMIT = Column(DOUBLE(asdecimal=False))  # 暂停大额申购上限
    OTCLPLIMITJG = Column(DOUBLE(asdecimal=False))  # 场外暂停大额申购上限(机构)
    OTCLPLIMITGR = Column(DOUBLE(asdecimal=False))  # 场外暂停大额申购上限(个人)
    TRADESTATUS = Column(CHAR(16))  # 交易状态
    PCHMINAMT = Column(DOUBLE(asdecimal=False))  # 申购金额下限
    REDMMINAMT = Column(DOUBLE(asdecimal=False))  # 单笔赎回份额下限


class EMIndexPct(Base):
    '''Choice指数估值数据'''

    __tablename__ = 'em_index_pct'
    index_id = Column(CHAR(20), primary_key=True) # 合约代码
    datetime = Column(DATE, primary_key=True) # 日期
    pe_ttm = Column(DOUBLE(asdecimal=False)) # pe
    pe_pct = Column(DOUBLE(asdecimal=False)) # pe 百分位


class EmStockPrice(Base):
    '''Choice股票不复权数据表'''

    __tablename__ = 'em_stock_price'

    CODES = Column('stock_id', CHAR(10), primary_key=True) # EM股票ID
    DATES = Column('datetime', DATE, primary_key=True) # 日期
    OPEN = Column('open', DOUBLE(asdecimal=False), nullable=False) # 开盘价
    CLOSE = Column('close', DOUBLE(asdecimal=False), nullable=False) # 收盘价
    HIGH = Column('high', DOUBLE(asdecimal=False), nullable=False) # 最高价
    LOW = Column('low', DOUBLE(asdecimal=False), nullable=False) # 最低价
    PRECLOSE = Column('pre_close', DOUBLE(asdecimal=False), nullable=False) # 前收盘价
    AVERAGE = Column('average', DOUBLE(asdecimal=False), server_default=text("0")) # 均价
    AMOUNT = Column('amount', DOUBLE(asdecimal=False), server_default=text('0')) # 成交额
    VOLUME = Column('volume', DOUBLE(asdecimal=False), server_default=text('0')) # 成交量  不复权和后复权的交易量不同
    TURN = Column('turn', DOUBLE(asdecimal=False), server_default=text('0')) # 换手率
    TRADESTATUS = Column('trade_status', CHAR(20), nullable=False) # 交易状态
    TNUM = Column('t_num', DOUBLE(asdecimal=False), server_default=text('0')) # 成交笔数
    BUYVOL = Column('buy_vol', DOUBLE(asdecimal=False), server_default=text('0')) # 内盘成交量
    SELLVOL = Column('sell_vol', DOUBLE(asdecimal=False), server_default=text('0')) # 外盘成交量

    __table_args__ = (
        Index('idx_em_stock_price_datetime', 'datetime'),
    )

class EmStockPostPrice(Base):
    '''Choice股票后复权数据表'''

    __tablename__ = 'em_stock_post_price'

    CODES = Column('stock_id', CHAR(10), primary_key=True) # EM股票ID
    DATES = Column('datetime', DATE, primary_key=True) # 日期
    OPEN = Column('open', DOUBLE(asdecimal=False), nullable=False) # 开盘价
    CLOSE = Column('close', DOUBLE(asdecimal=False), nullable=False) # 收盘价
    HIGH = Column('high', DOUBLE(asdecimal=False), nullable=False) # 最高价
    LOW = Column('low', DOUBLE(asdecimal=False), nullable=False) # 最低价
    PRECLOSE = Column('pre_close', DOUBLE(asdecimal=False), nullable=False) # 前收盘价
    AVERAGE = Column('average', DOUBLE(asdecimal=False), server_default=text("0")) # 均价
    AMOUNT = Column('amount', DOUBLE(asdecimal=False), server_default=text('0')) # 成交额
    VOLUME = Column('volume', DOUBLE(asdecimal=False), server_default=text('0')) # 成交量
    TRADESTATUS = Column('trade_status', CHAR(20), nullable=False) # 交易状态
    TAFACTOR = Column('tafactor', DOUBLE(asdecimal=False), server_default=text("0")) # 复权因子（后）

    __table_args__ = (
        Index('idx_em_stock_post_price_datetime', 'datetime'),
    )

class EmStockDailyInfo(Base):
    '''Choice股票每日更新'''

    __tablename__ = 'em_stock_daily_info'

    CODES = Column("stock_id", CHAR(10), primary_key=True) # EM股票ID
    DATES = Column('datetime', DATE, primary_key=True) # 日期
    TOTALSHARE = Column("total_share", DOUBLE(asdecimal=False), nullable=False) # 总股本
    LIQSHARE = Column("liq_share", DOUBLE(asdecimal=False), nullable=False) # 流通股本
    HOLDFROZENAMTACCUMRATIO = Column('hold_frozen_amt_accum_ratio', DOUBLE(asdecimal=False))  # 控股股东累计质押数量占持股比例
    PETTMDEDUCTED = Column('pe_ttm_deducted', DOUBLE(asdecimal=False))  # 市盈率TTM(扣除非经常性损益)
    PBLYRN = Column('pb_lyr_n', DOUBLE(asdecimal=False))  # 市净率(PB，LYR)(按公告日)
    PSTTM = Column('ps_ttm', DOUBLE(asdecimal=False))  # 市销率(PS，TTM)
    AHOLDER = Column('a_holder', TEXT)  # 实际控制人
    ESTPEG = Column('est_peg', DOUBLE(asdecimal=False)) # 预测PEG(最近一年)
    SHAREHDPCT = Column('share_hd_pct', DOUBLE(asdecimal=False)) # 沪深港通持股比例
    EVWITHOUTCASH = Column('ev_without_cash', DOUBLE(asdecimal=False)) # 企业价值(剔除货币资金)(EV2)

    __table_args__ = (
        Index('idx_em_stock_daily_info_datetime', 'datetime'),
    )

class EmStockInfo(Base):
    '''Choice股票信息表'''

    __tablename__ = 'em_stock_info'

    CODES = Column("stock_id", CHAR(10), primary_key=True) # EM股票ID
    NAME = Column("name", TEXT, nullable=False) # 股票简称
    ENGNAME = Column("eng_name", TEXT) # 证券英文简称
    COMPNAME = Column("comp_name", TEXT, nullable=False) # 公司中文名称
    COMPNAMEENG = Column("comp_name_eng", TEXT) # 公司英文名称
    LISTDATE = Column("list_date", DATE, nullable=False) # 首发上市日期
    FINPURCHORNOT = Column("fin_purch_ornot", BOOLEAN, nullable=False) # 是否属于融资标的
    FINSELLORNOT = Column("fin_sell_ornot", BOOLEAN, nullable=False) # 是否属于融券标的
    STOHSTOCKCONNECTEDORNOT = Column("stoh_stock_connected_ornot", BOOLEAN, nullable=False) # 是否属于沪股通标的
    SHENGUTONGTARGET = Column("shengutong_target", BOOLEAN, nullable=False) # 是否属于深股通标的
    BLEMINDCODE = Column("bl_em_ind_code", CHAR(40)) # 所属东财行业指数代码
    BLSWSINDCODE = Column("bl_sws_ind_code", CHAR(40)) # 所属申万行业指数代码
    SW2014CODE = Column("sw_2014_code", CHAR(40)) # 所属申万行业代码
    EMINDCODE2016 = Column("em_ind_code_2016", CHAR(40), nullable=False) # 所属东财行业(2016)代码
    CITICCODE2020 = Column("citic_code_2020", CHAR(40)) # 所属中信行业代码(2020)
    BLCSRCINDCODE = Column("bl_csrc_ind_code", CHAR(32)) # 所属证监会行业指数代码
    CSRCCODENEW = Column("csrc_code_new", CHAR(16)) # 所属证监会行业(新)代码
    CSINDCODE2016 = Column("cs_ind_code_2016", CHAR(32)) # 所属中证行业(2016)代码
    GICSCODE = Column("gics_code", CHAR(32), nullable=False) # 所属GICS行业代码
    CAPUNCAPDATE = Column("cap_uncap_date", TEXT) # 戴帽摘帽日期
    DELISTDATE = Column("delist_date", DATE) # 摘牌日期
    BCODE = Column("b_code", CHAR(10)) # 同公司B股代码
    BNAME = Column("b_name", TEXT) # 同公司B股简称
    HCODE = Column("h_code", CHAR(10)) # 同公司H股代码
    HNAME = Column("h_name", TEXT) # 同公司H股简称
    BACKDOOR = Column("backdoor", BOOLEAN, nullable=False) # 是否借壳上市
    BACKDOORDATE = Column("backdoor_date", DATE) # 借壳上市日期

class EmStockFinFac(Base):
    '''Choice股票财务因子 '''

    __tablename__ = 'em_stock_fin_fac'

    CODES = Column("stock_id", CHAR(10), primary_key=True) # EM股票id
    DATES = Column("datetime", DATE, primary_key=True) # 日期
    STMTACTDATE = Column('stmt_act_date', DATE)  # 定期报告实际披露日期
    EBIT = Column("ebit", DOUBLE(asdecimal=False)) # 息税前利润EBIT(反推法)
    EBITDA = Column("ebitda", DOUBLE(asdecimal=False)) # 息税折旧摊销前利润EBITDA(反推法)
    EXTRAORDINARY = Column("extra_ordinary", DOUBLE(asdecimal=False)) # 非经常性损益
    LOWERDIANDNI = Column("lower_diandni", DOUBLE(asdecimal=False)) # 扣非前后净利润孰低
    GROSSMARGIN = Column("gross_margin", DOUBLE(asdecimal=False)) # 毛利
    OPERATEINCOME = Column("operate_income", DOUBLE(asdecimal=False)) # 经营活动净收益
    INVESTINCOME = Column("invest_income", DOUBLE(asdecimal=False)) # 价值变动净收益
    EBITDRIVE = Column("ebit_drive", DOUBLE(asdecimal=False)) # 息税前利润EBIT(正推法)
    TOTALCAPITAL = Column("total_capital", DOUBLE(asdecimal=False)) # 全部投入资本
    WORKINGCAPITAL = Column("working_capital", DOUBLE(asdecimal=False)) # 营运资本
    NETWORKINGCAPITAL = Column("networking_capital", DOUBLE(asdecimal=False)) # 净营运资本
    TANGIBLEASSET = Column("tangible_asset", DOUBLE(asdecimal=False)) # 有形资产
    RETAINED = Column("retained", DOUBLE(asdecimal=False)) # 留存收益
    INTERESTLIBILITY = Column("interest_liability", DOUBLE(asdecimal=False)) # 带息负债
    NETLIBILITY = Column("net_liability", DOUBLE(asdecimal=False)) # 净债务
    EXINTERESTCL = Column("ex_interest_cl", DOUBLE(asdecimal=False)) # 无息流动负债
    EXINTERESTNCL = Column("ex_interest_ncl", DOUBLE(asdecimal=False)) # 无息非流动负债
    FCFF = Column("fcff", DOUBLE(asdecimal=False)) # 企业自由现金流量FCFF
    FCFE = Column("fcfe", DOUBLE(asdecimal=False)) # 股权自由现金流量FCFE
    DA = Column("da", DOUBLE(asdecimal=False)) # 当期计提折旧与摊销
    FCFFDRIVE = Column("fcff_drive", DOUBLE(asdecimal=False)) # 企业自由现金流量FCFF(正推法)
    DEDUCTEDINCOME_BA = Column("deducted_income_ba", DOUBLE(asdecimal=False)) # 归属于上市公司股东的扣除非经常性损益后的净利润(调整前)
    DEDUCTEDINCOME_AA = Column("deducted_income_aa", DOUBLE(asdecimal=False)) # 归属于上市公司股东的扣除非经常性损益后的净利润(调整后)
    GRTTMR = Column("gr_ttmr", DOUBLE(asdecimal=False)) # 营业总收入TTM(报告期)
    GCTTMR = Column("gc_ttmr", DOUBLE(asdecimal=False)) # 营业总成本TTM(报告期)
    ORTTMR = Column("or_ttmr", DOUBLE(asdecimal=False)) # 营业收入TTM(报告期)
    OCTTMR = Column("oc_ttmr", DOUBLE(asdecimal=False)) # 营业成本非金融类TTM(报告期)
    EXPENSETTMR = Column("expense_ttmr", DOUBLE(asdecimal=False)) # 营业支出金融类TTM(报告期)
    GROSSMARGINTTMR = Column("gross_margin_ttmr", DOUBLE(asdecimal=False)) # 毛利TTM(报告期)
    OPERATEEXPENSETTMR = Column("operate_expense_ttmr", DOUBLE(asdecimal=False)) # 销售费用TTM(报告期)
    ADMINEXPENSETTMR = Column("admin_expense_ttmr", DOUBLE(asdecimal=False)) # 管理费用TTM(报告期)
    FINAEXPENSETTMR = Column("fina_expense_ttmr", DOUBLE(asdecimal=False)) # 财务费用TTM(报告期)
    IMPAIRMENTTTMR = Column("impairment_ttmr", DOUBLE(asdecimal=False)) # 资产减值损失TTM(报告期)
    OPERATEINCOMETTMR = Column("operate_income_ttmr", DOUBLE(asdecimal=False)) # 经营活动净收益TTM(报告期)
    INVESTINCOMETTMR = Column("invest_income_ttmr", DOUBLE(asdecimal=False)) # 价值变动净收益TTM(报告期)
    OPTTMR = Column("op_ttmr", DOUBLE(asdecimal=False)) # 营业利润TTM(报告期)
    NONOPERATEPROFITTTMR = Column("non_operate_profi_ttmr", DOUBLE(asdecimal=False)) # 营业外收支净额TTM(报告期)
    EBITTTMR = Column("ebit_ttmr", DOUBLE(asdecimal=False)) # 息税前利润TTM(报告期)
    EBTTTMR = Column("ebt_ttmr", DOUBLE(asdecimal=False)) # 利润总额TTM(报告期)
    TAXTTMR = Column("tax_ttmr", DOUBLE(asdecimal=False)) # 所得税TTM(报告期)
    PNITTMR = Column("pni_ttmr", DOUBLE(asdecimal=False)) # 归属母公司股东的净利润TTM(报告期)
    KCFJCXSYJLRTTMR = Column("kcfjcxsyjlr_ttmr", DOUBLE(asdecimal=False)) # 扣除非经常性损益净利润TTM(报告期)
    NPTTMRP = Column("np_ttmrp", DOUBLE(asdecimal=False)) # 净利润TTM(报告期)
    FVVPALRP = Column("fvvpal_rp", DOUBLE(asdecimal=False)) # 公允价值变动损益TTM(报告期)
    IRTTMRP = Column("irtt_mrp", DOUBLE(asdecimal=False)) # 投资收益TTM(报告期)
    IITTMFJVAJVRP = Column("iittmfjvajv_rp", DOUBLE(asdecimal=False)) # 对联营企业和合营企业的投资收益TTM(报告期)
    BTAATTMRP = Column("btaa_ttmrp", DOUBLE(asdecimal=False)) # 营业税金及附加TTM(报告期)
    SALESCASHINTTMR = Column("sales_cashin_ttmr", DOUBLE(asdecimal=False)) # 销售商品提供劳务收到的现金TTM(报告期)
    CFOTTMR = Column("cfo_ttmr", DOUBLE(asdecimal=False)) # 经营活动现金净流量TTM(报告期)
    CFITTMR = Column("cfi_ttmr", DOUBLE(asdecimal=False)) # 投资活动现金净流量TTM(报告期)
    CFFTTMR = Column("cff_ttmr", DOUBLE(asdecimal=False)) # 筹资活动现金净流量TTM(报告期)
    CFTTMR = Column("cf_ttmr", DOUBLE(asdecimal=False)) # 现金净流量TTM(报告期)
    CAPEXR = Column("cap_exr", DOUBLE(asdecimal=False)) # 资本支出TTM(报告期)
    PERFORMANCEEXPRESSPARENTNI = Column('performance_express_parent_ni', DOUBLE(asdecimal=False)) # 业绩快报.归属母公司股东的净利润
    MBSALESCONS = Column('mb_sales_cons', TEXT) # 主营收入构成(按行业)
    MBSALESCONS_P = Column('mb_sales_cons_p', TEXT) # 主营收入构成(按产品)
    GPMARGIN = Column('gp_margin', DOUBLE(asdecimal=False)) # 销售毛利率
    NPMARGIN = Column('np_margin', DOUBLE(asdecimal=False)) # 销售净利率(营业收入/净利润)
    EXPENSETOOR = Column('expense_toor', DOUBLE(asdecimal=False)) # 销售期间费用率
    INVTURNRATIO = Column('inv_turn_ratio', DOUBLE(asdecimal=False)) # 存货周转率
    ARTURNRATIO = Column('ar_turn_ratio', DOUBLE(asdecimal=False)) # 应收账款周转率(含应收票据)
    ROEAVG = Column('roe_avg', DOUBLE(asdecimal=False)) # 净资产收益率ROE(平均)
    ROEWA = Column('roe_wa', DOUBLE(asdecimal=False)) # 净资产收益率ROE(加权)
    EPSBASIC = Column('eps_basic', DOUBLE(asdecimal=False)) # 每股收益EPS(基本)
    EPSDILUTED = Column('eps_diluted', DOUBLE(asdecimal=False)) # 每股收益EPS(稀释)
    BPS = Column('bps', DOUBLE(asdecimal=False)) # 每股净资产
    MBREVENUE = Column('mb_revenue', DOUBLE(asdecimal=False)) # 主营业务收入
    MBCOST = Column('mb_cost', DOUBLE(asdecimal=False)) # 主营业务支出
    BALANCESTATEMENT_9 = Column('balance_statement_9', DOUBLE(asdecimal=False)) # 货币资金
    BALANCESTATEMENT_25 = Column('balance_statement_25', DOUBLE(asdecimal=False)) # 流动资产合计
    BALANCESTATEMENT_31 = Column('balance_statement_31', DOUBLE(asdecimal=False)) # 固定资产
    BALANCESTATEMENT_46 = Column('balance_statement_46', DOUBLE(asdecimal=False)) # 非流动资产合计
    BALANCESTATEMENT_74 = Column('balance_statement_74', DOUBLE(asdecimal=False)) # 资产总计
    BALANCESTATEMENT_93 = Column('balance_statement_93', DOUBLE(asdecimal=False)) # 流动负债合计
    BALANCESTATEMENT_103 = Column('balance_statement_103', DOUBLE(asdecimal=False)) # 非流动负债合计
    BALANCESTATEMENT_128 = Column('balance_statement_128', DOUBLE(asdecimal=False)) # 负债合计
    BALANCESTATEMENT_140 = Column('balance_statement_140', DOUBLE(asdecimal=False)) # 归属于母公司股东权益合计
    BALANCESTATEMENT_141 = Column('balance_statement_141', DOUBLE(asdecimal=False)) # 股东权益合计
    BALANCESTATEMENT_141_ADJ = Column('balance_statement_141_adj', DOUBLE(asdecimal=False)) # 股东权益合计(调整)
    BALANCESTATEMENT_195 = Column('balance_statement_195', DOUBLE(asdecimal=False)) # 其他权益工具
    BALANCESTATEMENT_196 = Column('balance_statement_196', DOUBLE(asdecimal=False)) # 其中:优先股(其他权益工具)
    INCOMESTATEMENT_9 = Column('income_statement_9', DOUBLE(asdecimal=False)) # 营业收入
    INCOMESTATEMENT_14 = Column('income_statement_14', DOUBLE(asdecimal=False)) # 财务费用
    INCOMESTATEMENT_48 = Column('income_statement_48', DOUBLE(asdecimal=False)) # 营业利润
    INCOMESTATEMENT_56 = Column('income_statement_56', DOUBLE(asdecimal=False)) # 所得税(费用)
    INCOMESTATEMENT_60 = Column('income_statement_60', DOUBLE(asdecimal=False)) # 净利润
    INCOMESTATEMENT_61 = Column('income_statement_61', DOUBLE(asdecimal=False)) # 归属于母公司股东的净利润
    INCOMESTATEMENT_83 = Column('income_statement_83', DOUBLE(asdecimal=False)) # 营业总收入
    INCOMESTATEMENT_85 = Column('income_statement_85', DOUBLE(asdecimal=False)) # 其他业务收入
    INCOMESTATEMENT_127 = Column('income_statement_127', DOUBLE(asdecimal=False)) # 利息费用
    CASHFLOWSTATEMENT_9 = Column('cashflow_statement_9', DOUBLE(asdecimal=False)) # 销售商品、提供劳务收到的现金
    CASHFLOWSTATEMENT_39 = Column('cashflow_statement_39', DOUBLE(asdecimal=False)) # 经营活动产生的现金流量净额
    CASHFLOWSTATEMENT_59 = Column('cashflow_statement_59', DOUBLE(asdecimal=False)) # 投资活动产生的现金流量净额
    CASHFLOWSTATEMENT_70 = Column('cashflow_statement_70', DOUBLE(asdecimal=False)) # 分配股利、利润或偿付利息支付的现金
    CASHFLOWSTATEMENT_77 = Column('cashflow_statement_77', DOUBLE(asdecimal=False)) # 筹资活动产生的现金流量净额
    CASHFLOWSTATEMENT_82 = Column('cashflow_statement_82', DOUBLE(asdecimal=False)) # 现金及现金等价物净增加额
    CASHFLOWSTATEMENT_86 = Column('cashflow_statement_86', DOUBLE(asdecimal=False)) # 资产减值准备
    CASHFLOWSTATEMENT_87 = Column('cashflow_statement_87', DOUBLE(asdecimal=False)) # 固定资产折旧
    CASHFLOWSTATEMENT_88 = Column('cashflow_statement_88', DOUBLE(asdecimal=False)) # 无形资产摊销
    CASHFLOWSTATEMENT_89 = Column('cashflow_statement_89', DOUBLE(asdecimal=False)) # 长期待摊费用摊销

    __table_args__ = (
        Index('idx_em_stock_fin_fac_datetime', 'datetime'),
    )

class EmStockRefinancing(Base):
    '''Choice股票再融资信息表'''

    __tablename__ = 'em_stock_refinancing'

    id = Column(Integer, primary_key=True)
    SECURITYCODE = Column('stock_id', CHAR(10), primary_key=True)  # EM股票id
    PLANNOTICEDDATE = Column('plan_noticed_date', primary_key=True)  # 首次公告日
    APPROVENOTICEDATE = Column('approve_notice_date', DATE, nullable=False)  # 最新公告日
    NEWPROGRESS = Column('new_progress', TEXT)  # 方案进度
    ISSUEOBJECT = Column('issue_object', TEXT)  # 发行对象
    SUMFINA_T = Column('sum_fina_t', DOUBLE(asdecimal=False))  # 预计募资_上限(亿元)
    PRICEPRINCIPLE = Column('price_principle', TEXT)  # 定价规则
    ATTACHNAME = Column('attach_name', TEXT)  # 原始公告链接
    ADDPURPOSE = Column('add_purpose', TEXT)  # 增发目的

    __table_args__ = (
        Index('idx_em_stock_refinancing_plan_noticed_date', 'plan_noticed_date'),
    )

class EmStockRefinancingImpl(Base):
    '''Choice股票再融资实施表'''

    __tablename__ = 'em_stock_refinancing_impl'

    id = Column(Integer, primary_key=True)
    MSECUCODE = Column('stock_id', CHAR(10), primary_key=True)  # EM股票id
    NOTICEDATE = Column('notice_date', DATE, primary_key=True)  # 增发公告日
    DAT_FAXINGRIQI = Column('record_date', DATE)  # 股权登记日
    DAT_SHANGSHIRIQI = Column('listing_date', DATE, nullable=False)  # 增发上市日
    PRICEPRINCIPLE = Column('price_principle', TEXT, nullable=False)  # 定价规则
    ISSUEOBJECT = Column('issue_object', TEXT, nullable=False)  # 发行对象
    ISSUEPRICE = Column('issue_price', DOUBLE(asdecimal=False), nullable=False) # 股价(元)_增发
    DEC_SHAREISSUED = Column('share_issued', DOUBLE(asdecimal=False), nullable=False)  # 增发数量(万股)
    SUMFINAPLAN = Column('sum_fina_plan', DOUBLE(asdecimal=False), nullable=False)  # 募资总额(亿元)
    ATTACHNAME = Column('attach_name', TEXT)  # 公告链接
    DATE = Column('datetime', DATE, nullable=False)  # 最新公告日
    ZFZZGBBL = Column('refi_share_ratio', DOUBLE(asdecimal=False), nullable=False)  # 增发数量占发行前总股本比例

    __table_args__ = (
        Index('idx_em_stock_refinancing_impl_datetime', 'datetime'),
    )

class EmStockEstimateFac(Base):
    '''Choice预测因子数据'''

    __tablename__ = 'em_stock_estimate_fac'

    CODES = Column('stock_id', CHAR(16), primary_key=True) # EM股票ID
    DATES = Column('datetime', DATE, primary_key=True) # 日期
    predict_year = Column(YEAR, nullable=False) # 预测年度
    ESTGR = Column('est_gr', DOUBLE(asdecimal=False), nullable=False) # 预测营业总收入平均值
    ESTNI = Column('est_ni', DOUBLE(asdecimal=False), nullable=False) # 预测归属于母公司的净利润平均值

    __table_args__ = (
        Index('idx_em_stock_estimate_fac_datetime', 'datetime'),
        Index('idx_em_stock_estimate_fac_predict_year', 'predict_year'),
    )

class EmIndexVal(Base):
    '''Choice指数估值数据'''

    __tablename__ = 'em_index_val'

    CODES = Column("em_id", CHAR(16), primary_key=True) # EM股票id
    DATES = Column("datetime", DATE, primary_key=True) # 日期
    PETTM = Column("pe_ttm", DOUBLE(asdecimal=False)) # 市盈率PE(TTM)
    PETTM_NN = Column("pe_ttm_nn", DOUBLE(asdecimal=False)) # 市盈率PE(TTM)(剔除负值)
    PBMRQ = Column("pb_mrq", DOUBLE(asdecimal=False)) # 市净率PB(MRQ)
    DIVIDENDRATETTM = Column("dividend_yield", DOUBLE(asdecimal=False)) # 股息率
    PSTTM = Column("ps_ttm", DOUBLE(asdecimal=False)) # 市销率PS(TTM)
    PCFTTM = Column("pcf_ttm", DOUBLE(asdecimal=False)) # 市现率PCF(TTM)
    ROE = Column("roe", DOUBLE(asdecimal=False)) # 净资产收益率
    EPSTTM = Column("eps_ttm", DOUBLE(asdecimal=False)) # 每股收益TTM
    ESTPEG = Column("est_peg", DOUBLE(asdecimal=False)) # 预测PEG
    MV = Column("mv", DOUBLE(asdecimal=False)) # 总市值
    LIQMV = Column("liqmv", DOUBLE(asdecimal=False)) # 流通市值
    FREELIQMV = Column("freeliqmv", DOUBLE(asdecimal=False)) # 自由流通市值

class EmTradeDates(Base):
    '''Choice交易日数据'''

    __tablename__ = 'em_tradedates'
    TRADEDATES = Column(DATE, primary_key=True)

class EmIndexComponent(Base):
    '''Choice指数成分'''

    __tablename__ = 'em_index_component'

    index_id = Column(CHAR(20), primary_key=True)
    datetime = Column(DATE, primary_key=True) # 日期
    em_id = Column(CHAR(20), nullable=False)  # Choice ID
    em_plate_id = Column(CHAR(20), nullable=False)  # Choice板块ID
    stock_list = Column(TEXT, nullable=False)  # 股票列表

class CSIndexComponent(Base):

    __tablename__ = 'cs_index_component'

    index_id = Column(CHAR(20), primary_key=True)
    datetime = Column(DATE, primary_key=True)  # 日期
    num = Column(Integer, nullable=False)  # 成分股数量
    id_cat = Column(Enum(SectorType), nullable=False)  # 所属类型 industry-行业 topic-主题
    sector = Column(TEXT, nullable=False)  # 所属板块
    top10 = Column(TEXT, nullable=False)  # 前10成分及权重
    related_funds = Column(TEXT)  # 相关产品
    all_constitu = Column(MEDIUMTEXT, nullable=False)  # 所有成分及权重(from Choice)

class EmFundHoldingRate(Base):
    '''Choice基金持有人比例'''

    __tablename__ = 'em_fund_holding_rate'

    CODES = Column(CHAR(10), primary_key=True) # 合约代码
    DATES = Column(DATE, primary_key=True) # 日期
    HOLDPERSONALHOLDINGPCT = Column(DOUBLE(asdecimal=False)) # 个人持有比例 单位百分比
    HOLDINSTIHOLDINGPCT = Column(DOUBLE(asdecimal=False)) # 机构持有比例 单位百分比
    HOLDNUM = Column(DOUBLE(asdecimal=False))  # 基金份额持有人户数

class EmFundList(Base):
    '''Choice基金列表'''

    __tablename__ = 'em_fund_list'

    datetime = Column(DATE, primary_key=True) # 日期
    all_live_fund_list = Column(MEDIUMTEXT, nullable=False) # 全部基金列表(不包含未成立、已到期)
    delisted_fund_list = Column(MEDIUMTEXT, nullable=False) # 已摘牌基金列表

class EmFundInfo(Base):
    '''Choice基金信息表'''

    __tablename__ = 'em_fund_info'

    CODES = Column('em_id', CHAR(16), primary_key=True) # 基金代码
    NAME = Column('name', CHAR(32), nullable=False) # 基金名称
    FNAME = Column('full_name', CHAR(128), nullable=False) # 基金全称
    FOUNDDATE = Column('start_date', DATE) # 成立日期
    MATURITYDATE = Column('end_date', DATE) # 结束日期
    FIRSTINVESTTYPE = Column('invest_type_class_1', CHAR(32), nullable=False) # 投资类型（一级）
    SECONDINVESTTYPE = Column('invest_type_class_2', CHAR(32), nullable=False) # 投资类型（二级）
    RISKLEVEL = Column('risk_level', CHAR(2)) # 风险等级
    TRADECUR = Column('currency', CHAR(16), nullable=False) # 交易币种
    STRUCFUNDORNOT = Column('is_structured', BOOLEAN, nullable=False) # 是否分级基金
    GFCODEM = Column('base_fund_id', CHAR(16)) # 分级基金母基金代码
    FUNDTYPE = Column('is_open', BOOLEAN, nullable=False) # 是否定期开放基金, 以Choice的FUNDTYPE来判断
    PREDFUNDMANAGER = Column('manager_id', TEXT, nullable=False) # 基金经理(历任)
    MGRCOMP = Column('company_id', CHAR(64), nullable=False) # 基金公司名称
    CUSTODIANBANK = Column('custodian_bank', CHAR(64))  # 基金托管人
    FOREIGNCUSTODIAN = Column('foreign_custodian', CHAR(64))  # 境外托管人
    FRONTENDFEECODE = Column('frontend_fee_code', CHAR(12))   # 前端收费代码
    BACKENDFEECODE = Column('backend_fee_code', CHAR(12))  # 后端收费代码
    ARCODEIN = Column('ar_code_in', CHAR(12))  # 场内申赎代码

class EmFundBenchmark(Base):
    '''Choice基金业绩比较基准表'''

    __tablename__ = 'em_fund_benchmark'

    CODES = Column('em_id', CHAR(16), primary_key=True) # 基金代码
    DATES = Column('datetime', DATE, primary_key=True) # 日期
    BENCHMARK = Column('benchmark', TEXT, nullable=False) # 业绩比较基准

    __table_args__ = (
        Index('idx_em_fund_benchmark_datetime', 'datetime'),
    )

class EmFundFee(Base):
    '''基金费率'''

    __tablename__ = 'em_fund_fee'

    CODES = Column('em_id', CHAR(16), primary_key=True)  # 基金代码
    MANAGFEERATIO = Column('manage_fee', TEXT)  # 管理费率
    CUSTODIANFEERATIO = Column('trustee_fee', TEXT)  # 托管费率
    SUBSCRFEERATIO = Column('subscr_fee', TEXT)  # 认购费率
    PURCHFEERATIO = Column('purchase_fee', TEXT)  # 申购费率
    REDEMFEERATIO = Column('redeem_fee', TEXT)  # 赎回费率
    SERVICEFEERATIO = Column('service_fee', TEXT)  # 销售服务费率
    CODEFEEMODE = Column('code_fee_mode', Enum(CodeFeeMode), nullable=False)  # 代码适用收费模式

class WindFundHolderStructure(Base):
    '''万德静态数据 中国共同基金持有人结构'''

    __tablename__ = 'wind_fund_holder_structure'

    END_DT = Column(CHAR(8), primary_key=True)  # 日期
    S_INFO_WINDCODE = Column(CHAR(20), primary_key=True)  # wind id
    SEC_ID = Column(CHAR(15))  # 证券id
    ANN_DT = Column(CHAR(8))  # 报告日
    SCOPE = Column(CHAR(8))  # 范围
    HOLDER_NUMBER = Column(DOUBLE(asdecimal=False)) # 基金份额持有人户数（户）
    HOLDER_AVGHOLDING = Column(DOUBLE(asdecimal=False)) # 平均每户持有基金份额（份）
    HOLDER_INSTITUTION_HOLDING = Column(DOUBLE(asdecimal=False)) # 机构投资者持有份额(份)
    HOLDER_INSTITUTION_HOLDINGPCT = Column(DOUBLE(asdecimal=False)) # 机构投资者持有份额占比(%)
    HOLDER_PERSONAL_HOLDING = Column(DOUBLE(asdecimal=False)) # 个人投资者持有份额(份)
    HOLDER_PERSONAL_HOLDINGPCT = Column(DOUBLE(asdecimal=False)) # 个人投资者持有份额占比(%)
    HOLDER_MNGEMP_HOLDING = Column(DOUBLE(asdecimal=False)) # 管理人员工持有份额(份)
    HOLDER_MNGEMP_HOLDINGPCT = Column(DOUBLE(asdecimal=False)) # 管理人员工持有份额占比(%)
    HOLDER_FEEDER_HOLDING = Column(DOUBLE(asdecimal=False)) # 联接基金持有份额(份)
    HOLDER_FEEDER_HOLDINGPCT = Column(DOUBLE(asdecimal=False)) # 联接基金持有份额占比(%)
    PUR_COST = Column(DOUBLE(asdecimal=False)) # 报告期买入股票成本总额(元)
    SELL_INCOME = Column(DOUBLE(asdecimal=False)) # 报告期卖出股票收入总额(元)

class WindFundStockPortfolio(Base):
    '''万德静态数据 中国共同基金投资组合 持股明细'''

    __tablename__ = 'wind_fund_stock_portfolio'

    F_PRT_ENDDATE = Column(CHAR(8), primary_key=True)  # 日期
    S_INFO_STOCKWINDCODE = Column(CHAR(10), primary_key=True)  # 万德股票id
    S_INFO_WINDCODE = Column(CHAR(20), primary_key=True)  # wind id
    CRNCY_CODE = Column(CHAR(5))  # 货币
    F_PRT_STKVALUE = Column(DOUBLE(asdecimal=False)) # 持有股票市值 元
    F_PRT_STKQUANTITY = Column(DOUBLE(asdecimal=False)) # 持有股票数量 股
    F_PRT_STKVALUETONAV = Column(DOUBLE(asdecimal=False)) # 持有股票市值占基金净值比例
    F_PRT_POSSTKVALUE = Column(DOUBLE(asdecimal=False)) # 积极投资持有股票市值 元
    F_PRT_POSSTKQUANTITY = Column(DOUBLE(asdecimal=False)) # 积极投资持有股数 股
    F_PRT_POSSTKTONAV = Column(DOUBLE(asdecimal=False)) # 积极投资持有股票市值占净资产比例
    F_PRT_PASSTKEVALUE = Column(DOUBLE(asdecimal=False)) # 指数投资持有股票市值 元
    F_PRT_PASSTKQUANTITY = Column(DOUBLE(asdecimal=False)) # 指数投资持有股数 股
    F_PRT_PASSTKTONAV = Column(DOUBLE(asdecimal=False)) # 指数投资持有股票市值占净资产比例
    ANN_DATE = Column(CHAR(8))  # 公告日期
    STOCK_PER = Column(DOUBLE(asdecimal=False)) # 占股票市值比
    FLOAT_SHR_PER = Column(DOUBLE(asdecimal=False)) # 占流通股本比例

class WindFundBondPortfolio(Base):
    '''万德静态数据 中国共同基金投资组合 持债明细'''

    __tablename__ = 'wind_fund_bond_portfolio'

    F_PRT_ENDDATE = Column(DATE, primary_key=True)  # 日期
    S_INFO_WINDCODE = Column(CHAR(16), primary_key=True)  # wind基金id
    S_INFO_BONDWINDCODE = Column(CHAR(16), primary_key=True)  # wind债券id
    CRNCY_CODE = Column(CHAR(5))  # 货币类型
    F_PRT_BDVALUE = Column(DOUBLE(asdecimal=False)) # 持有债券市值
    F_PRT_BDQUANTITY = Column(DOUBLE(asdecimal=False)) # 持有债券数量
    F_PRT_BDVALUETONAV = Column(DOUBLE(asdecimal=False)) # 持有债券市值占基金净值比例

class WindFundNav(Base):
    '''万德静态数据 中国共同基金净值'''

    __tablename__ = 'wind_fund_nav'

    F_INFO_WINDCODE =  Column(CHAR(20), primary_key=True)  # wind id
    PRICE_DATE = Column(CHAR(8), primary_key=True)  # 日期
    ANN_DATE = Column(CHAR(8))  # 公告日期
    F_NAV_UNIT = Column(DOUBLE(asdecimal=False)) # 单位净值
    F_NAV_ACCUMULATED = Column(DOUBLE(asdecimal=False)) # 累计净值
    F_NAV_DIVACCUMULATED = Column(DOUBLE(asdecimal=False)) # 累计分红
    F_NAV_ADJFACTOR = Column(DOUBLE(asdecimal=False)) # 复权因子
    CRNCY_CODE = Column(CHAR(5)) # 货币
    F_PRT_NETASSET = Column(DOUBLE(asdecimal=False)) # 资产净值
    F_ASSET_MERGEDSHARESORNOT = Column(DOUBLE(asdecimal=False)) # 是否合计数据
    NETASSET_TOTAL = Column(DOUBLE(asdecimal=False)) # 合计资产净值
    F_NAV_ADJUSTED = Column(DOUBLE(asdecimal=False)) # 复权单位净值
    IS_EXDIVIDENDDATE = Column(DOUBLE(asdecimal=False)) # 是否净值除权日
    F_NAV_DISTRIBUTION = Column(DOUBLE(asdecimal=False)) # 累计单位分配

class WindFundManager(Base):
    '''万德静态数据 中国共同基金基金经理表'''

    __tablename__ = 'wind_fund_manager'

    F_INFO_FUNDMANAGER_ID = Column(CHAR(10), primary_key=True) # 基金经理ID
    F_INFO_WINDCODE = Column(CHAR(20),  primary_key=True) # 万德基金ID
    ANN_DATE = Column(CHAR(8),  primary_key=True) # 报告日期
    F_INFO_FUNDMANAGER = Column(CHAR(10)) # 姓名
    F_INFO_MANAGER_GENDER = Column(CHAR(1)) # 性别
    F_INFO_MANAGER_BIRTHYEAR = Column(CHAR(4)) # 出生年份
    F_INFO_MANAGER_EDUCATION = Column(CHAR(10)) # 学历
    F_INFO_MANAGER_NATIONALITY = Column(CHAR(10)) # 国籍
    F_INFO_MANAGER_STARTDATE = Column(CHAR(8)) # 任职日期
    F_INFO_MANAGER_LEAVEDATE = Column(CHAR(8)) # 离职日期
    F_INFO_MANAGER_RESUME = Column(TEXT) # 简历
    S_INFO_MANAGER_POST = Column(CHAR(255)) # 备注（对于特殊基金经理的备注）
    F_INFO_ESCROW_FUNDMANAGER = Column(CHAR(20)) # 代管基金经理
    F_INFO_ESCROW_STARTDATE = Column(CHAR(8)) # 代管起始日期
    F_INFO_ESCROW_LEAVEDATE = Column(CHAR(8)) # 代管结束日期
    F_INFO_DIS_SERIAL_NUMBER = Column(CHAR(5)) # wind 展示序号

class WindIndPortfolio(Base):
    '''万德静态数据 中国共同基金基金持仓行业明细'''

    __tablename__ = 'wind_ind_portfolio'

    S_INFO_WINDCODE = Column(CHAR(20), primary_key=True) # 万德基金ID
    F_PRT_ENDDATE = Column(CHAR(8), primary_key=True) # 日期
    S_INFO_CSRCINDUSCODE = Column(CHAR(20), primary_key=True) # 证监会行业编号
    F_PRT_INDUSVALUE = Column(DOUBLE(asdecimal=False)) # 持有行业市值 元
    F_PRT_INDUSTONAV = Column(DOUBLE(asdecimal=False)) # 持有行业市值占基金净值比例 %
    F_PRT_INDPOSVALUE = Column(DOUBLE(asdecimal=False)) # 积极投资持有行业市值 元
    F_PRT_INDPOSPRO = Column(DOUBLE(asdecimal=False)) # 积极投资持有行业比例 %
    F_PRT_INDPASSIVEVALUE = Column(DOUBLE(asdecimal=False)) # 指数投资持有行业市值 元
    F_PRT_INDPASSIVEPRO = Column(DOUBLE(asdecimal=False)) # 指数投资持有行业比例 %
    F_PRT_INDUSTONAVCHANGE = Column(DOUBLE(asdecimal=False)) # 持有行业市值比例较上期变化 %
    S_INFO_CSRCINDUSNAME = Column(CHAR(50)) # 行业名称
    F_ANN_DATE = Column(CHAR(8)) # 公告日期

class FundBenchmark(Base):
    '''基金业绩比较基准表'''

    __tablename__ = 'fund_benchmark'

    em_id = Column(CHAR(16), primary_key=True)  # 基金代码
    fund_id = Column(CHAR(16))  # 内部基金代码
    # datetime = Column(DATE, primary_key=True)  # 日期
    index_text = Column(TEXT, nullable=False)  # 业绩比较基准
    benchmark = Column(TEXT, nullable=False)  # 解析出来的业绩比较基准
    assets = Column(CHAR(32))  # 追踪的标的
    industry = Column(CHAR(64))  # 行业分类


class EMFundRate(Base):
    '''东财基金评级'''

    __tablename__ = 'em_fund_rate'

    CODES = Column(CHAR(20), primary_key=True) # 东财基金ID
    DATES = Column(DATE, primary_key=True) # 日期
    MKTCOMPRE3YRAT = Column(CHAR(15)) # 市场综合3年评级
    MORNSTAR3YRAT = Column(CHAR(15)) # 晨星3年评级
    MORNSTAR5YRAT = Column(CHAR(15)) # 晨星5年评级
    MERCHANTS3YRAT = Column(CHAR(15)) # 招商3年评级
    TXCOMRATRAT = Column(CHAR(15)) # 天相投顾综合评级
    SHSTOCKSTAR3YCOMRAT = Column(CHAR(15)) #上海证券3年评级(综合评级)
    SHSTOCKSTAR3YSTOCKRAT = Column(CHAR(15)) #上海证券3年评级(选证能力)
    SHSTOCKSTAR3YTIMERAT = Column(CHAR(15)) # 上海证券3年评级(择时能力)
    SHSTOCKSTAR3YSHARPERAT = Column(CHAR(15)) # 上海证券3年评级(夏普比率)
    SHSTOCKSTAR5YCOMRATRAT = Column(CHAR(15)) # 上海证券5年评级(综合评级)
    SHSTOCKSTAR5YSTOCKRAT = Column(CHAR(15)) # 上海证券5年评级(选证能力)
    SHSTOCKSTAR5YTIMERAT = Column(CHAR(15)) # 上海证券5年评级(择时能力)
    SHSTOCKSTAR5YSHARPRAT = Column(CHAR(15)) # 上海证券5年评级(夏普比率)
    JAJXCOMRAT = Column(CHAR(15)) # 济安金信基金评级(综合评级)
    JAJXEARNINGPOWERRAT = Column(CHAR(15)) # 济安金信基金评级(盈利能力)
    JAJXACHIEVESTABILITYRAT = Column(CHAR(15)) # 济安金信基金评级(业绩稳定性)
    JAJXANTIRISKRAT = Column(CHAR(15)) # 济安金信基金评级(抗风险能力)
    JAJXSTOCKSELECTIONRAT = Column(CHAR(15)) # 济安金信基金评级(选股能力)
    JAJXTIMESELECTIONRAT = Column(CHAR(15)) # 济安金信基金评级(择时能力)
    JAJXBENCHMARKTRACKINGRAT = Column(CHAR(15)) # 济安金信基金评级(基准跟踪能力)
    JAJXEXCESSEARNINGSRAT = Column(CHAR(15)) # 济安金信基金评级(超额收益能力)
    JAJXTOTALFEERAT = Column(CHAR(15)) # 济安金信基金评级(整体费用)

class EMFundHoldAsset(Base):
    '''东财基金资产配置'''

    __tablename__ = 'em_fund_asset'

    CODES = Column(CHAR(20), primary_key=True) # 东财基金ID
    DATES = Column(DATE, primary_key=True) # 日期
    PRTSTOCKTONAV = Column(DOUBLE(asdecimal=False)) # 股票市值占基金资产净值比
    PRTBONDTONAV = Column(DOUBLE(asdecimal=False)) # 债券市值占基金资产净值比
    PRTFUNDTONAV = Column(DOUBLE(asdecimal=False)) # 基金市值占基金资产净值比
    PRTCASHTONAV = Column(DOUBLE(asdecimal=False)) # 银行存款占基金资产净值比
    PRTOTHERTONAV = Column(DOUBLE(asdecimal=False)) # 其他资产占基金资产净值比
    MMFFIRSTREPOTONAV = Column(DOUBLE(asdecimal=False))  # 报告期内债券回购融资余额占基金资产净值比例
    MMFAVGPTM = Column(DOUBLE(asdecimal=False))  # 报告期末投资组合平均剩余期限

class EMFundHoldIndustry(Base):
    '''东财基金行业配置'''

    __tablename__ = 'em_fund_industry'

    CODES = Column(CHAR(20), primary_key=True) # 东财基金ID
    DATES = Column(DATE, primary_key=True) # 日期
    rank1_indname = Column(CHAR(50)) #第一排名行业名称
    rank1_indweight = Column(DOUBLE(asdecimal=False)) #第一排名行业市值占基金资产总值比
    rank2_indname = Column(CHAR(50)) #第二排名行业名称
    rank2_indweight = Column(DOUBLE(asdecimal=False)) #第二排名行业市值占基金资产总值比
    rank3_indname = Column(CHAR(50)) #第三排名行业名称
    rank3_indweight = Column(DOUBLE(asdecimal=False)) #第三排名行业市值占基金资产总值比

class EMFundHoldIndustryQDII(Base):
    '''东财基金行业配置'''

    __tablename__ = 'em_fund_industry_qdii'

    CODES = Column(CHAR(20), primary_key=True) # 东财基金ID
    DATES = Column(DATE, primary_key=True) # 日期
    rank1_indname = Column(CHAR(50)) #第一排名行业名称
    rank1_indweight = Column(DOUBLE(asdecimal=False)) #第一排名行业市值占基金资产总值比
    rank2_indname = Column(CHAR(50)) #第二排名行业名称
    rank2_indweight = Column(DOUBLE(asdecimal=False)) #第二排名行业市值占基金资产总值比
    rank3_indname = Column(CHAR(50)) #第三排名行业名称
    rank3_indweight = Column(DOUBLE(asdecimal=False)) #第三排名行业市值占基金资产总值比

class EMFundHoldStock(Base):
    '''东财基金重仓股'''

    __tablename__ = 'em_fund_stock'

    CODES = Column(CHAR(20), primary_key=True) # 东财基金ID
    DATES = Column(DATE, primary_key=True) # 日期
    rank1_stock = Column(CHAR(20)) #股票名
    rank1_stock_code = Column(CHAR(16))  # 股票ID
    rank1_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank1_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank2_stock = Column(CHAR(20)) #股票名
    rank2_stock_code = Column(CHAR(16))  # 股票ID
    rank2_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank2_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank3_stock = Column(CHAR(20)) #股票名
    rank3_stock_code = Column(CHAR(16))  # 股票ID
    rank3_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank3_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank4_stock = Column(CHAR(20)) #股票名
    rank4_stock_code = Column(CHAR(16))  # 股票ID
    rank4_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank4_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank5_stock = Column(CHAR(20)) #股票名
    rank5_stock_code = Column(CHAR(16))  # 股票ID
    rank5_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank5_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank6_stock = Column(CHAR(20)) #股票名
    rank6_stock_code = Column(CHAR(16))  # 股票ID
    rank6_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank6_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank7_stock = Column(CHAR(20)) #股票名
    rank7_stock_code = Column(CHAR(16))  # 股票ID
    rank7_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank7_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank8_stock = Column(CHAR(20)) #股票名
    rank8_stock_code = Column(CHAR(16))  # 股票ID
    rank8_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank8_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank9_stock = Column(CHAR(20)) #股票名
    rank9_stock_code = Column(CHAR(16))  # 股票ID
    rank9_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank9_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank10_stock = Column(CHAR(20)) #股票名
    rank10_stock_code = Column(CHAR(16))  # 股票ID
    rank10_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank10_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重

class EMFundHoldStockQDII(Base):
    '''东财基金QDII重仓信息'''

    __tablename__ = 'em_fund_stock_qdii'

    CODES = Column(CHAR(20), primary_key=True) # 东财基金ID
    DATES = Column(DATE, primary_key=True) # 日期
    rank1_stock = Column(TEXT) #股票名
    rank1_stock_code = Column(TEXT)  # 股票ID
    rank1_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank1_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank1_type = Column(CHAR(20)) #类型
    rank2_stock = Column(TEXT) #股票名
    rank2_stock_code = Column(TEXT)  # 股票ID
    rank2_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank2_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank2_type = Column(CHAR(20)) #类型
    rank3_stock = Column(TEXT) #股票名
    rank3_stock_code = Column(TEXT)  # 股票ID
    rank3_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank3_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank3_type = Column(CHAR(20)) #类型
    rank4_stock = Column(TEXT) #股票名
    rank4_stock_code = Column(TEXT)  # 股票ID
    rank4_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank4_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank4_type = Column(CHAR(20)) #类型
    rank5_stock = Column(TEXT) #股票名
    rank5_stock_code = Column(TEXT)  # 股票ID
    rank5_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank5_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank5_type = Column(CHAR(20)) #类型
    rank6_stock = Column(TEXT) #股票名
    rank6_stock_code = Column(TEXT)  # 股票ID
    rank6_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank6_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank6_type = Column(CHAR(20)) #类型
    rank7_stock = Column(TEXT) #股票名
    rank7_stock_code = Column(TEXT)  # 股票ID
    rank7_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank7_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank7_type = Column(CHAR(20)) #类型
    rank8_stock = Column(TEXT) #股票名
    rank8_stock_code = Column(TEXT)  # 股票ID
    rank8_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank8_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank8_type = Column(CHAR(20)) #类型
    rank9_stock = Column(TEXT) #股票名
    rank9_stock_code = Column(TEXT)  # 股票ID
    rank9_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank9_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank9_type = Column(CHAR(20)) #类型
    rank10_stock = Column(TEXT) #股票名
    rank10_stock_code = Column(TEXT)  # 股票ID
    rank10_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank10_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank10_type = Column(CHAR(20)) #类型
    rank11_stock = Column(TEXT) #股票名
    rank11_stock_code = Column(TEXT)  # 股票ID
    rank11_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank11_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank11_type = Column(CHAR(20)) #类型
    rank12_stock = Column(TEXT) #股票名
    rank12_stock_code = Column(TEXT)  # 股票ID
    rank12_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank12_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank12_type = Column(CHAR(20)) #类型
    rank13_stock = Column(TEXT) #股票名
    rank13_stock_code = Column(TEXT)  # 股票ID
    rank13_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank13_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank13_type = Column(CHAR(20)) #类型
    rank14_stock = Column(TEXT) #股票名
    rank14_stock_code = Column(TEXT)  # 股票ID
    rank14_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank14_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank14_type = Column(CHAR(20)) #类型
    rank15_stock = Column(TEXT) #股票名
    rank15_stock_code = Column(TEXT)  # 股票ID
    rank15_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank15_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank15_type = Column(CHAR(20)) #类型
    rank16_stock = Column(TEXT) #股票名
    rank16_stock_code = Column(TEXT)  # 股票ID
    rank16_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank16_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank16_type = Column(CHAR(20)) #类型
    rank17_stock = Column(TEXT) #股票名
    rank17_stock_code = Column(TEXT)  # 股票ID
    rank17_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank17_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank17_type = Column(CHAR(20)) #类型
    rank18_stock = Column(TEXT) #股票名
    rank18_stock_code = Column(TEXT)  # 股票ID
    rank18_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank18_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank18_type = Column(CHAR(20)) #类型
    rank19_stock = Column(TEXT) #股票名
    rank19_stock_code = Column(TEXT)  # 股票ID
    rank19_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank19_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank19_type = Column(CHAR(20)) #类型
    rank20_stock = Column(TEXT) #股票名
    rank20_stock_code = Column(TEXT)  # 股票ID
    rank20_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank20_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank20_type = Column(CHAR(20)) #类型

class EMFundHoldBond(Base):
    '''东财基金重仓债'''

    __tablename__ = 'em_fund_bond'
    CODES = Column(CHAR(20), primary_key=True) # 东财基金ID
    DATES = Column(DATE, primary_key=True) # 日期
    rank1_bond = Column(CHAR(30)) #债券名
    rank1_bond_code =  Column(CHAR(15)) # 债券id
    rank1_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank1_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank2_bond = Column(CHAR(30)) #债券名
    rank2_bond_code =  Column(CHAR(15)) # 债券id
    rank2_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank2_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank3_bond = Column(CHAR(30)) #债券名
    rank3_bond_code =  Column(CHAR(15)) # 债券id
    rank3_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank3_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank4_bond = Column(CHAR(30)) #债券名
    rank4_bond_code =  Column(CHAR(15)) # 债券id
    rank4_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank4_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank5_bond = Column(CHAR(30)) #债券名
    rank5_bond_code =  Column(CHAR(15)) # 债券id
    rank5_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank5_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank6_bond = Column(CHAR(30)) #债券名
    rank6_bond_code =  Column(CHAR(15)) # 债券id
    rank6_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank6_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank7_bond = Column(CHAR(30)) #债券名
    rank7_bond_code =  Column(CHAR(15)) # 债券id
    rank7_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank7_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank8_bond = Column(CHAR(30)) #债券名
    rank8_bond_code =  Column(CHAR(15)) # 债券id
    rank8_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank8_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank9_bond = Column(CHAR(30)) #债券名
    rank9_bond_code =  Column(CHAR(15)) # 债券id
    rank9_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank9_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank10_bond = Column(CHAR(30)) #债券名
    rank10_bond_code =  Column(CHAR(15)) # 债券id
    rank10_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank10_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重

class EmStockDividend(Base):
    '''东财股票分红数据 '''

    __tablename__ = 'em_stock_dividend'

    CODES = Column(CHAR(10), primary_key=True) # 东财基金ID
    DATES = Column(DATE, primary_key=True) # 日期
    DIVPROGRESS = Column(CHAR(16)) # 分红方案进度
    DIVCASHPSBFTAX = Column(DOUBLE(asdecimal=False)) # 每股股利(税前)
    DIVSTOCKPS = Column(DOUBLE(asdecimal=False)) # 每股红股
    DIVCAPITALIZATIONPS = Column(DOUBLE(asdecimal=False)) # 每股转增股本
    DIVPRENOTICEDATE = Column(DATE) # 预披露公告日
    DIVPLANANNCDATE = Column(DATE) # 预案公告日
    DIVAGMANNCDATE = Column(DATE) # 股东大会公告日
    DIVIMPLANNCDATE = Column(DATE) # 分红实施公告日
    DIVRECORDDATE = Column(DATE) # 股权登记日
    DIVEXDATE = Column(DATE) # 除权除息日
    DIVPAYDATE = Column(DATE) # 派息日
    DIVBONUSLISTEDDATE = Column(DATE) # 送转股份上市交易日
    DIVOBJ = Column(CHAR(16)) # 分配对象
    DIVORNOT = Column(CHAR(1)) # 是否分红

class EMMngInfo(Base):
    '''东财基金经理信息表'''

    __tablename__ = 'em_mng_info'

    start_mng_date = Column(DATE, primary_key=True) # 最早任职基金经理日期
    mng_name = Column(CHAR(25), primary_key=True) # 基金经理
    code = Column(CHAR(10), primary_key=True) # 代码
    desc_name = Column(CHAR(70)) # 名称
    fund_size = Column(DOUBLE(asdecimal=False)) # 在管基金规模(亿元)
    start_date = Column(DATE) # 任职日期
    work_days = Column(DOUBLE(asdecimal=False)) # 任职天数
    his_ret = Column(DOUBLE(asdecimal=False)) # 任职以来回报(%)
    his_annual_ret = Column(DOUBLE(asdecimal=False)) # 任职以来年化回报(%)
    benchmark = Column(TEXT) # 业绩比较基准
    fund_type = Column(CHAR(25)) # 基金类型
    company_name = Column(CHAR(25)) # 管理公司
    coworkers = Column(CHAR(40)) # 共同任职经理
    mng_work_year = Column(DOUBLE(asdecimal=False)) # 基金经理年限
    worked_funds_num = Column(DOUBLE(asdecimal=False)) # 任职基金数
    worked_com_num = Column(DOUBLE(asdecimal=False)) # 任职基金公司数
    fund_total_geo_ret = Column(DOUBLE(asdecimal=False)) # 任职基金几何总回报(%)
    geo_annual_ret = Column(DOUBLE(asdecimal=False)) # 几何平均年化收益率(%)
    cal_annual_ret = Column(DOUBLE(asdecimal=False)) # 算术平均年化收益率(%)
    gender = Column(CHAR(2)) # 性别
    birth_year = Column(CHAR(4)) # 出生年份
    age =  Column(DOUBLE(asdecimal=False)) # 年龄
    education = Column(CHAR(4)) # 学历
    nationality =  Column(CHAR(10)) # 国籍
    resume = Column(TEXT) # 简历

    __table_args__ = (
        Index('idx_em_mng_info_code', 'code'),
    )

class EMFundMngChange(Base):
    '''东财基金经理变更表'''

    __tablename__ = 'em_fund_mng_change'

    code = Column(CHAR(10), primary_key=True) # 代码
    desc_name = Column(CHAR(70)) # 名称
    mng_now = Column(CHAR(40)) # 现任基金经理
    mng_now_start_date = Column(TEXT) # 现任经理最新任职日期
    mng_begin = Column(CHAR(40)) # 最早任职基金经理
    mng_begin_date = Column(DATE) # 最早任职基金经理日期
    mng_now_work_year = Column(DOUBLE(asdecimal=False)) # 现任基金经理年限
    same_type_fund_work_year = Column(DOUBLE(asdecimal=False)) # 同类型基金现任基金经理年限均值
    resign_mngs = Column(TEXT) # 已离任基金经理
    total_mng_num = Column(DOUBLE(asdecimal=False)) # 已离任基金经理
    total_mng_avg_work_year = Column(DOUBLE(asdecimal=False)) # 历任基金经理人均任职年限
    fund_type = Column(CHAR(25)) # 基金类型
    company = Column(CHAR(35)) # 管理公司
    region = Column(CHAR(5)) # 监管辖区

class EMFundCompMngChange(Base):
    '''东财基金公司经理变更表'''

    __tablename__ = 'em_fund_comp_mng_change'

    company = Column(CHAR(35),  primary_key=True ) # 管理公司
    total_mng_num = Column(DOUBLE(asdecimal=False)) # 基金经理数
    mng_avg_year = Column(DOUBLE(asdecimal=False)) # 基金经理平均年限
    mng_max_year = Column(DOUBLE(asdecimal=False)) # 基金经理最大年限
    team_stability = Column(DOUBLE(asdecimal=False)) # 团队稳定性
    new_mng_num = Column(DOUBLE(asdecimal=False)) # 新聘基金经理数
    resign_mng_num = Column(DOUBLE(asdecimal=False)) # 离职基金经理数
    mng_turnover_rate = Column(DOUBLE(asdecimal=False)) # 基金经理变动率
    exp_less_than_1 = Column(DOUBLE(asdecimal=False)) # 1年以内
    exp_1_to_2 = Column(DOUBLE(asdecimal=False)) # 1-2年
    exp_2_to_3 = Column(DOUBLE(asdecimal=False)) # 2-3年
    exp_3_to_4 = Column(DOUBLE(asdecimal=False)) # 3-4年
    exp_more_than_4 = Column(DOUBLE(asdecimal=False)) # 4年以上

class EMFundCompCoreMng(Base):
    '''东财基金公司核心人员稳定性'''

    __tablename__ = 'em_fund_comp_core_mng'

    code = Column(CHAR(10), primary_key=True) # 代码
    desc_name = Column(CHAR(70)) # 名称
    fund_resign_mng_num = Column(DOUBLE(asdecimal=False)) # 本基金离职基金经理人数
    company = Column(CHAR(35)) # 管理公司
    com_mng_num = Column(DOUBLE(asdecimal=False)) # 基金公司基金经理数
    com_resign_mng_num = Column(DOUBLE(asdecimal=False)) # 基金公司离职基金经理数
    com_resign_mng_rate = Column(DOUBLE(asdecimal=False)) # 基金公司基金经理离职率(%)
    com_core_mng_num = Column(DOUBLE(asdecimal=False)) # 基金公司核心人员人数
    com_core_mng_resign_num = Column(DOUBLE(asdecimal=False)) #基金公司核心人员离职人数
    com_core_mng_resign_rate = 	Column(DOUBLE(asdecimal=False)) #基金公司核心人员离职率(%)
    fund_type = Column(CHAR(25)) # 基金类型
    region = Column(CHAR(5)) # 监管辖区

class EmBondInfo(Base):
    '''Choice债券信息'''

    __tablename__ = 'em_bond_info'

    CODES = Column('bond_id', CHAR(16), primary_key=True) # EM债券ID
    NAME = Column("name", TEXT, nullable=False) # 债券名称
    CORPCODE = Column('corp_code', CHAR(64)) # 公司债对应上市公司代码
    EM1TYPE = Column('em1_type', CHAR(12)) # 东财债券一级分类
    EM2TYPE = Column('em2_type', CHAR(12)) # 东财债券二级分类
    CBL1TYPE = Column('cbl1_type', CHAR(16)) # 中债债券一级分类
    CBL2TYPE = Column('cbl2_type', CHAR(16)) # 中债债券二级分类
    ISCITYBOND = Column('is_city_bond', TINYINT(1)) # 是否城投债

class EmBondRateMaturity(Base):
    '''Choice债券信息'''

    __tablename__ = 'em_bond_rate_maturity'

    bond_id = Column(CHAR(16), primary_key=True) # EM债券ID
    name = Column(TEXT, nullable=False) # 债券名称
    maturity = Column(DATE) # 到期日期
    subject_rate = Column(CHAR(8)) # 发债主体评级信用等级 国债没有和省市没有主体评级 可以理解
    
class EmBondCleanPrice(Base):
    '''Choice债券价格数据(净价)'''

    __tablename__ = 'em_bond_clean_price'

    CODES = Column('bond_id', CHAR(16), primary_key=True)  # EM债券ID
    DATES = Column('datetime', DATE, primary_key=True)  # 日期
    PRECLOSE = Column('pre_close', DOUBLE(asdecimal=False), nullable=False)  # 前收盘价
    OPEN = Column('open', DOUBLE(asdecimal=False), nullable=False)  # 开盘价
    HIGH = Column('high', DOUBLE(asdecimal=False), nullable=False)  # 最高价
    LOW = Column('low', DOUBLE(asdecimal=False), nullable=False)  # 最低价
    CLOSE = Column('close', DOUBLE(asdecimal=False), nullable=False)  # 收盘价(每日结算价)

class EmBondDirtyPrice(Base):
    '''Choice债券价格数据(全价)'''

    __tablename__ = 'em_bond_dirty_price'

    CODES = Column('bond_id', CHAR(16), primary_key=True)  # EM债券ID
    DATES = Column('datetime', DATE, primary_key=True)  # 日期
    PRECLOSE = Column('pre_close', DOUBLE(asdecimal=False))  # 前收盘价
    OPEN = Column('open', DOUBLE(asdecimal=False), nullable=False)  # 开盘价
    HIGH = Column('high', DOUBLE(asdecimal=False), nullable=False)  # 最高价
    LOW = Column('low', DOUBLE(asdecimal=False), nullable=False)  # 最低价
    CLOSE = Column('close', DOUBLE(asdecimal=False), nullable=False)  # 收盘价(每日结算价)
    VOLUME = Column('volume', DOUBLE(asdecimal=False), nullable=False)  # 成交量
    AMOUNT = Column('amount', DOUBLE(asdecimal=False), nullable=False)  # 成交额

class EmBondRating(Base):
    '''Choice债券评级'''

    __tablename__ = 'em_bond_rating'

    CODES = Column('bond_id', CHAR(16), primary_key=True) # EM债券ID
    DATES = Column('datetime', DATE, primary_key=True) # 日期

    APPORATE = Column('appo_rate', CHAR(8))  # 指定日债项评级

    __table_args__ = (
        Index('idx_em_bond_rating_datetime', 'datetime'),
    )

class EmMacroEconomicInfo(Base):
    '''Choice宏观经济数据信息'''

    __tablename__ = 'em_macro_economic_info'

    codes = Column(CHAR(12), primary_key=True)  # 代码
    em_codes = Column(CHAR(16), nullable=False)  # EM代码
    desc_name = Column(TEXT, nullable=False)  # 中文描述


class EmMacroEconomicMonthly(Base):
    '''Choice宏观经济数据(月度)'''

    __tablename__ = 'em_macro_economic_monthly'

    codes = Column(CHAR(12), primary_key=True)
    datetime = Column(DATE, primary_key=True) # 日期

    value = Column(DOUBLE(asdecimal=False)) # 数据


class EmMacroEconomicDaily(Base):
    '''Choice宏观经济数据(日度)'''

    __tablename__ = 'em_macro_economic_daily'

    # TB_1Y: 中债国债到期收益率：1年
    # TB_3Y: 中债国债到期收益率：3年
    # TB_5Y: 中债国债到期收益率：5年
    # TB_10Y: 中债国债到期收益率：10年
    # SHIBOR_1M: 1个月SHIBOR
    # SHIBOR_3M: 3个月SHIBOR
    # CB_AAA_1Y: 交易所公司债到期收益率(AAA):1年
    # EX_DR_RATIO: 超额存款准备金率：日
    codes = Column(CHAR(12), primary_key=True)
    datetime = Column(DATE, primary_key=True) # 日期

    value = Column(DOUBLE(asdecimal=False)) # 数据

class EmFundIPOStats(Base):
    '''基金打新收益率统计'''

    __tablename__ = 'em_fund_ipo_stats'

    em_id = Column(CHAR(10), primary_key=True) # 代码
    end_date = Column(DATE, primary_key=True) # 结束统计日
    ipo_allocation_num = Column(Integer) # 打中新股数量
    ipo_allocation_share_num = Column(DOUBLE(asdecimal=False)) # 累计获配股数(万股)
    ipo_allocation_amount = Column(DOUBLE(asdecimal=False)) # 累计获配金额(万元)
    ipo_allocation_ret = Column(DOUBLE(asdecimal=False)) # 打新收益率(%)
    start_date = Column(DATE)  # 开始统计日期

class EmFundConvInfo(Base):
    '''可转债发行'''

    __tablename__ = 'em_fund_conv_info'
    issue_date = Column(DATE, primary_key=True) # 发行日期
    conv_bond_id = Column(CHAR(10), primary_key=True) # 转债代码
    bond_name = Column(CHAR(64), primary_key=True) # 转债名称
    em_id = Column(CHAR(10)) #代码
    desc_name = Column(CHAR(64)) # 基金名称名称
    conv_bond_id = Column(CHAR(10)) # 转债代码
    ipo_method = Column(TEXT) # 发行方式
    ipo_size = Column(DOUBLE(asdecimal=False)) # 发行规模(亿元)
    duration = Column(DOUBLE(asdecimal=False)) # 发行期限(年)
    rating = Column(CHAR(10)) # 信用评级
    coupon_rate = Column(DOUBLE(asdecimal=False)) # 票面利率(%)
    compensation_rate = Column(DOUBLE(asdecimal=False)) # 补偿利率(%)
    rate_type = Column(CHAR(15)) # 利率类型
    latest_balance = Column(DOUBLE(asdecimal=False)) # 最新余额(万元)
    payment_frequency = Column(CHAR(15)) # 付息频率
    payment_doc = Column(CHAR(15)) # 付息说明
    listing_date = Column(DATE) # 上市日期
    value_date = Column(DATE) # 起息日期
    date_of_expiry = Column(DATE) # 到期日期
    conv_start_date = Column(DATE) # 转股起始日
    init_conv_price = Column(DOUBLE(asdecimal=False)) # 初始转股价
    latest_conv_price = Column(DOUBLE(asdecimal=False)) # 最新转股价
    rate_doc = Column(TEXT) # 利率说明
    redemption_clause = Column(TEXT) # 赎回条款
    resale_clause = Column(TEXT) # 回售条款
    downward_amendment = Column(TEXT) # 特别向下修正条款
    conv_clause = Column(TEXT) # 转股条款
    warrent = Column(CHAR(100)) # 担保人
    warrent_method = Column(CHAR(30)) # 担保方式
    warrent_scope = Column(TEXT) # 担保范围
    credit_rating = Column(CHAR(10)) # 信用等级
    evaluation_agency = Column(CHAR(50)) # 评估机构
    lead_underwriter = Column(TEXT) # 主承销商
    industry = Column(CHAR(40)) # 证监会行业(2012)
    em_industry = Column(CHAR(20)) # 东财行业

class EmFundIPODetail(Base):
    '''打新明细'''
    #TODO 东财这部分下数据接口在11月上限，当前没有直接使用，通过客户端接口下载csv数据倒入数据库，只有一个基金明细

    __tablename__ = 'em_fund_ipo_detail'
    stock_id = Column(CHAR(10), primary_key=True) # 代码
    em_id = Column(CHAR(10), primary_key=True) # 基金代码
    desc_name = Column(CHAR(20)) # 名称
    placedate = Column(DATE) # 配售日期
    effective_volume = Column(DOUBLE(asdecimal=False)) # 有效申购数量(万股)
    actual_volume = Column(DOUBLE(asdecimal=False)) # 实际配售数量(万股)
    place_rate = Column(DOUBLE(asdecimal=False)) # 获配比例(%)
    place_amt = Column(DOUBLE(asdecimal=False)) # 获配金额(万元)
    lock_up_period = Column(TEXT) # 锁定期限
    issue_price = Column(DOUBLE(asdecimal=False)) # 发行价格(元)
    first_open_d_ret = Column(DOUBLE(asdecimal=False)) # 首个开板日涨跌幅(%)
    historcal_ret = Column(DOUBLE(asdecimal=False)) # 上市以来最高涨幅(%)
    ipo_allocation_ret = Column(DOUBLE(asdecimal=False)) # 打新收益率(%)
    annual_allocation_ret = Column(DOUBLE(asdecimal=False)) # 年化打新收益率(%)
    industry = Column(CHAR(40)) # 证监会行业(2012)
    em_industry = Column(CHAR(20)) # 东财行业


class EmFundOpen(Base):
    '''东财定期开放基金'''

    __tablename__ = 'em_fund_open'
    em_id = Column(CHAR(10), primary_key=True) # 基金代码
    desc_name = Column(CHAR(20)) # 名称


class EmFundStockPortfolio(Base):
    '''Choice基金的股票全部持仓'''

    __tablename__ = 'em_fund_stock_portfolio'

    em_id = Column(CHAR(10), primary_key=True)  # 基金代码
    report_date = Column(DATE, primary_key=True)  # 报告期
    stock_id = Column(CHAR(10), primary_key=True)  # 股票代码
    hold_number = Column(DOUBLE(asdecimal=True), nullable=False)  # 持股数量(万股)
    semi_change = Column(DOUBLE(asdecimal=True))  # 半年度持股变动(万股)
    stock_mv = Column(DOUBLE(asdecimal=True))  # 持股市值(万元)
    net_asset_ratio = Column(DOUBLE(asdecimal=True))  # 占净值比(%)
    mv_ratio = Column(DOUBLE(asdecimal=True))  # 占股票投资市值比(%)


class EmStockFSBalanceSheet(Base):
    '''Choice股票资产负债表'''

    __tablename__ = 'em_stock_fs_balance_sheet'

    CODES = Column(CHAR(10), primary_key=True)  # EM股票ID
    DATES = Column(DATE, primary_key=True)  # 财报日期
    # 流动资产部分
    BALANCESTATEMENT_9 = Column(DOUBLE(asdecimal=True))  # 货币资金
    BALANCESTATEMENT_67 = Column(DOUBLE(asdecimal=True))  # 结算备付金
    BALANCESTATEMENT_181 = Column(DOUBLE(asdecimal=True))  # 融出资金
    BALANCESTATEMENT_50 = Column(DOUBLE(asdecimal=True))  # 拆出资金
    BALANCESTATEMENT_224 = Column(DOUBLE(asdecimal=True))  # 交易性金融资产
    BALANCESTATEMENT_163 = Column(DOUBLE(asdecimal=True))  # 以公允价值计量且其变动计入当期损益的金融资产
    BALANCESTATEMENT_10 = Column(DOUBLE(asdecimal=True))  # 其中:交易性金融资产
    BALANCESTATEMENT_164 = Column(DOUBLE(asdecimal=True))  # 其中:指定以公允价值计量且其变动计入当期损益的金融资产
    BALANCESTATEMENT_51 = Column(DOUBLE(asdecimal=True))  # 衍生金融资产
    BALANCESTATEMENT_216 = Column(DOUBLE(asdecimal=True))  # 应收票据及应收账款
    BALANCESTATEMENT_11 = Column(DOUBLE(asdecimal=True))  # 应收票据
    BALANCESTATEMENT_12 = Column(DOUBLE(asdecimal=True))  # 应收账款
    BALANCESTATEMENT_223 = Column(DOUBLE(asdecimal=True))  # 应收款项融资
    BALANCESTATEMENT_14 = Column(DOUBLE(asdecimal=True))  # 预付款项
    BALANCESTATEMENT_55 = Column(DOUBLE(asdecimal=True))  # 应收保费
    BALANCESTATEMENT_57 = Column(DOUBLE(asdecimal=True))  # 应收分保账款
    BALANCESTATEMENT_152 = Column(DOUBLE(asdecimal=True))  # 应收分保合同准备金
    BALANCESTATEMENT_222 = Column(DOUBLE(asdecimal=True))  # 其他应收款合计
    BALANCESTATEMENT_16 = Column(DOUBLE(asdecimal=True))  # 其中:应收利息
    BALANCESTATEMENT_15 = Column(DOUBLE(asdecimal=True))  # 其中:应收股利
    BALANCESTATEMENT_13 = Column(DOUBLE(asdecimal=True))  # 其中:其他应收款
    BALANCESTATEMENT_156 = Column(DOUBLE(asdecimal=True))  # 应收出口退税
    BALANCESTATEMENT_157 = Column(DOUBLE(asdecimal=True))  # 应收补贴款
    BALANCESTATEMENT_158 = Column(DOUBLE(asdecimal=True))  # 内部应收款
    BALANCESTATEMENT_52 = Column(DOUBLE(asdecimal=True))  # 买入返售金融资产
    BALANCESTATEMENT_206 = Column(DOUBLE(asdecimal=True))  # 以摊余成本计量的金融资产
    BALANCESTATEMENT_17 = Column(DOUBLE(asdecimal=True))  # 存货
    BALANCESTATEMENT_207 = Column(DOUBLE(asdecimal=True))  # 以公允价值计量且其变动计入其他综合收益的金融资产
    BALANCESTATEMENT_209 = Column(DOUBLE(asdecimal=True))  # 合同资产
    BALANCESTATEMENT_202 = Column(DOUBLE(asdecimal=True))  # 划分为持有待售的资产
    BALANCESTATEMENT_20 = Column(DOUBLE(asdecimal=True))  # 一年内到期的非流动资产
    BALANCESTATEMENT_190 = Column(DOUBLE(asdecimal=True))  # 代理业务资产
    BALANCESTATEMENT_21 = Column(DOUBLE(asdecimal=True))  # 其他流动资产
    BALANCESTATEMENT_22 = Column(DOUBLE(asdecimal=True))  # 流动资产其他项目
    BALANCESTATEMENT_23 = Column(DOUBLE(asdecimal=True))  # 流动资产平衡项目
    BALANCESTATEMENT_25 = Column(DOUBLE(asdecimal=True))  # 流动资产合计
    # 非流动资产部分
    BALANCESTATEMENT_53 = Column(DOUBLE(asdecimal=True))  # 发放贷款及垫款
    BALANCESTATEMENT_217 = Column(DOUBLE(asdecimal=True))  # 债权投资
    BALANCESTATEMENT_218 = Column(DOUBLE(asdecimal=True))  # 其他债权投资
    BALANCESTATEMENT_211 = Column(DOUBLE(asdecimal=True))  # 以摊余成本计量的金融资产(非流动)
    BALANCESTATEMENT_212 = Column(DOUBLE(asdecimal=True))  # 以公允价值计量且其变动计入其他综合收益的金融资产(非流动)
    BALANCESTATEMENT_26 = Column(DOUBLE(asdecimal=True))  # 可供出售金融资产
    BALANCESTATEMENT_27 = Column(DOUBLE(asdecimal=True))  # 持有至到期投资
    BALANCESTATEMENT_30 = Column(DOUBLE(asdecimal=True))  # 长期应收款
    BALANCESTATEMENT_29 = Column(DOUBLE(asdecimal=True))  # 长期股权投资
    BALANCESTATEMENT_28 = Column(DOUBLE(asdecimal=True))  # 投资性房地产
    BALANCESTATEMENT_31 = Column(DOUBLE(asdecimal=True))  # 固定资产
    BALANCESTATEMENT_33 = Column(DOUBLE(asdecimal=True))  # 在建工程
    BALANCESTATEMENT_32 = Column(DOUBLE(asdecimal=True))  # 工程物资
    BALANCESTATEMENT_219 = Column(DOUBLE(asdecimal=True))  # 其他权益工具投资
    BALANCESTATEMENT_220 = Column(DOUBLE(asdecimal=True))  # 其他非流动金融资产
    BALANCESTATEMENT_34 = Column(DOUBLE(asdecimal=True))  # 固定资产清理
    BALANCESTATEMENT_35 = Column(DOUBLE(asdecimal=True))  # 生产性生物资产
    BALANCESTATEMENT_36 = Column(DOUBLE(asdecimal=True))  # 油气资产
    BALANCESTATEMENT_225 = Column(DOUBLE(asdecimal=True))  # 使用权资产
    BALANCESTATEMENT_37 = Column(DOUBLE(asdecimal=True))  # 无形资产
    BALANCESTATEMENT_44 = Column(DOUBLE(asdecimal=True))  # 非流动资产平衡项目
    BALANCESTATEMENT_38 = Column(DOUBLE(asdecimal=True))  # 开发支出
    BALANCESTATEMENT_39 = Column(DOUBLE(asdecimal=True))  # 商誉
    BALANCESTATEMENT_40 = Column(DOUBLE(asdecimal=True))  # 长期待摊费用
    BALANCESTATEMENT_41 = Column(DOUBLE(asdecimal=True))  # 递延所得税资产
    BALANCESTATEMENT_42 = Column(DOUBLE(asdecimal=True))  # 其他非流动资产
    BALANCESTATEMENT_43 = Column(DOUBLE(asdecimal=True))  # 非流动资产其他项目
    BALANCESTATEMENT_46 = Column(DOUBLE(asdecimal=True))  # 非流动资产合计
    BALANCESTATEMENT_71 = Column(DOUBLE(asdecimal=True))  # 资产其他项目
    BALANCESTATEMENT_72 = Column(DOUBLE(asdecimal=True))  # 资产平衡项目
    BALANCESTATEMENT_74 = Column(DOUBLE(asdecimal=True))  # 资产总计
    # 流动负债
    BALANCESTATEMENT_75 = Column(DOUBLE(asdecimal=True))  # 短期借款
    BALANCESTATEMENT_105 = Column(DOUBLE(asdecimal=True))  # 向中央银行借款
    BALANCESTATEMENT_153 = Column(DOUBLE(asdecimal=True))  # 吸收存款及同业存放
    BALANCESTATEMENT_106 = Column(DOUBLE(asdecimal=True))  # 拆入资金
    BALANCESTATEMENT_226 = Column(DOUBLE(asdecimal=True))  # 交易性金融负债
    BALANCESTATEMENT_170 = Column(DOUBLE(asdecimal=True))  # 以公允价值计量且其变动计入当期损益的金融负债
    BALANCESTATEMENT_76 = Column(DOUBLE(asdecimal=True))  # 其中:交易性金融负债
    BALANCESTATEMENT_171 = Column(DOUBLE(asdecimal=True))  # 其中:指定以公允价值计量且其变动计入当期损益的金融负债
    BALANCESTATEMENT_107 = Column(DOUBLE(asdecimal=True))  # 衍生金融负债
    BALANCESTATEMENT_221 = Column(DOUBLE(asdecimal=True))  # 应付票据及应付账款
    BALANCESTATEMENT_77 = Column(DOUBLE(asdecimal=True))  # 应付票据
    BALANCESTATEMENT_78 = Column(DOUBLE(asdecimal=True))  # 应付账款
    BALANCESTATEMENT_79 = Column(DOUBLE(asdecimal=True))  # 预收款项
    BALANCESTATEMENT_213 = Column(DOUBLE(asdecimal=True))  # 合同负债
    BALANCESTATEMENT_108 = Column(DOUBLE(asdecimal=True))  # 卖出回购金融资产款
    BALANCESTATEMENT_113 = Column(DOUBLE(asdecimal=True))  # 应付手续费及佣金
    BALANCESTATEMENT_80 = Column(DOUBLE(asdecimal=True))  # 应付职工薪酬
    BALANCESTATEMENT_81 = Column(DOUBLE(asdecimal=True))  # 应交税费
    BALANCESTATEMENT_227 = Column(DOUBLE(asdecimal=True))  # 其他应付款合计
    BALANCESTATEMENT_82 = Column(DOUBLE(asdecimal=True))  # 其中:应付利息
    BALANCESTATEMENT_83 = Column(DOUBLE(asdecimal=True))  # 其中:应付股利
    BALANCESTATEMENT_84 = Column(DOUBLE(asdecimal=True))  # 其中:其他应付款
    BALANCESTATEMENT_114 = Column(DOUBLE(asdecimal=True))  # 应付分保账款
    BALANCESTATEMENT_188 = Column(DOUBLE(asdecimal=True))  # 内部应付款
    BALANCESTATEMENT_189 = Column(DOUBLE(asdecimal=True))  # 预计流动负债
    BALANCESTATEMENT_154 = Column(DOUBLE(asdecimal=True))  # 保险合同准备金
    BALANCESTATEMENT_123 = Column(DOUBLE(asdecimal=True))  # 代理买卖证券款
    BALANCESTATEMENT_124 = Column(DOUBLE(asdecimal=True))  # 代理承销证券款
    BALANCESTATEMENT_87 = Column(DOUBLE(asdecimal=True))  # 一年内的递延收益
    BALANCESTATEMENT_208 = Column(DOUBLE(asdecimal=True))  # 以摊余成本计量的金融负债
    BALANCESTATEMENT_147 = Column(DOUBLE(asdecimal=True))  # 应付短期债券
    BALANCESTATEMENT_203 = Column(DOUBLE(asdecimal=True))  # 划分为持有待售的负债
    BALANCESTATEMENT_88 = Column(DOUBLE(asdecimal=True))  # 一年内到期的非流动负债
    BALANCESTATEMENT_191 = Column(DOUBLE(asdecimal=True))  # 代理业务负债
    BALANCESTATEMENT_89 = Column(DOUBLE(asdecimal=True))  # 其他流动负债
    BALANCESTATEMENT_90 = Column(DOUBLE(asdecimal=True))  # 流动负债其他项目
    BALANCESTATEMENT_91 = Column(DOUBLE(asdecimal=True))  # 流动负债平衡项目
    BALANCESTATEMENT_93 = Column(DOUBLE(asdecimal=True))  # 流动负债合计
    # 非流动负债
    BALANCESTATEMENT_94 = Column(DOUBLE(asdecimal=True))  # 长期借款
    BALANCESTATEMENT_215 = Column(DOUBLE(asdecimal=True))  # 以摊余成本计量的金融负债(非流动)
    BALANCESTATEMENT_95 = Column(DOUBLE(asdecimal=True))  # 应付债券
    BALANCESTATEMENT_193 = Column(DOUBLE(asdecimal=True))  # 其中:优先股(应付债券)
    BALANCESTATEMENT_194 = Column(DOUBLE(asdecimal=True))  # 其中:永续债(应付债券)
    BALANCESTATEMENT_228 = Column(DOUBLE(asdecimal=True))  # 租赁负债
    BALANCESTATEMENT_96 = Column(DOUBLE(asdecimal=True))  # 长期应付款
    BALANCESTATEMENT_201 = Column(DOUBLE(asdecimal=True))  # 长期应付职工薪酬
    BALANCESTATEMENT_97 = Column(DOUBLE(asdecimal=True))  # 专项应付款
    BALANCESTATEMENT_86 = Column(DOUBLE(asdecimal=True))  # 预计负债
    BALANCESTATEMENT_148 = Column(DOUBLE(asdecimal=True))  # 递延收益
    BALANCESTATEMENT_98 = Column(DOUBLE(asdecimal=True))  # 递延所得税负债
    BALANCESTATEMENT_99 = Column(DOUBLE(asdecimal=True))  # 其他非流动负债
    BALANCESTATEMENT_100 = Column(DOUBLE(asdecimal=True))  # 非流动负债其他项目
    BALANCESTATEMENT_101 = Column(DOUBLE(asdecimal=True))  # 非流动负债平衡项目
    BALANCESTATEMENT_103 = Column(DOUBLE(asdecimal=True))  # 非流动负债合计
    BALANCESTATEMENT_125 = Column(DOUBLE(asdecimal=True))  # 负债其他项目
    BALANCESTATEMENT_126 = Column(DOUBLE(asdecimal=True))  # 负债平衡项目
    BALANCESTATEMENT_128 = Column(DOUBLE(asdecimal=True))  # 负债合计
    # 所有者权益
    BALANCESTATEMENT_129 = Column(DOUBLE(asdecimal=True))  # 实收资本(股本)
    BALANCESTATEMENT_195 = Column(DOUBLE(asdecimal=True))  # 其他权益工具
    BALANCESTATEMENT_196 = Column(DOUBLE(asdecimal=True))  # 其中:优先股(其他权益工具)
    BALANCESTATEMENT_197 = Column(DOUBLE(asdecimal=True))  # 其中:永续债(其他权益工具)
    BALANCESTATEMENT_198 = Column(DOUBLE(asdecimal=True))  # 其中:其他(其他权益工具)
    BALANCESTATEMENT_130 = Column(DOUBLE(asdecimal=True))  # 资本公积
    BALANCESTATEMENT_199 = Column(DOUBLE(asdecimal=True))  # 其他综合收益
    BALANCESTATEMENT_133 = Column(DOUBLE(asdecimal=True))  # 库存股
    BALANCESTATEMENT_159 = Column(DOUBLE(asdecimal=True))  # 专项储备
    BALANCESTATEMENT_131 = Column(DOUBLE(asdecimal=True))  # 盈余公积
    BALANCESTATEMENT_134 = Column(DOUBLE(asdecimal=True))  # 一般风险准备
    BALANCESTATEMENT_151 = Column(DOUBLE(asdecimal=True))  # 未确定的投资损失
    BALANCESTATEMENT_132 = Column(DOUBLE(asdecimal=True))  # 未分配利润
    BALANCESTATEMENT_160 = Column(DOUBLE(asdecimal=True))  # 拟分配现金股利
    BALANCESTATEMENT_135 = Column(DOUBLE(asdecimal=True))  # 外币报表折算差额
    BALANCESTATEMENT_161 = Column(DOUBLE(asdecimal=True))  # 归属于母公司股东权益其他项目
    BALANCESTATEMENT_162 = Column(DOUBLE(asdecimal=True))  # 归属于母公司股东权益平衡项目
    BALANCESTATEMENT_140 = Column(DOUBLE(asdecimal=True))  # 归属于母公司股东权益合计
    BALANCESTATEMENT_136 = Column(DOUBLE(asdecimal=True))  # 少数股东权益
    BALANCESTATEMENT_137 = Column(DOUBLE(asdecimal=True))  # 股东权益其他项目
    BALANCESTATEMENT_138 = Column(DOUBLE(asdecimal=True))  # 股东权益平衡项目
    BALANCESTATEMENT_141 = Column(DOUBLE(asdecimal=True))  # 股东权益合计
    BALANCESTATEMENT_142 = Column(DOUBLE(asdecimal=True))  # 负债和股东权益其他项目
    BALANCESTATEMENT_143 = Column(DOUBLE(asdecimal=True))  # 负债和股东权益平衡项目
    BALANCESTATEMENT_145 = Column(DOUBLE(asdecimal=True))  # 负债和股东权益合计

    __table_args__ = (
        Index('idx_em_stock_fs_balance_sheet_datetime', 'DATES'),
    )

class EmStockFSIncomeStatement(Base):
    '''Choice股票利润表'''

    __tablename__ = 'em_stock_fs_income_statement'

    CODES = Column(CHAR(10), primary_key=True)  # EM股票ID
    DATES = Column(DATE, primary_key=True)  # 财报日期
    INCOMESTATEMENT_83 = Column(DOUBLE(asdecimal=True))  # 营业总收入
    INCOMESTATEMENT_9 = Column(DOUBLE(asdecimal=True))  # 营业收入
    INCOMESTATEMENT_19 = Column(DOUBLE(asdecimal=True))  # 利息收入
    INCOMESTATEMENT_28 = Column(DOUBLE(asdecimal=True))  # 已赚保费
    INCOMESTATEMENT_22 = Column(DOUBLE(asdecimal=True))  # 手续费及佣金收入
    INCOMESTATEMENT_85 = Column(DOUBLE(asdecimal=True))  # 其他业务收入
    INCOMESTATEMENT_88 = Column(DOUBLE(asdecimal=True))  # 营业总收入其他项目
    INCOMESTATEMENT_84 = Column(DOUBLE(asdecimal=True))  # 营业总成本
    INCOMESTATEMENT_10 = Column(DOUBLE(asdecimal=True))  # 营业成本
    INCOMESTATEMENT_20 = Column(DOUBLE(asdecimal=True))  # 利息支出
    INCOMESTATEMENT_23 = Column(DOUBLE(asdecimal=True))  # 手续费及佣金支出
    INCOMESTATEMENT_89 = Column(DOUBLE(asdecimal=True))  # 研发费用
    INCOMESTATEMENT_39 = Column(DOUBLE(asdecimal=True))  # 退保金
    INCOMESTATEMENT_33 = Column(DOUBLE(asdecimal=True))  # 赔付支出净额
    INCOMESTATEMENT_35 = Column(DOUBLE(asdecimal=True))  # 提取保险合同准备金净额
    INCOMESTATEMENT_40 = Column(DOUBLE(asdecimal=True))  # 保单红利支出
    INCOMESTATEMENT_38 = Column(DOUBLE(asdecimal=True))  # 分保费用
    INCOMESTATEMENT_86 = Column(DOUBLE(asdecimal=True))  # 其他业务成本
    INCOMESTATEMENT_11 = Column(DOUBLE(asdecimal=True))  # 税金及附加
    INCOMESTATEMENT_12 = Column(DOUBLE(asdecimal=True))  # 销售费用
    INCOMESTATEMENT_13 = Column(DOUBLE(asdecimal=True))  # 管理费用
    INCOMESTATEMENT_14 = Column(DOUBLE(asdecimal=True))  # 财务费用
    INCOMESTATEMENT_127 = Column(DOUBLE(asdecimal=True))  # 其中:利息支出
    INCOMESTATEMENT_128 = Column(DOUBLE(asdecimal=True))  # 其中:利息收入
    INCOMESTATEMENT_15 = Column(DOUBLE(asdecimal=True))  # 资产减值损失
    INCOMESTATEMENT_129 = Column(DOUBLE(asdecimal=True))  # 信用减值损失
    INCOMESTATEMENT_90 = Column(DOUBLE(asdecimal=True))  # 营业总成本其他项目
    INCOMESTATEMENT_16 = Column(DOUBLE(asdecimal=True))  # 公允价值变动收益
    INCOMESTATEMENT_17 = Column(DOUBLE(asdecimal=True))  # 投资收益
    INCOMESTATEMENT_82 = Column(DOUBLE(asdecimal=True))  # 对联营企业和合营企业的投资收益
    INCOMESTATEMENT_130 = Column(DOUBLE(asdecimal=True))  # 净敞口套期收益
    INCOMESTATEMENT_25 = Column(DOUBLE(asdecimal=True))  # 汇兑收益
    INCOMESTATEMENT_180 = Column(DOUBLE(asdecimal=True))  # 资产减值损失(新)
    INCOMESTATEMENT_182 = Column(DOUBLE(asdecimal=True))  # 信用减值损失(新)
    INCOMESTATEMENT_123 = Column(DOUBLE(asdecimal=True))  # 资产处置收益
    INCOMESTATEMENT_124 = Column(DOUBLE(asdecimal=True))  # 其他收益
    INCOMESTATEMENT_45 = Column(DOUBLE(asdecimal=True))  # 营业利润其他项目
    INCOMESTATEMENT_46 = Column(DOUBLE(asdecimal=True))  # 营业利润平衡项目
    INCOMESTATEMENT_48 = Column(DOUBLE(asdecimal=True))  # 营业利润
    INCOMESTATEMENT_49 = Column(DOUBLE(asdecimal=True))  # 营业外收入
    INCOMESTATEMENT_118 = Column(DOUBLE(asdecimal=True))  # 非流动资产处置利得
    INCOMESTATEMENT_50 = Column(DOUBLE(asdecimal=True))  # 营业外支出
    INCOMESTATEMENT_51 = Column(DOUBLE(asdecimal=True))  # 非流动资产处置净损失
    INCOMESTATEMENT_52 = Column(DOUBLE(asdecimal=True))  # 影响利润总额的其他项目
    INCOMESTATEMENT_53 = Column(DOUBLE(asdecimal=True))  # 利润总额平衡项目
    INCOMESTATEMENT_55 = Column(DOUBLE(asdecimal=True))  # 利润总额
    INCOMESTATEMENT_56 = Column(DOUBLE(asdecimal=True))  # 所得税
    INCOMESTATEMENT_87 = Column(DOUBLE(asdecimal=True))  # 未确认投资损失
    INCOMESTATEMENT_57 = Column(DOUBLE(asdecimal=True))  # 影响净利润的其他项目
    INCOMESTATEMENT_120 = Column(DOUBLE(asdecimal=True))  # 净利润差额(合计平衡项目2)
    INCOMESTATEMENT_60 = Column(DOUBLE(asdecimal=True))  # 净利润
    INCOMESTATEMENT_125 = Column(DOUBLE(asdecimal=True))  # 持续经营净利润
    INCOMESTATEMENT_126 = Column(DOUBLE(asdecimal=True))  # 终止经营净利润
    INCOMESTATEMENT_91 = Column(DOUBLE(asdecimal=True))  # 被合并方在合并前实现利润
    INCOMESTATEMENT_61 = Column(DOUBLE(asdecimal=True))  # 归属于母公司股东的净利润
    INCOMESTATEMENT_62 = Column(DOUBLE(asdecimal=True))  # 少数股东损益
    INCOMESTATEMENT_92 = Column(DOUBLE(asdecimal=True))  # 净利润其他项目
    INCOMESTATEMENT_58 = Column(DOUBLE(asdecimal=True))  # 净利润差额(合计平衡项目)
    INCOMESTATEMENT_80 = Column(DOUBLE(asdecimal=True))  # 基本每股收益
    INCOMESTATEMENT_81 = Column(DOUBLE(asdecimal=True))  # 稀释每股收益
    INCOMESTATEMENT_114 = Column(DOUBLE(asdecimal=True))  # 其他综合收益
    INCOMESTATEMENT_116 = Column(DOUBLE(asdecimal=True))  # 归属于母公司股东的其他综合收益
    INCOMESTATEMENT_115 = Column(DOUBLE(asdecimal=True))  # 归属于少数股东的其他综合收益
    INCOMESTATEMENT_113 = Column(DOUBLE(asdecimal=True))  # 综合收益总额
    INCOMESTATEMENT_93 = Column(DOUBLE(asdecimal=True))  # 归属于母公司所有者的综合收益总额
    INCOMESTATEMENT_94 = Column(DOUBLE(asdecimal=True))  # 归属于少数股东的综合收益总额
    INCOMESTATEMENT_139 = Column(DOUBLE(asdecimal=True))  # 以摊余成本计量的金融资产终止确认收益

    __table_args__ = (
        Index('idx_em_stock_fs_income_statement_datetime', 'DATES'),
    )

class EmStockFSCashflowStatement(Base):
    '''Choice股票现金流量表'''

    __tablename__ = 'em_stock_fs_cashflow_statement'

    CODES = Column(CHAR(10), primary_key=True)  # EM股票ID
    DATES = Column(DATE, primary_key=True)  # 财报日期
    # 经营活动产生的现金流量部分
    CASHFLOWSTATEMENT_9 = Column(DOUBLE(asdecimal=True))  # 销售商品、提供劳务收到的现金
    CASHFLOWSTATEMENT_12 = Column(DOUBLE(asdecimal=True))  # 客户存款和同业存放款项净增加额
    CASHFLOWSTATEMENT_13 = Column(DOUBLE(asdecimal=True))  # 向中央银行借款净增加额
    CASHFLOWSTATEMENT_14 = Column(DOUBLE(asdecimal=True))  # 向其他金融机构拆入资金净增加额
    CASHFLOWSTATEMENT_16 = Column(DOUBLE(asdecimal=True))  # 收到原保险合同保费取得的现金
    CASHFLOWSTATEMENT_17 = Column(DOUBLE(asdecimal=True))  # 收到再保险业务现金净额
    CASHFLOWSTATEMENT_64 = Column(DOUBLE(asdecimal=True))  # 保户储金及投资款净增加额
    CASHFLOWSTATEMENT_18 = Column(DOUBLE(asdecimal=True))  # 处置交易性金融资产净增加额
    CASHFLOWSTATEMENT_186 = Column(DOUBLE(asdecimal=True))  # 收取利息、手续费及佣金的现金
    CASHFLOWSTATEMENT_20 = Column(DOUBLE(asdecimal=True))  # 拆入资金净增加额
    CASHFLOWSTATEMENT_120 = Column(DOUBLE(asdecimal=True))  # 发放贷款及垫款的净减少额
    CASHFLOWSTATEMENT_21 = Column(DOUBLE(asdecimal=True))  # 回购业务资金净增加额
    CASHFLOWSTATEMENT_10 = Column(DOUBLE(asdecimal=True))  # 收到的税费返还
    CASHFLOWSTATEMENT_11 = Column(DOUBLE(asdecimal=True))  # 收到其他与经营活动有关的现金
    CASHFLOWSTATEMENT_22 = Column(DOUBLE(asdecimal=True))  # 经营活动现金流入其他项目
    CASHFLOWSTATEMENT_23 = Column(DOUBLE(asdecimal=True))  # 经营活动现金流入平衡项目
    CASHFLOWSTATEMENT_25 = Column(DOUBLE(asdecimal=True))  # 经营活动现金流入小计
    CASHFLOWSTATEMENT_26 = Column(DOUBLE(asdecimal=True))  # 购买商品、接受劳务支付的现金
    CASHFLOWSTATEMENT_30 = Column(DOUBLE(asdecimal=True))  # 客户贷款及垫款净增加额
    CASHFLOWSTATEMENT_31 = Column(DOUBLE(asdecimal=True))  # 存放中央银行和同业款项净增加额
    CASHFLOWSTATEMENT_32 = Column(DOUBLE(asdecimal=True))  # 支付原保险合同赔付款项的现金
    CASHFLOWSTATEMENT_33 = Column(DOUBLE(asdecimal=True))  # 支付利息、手续费及佣金的现金
    CASHFLOWSTATEMENT_195 = Column(DOUBLE(asdecimal=True))  # 支付保单红利的现金
    CASHFLOWSTATEMENT_27 = Column(DOUBLE(asdecimal=True))  # 支付给职工以及为职工支付的现金
    CASHFLOWSTATEMENT_28 = Column(DOUBLE(asdecimal=True))  # 支付的各项税费
    CASHFLOWSTATEMENT_29 = Column(DOUBLE(asdecimal=True))  # 支付其他与经营活动有关的现金
    CASHFLOWSTATEMENT_34 = Column(DOUBLE(asdecimal=True))  # 经营活动现金流出其他项目
    CASHFLOWSTATEMENT_35 = Column(DOUBLE(asdecimal=True))  # 经营活动现金流出平衡项目
    CASHFLOWSTATEMENT_37 = Column(DOUBLE(asdecimal=True))  # 经营活动现金流出小计
    CASHFLOWSTATEMENT_121 = Column(DOUBLE(asdecimal=True))  # 经营活动产生的现金流量净额其他项目
    CASHFLOWSTATEMENT_38 = Column(DOUBLE(asdecimal=True))  # 经营活动产生的现金流量净额平衡项目
    CASHFLOWSTATEMENT_39 = Column(DOUBLE(asdecimal=True))  # 经营活动产生的现金流量净额
    # 投资活动产生的现金流量部分
    CASHFLOWSTATEMENT_40 = Column(DOUBLE(asdecimal=True))  # 收回投资收到的现金
    CASHFLOWSTATEMENT_41 = Column(DOUBLE(asdecimal=True))  # 取得投资收益收到的现金
    CASHFLOWSTATEMENT_42 = Column(DOUBLE(asdecimal=True))  # 处置固定资产、无形资产和其他长期资产收回的现金净额
    CASHFLOWSTATEMENT_43 = Column(DOUBLE(asdecimal=True))  # 处置子公司及其他营业单位收到的现金净额
    CASHFLOWSTATEMENT_232 = Column(DOUBLE(asdecimal=True))  # 减少质押和定期存款所收到的现金
    CASHFLOWSTATEMENT_44 = Column(DOUBLE(asdecimal=True))  # 收到其他与投资活动有关的现金
    CASHFLOWSTATEMENT_45 = Column(DOUBLE(asdecimal=True))  # 投资活动现金流入其他项目
    CASHFLOWSTATEMENT_46 = Column(DOUBLE(asdecimal=True))  # 投资活动现金流入平衡项目
    CASHFLOWSTATEMENT_48 = Column(DOUBLE(asdecimal=True))  # 投资活动现金流入小计
    CASHFLOWSTATEMENT_49 = Column(DOUBLE(asdecimal=True))  # 购建固定资产、无形资产和其他长期资产支付的现金
    CASHFLOWSTATEMENT_50 = Column(DOUBLE(asdecimal=True))  # 投资支付的现金
    CASHFLOWSTATEMENT_53 = Column(DOUBLE(asdecimal=True))  # 质押贷款净增加额
    CASHFLOWSTATEMENT_51 = Column(DOUBLE(asdecimal=True))  # 取得子公司及其他营业单位支付的现金净额
    CASHFLOWSTATEMENT_233 = Column(DOUBLE(asdecimal=True))  # 增加质押和定期存款所支付的现金
    CASHFLOWSTATEMENT_52 = Column(DOUBLE(asdecimal=True))  # 支付其他与投资活动有关的现金
    CASHFLOWSTATEMENT_54 = Column(DOUBLE(asdecimal=True))  # 投资活动现金流出其他项目
    CASHFLOWSTATEMENT_55 = Column(DOUBLE(asdecimal=True))  # 投资活动现金流出平衡项目
    CASHFLOWSTATEMENT_57 = Column(DOUBLE(asdecimal=True))  # 投资活动现金流出小计
    CASHFLOWSTATEMENT_122 = Column(DOUBLE(asdecimal=True))  # 投资活动产生的现金流量净额其他项目
    CASHFLOWSTATEMENT_58 = Column(DOUBLE(asdecimal=True))  # 投资活动产生的现金流量净额平衡项目
    CASHFLOWSTATEMENT_59 = Column(DOUBLE(asdecimal=True))  # 投资活动产生的现金流量净额
    # 筹资活动产生的现金流量部分
    CASHFLOWSTATEMENT_60 = Column(DOUBLE(asdecimal=True))  # 吸收投资收到的现金
    CASHFLOWSTATEMENT_118 = Column(DOUBLE(asdecimal=True))  # 其中:子公司吸收少数股东投资收到的现金
    CASHFLOWSTATEMENT_61 = Column(DOUBLE(asdecimal=True))  # 取得借款收到的现金
    CASHFLOWSTATEMENT_63 = Column(DOUBLE(asdecimal=True))  # 发行债券收到的现金
    CASHFLOWSTATEMENT_62 = Column(DOUBLE(asdecimal=True))  # 收到其他与筹资活动有关的现金
    CASHFLOWSTATEMENT_65 = Column(DOUBLE(asdecimal=True))  # 筹资活动现金流入其他项目
    CASHFLOWSTATEMENT_66 = Column(DOUBLE(asdecimal=True))  # 筹资活动现金流入平衡项目
    CASHFLOWSTATEMENT_68 = Column(DOUBLE(asdecimal=True))  # 筹资活动现金流入小计
    CASHFLOWSTATEMENT_69 = Column(DOUBLE(asdecimal=True))  # 偿还债务支付的现金
    CASHFLOWSTATEMENT_70 = Column(DOUBLE(asdecimal=True))  # 分配股利、利润或偿付利息支付的现金
    CASHFLOWSTATEMENT_119 = Column(DOUBLE(asdecimal=True))  # 其中:子公司支付给少数股东的股利、利润
    CASHFLOWSTATEMENT_123 = Column(DOUBLE(asdecimal=True))  # 购买子公司少数股权而支付的现金
    CASHFLOWSTATEMENT_71 = Column(DOUBLE(asdecimal=True))  # 支付其他与筹资活动有关的现金
    CASHFLOWSTATEMENT_124 = Column(DOUBLE(asdecimal=True))  # 其中:子公司减资支付给少数股东的现金
    CASHFLOWSTATEMENT_72 = Column(DOUBLE(asdecimal=True))  # 筹资活动现金流出其他项目
    CASHFLOWSTATEMENT_73 = Column(DOUBLE(asdecimal=True))  # 筹资活动现金流出平衡项目
    CASHFLOWSTATEMENT_75 = Column(DOUBLE(asdecimal=True))  # 筹资活动现金流出小计
    CASHFLOWSTATEMENT_125 = Column(DOUBLE(asdecimal=True))  # 筹资活动产生的现金流量净额其他项目
    CASHFLOWSTATEMENT_76 = Column(DOUBLE(asdecimal=True))  # 筹资活动产生的现金流量净额平衡项目
    CASHFLOWSTATEMENT_77 = Column(DOUBLE(asdecimal=True))  # 筹资活动产生的现金流量净额
    # 现金及现金等价物净增加
    CASHFLOWSTATEMENT_78 = Column(DOUBLE(asdecimal=True))  # 汇率变动对现金及现金等价物的影响
    CASHFLOWSTATEMENT_79 = Column(DOUBLE(asdecimal=True))  # 现金及现金等价物净增加额其他项目
    CASHFLOWSTATEMENT_80 = Column(DOUBLE(asdecimal=True))  # 现金及现金等价物净增加额平衡项目
    CASHFLOWSTATEMENT_82 = Column(DOUBLE(asdecimal=True))  # 现金及现金等价物净增加额
    CASHFLOWSTATEMENT_83 = Column(DOUBLE(asdecimal=True))  # 期初现金及现金等价物余额
    CASHFLOWSTATEMENT_126 = Column(DOUBLE(asdecimal=True))  # 期末现金及现金等价物余额其他项目
    CASHFLOWSTATEMENT_127 = Column(DOUBLE(asdecimal=True))  # 期末现金及现金等价物余额平衡项目
    CASHFLOWSTATEMENT_84 = Column(DOUBLE(asdecimal=True))  # 期末现金及现金等价物余额
    # 补充资料
    CASHFLOWSTATEMENT_85 = Column(DOUBLE(asdecimal=True))  # 净利润-现金流量表
    CASHFLOWSTATEMENT_86 = Column(DOUBLE(asdecimal=True))  # 资产减值准备
    CASHFLOWSTATEMENT_206 = Column(DOUBLE(asdecimal=True))  # 固定资产和投资性房地产折旧
    CASHFLOWSTATEMENT_87 = Column(DOUBLE(asdecimal=True))  # 其中：固定资产折旧、油气资产折耗、生产性生物资产折旧
    CASHFLOWSTATEMENT_207 = Column(DOUBLE(asdecimal=True))  # 其中：投资性房地产折旧
    CASHFLOWSTATEMENT_88 = Column(DOUBLE(asdecimal=True))  # 无形资产摊销
    CASHFLOWSTATEMENT_89 = Column(DOUBLE(asdecimal=True))  # 长期待摊费用摊销
    CASHFLOWSTATEMENT_208 = Column(DOUBLE(asdecimal=True))  # 递延收益摊销
    CASHFLOWSTATEMENT_90 = Column(DOUBLE(asdecimal=True))  # 待摊费用的减少
    CASHFLOWSTATEMENT_91 = Column(DOUBLE(asdecimal=True))  # 预提费用的增加
    CASHFLOWSTATEMENT_92 = Column(DOUBLE(asdecimal=True))  # 处置固定资产、无形资产和其他长期资产的损失
    CASHFLOWSTATEMENT_93 = Column(DOUBLE(asdecimal=True))  # 固定资产报废损失
    CASHFLOWSTATEMENT_94 = Column(DOUBLE(asdecimal=True))  # 公允价值变动损失
    CASHFLOWSTATEMENT_95 = Column(DOUBLE(asdecimal=True))  # 财务费用
    CASHFLOWSTATEMENT_96 = Column(DOUBLE(asdecimal=True))  # 投资损失
    CASHFLOWSTATEMENT_209 = Column(DOUBLE(asdecimal=True))  # 递延所得税
    CASHFLOWSTATEMENT_97 = Column(DOUBLE(asdecimal=True))  # 其中：递延所得税资产减少
    CASHFLOWSTATEMENT_98 = Column(DOUBLE(asdecimal=True))  # 其中：递延所得税负债增加
    CASHFLOWSTATEMENT_210 = Column(DOUBLE(asdecimal=True))  # 预计负债的增加
    CASHFLOWSTATEMENT_99 = Column(DOUBLE(asdecimal=True))  # 存货的减少
    CASHFLOWSTATEMENT_100 = Column(DOUBLE(asdecimal=True))  # 经营性应收项目的减少
    CASHFLOWSTATEMENT_101 = Column(DOUBLE(asdecimal=True))  # 经营性应付项目的增加
    CASHFLOWSTATEMENT_117 = Column(DOUBLE(asdecimal=True))  # 其他
    CASHFLOWSTATEMENT_102 = Column(DOUBLE(asdecimal=True))  # 经营活动产生的现金流量净额其他项目
    CASHFLOWSTATEMENT_103 = Column(DOUBLE(asdecimal=True))  # 经营活动产生的现金流量净额平衡项目
    CASHFLOWSTATEMENT_105 = Column(DOUBLE(asdecimal=True))  # 间接法—经营活动产生的现金流量净额
    CASHFLOWSTATEMENT_106 = Column(DOUBLE(asdecimal=True))  # 债务转为资本
    CASHFLOWSTATEMENT_107 = Column(DOUBLE(asdecimal=True))  # 一年内到期的可转换公司债券
    CASHFLOWSTATEMENT_108 = Column(DOUBLE(asdecimal=True))  # 融资租入固定资产
    CASHFLOWSTATEMENT_212 = Column(DOUBLE(asdecimal=True))  # 不涉及现金收支的投资和筹资活动金额其他项目
    CASHFLOWSTATEMENT_109 = Column(DOUBLE(asdecimal=True))  # 现金的期末余额
    CASHFLOWSTATEMENT_110 = Column(DOUBLE(asdecimal=True))  # 现金的期初余额
    CASHFLOWSTATEMENT_111 = Column(DOUBLE(asdecimal=True))  # 现金等价物的期末余额
    CASHFLOWSTATEMENT_112 = Column(DOUBLE(asdecimal=True))  # 现金等价物的期初余额
    CASHFLOWSTATEMENT_113 = Column(DOUBLE(asdecimal=True))  # 现金及现金等价物净增加额其他项目
    CASHFLOWSTATEMENT_114 = Column(DOUBLE(asdecimal=True))  # 现金及现金等价物净增加额平衡项目
    CASHFLOWSTATEMENT_116 = Column(DOUBLE(asdecimal=True))  # 间接法—现金及现金等价物的净增加额
    CASHFLOWSTATEMENT_243 = Column(DOUBLE(asdecimal=True))  # 信用减值损失

    __table_args__ = (
        Index('idx_em_stock_fs_cashflow_statement_datetime', 'DATES'),
    )


class EmStockFSIncomeStatementQ(Base):
    '''Choice股票利润表(单季度)'''

    __tablename__ = 'em_stock_fs_income_statement_q'

    CODES = Column(CHAR(10), primary_key=True)  # EM股票ID
    DATES = Column(DATE, primary_key=True)  # 财报日期
    INCOMESTATEMENTQ_83 = Column(DOUBLE(asdecimal=True))  # 单季度.营业总收入
    INCOMESTATEMENTQ_9 = Column(DOUBLE(asdecimal=True))  # 单季度.营业收入
    INCOMESTATEMENTQ_19 = Column(DOUBLE(asdecimal=True))  # 单季度.利息收入
    INCOMESTATEMENTQ_28 = Column(DOUBLE(asdecimal=True))  # 单季度.已赚保费
    INCOMESTATEMENTQ_22 = Column(DOUBLE(asdecimal=True))  # 单季度.手续费及佣金收入
    INCOMESTATEMENTQ_85 = Column(DOUBLE(asdecimal=True))  # 单季度.其他业务收入
    INCOMESTATEMENTQ_88 = Column(DOUBLE(asdecimal=True))  # 单季度.营业总收入其他项目
    INCOMESTATEMENTQ_84 = Column(DOUBLE(asdecimal=True))  # 单季度.营业总成本
    INCOMESTATEMENTQ_10 = Column(DOUBLE(asdecimal=True))  # 单季度.营业成本
    INCOMESTATEMENTQ_20 = Column(DOUBLE(asdecimal=True))  # 单季度.利息支出
    INCOMESTATEMENTQ_23 = Column(DOUBLE(asdecimal=True))  # 单季度.手续费及佣金支出
    INCOMESTATEMENTQ_89 = Column(DOUBLE(asdecimal=True))  # 单季度.研发费用
    INCOMESTATEMENTQ_39 = Column(DOUBLE(asdecimal=True))  # 单季度.退保金
    INCOMESTATEMENTQ_33 = Column(DOUBLE(asdecimal=True))  # 单季度.赔付支出净额
    INCOMESTATEMENTQ_35 = Column(DOUBLE(asdecimal=True))  # 单季度.提取保险合同准备金净额
    INCOMESTATEMENTQ_40 = Column(DOUBLE(asdecimal=True))  # 单季度.保单红利支出
    INCOMESTATEMENTQ_38 = Column(DOUBLE(asdecimal=True))  # 单季度.分保费用
    INCOMESTATEMENTQ_86 = Column(DOUBLE(asdecimal=True))  # 单季度.其他业务成本
    INCOMESTATEMENTQ_11 = Column(DOUBLE(asdecimal=True))  # 单季度.税金及附加
    INCOMESTATEMENTQ_12 = Column(DOUBLE(asdecimal=True))  # 单季度.销售费用
    INCOMESTATEMENTQ_13 = Column(DOUBLE(asdecimal=True))  # 单季度.管理费用
    INCOMESTATEMENTQ_14 = Column(DOUBLE(asdecimal=True))  # 单季度.财务费用
    INCOMESTATEMENTQ_127 = Column(DOUBLE(asdecimal=True))  # 单季度.其中:利息费用
    INCOMESTATEMENTQ_128 = Column(DOUBLE(asdecimal=True))  # 单季度.其中:利息收入
    INCOMESTATEMENTQ_15 = Column(DOUBLE(asdecimal=True))  # 单季度.资产减值损失
    INCOMESTATEMENTQ_129 = Column(DOUBLE(asdecimal=True))  # 单季度.信用减值损失
    INCOMESTATEMENTQ_90 = Column(DOUBLE(asdecimal=True))  # 单季度.营业总成本其他项目
    INCOMESTATEMENTQ_16 = Column(DOUBLE(asdecimal=True))  # 单季度.公允价值变动净收益
    INCOMESTATEMENTQ_17 = Column(DOUBLE(asdecimal=True))  # 单季度.投资净收益
    INCOMESTATEMENTQ_82 = Column(DOUBLE(asdecimal=True))  # 单季度.对联营企业和合营企业的投资收益
    INCOMESTATEMENTQ_130 = Column(DOUBLE(asdecimal=True))  # 单季度.净敞口套期收益
    INCOMESTATEMENTQ_25 = Column(DOUBLE(asdecimal=True))  # 单季度.汇兑收益
    INCOMESTATEMENTQ_123 = Column(DOUBLE(asdecimal=True))  # 单季度.资产处置收益
    INCOMESTATEMENTQ_124 = Column(DOUBLE(asdecimal=True))  # 单季度.其他收益
    INCOMESTATEMENTQ_45 = Column(DOUBLE(asdecimal=True))  # 单季度.营业利润其他项目
    INCOMESTATEMENTQ_46 = Column(DOUBLE(asdecimal=True))  # 单季度.营业利润平衡项目
    INCOMESTATEMENTQ_48 = Column(DOUBLE(asdecimal=True))  # 单季度.营业利润
    INCOMESTATEMENTQ_49 = Column(DOUBLE(asdecimal=True))  # 单季度.营业外收入
    INCOMESTATEMENTQ_118 = Column(DOUBLE(asdecimal=True))  # 单季度.非流动资产处置利得
    INCOMESTATEMENTQ_50 = Column(DOUBLE(asdecimal=True))  # 单季度.营业外支出
    INCOMESTATEMENTQ_51 = Column(DOUBLE(asdecimal=True))  # 单季度.非流动资产处置净损失
    INCOMESTATEMENTQ_52 = Column(DOUBLE(asdecimal=True))  # 单季度.影响利润总额的其他项目
    INCOMESTATEMENTQ_53 = Column(DOUBLE(asdecimal=True))  # 单季度.利润总额平衡项目
    INCOMESTATEMENTQ_55 = Column(DOUBLE(asdecimal=True))  # 单季度.利润总额
    INCOMESTATEMENTQ_56 = Column(DOUBLE(asdecimal=True))  # 单季度.所得税费用
    INCOMESTATEMENTQ_87 = Column(DOUBLE(asdecimal=True))  # 单季度.未确认的投资损失
    INCOMESTATEMENTQ_57 = Column(DOUBLE(asdecimal=True))  # 单季度.影响净利润的其他项目
    INCOMESTATEMENTQ_120 = Column(DOUBLE(asdecimal=True))  # 单季度.净利润差额(合计平衡项目2)
    INCOMESTATEMENTQ_60 = Column(DOUBLE(asdecimal=True))  # 单季度.净利润
    INCOMESTATEMENTQ_125 = Column(DOUBLE(asdecimal=True))  # 单季度.持续经营净利润
    INCOMESTATEMENTQ_126 = Column(DOUBLE(asdecimal=True))  # 单季度.终止经营净利润
    INCOMESTATEMENTQ_91 = Column(DOUBLE(asdecimal=True))  # 单季度.被合并方在合并前实现利润
    INCOMESTATEMENTQ_61 = Column(DOUBLE(asdecimal=True))  # 单季度.归属母公司股东的净利润
    INCOMESTATEMENTQ_62 = Column(DOUBLE(asdecimal=True))  # 单季度.少数股东损益
    INCOMESTATEMENTQ_92 = Column(DOUBLE(asdecimal=True))  # 单季度.净利润其他项目
    INCOMESTATEMENTQ_80 = Column(DOUBLE(asdecimal=True))  # 单季度.基本每股收益
    INCOMESTATEMENTQ_81 = Column(DOUBLE(asdecimal=True))  # 单季度.稀释每股收益
    INCOMESTATEMENTQ_114 = Column(DOUBLE(asdecimal=True))  # 单季度.其他综合收益
    INCOMESTATEMENTQ_116 = Column(DOUBLE(asdecimal=True))  # 单季度.归属于母公司股东的其他综合收益
    INCOMESTATEMENTQ_115 = Column(DOUBLE(asdecimal=True))  # 单季度.归属于少数股东的其他综合收益总额
    INCOMESTATEMENTQ_113 = Column(DOUBLE(asdecimal=True))  # 单季度.综合收益总额
    INCOMESTATEMENTQ_93 = Column(DOUBLE(asdecimal=True))  # 单季度.归属于母公司所有者的综合收益总额
    INCOMESTATEMENTQ_94 = Column(DOUBLE(asdecimal=True))  # 单季度.归属于少数股东的综合收益总额
    INCOMESTATEMENTQ_182 = Column(DOUBLE(asdecimal=True))  # 单季度.信用减值损失(新)
    INCOMESTATEMENTQ_180 = Column(DOUBLE(asdecimal=True))  # 单季度.资产减值损失(新)

    __table_args__ = (
        Index('idx_em_stock_fs_income_statement_q_datetime', 'DATES'),
    )

class EmStockFSCashflowStatementQ(Base):
    '''Choice股票现金流量表(单季度)'''

    __tablename__ = 'em_stock_fs_cashflow_statement_q'

    CODES = Column(CHAR(10), primary_key=True)  # EM股票ID
    DATES = Column(DATE, primary_key=True)  # 财报日期
    # 经营活动产生的现金流量
    CASHFLOWSTATEMENTQ_9 = Column(DOUBLE(asdecimal=True))  # 单季度.销售商品、提供劳务收到的现金
    CASHFLOWSTATEMENTQ_12 = Column(DOUBLE(asdecimal=True))  # 单季度.客户存款和同业存放款项净增加额
    CASHFLOWSTATEMENTQ_13 = Column(DOUBLE(asdecimal=True))  # 单季度.向中央银行借款净增加额
    CASHFLOWSTATEMENTQ_14 = Column(DOUBLE(asdecimal=True))  # 单季度.向其他金融机构拆入资金净增加额
    CASHFLOWSTATEMENTQ_16 = Column(DOUBLE(asdecimal=True))  # 单季度.收到原保险合同保费取得的现金
    CASHFLOWSTATEMENTQ_17 = Column(DOUBLE(asdecimal=True))  # 单季度.收到再保险业务现金净额
    CASHFLOWSTATEMENTQ_64 = Column(DOUBLE(asdecimal=True))  # 单季度.保户储金及投资款净增加额
    CASHFLOWSTATEMENTQ_18 = Column(DOUBLE(asdecimal=True))  # 单季度.处置交易性金融资产净增加额
    CASHFLOWSTATEMENTQ_186 = Column(DOUBLE(asdecimal=True))  # 单季度.收取利息、手续费及佣金的现金
    CASHFLOWSTATEMENTQ_20 = Column(DOUBLE(asdecimal=True))  # 单季度.拆入资金净增加额
    CASHFLOWSTATEMENTQ_120 = Column(DOUBLE(asdecimal=True))  # 单季度.发放贷款及垫款的净减少额
    CASHFLOWSTATEMENTQ_21 = Column(DOUBLE(asdecimal=True))  # 单季度.回购业务资金净增加额
    CASHFLOWSTATEMENTQ_10 = Column(DOUBLE(asdecimal=True))  # 单季度.收到的税费返还
    CASHFLOWSTATEMENTQ_11 = Column(DOUBLE(asdecimal=True))  # 单季度.收到的其他与经营活动有关的现金
    CASHFLOWSTATEMENTQ_22 = Column(DOUBLE(asdecimal=True))  # 单季度.经营活动现金流入其他项目
    CASHFLOWSTATEMENTQ_23 = Column(DOUBLE(asdecimal=True))  # 单季度.经营活动现金流入平衡项目
    CASHFLOWSTATEMENTQ_25 = Column(DOUBLE(asdecimal=True))  # 单季度.经营活动现金流入小计
    CASHFLOWSTATEMENTQ_26 = Column(DOUBLE(asdecimal=True))  # 单季度.购买商品、接受劳务支付的现金
    CASHFLOWSTATEMENTQ_30 = Column(DOUBLE(asdecimal=True))  # 单季度.客户贷款及垫款净增加额
    CASHFLOWSTATEMENTQ_31 = Column(DOUBLE(asdecimal=True))  # 单季度.存放中央银行和同业款项净增加额
    CASHFLOWSTATEMENTQ_32 = Column(DOUBLE(asdecimal=True))  # 单季度.支付原保险合同赔付款项的现金
    CASHFLOWSTATEMENTQ_33 = Column(DOUBLE(asdecimal=True))  # 单季度.支付利息、手续费及佣金的现金
    CASHFLOWSTATEMENTQ_195 = Column(DOUBLE(asdecimal=True))  # 单季度.支付保单红利的现金
    CASHFLOWSTATEMENTQ_27 = Column(DOUBLE(asdecimal=True))  # 单季度.支付给职工以及为职工支付的现金
    CASHFLOWSTATEMENTQ_28 = Column(DOUBLE(asdecimal=True))  # 单季度.支付的各项税费
    CASHFLOWSTATEMENTQ_29 = Column(DOUBLE(asdecimal=True))  # 单季度.支付的其他与经营活动有关的现金
    CASHFLOWSTATEMENTQ_34 = Column(DOUBLE(asdecimal=True))  # 单季度.经营活动现金流出其他项目
    CASHFLOWSTATEMENTQ_35 = Column(DOUBLE(asdecimal=True))  # 单季度.经营活动现金流出平衡项目
    CASHFLOWSTATEMENTQ_37 = Column(DOUBLE(asdecimal=True))  # 单季度.经营活动现金流出小计
    CASHFLOWSTATEMENTQ_121 = Column(DOUBLE(asdecimal=True))  # 单季度.经营活动产生的现金流量净额其他项目
    CASHFLOWSTATEMENTQ_38 = Column(DOUBLE(asdecimal=True))  # 单季度.经营活动产生的现金流量净额平衡项目
    CASHFLOWSTATEMENTQ_39 = Column(DOUBLE(asdecimal=True))  # 单季度.经营活动产生的现金流量净额
    CASHFLOWSTATEMENTQ_192 = Column(DOUBLE(asdecimal=True))  # 银行业务及证券业务拆借资金净减少额
    # 投资活动产生的现金流量
    CASHFLOWSTATEMENTQ_40 = Column(DOUBLE(asdecimal=True))  # 单季度.收回投资收到的现金
    CASHFLOWSTATEMENTQ_41 = Column(DOUBLE(asdecimal=True))  # 单季度.取得投资收益收到的现金
    CASHFLOWSTATEMENTQ_42 = Column(DOUBLE(asdecimal=True))  # 单季度.处置固定资产、无形资产和其他长期资产所收回的现金净额
    CASHFLOWSTATEMENTQ_43 = Column(DOUBLE(asdecimal=True))  # 单季度.处置子公司及其他营业单位收到的现金净额
    CASHFLOWSTATEMENTQ_232 = Column(DOUBLE(asdecimal=True))  # 单季度.减少质押和定期存款所收到的现金
    CASHFLOWSTATEMENTQ_44 = Column(DOUBLE(asdecimal=True))  # 单季度.收到的其他与投资活动有关的现金
    CASHFLOWSTATEMENTQ_45 = Column(DOUBLE(asdecimal=True))  # 单季度.投资活动现金流入其他项目
    CASHFLOWSTATEMENTQ_46 = Column(DOUBLE(asdecimal=True))  # 单季度.投资活动现金流入平衡项目
    CASHFLOWSTATEMENTQ_48 = Column(DOUBLE(asdecimal=True))  # 单季度.投资活动现金流入小计
    CASHFLOWSTATEMENTQ_49 = Column(DOUBLE(asdecimal=True))  # 单季度.购建固定资产、无形资产和其他长期资产所支付的现金
    CASHFLOWSTATEMENTQ_50 = Column(DOUBLE(asdecimal=True))  # 单季度.投资所支付的现金
    CASHFLOWSTATEMENTQ_53 = Column(DOUBLE(asdecimal=True))  # 单季度.质押贷款净增加额
    CASHFLOWSTATEMENTQ_51 = Column(DOUBLE(asdecimal=True))  # 单季度.取得子公司及其他营业单位支付的现金净额
    CASHFLOWSTATEMENTQ_233 = Column(DOUBLE(asdecimal=True))  # 单季度.增加质押和定期存款所支付的现金
    CASHFLOWSTATEMENTQ_52 = Column(DOUBLE(asdecimal=True))  # 单季度.支付的其他与投资活动有关的现金
    CASHFLOWSTATEMENTQ_54 = Column(DOUBLE(asdecimal=True))  # 单季度.投资活动现金流出其他项目
    CASHFLOWSTATEMENTQ_57 = Column(DOUBLE(asdecimal=True))  # 单季度.投资活动现金流出小计
    CASHFLOWSTATEMENTQ_55 = Column(DOUBLE(asdecimal=True))  # 单季度.投资活动现金流出平衡项目
    CASHFLOWSTATEMENTQ_122 = Column(DOUBLE(asdecimal=True))  # 单季度.投资活动产生的现金流量净额其他项目
    CASHFLOWSTATEMENTQ_59 = Column(DOUBLE(asdecimal=True))  # 单季度.投资活动产生的现金流量净额
    CASHFLOWSTATEMENTQ_58 = Column(DOUBLE(asdecimal=True))  # 单季度.投资活动产生的现金流量净额平衡项目
    # 筹资活动产生的现金流量
    CASHFLOWSTATEMENTQ_60 = Column(DOUBLE(asdecimal=True))  # 单季度.吸收投资收到的现金
    CASHFLOWSTATEMENTQ_118 = Column(DOUBLE(asdecimal=True))  # 单季度.子公司吸收少数股东投资收到的现金
    CASHFLOWSTATEMENTQ_61 = Column(DOUBLE(asdecimal=True))  # 单季度.取得借款收到的现金
    CASHFLOWSTATEMENTQ_63 = Column(DOUBLE(asdecimal=True))  # 单季度.发行债券收到的现金
    CASHFLOWSTATEMENTQ_62 = Column(DOUBLE(asdecimal=True))  # 单季度.收到其他与筹资活动有关的现金
    CASHFLOWSTATEMENTQ_65 = Column(DOUBLE(asdecimal=True))  # 单季度.筹资活动现金流入其他项目
    CASHFLOWSTATEMENTQ_66 = Column(DOUBLE(asdecimal=True))  # 单季度.筹资活动现金流入平衡项目
    CASHFLOWSTATEMENTQ_68 = Column(DOUBLE(asdecimal=True))  # 单季度.筹资活动现金流入小计
    CASHFLOWSTATEMENTQ_69 = Column(DOUBLE(asdecimal=True))  # 单季度.偿还债务支付的现金
    CASHFLOWSTATEMENTQ_70 = Column(DOUBLE(asdecimal=True))  # 单季度.分配股利、利润或偿付利息所支付的现金
    CASHFLOWSTATEMENTQ_119 = Column(DOUBLE(asdecimal=True))  # 单季度.子公司支付给少数股东的股利、利润
    CASHFLOWSTATEMENTQ_123 = Column(DOUBLE(asdecimal=True))  # 单季度.购买子公司少数股权而支付的现金
    CASHFLOWSTATEMENTQ_71 = Column(DOUBLE(asdecimal=True))  # 单季度.支付其他与筹资活动有关的现金
    CASHFLOWSTATEMENTQ_124 = Column(DOUBLE(asdecimal=True))  # 单季度.子公司减资支付给少数股东的现金
    CASHFLOWSTATEMENTQ_72 = Column(DOUBLE(asdecimal=True))  # 单季度.筹资活动现金流出其他项目
    CASHFLOWSTATEMENTQ_73 = Column(DOUBLE(asdecimal=True))  # 单季度.筹资活动现金流出平衡项目
    CASHFLOWSTATEMENTQ_75 = Column(DOUBLE(asdecimal=True))  # 单季度.筹资活动现金流出小计
    CASHFLOWSTATEMENTQ_125 = Column(DOUBLE(asdecimal=True))  # 单季度.筹资活动产生的现金流量净额其他项目
    CASHFLOWSTATEMENTQ_76 = Column(DOUBLE(asdecimal=True))  # 单季度.筹资活动产生的现金流量净额平衡项目
    CASHFLOWSTATEMENTQ_77 = Column(DOUBLE(asdecimal=True))  # 单季度.筹资活动产生的现金流量净额
    # 现金及现金等价物净增加值
    CASHFLOWSTATEMENTQ_78 = Column(DOUBLE(asdecimal=True))  # 单季度.汇率变动对现金及现金等价物的影响
    CASHFLOWSTATEMENTQ_79 = Column(DOUBLE(asdecimal=True))  # 单季度.现金及现金等价物净增加额其他项目
    CASHFLOWSTATEMENTQ_80 = Column(DOUBLE(asdecimal=True))  # 单季度.现金及现金等价物净增加额平衡项目
    CASHFLOWSTATEMENTQ_82 = Column(DOUBLE(asdecimal=True))  # 单季度.现金及现金等价物净增加额
    CASHFLOWSTATEMENTQ_83 = Column(DOUBLE(asdecimal=True))  # 单季度.期初现金及现金等价物余额
    CASHFLOWSTATEMENTQ_126 = Column(DOUBLE(asdecimal=True))  # 单季度.期末现金及现金等价物余额其他项目
    CASHFLOWSTATEMENTQ_127 = Column(DOUBLE(asdecimal=True))  # 单季度.期末现金及现金等价物余额平衡项目
    CASHFLOWSTATEMENTQ_84 = Column(DOUBLE(asdecimal=True))  # 单季度.期末现金及现金等价物余额

    __table_args__ = (
        Index('idx_em_stock_fs_cashflow_statement_q_datetime', 'DATES'),
    )

class EmStockIndustrialCapital(Base):
    '''Choice产业资本流动数据'''

    __tablename__ = 'em_stock_industrial_capital'

    datetime = Column(DATE, primary_key=True)  # 日期
    period = Column(CHAR(1), primary_key=True)  # 时间周期(D/W/M/Y)
    inc_amt_all = Column(DOUBLE(asdecimal=False))  # 全市场增持金额
    inc_amt_gem = Column(DOUBLE(asdecimal=False))  # 创业板增持金额
    dec_amt_all = Column(DOUBLE(asdecimal=False))  # 全市场减持金额
    dec_amt_gem = Column(DOUBLE(asdecimal=False))  # 创业板减持金额

class EmStockIndustrialCapitalTradeDetail(Base):
    '''Choice产业资本二级市场交易明细'''

    __tablename__ = 'em_stock_industrial_capital_trade_detail'

    sec_code = Column(CHAR(10), primary_key=True)  # EM股票ID
    notice_date = Column(DATE, primary_key=True)  # 公告日期
    id = Column(Integer, primary_key=True, autoincrement=True)
    share_hd_type = Column(CHAR(2), nullable=False)  # 股东类型
    share_hd_name = Column(TEXT, nullable=False)  # 股东名称
    is_ctrl = Column(CHAR(1), nullable=False)  # 是否实际控制人
    position1 = Column(TEXT)  # 高管职务
    fx = Column(CHAR(2), nullable=False)  # 方向
    change_num = Column(DOUBLE(asdecimal=False), nullable=False)  # 变动_流通股数量(万股)
    bdsl_zltb = Column(DOUBLE(asdecimal=False))  # 变动_占流通股比例(%)
    tg_dzjy_ptzr = Column(DOUBLE(asdecimal=False))  # 变动_大宗交易转让(万股)
    bdh_cyltgsl = Column(DOUBLE(asdecimal=False))  # 变动后_持流通股数量(万股)
    bdh_cyltslzltgb = Column(DOUBLE(asdecimal=False))  # 变动后_占流通股比例(%)
    bdh_cgzs = Column(DOUBLE(asdecimal=False))  # 变动后_持股总数
    bdh_cgbl = Column(DOUBLE(asdecimal=False))  # 变动后_占总股本比例(%)
    jyp_jj = Column(DOUBLE(asdecimal=False))  # 成交均价(元)
    latest_price = Column(DOUBLE(asdecimal=False))  # 最新收盘价(元)
    dec_jypjj_rate = Column(DOUBLE(asdecimal=False))  # 最新价格交成交均价涨跌幅(%)
    bdqj_gpjj = Column(DOUBLE(asdecimal=False))  # 变动期间股票均价(元)
    bdbf_cksz = Column(DOUBLE(asdecimal=False))  # 变动部分参考市值(元)
    bd_qsrq = Column(DATE, nullable=False)  # 变动起始日期
    bd_jzrq = Column(DATE, nullable=False)  # 变动截止日期
    clb_remark = Column(TEXT)  # 说明
    publish_name_dc3 = Column(TEXT, nullable=False)  # 东财三级行业
    trade_type = Column(TEXT, nullable=False)  # 变动类型

class EmSHSZToHKStockConnect(Base):
    '''Choice沪深股通(即北向)活跃成交股'''

    __tablename__ = 'em_stock_to_hk_connect'

    datetime = Column(DATE, primary_key=True)  # 日期
    market = Column(CHAR(2), primary_key=True)  # 市场(SH/SZ)
    period = Column(CHAR(1), primary_key=True)  # 时间周期(D/W/M/Y)
    dec_rank = Column(SMALLINT, primary_key=True)  # 排名
    msecu_code = Column(CHAR(10), nullable=False)  # EM股票ID
    bmoney = Column(DOUBLE(asdecimal=False), nullable=False)  # 买入金额(万元)
    smoney = Column(DOUBLE(asdecimal=False), nullable=False)  # 卖出金额(万元)
    tval = Column(DOUBLE(asdecimal=False), nullable=False)  # 沪/深股通成交金额(万元)
    ztval = Column(DOUBLE(asdecimal=False), nullable=False)  # 总成交金额(万元)
    zsz = Column(DOUBLE(asdecimal=False), nullable=False)  # 总市值(亿元)
    cnt = Column(Integer, nullable=False)  # 累计上榜次数
    publish_name_dc3 = Column(TEXT, nullable=False)  # 东财行业

class EMNorthCapital(Base):
    '''Choice沪深股通(即北向)资金'''

    __tablename__ = 'em_north_capital'

    datetime = Column(DATE, primary_key=True)  # 日期
    sh_hk_sc = Column(DOUBLE(asdecimal=False), nullable=False)  # 港沪股通
    sz_hk_sc = Column(DOUBLE(asdecimal=False), nullable=False)  # 港深股通
    north_cap = Column(DOUBLE(asdecimal=False), nullable=False)  # 北上资金

class EMSouthCapital(Base):
    '''Choice沪深股通(即南向)资金'''

    __tablename__ = 'em_south_capital'

    datetime = Column(DATE, primary_key=True)  # 日期
    hk_sz_sc = Column(DOUBLE(asdecimal=False), nullable=False)  # 沪港股通
    hk_sh_sc = Column(DOUBLE(asdecimal=False), nullable=False)  # 深港股通
    south_cap = Column(DOUBLE(asdecimal=False), nullable=False)  # 北上资金


class EmStockResearchInfo(Base):
    '''Choice机构调研上市公司信息'''

    __tablename__ = 'em_stock_research_info'

    CODES = Column('em_id', CHAR(10), primary_key=True) # EM股票ID
    DATES = Column('datetime', DATE, primary_key=True)  # 日期
    RESERCHNUM = Column('research_num', DOUBLE(asdecimal=False), nullable=False)  # 接待量
    RESERCHINSTITUTENUM = Column('research_institute_num', DOUBLE(asdecimal=False))  # 机构来访接待量
    RESERCHOTHERNUM = Column('research_other_num', DOUBLE(asdecimal=False))  # 其他来访接待量
    RESERCHSECUNUM = Column('research_secu_num', DOUBLE(asdecimal=False))  # 证券公司调研家数
    RESERCHSECUNAME = Column('research_ecu_name', TEXT)  # 调研的证券公司
    RESERCHSECUFREQUENCY1 = Column('research_secu_freq1', DOUBLE(asdecimal=False))  # 证券公司调研频次


class EmStockYearly(Base):
    '''Choice股票年度数据'''

    __tablename__ = 'em_stock_yearly'

    CODES = Column('stock_id', CHAR(10), primary_key=True)  # EM股票ID
    year = Column(YEAR, primary_key=True)  # 年度
    DIVANNUACCUM = Column('div_annu_accum', DOUBLE(asdecimal=False))  # 年度累计分红


class EmIndustryInfo(Base):
    '''Choice行业信息表'''

    __tablename__ = 'em_industry_info'

    em_id = Column(CHAR(16), primary_key=True)  # EM ID
    ind_name = Column(TEXT, nullable=False)  # 行业名称
    ind_class_type = Column(Enum(IndClassType), nullable=False)  # 行业分类类型


class SuntimeReportEarningsAdjust(Base):
    '''朝阳永续报告盈利预测调整表'''

    __tablename__ = 'suntime_report_earnings_adjust'

    stock_code = Column('stock_id', CHAR(10), primary_key=True)  # 股票代码
    report_year = Column(YEAR, primary_key=True)  # 预测年度
    id = Column(Integer, primary_key=True, autoincrement=True)
    report_id = Column(Integer, nullable=False)  # 报告ID
    title = Column(TEXT) # 标题
    report_type = Column(SMALLINT, nullable=False)  # 报告类型
    organ_id = Column(Integer, nullable=False)  # 机构ID
    author = Column(TEXT)  # 研究员姓名
    current_create_date = Column(DATE, nullable=False)  # 本次预测日期
    previous_create_date = Column(DATE)  # 上次预测日期
    current_forecast_np = Column(DOUBLE(asdecimal=False))  # 本次预测净利润(归属母公司净利润)
    previous_forecast_np = Column(DOUBLE(asdecimal=False))  # 上次预测净利润(归属母公司净利润)
    np_adjust_rate = Column(DOUBLE(asdecimal=False))  # 预期净利润调整比率(归属母公司净利润)
    np_adjust_mark = Column(TINYINT)  # 预期净利润调整调整标记(归属母公司净利润)
    current_forecast_eps = Column(DOUBLE(asdecimal=False))  # 本次预测 EPS
    previous_forecast_eps = Column(DOUBLE(asdecimal=False))  # 上次预测 EPS
    eps_adjust_rate = Column(DOUBLE(asdecimal=False))  # EPS 调整比率
    is_capital_different = Column(TINYINT)  # 本次和上次预测股本是否有差异
    eps_adjust_mark = Column(TINYINT)  # EPS 调整标记


class SuntimeReportOrganInfo(Base):
    '''朝阳永续机构信息表'''

    __tablename__ = 'suntime_report_organ_info'

    organ_id = Column(Integer, primary_key=True)  # 机构ID
    organ_name = Column(TEXT, nullable=False)  # 机构简称
    py_organ_name = Column(TEXT, nullable=False)  # 机构拼音
    organ_type = Column(SMALLINT)  # 机构分类
    is_con_forecast_organ = Column(BOOLEAN, nullable=False)  # 是否一致预期选用机构
    is_over_50_reports = Column(BOOLEAN, nullable=False)  # 是否一年内撰写报告 50 篇以上
    is_hk_reports_organ = Column(BOOLEAN, nullable=False)  # 是否港股报告撰写机构

class OSFundInfo(Base):
    '''海外基金信息表'''

    __tablename__ = 'oversea_fund_info'

    codes = Column(CHAR(20), primary_key=True)  # 基金id
    desc_name = Column(TEXT)  # 基金名称
    company_name = Column(TEXT)  # 基金管理公司
    fund_type = Column(CHAR(30))  # 基金类型
    industry = Column(CHAR(20))  # 行业
    area = Column(CHAR(20))  # 地区
    latest_nav = Column(DOUBLE(asdecimal=False))  # 最新净值
    fund_series = Column(Integer)  # 基金系列
    is_new_fund = Column(BOOLEAN)  # 是否为新基金
    redeem_dates = Column(Integer)  # 赎回资金到账天数
    excg_out_t_delay = Column(Integer)  # 换出基金指示滞延时间
    excg_in_t_delay = Column(Integer)  # 换入基金指示滞延时间
    min_init_trade_amt = Column(Integer)  # 最低初始投资额
    min_ag_trade_amt = Column(Integer)  # 最低后续投资额
    min_redeem_type = Column(CHAR(10))  # 最小赎回类型
    min_redeem_vol = Column(Integer)  # 最小赎回数量
    min_pos_type = Column(CHAR(10))  # 最小持有类型
    min_pos_vol = Column(Integer)  # 最小持有数量
    purchase_period = Column(CHAR(128))  # 申购周期
    risk_level = Column(CHAR(5))  # 风险级别
    is_purchase = Column(BOOLEAN)  # 可供认购
    is_CSRC_approve = Column(BOOLEAN)  # 证监会是否认可
    yearly_fee = Column(DOUBLE(asdecimal=False))  # 年费
    purchase_process_freq = Column(CHAR(10))  # 申购处理频率
    money_type = Column(CHAR(10))  # 币种
    is_sup_exchg_fund = Column(BOOLEAN)  # 支持转换基金
    is_sup_same_series_fund = Column(BOOLEAN)  # 支持转换为同系列其他基金
    is_sup_same_series_exchg = Column(BOOLEAN)  # 支持同系列其他基金转换为本基金
    redeem_fee = Column(DOUBLE(asdecimal=False))  # 赎回费(%)
    redeem_method = Column(CHAR(10))  # 赎回方式
    is_derivatives = Column(BOOLEAN)  # 是否衍生产品
    divident_distbt_mtd = Column(CHAR(10))  # 股息分派方式
    divident_freq = Column(CHAR(15))  # 派息频率
    asset_type = Column(CHAR(64))  # 资产类别
    asset_code = Column(CHAR(32))  # 资产编号
    issue_date = Column(DATE)  # 发行日期
    issue_price = Column(DOUBLE(asdecimal=False))  # 发行价
    fund_size_biln = Column(DOUBLE(asdecimal=False))  # 基金规模（单位：百万）
    fund_size_calc_date = Column(DATE)  # 基金规模统计日期
    fund_size_money_type = Column(CHAR(10))  # 基金规模币种
    fee_rate = Column(DOUBLE(asdecimal=False))  # 费率
    fee_calc_date = Column(DATE)  # 费率统计日期
    is_compx_product = Column(BOOLEAN)  # 复杂产品
    isin_code = Column(CHAR(15)) # isin 代码
    manager = Column(CHAR(40)) # 基金经理名字
    style = Column(CHAR(10)) # 基金风格

class OSFundHoldAsset(Base):
    '''海外基金持仓资产类别权重'''

    __tablename__ = 'oversea_fund_hold_asset'

    codes = Column(CHAR(20), primary_key=True)  # 基金id
    report_date = Column(DATE, primary_key=True)  # 报告期日
    desc_name = Column(TEXT)  # 基金名称
    isin_code = Column(CHAR(15)) # isin 代码
    top_10_hold_weights = Column(DOUBLE(asdecimal=False))  # 前十大持仓占比（%）
    top_10_equity_w = Column(DOUBLE(asdecimal=False))  # 基金资产-股票占比(%)
    top_10_corp_bond_w = Column(DOUBLE(asdecimal=False))  # 基金资产-公司债占比(%)
    top_10_national_bond_w = Column(DOUBLE(asdecimal=False))  # 基金资产-国债占比(%)
    top_10_mtge_bond_w = Column(DOUBLE(asdecimal=False))  #基金资产-抵押债占比(%)
    top_10_pfd_w = Column(DOUBLE(asdecimal=False))  # 基金资产-优先股占比(%)
    top_10_district_bond_w = Column(DOUBLE(asdecimal=False))  # 基金资产-地方债占比(%)
    top_10_cash_w = Column(DOUBLE(asdecimal=False))  # 基金资产-现金与其他占比(%)
    
class OSFundHoldDistrict(Base):
    '''海外基金持仓资产地区权重'''

    __tablename__ = 'oversea_fund_hold_district'

    codes = Column(CHAR(20), primary_key=True)  # 基金id
    report_date = Column(DATE, primary_key=True)  # 报告期日
    desc_name = Column(TEXT)  # 基金名称
    isin_code = Column(CHAR(15)) # isin 代码
    north_america = Column(DOUBLE(asdecimal=False)) # 北美地区
    south_n_central_america = Column(DOUBLE(asdecimal=False)) # 中南美地区
    western_europe = Column(DOUBLE(asdecimal=False)) # 西欧地区
    asia_pacific = Column(DOUBLE(asdecimal=False)) # 亚太地区
    eastern_europe = Column(DOUBLE(asdecimal=False)) # 东欧地区
    central_asia = Column(DOUBLE(asdecimal=False)) # 中亚地区
    africa_n_middle_east = Column(DOUBLE(asdecimal=False)) # 非洲及中东

class OSFundHoldIndustry(Base):
    '''海外基金持仓行业权重''' 

    __tablename__ = 'oversea_fund_hold_industry'

    codes = Column(CHAR(20), primary_key=True)  # 基金id
    report_date = Column(DATE, primary_key=True)  # 报告期日
    desc_name = Column(TEXT)  # 基金名称
    isin_code = Column(CHAR(15)) # isin 代码
    asset_backed_securities = Column(DOUBLE(asdecimal=False)) # 资产抵押债券
    basic_materials = Column(DOUBLE(asdecimal=False)) # 基础材料
    communications = Column(DOUBLE(asdecimal=False)) # 电信服务
    consumer_cyclical = Column(DOUBLE(asdecimal=False)) # 周期性消费
    consumer_non_cylical = Column(DOUBLE(asdecimal=False)) # 非周期消费
    diversified = Column(DOUBLE(asdecimal=False)) # 多元
    energy = Column(DOUBLE(asdecimal=False)) # 能源
    financial = Column(DOUBLE(asdecimal=False)) # 金融服务
    government = Column(DOUBLE(asdecimal=False)) # 政府
    industrial = Column(DOUBLE(asdecimal=False)) # 工业
    mortgage_securities = Column(DOUBLE(asdecimal=False)) # 不动产抵押债券
    technology = Column(DOUBLE(asdecimal=False)) # 科技
    utilities = Column(DOUBLE(asdecimal=False)) # 公用事业
    funds = Column(DOUBLE(asdecimal=False)) # 基金

class OSFundHoldBondTerm(Base):
    '''海外基金持有债券期限分布'''

    __tablename__ = 'oversea_fund_hold_bond_term'

    codes = Column(CHAR(20), primary_key=True)  # 基金id
    report_date = Column(DATE, primary_key=True)  # 报告期日
    desc_name = Column(TEXT)  # 基金名称
    isin_code = Column(CHAR(15)) # isin 代码
    intermediate_term = Column(DOUBLE(asdecimal=False)) # 中长期 3-10年
    long_term = Column(DOUBLE(asdecimal=False)) # 长期 >10年
    short_term = Column(DOUBLE(asdecimal=False)) # 短期 1-3年
    
class OSFundHoldTop10Pos(Base):
    '''海外基金前十大持仓'''

    __tablename__ = 'oversea_fund_hold_top10_pos'

    codes = Column(CHAR(20), primary_key=True)  # 基金id
    report_date = Column(DATE, primary_key=True)  # 报告期日
    desc_name = Column(TEXT)  # 基金名称
    isin_code = Column(CHAR(15)) # isin 代码
    pos_1 = Column(CHAR(32)) # 持仓名1
    pos_2 = Column(CHAR(32)) # 持仓名2
    pos_3 = Column(CHAR(32)) # 持仓名3
    pos_4 = Column(CHAR(32)) # 持仓名4
    pos_5 = Column(CHAR(32)) # 持仓名5
    pos_6 = Column(CHAR(32)) # 持仓名6
    pos_7 = Column(CHAR(32)) # 持仓名7
    pos_8 = Column(CHAR(32)) # 持仓名8
    pos_9 = Column(CHAR(32)) # 持仓名9
    pos_10 = Column(CHAR(32)) # 持仓名10
    pos_1_w = Column(DOUBLE(asdecimal=False)) # 持仓权重1 
    pos_2_w = Column(DOUBLE(asdecimal=False)) # 持仓权重2
    pos_3_w = Column(DOUBLE(asdecimal=False)) # 持仓权重3 
    pos_4_w = Column(DOUBLE(asdecimal=False)) # 持仓权重4 
    pos_5_w = Column(DOUBLE(asdecimal=False)) # 持仓权重5 
    pos_6_w = Column(DOUBLE(asdecimal=False)) # 持仓权重6 
    pos_7_w = Column(DOUBLE(asdecimal=False)) # 持仓权重7 
    pos_8_w = Column(DOUBLE(asdecimal=False)) # 持仓权重8 
    pos_9_w = Column(DOUBLE(asdecimal=False)) # 持仓权重9 
    pos_10_w = Column(DOUBLE(asdecimal=False)) # 持仓权重10 

class OSFundBondHoldRate(Base):
    '''海外基金债券持仓等级分布'''

    __tablename__ = 'oversea_fund_bond_hold_rate'

    codes = Column(CHAR(20), primary_key=True)  # 基金id
    report_date = Column(DATE, primary_key=True)  # 报告期日
    desc_name = Column(TEXT)  # 基金名称
    isin_code = Column(CHAR(15)) # isin 代码
    a = Column(DOUBLE(asdecimal=False)) # a评级权重
    a_u = Column(DOUBLE(asdecimal=False)) # a+评级权重
    a_d = Column(DOUBLE(asdecimal=False)) # a-评级权重
    aa = Column(DOUBLE(asdecimal=False)) # aa评级权重
    aa_u = Column(DOUBLE(asdecimal=False)) # aa+评级权重
    aa_d = Column(DOUBLE(asdecimal=False)) # aa-评级权重
    aaa = Column(DOUBLE(asdecimal=False)) # aaa评级权重
    b = Column(DOUBLE(asdecimal=False)) # b评级权重
    b_u = Column(DOUBLE(asdecimal=False)) # b+评级权重
    b_d = Column(DOUBLE(asdecimal=False)) # b-评级权重
    bb = Column(DOUBLE(asdecimal=False)) # bb评级权重
    bb_u = Column(DOUBLE(asdecimal=False)) # bb+评级权重
    bb_d = Column(DOUBLE(asdecimal=False)) # bb-评级权重
    bbb = Column(DOUBLE(asdecimal=False)) # bbb评级权重
    bbb_u = Column(DOUBLE(asdecimal=False)) # bbb+评级权重
    bbb_d = Column(DOUBLE(asdecimal=False)) # bbb-评级权重
    cc_u = Column(DOUBLE(asdecimal=False)) # cc+评级权重
    ccc = Column(DOUBLE(asdecimal=False)) # ccc评级权重
    ccc_u = Column(DOUBLE(asdecimal=False)) # ccc+评级权重
    ccc_d = Column(DOUBLE(asdecimal=False)) # ccc-评级权重
    ddd_u = Column(DOUBLE(asdecimal=False)) # ddd+评级权重
    Na = Column(DOUBLE(asdecimal=False)) # N.A.
    NR = Column(DOUBLE(asdecimal=False)) # NR
    NullGroup = Column(DOUBLE(asdecimal=False)) # NullGroup
    cc = Column(DOUBLE(asdecimal=False)) # cc评级权重
    dd_u = Column(DOUBLE(asdecimal=False)) # dd+评级权重
    c_d = Column(DOUBLE(asdecimal=False)) # c-评级权重
    ddd = Column(DOUBLE(asdecimal=False)) # ddd评级权重
    c_u = Column(DOUBLE(asdecimal=False)) # c+评级权重
    cc_d = Column(DOUBLE(asdecimal=False)) # cc-评级权重
    c = Column(DOUBLE(asdecimal=False)) # c评级权重
    ddd_d = Column(DOUBLE(asdecimal=False)) # ddd_d评级权重
    dd = Column(DOUBLE(asdecimal=False)) # ddd_d评级权重

class OSFundBenchmark(Base):
    '''海外基金基准'''    

    __tablename__ = 'oversea_fund_benchmark'
    
    isin_code = Column(CHAR(15), primary_key=True) # 资产isin代码
    codes = Column(CHAR(20))  # 基金id
    desc_name = Column(CHAR(128)) # 基金名
    benchmark_1 = Column(CHAR(20)) # 基准1
    benchmark_2 = Column(CHAR(20)) # 基准2
    asset_type = Column(CHAR(32)) # 资产类别

class OSFundBenchmarks(Base):
    '''海外基金基准'''

    __tablename__ = 'oversea_fund_benchmarks'
    isin_code = Column(CHAR(15), primary_key=True) # 资产isin代码
    codes = Column(CHAR(20))  # 基金id
    desc_name = Column(CHAR(128)) # 基金名
    benchmark_1 = Column(CHAR(20)) # 基准1
    benchmark_2 = Column(CHAR(20)) # 基准2
    benchmark_3 = Column(CHAR(20)) # 基准3
    benchmark_ms = Column(CHAR(60)) # 基准晨星
    industry_1 = Column(CHAR(30)) # 类型1
    industry_2 = Column(CHAR(30)) # 类型2
    area = Column(CHAR(30)) # 地域
    morning_star_group = Column(CHAR(60)) # 晨星类别
    benchmark_artificial = Column(CHAR(60)) # 人工基准
    benchmark_final_mix = Column(CHAR(60)) # 最后汇总基准含bloomberg和晨星
    benchmark_final_bb_only = Column(CHAR(20)) # 最终基准bloomberg
    benchmark_final = Column(CHAR(20)) # 最终基准

class OSFundNav(Base):
    '''海外基金净值表'''

    __tablename__ = 'oversea_fund_nav'

    codes = Column(CHAR(20), primary_key=True)  # 基金id
    datetime = Column(DATE, primary_key=True) # 日期
    nav = Column(DOUBLE(asdecimal=False)) # 净值

class OSFundNavAdj(Base):
    '''海外基金后复权净值'''

    __tablename__ = 'oversea_fund_nav_adj'

    codes = Column(CHAR(20), primary_key=True)  # 基金id
    datetime = Column(DATE, primary_key=True) # 日期
    nav = Column(DOUBLE(asdecimal=False)) # 后复权净值

class OSFundNavTmp(Base):
    '''海外基金更新部分'''

    __tablename__ = 'ifast_nav'

    product_id = Column(CHAR(20), primary_key=True)  # 基金id
    nav_date = Column(DATE, primary_key=True) # 日期
    nav_price = Column(DOUBLE(asdecimal=False)) # 净值

class OSFundNAVDivFactor(Base):
    '''海外基金分红数据表'''

    __tablename__ = 'oversea_fund_nav_div_factor_ifast'

    product_id = Column(VARCHAR(20), primary_key=True)  # 基金id
    ex_date = Column(DATE, primary_key=True) # 分红日期
    single_factor = Column(DECIMAL(12, 8)) # 当日复权因子
    factor = Column(DECIMAL(12, 8)) # 复权因子
    dividend_rate = Column(DECIMAL(10, 7)) # 分红比例

class OSFundRet(Base):
    '''海外基金涨跌幅'''

    __tablename__ = 'oversea_fund_ret'

    codes = Column(CHAR(20), primary_key=True)  # 基金id
    datetime = Column(DATE, primary_key=True) # 日期
    ret = Column(DOUBLE(asdecimal=False)) # 日涨跌幅
    
    
class OSIndexPrice(Base):
    '''海外指数日线'''

    __tablename__ = 'oversea_index_price'

    codes = Column(CHAR(20), primary_key=True)  # 指数id
    datetime = Column(DATE, primary_key=True) # 日期
    close = Column(DOUBLE(asdecimal=False)) # 净值

class OSDistrictInfo(Base):
    '''海外国家地区信息'''

    __tablename__ = 'oversea_district_info'
    codes = Column(CHAR(5), primary_key=True)  # 地区id
    district_name_e = Column(CHAR(32)) # 地区英文名
    district_name_c = Column(CHAR(64)) # 地区中文名 

class OSStockInfo(Base):
    '''海外股票信息'''

    __tablename__ = 'oversea_stock_info'

    codes = Column(CHAR(20), primary_key=True)  # 全球股票代码
    stock_name_e = Column(CHAR(36)) # 股票英文名
    stock_name_c = Column(TEXT) # 股票中文名
    asset_type = Column(CHAR(8)) # 资产类别
    industry = Column(CHAR(32)) # 行业
    district_code = Column(CHAR(5)) # 地区代码

class OSIndexInfo(Base):
    '''海外指数名'''

    __tablename__ = 'oversea_index_info'

    index_id = Column(CHAR(30), primary_key=True)  # 基金代码
    index_name = Column(CHAR(100)) # 指数名称

class OSCorpBondInfo(Base):
    '''海外公司和地方政府债券信息（非美国）'''

    __tablename__ = 'oversea_corp_bond_info'

    codes = Column(CHAR(20), primary_key=True)  # 债券代码
    bond_name_e = Column(CHAR(36)) # 债券英文名
    company_name_c = Column(CHAR(128)) # 债券公司中文名
    company_code = Column(CHAR(20)) # 债券对应上市公司代码
    district_name_e = Column(CHAR(20)) # 地区名
    industry_1 = Column(CHAR(32)) # 一级行业
    industry_2 = Column(CHAR(32)) # 二级行业
    industry_3 = Column(CHAR(32)) # 三级行业
    asset_type = Column(CHAR(5)) # 资产类别
    maturity = Column(DATE)  # 到期日
    md_rate = Column(CHAR(10)) # 穆迪评级
    sp_rate = Column(CHAR(10)) # 标普评级
    hy_rate = Column(CHAR(10)) # 惠誉评级
    isin_code = Column(CHAR(15)) # isin 代码
    total_amount = Column(BIGINT) # 发行金额
    
class OSMainIndexInfo(Base):
    '''海外主要资产指数'''

    __tablename__ = 'oversea_main_index_info'

    index_id = Column(CHAR(20), primary_key=True)  # 指数代码
    index_name = Column(CHAR(30), primary_key=True) # 资产地域范围
    asset_type = Column(CHAR(10)) # 资产种类
    index_full_name = Column(CHAR(90)) # 指数全名
    
class OSMorningStarIndexInfo(Base):
    '''海外晨星指数信息'''

    __tablename__ = 'oversea_morning_star_index_info'

    index_id = Column(CHAR(20), primary_key=True)  # 指数代码
    ms_index = Column(CHAR(40), primary_key=True)  # 晨星代码
    index_full_name = Column(CHAR(90)) # 指数全名

class OSGovtBondInfo(Base):
    '''海外美国政府债券信息'''

    __tablename__ = 'oversea_govt_bond_info'

    codes = Column(CHAR(20), primary_key=True)  # 债券代码
    bond_name_e = Column(CHAR(20)) # 债券英文名
    bond_name_c = Column(CHAR(36)) # 债券中文名
    district_name = Column(CHAR(20)) # 债券英文名
    asset_type = Column(CHAR(5)) # 资产类别
    maturity = Column(DATE)  # 到期日
    md_rate = Column(CHAR(5)) # 债券英文名
    hy_rate = Column(CHAR(5)) # 债券英文名
    isin_code = Column(CHAR(15)) # isin 代码
    total_amount = Column(DOUBLE(asdecimal=False)) # 发行金额

class OSMtgeBondInfo(Base):
    '''海外抵押债信息'''

    __tablename__ = 'oversea_mtge_bond_info'

    codes = Column(CHAR(20), primary_key=True) # 抵押债代码
    bond_name_e = Column(CHAR(20)) # 抵押债英文名
    asset_type = Column(CHAR(5)) # 资产类别
    mtge_type = Column(CHAR(36)) # 抵押债类别
    mtge_pay_start = Column(DATE) # 抵押债本金偿付期限开始日期
    mtge_pay_end = Column(DATE) # 抵押债本金偿付期限结束日期
    isin_code = Column(CHAR(20)) # isin 代码

class OSIndexFutureInfo(Base):
    '''海外股指期货信息'''

    __tablename__ = 'oversea_index_future_info'

    codes = Column(CHAR(20), primary_key=True) # 股指期货
    asset_name_c = Column(CHAR(40)) # 资产名
    asset_type = Column(CHAR(5)) # 资产类别
    maturity = Column(DATE) # 到期日

class OSMuniInfo(Base):
    '''海外市政债信息'''

    __tablename__ = 'oversea_muni_info'

    codes = Column(CHAR(20), primary_key=True) # 市政债代码
    asset_name_e = Column(CHAR(40)) # 资产名
    asset_type = Column(CHAR(5)) # 资产类别
    industry = Column(CHAR(20)) # 行业
    isin_code = Column(CHAR(20)) # isin 代码

class OSPfdInfo(Base):
    '''海外优先股信息'''

    __tablename__ = 'oversea_pfd_info'

    codes = Column(CHAR(20), primary_key=True) # 优先股代码
    asset_name_e = Column(CHAR(40)) # 资产名
    asset_type = Column(CHAR(5)) # 资产类别
    industry = Column(CHAR(64)) # 行业
    maturity = Column(DATE) # 到期日
    maturity_type = Column(CHAR(20)) # 到期类型
    isin_code = Column(CHAR(20)) # isin 代码

class OSComdtyInfo(Base):
    '''海外商品期货信息'''

    __tablename__ = 'oversea_comdty_info'

    codes = Column(CHAR(20), primary_key=True) # 商品期货代码
    asset_name_e = Column(CHAR(40)) # 资产名
    asset_type = Column(CHAR(8)) # 资产类别
    future_type = Column(CHAR(32)) # 期货类别
    maturity = Column(DATE) # 到期日

class EmConvBondInfo(Base):

    __tablename__ = 'em_conv_bond_info'

    CODES = Column(CHAR(20), primary_key=True)  # 债券代码
    DATES = Column(DATE, primary_key=True) # 表信息日期
    CBCODE = Column(CHAR(20))  # 债券代码简写
    CBNAME = Column(CHAR(30))  # 可转债名称
    CBSTOCKNAME = Column(CHAR(30))  # 可转债对应股票名
    CBSTOCKCODE = Column(CHAR(20))  # 对应股票id

class EmStockIpoInfo(Base):

    __tablename__ = 'em_stock_ipo_info'

    CODES = Column(CHAR(20), primary_key=True)  #股票代码
    IPOPRICE = Column(DOUBLE(asdecimal=False))  #首发价格
    IPOISSUEDATE = Column(DATE) #首发发行日期
    IPOSHARESVOL = Column(DOUBLE(asdecimal=False)) #首发数量
    IPOPE = Column(DOUBLE(asdecimal=False)) #首发市盈率
    NAME = Column(CHAR(64)) #股票简称
    SUCRATIOONL = Column(DOUBLE(asdecimal=False)) #网上申购中签率
    PURCHACODEONL = Column(CHAR(20)) #网上申购代码
    CEILINGONL = Column(DOUBLE(asdecimal=False)) #网上申购上限
    EMIND2016 = Column(CHAR(64)) #东财行业
    TRADEMARKET = Column(CHAR(128)) #上市板块
    IPOPURCHDATEONL = Column(DATE) #网上申购日
    IPOANNCDATE = Column(DATE) #发行公告日
    WSZQJGGGDATE = Column(DATE) #网上中签结果公告日
    LISTDATE = Column(DATE) #首发上市日期
    ISSUEAMTONL = Column(DOUBLE(asdecimal=False)) # 网上发行数量
    LOTNUM = Column(TEXT) # 中签号
    COMPROFILE = Column(TEXT) # 公司简介
    BUSINESS = Column(TEXT) # 经营范围

class EmConvBondIpoInfo(Base):

    __tablename__ = 'em_conv_bond_ipo_info'

    CODES = Column(CHAR(20), primary_key=True)  # 转摘代码
    CBCODE = Column(CHAR(20)) # 转债代码
    CBNAME = Column(CHAR(64)) # 转债简称
    CBSTOCKCODE = Column(CHAR(20)) # 正股代码
    CBSTOCKNAME = Column(CHAR(64)) # 正股简称
    CBISSUEAMT = Column(DOUBLE(asdecimal=False)) # 发行总额(亿)
    IPOANNCDATE = Column(DATE) # 发行公告日
    CBIPOTYPE = Column(CHAR(20)) # 发行方式
    CBPURCODEONL = Column(CHAR(20)) # 网上发行申购代码
    ISSRATE = Column(CHAR(20)) # 发行时债项评级
    CBTERM = Column(DOUBLE(asdecimal=False)) # 发行期限
    CBISSUEPRICE = Column(DOUBLE(asdecimal=False)) # 发行价格
    ISSUEONLEDATE = Column(DATE) # 上网发行截止日期
    CBCONVPRICE = Column(DOUBLE(asdecimal=False)) # 转股价格
    CBDATEONL = Column(DATE) # 申购日
    CBLISTDATE = Column(DATE) # 上市日期
    CBRESULTDATE = Column(DATE) # 中签结果日
    CBSUCRATEONL = Column(DOUBLE(asdecimal=False)) # 网上中签率
    QUANTLIMITINTRO = Column(CHAR(255)) # 网上发行认购数量限制说明
    CBMATURITYDATE = Column(DATE) # 到期日
    CBREDEMPRICETM = Column(DOUBLE(asdecimal=False)) # 到期赎回价格
    CBRATIONCODE = Column(CHAR(20)) # 老股东配售代码
    CBSUCCESS = Column(TEXT) # 中签结果
    CBPUTBACKPRICEEXPLAIN = Column(TEXT) # 回售价格说明
    CBREDEMMEMO = Column(TEXT) # 赎回价格说明

class EmConvBondCleanPrice(Base):
    '''Choice可转债价格数据表(净价)'''

    __tablename__ = 'em_conv_bond_clean_price'

    CODES = Column('bond_id', CHAR(10), primary_key=True) # EM债券ID
    DATES = Column('datetime', DATE, primary_key=True) # 日期
    OPEN = Column('open', DOUBLE(asdecimal=False), nullable=False) # 开盘价
    CLOSE = Column('close', DOUBLE(asdecimal=False), nullable=False) # 收盘价
    HIGH = Column('high', DOUBLE(asdecimal=False), nullable=False) # 最高价
    LOW = Column('low', DOUBLE(asdecimal=False), nullable=False) # 最低价
    PRECLOSE = Column('pre_close', DOUBLE(asdecimal=False)) # 前收盘价
    AVERAGE = Column('average', DOUBLE(asdecimal=False)) # 均价
    AMOUNT = Column('amount', DOUBLE(asdecimal=False), server_default=text('0')) # 成交额
    VOLUME = Column('volume', DOUBLE(asdecimal=False), server_default=text('0')) # 成交量

    __table_args__ = (
        Index('idx_em_conv_bond_clean_price_datetime', 'datetime'),
    )

class EmConvBondDirtyPrice(Base):
    '''Choice可转债价格数据表(全价)'''

    __tablename__ = 'em_conv_bond_dirty_price'

    CODES = Column('bond_id', CHAR(10), primary_key=True) # EM债券ID
    DATES = Column('datetime', DATE, primary_key=True) # 日期
    OPEN = Column('open', DOUBLE(asdecimal=False), nullable=False) # 开盘价
    CLOSE = Column('close', DOUBLE(asdecimal=False), nullable=False) # 收盘价
    HIGH = Column('high', DOUBLE(asdecimal=False), nullable=False) # 最高价
    LOW = Column('low', DOUBLE(asdecimal=False), nullable=False) # 最低价
    PRECLOSE = Column('pre_close', DOUBLE(asdecimal=False)) # 前收盘价
    AVERAGE = Column('average', DOUBLE(asdecimal=False)) # 均价

    __table_args__ = (
        Index('idx_em_conv_bond_dirty_price_datetime', 'datetime'),
    )

class EmStockConceptInfo(Base):
    '''Choice股票概念2020-12-23'''

    __tablename__ = 'em_stock_concept_info'

    codes = Column(CHAR(10), primary_key=True) # 股票代码
    stock_name = Column(CHAR(32)) # 股票名字
    concepts = Column(TEXT) # 概念


class EmFuturePrice(Base):
    '''Choice期货行情信息'''

    __tablename__ = 'em_future_price'

    CODES = Column('future_id', CHAR(16), primary_key=True) # EM期货ID
    DATES = Column('datetime', DATE, primary_key=True) # 日期
    OPEN = Column('open', DOUBLE(asdecimal=False), nullable=False) # 开盘价
    CLOSE = Column('close', DOUBLE(asdecimal=False), nullable=False) # 收盘价
    HIGH = Column('high', DOUBLE(asdecimal=False), nullable=False) # 最高价
    LOW = Column('low', DOUBLE(asdecimal=False), nullable=False) # 最低价
    CLEAR = Column('clear', DOUBLE(asdecimal=False), nullable=False) # 结算价
    PRECLOSE = Column('pre_close', DOUBLE(asdecimal=False)) # 前收盘价
    PRECLEAR = Column('pre_clear', DOUBLE(asdecimal=False)) # 前结算价
    UNIHQOI = Column('uni_hq_oi', DOUBLE(asdecimal=False), nullable=False) # 持仓量(单边)
    UNIVOLUME = Column('uni_volume', DOUBLE(asdecimal=False), nullable=False) # 成交量(单边)
    UNIAMOUNT = Column('uni_amount', DOUBLE(asdecimal=False)) # 成交额(单边)
    SPREAD = Column('spread', DOUBLE(asdecimal=False), nullable=False) # 价差
    MAINFORCE = Column('main_force', TEXT) # 对应主力

class EmFutureInfo(Base):
    '''Choice期货行情信息'''

    __tablename__ = 'em_future_info'

    CODES = Column('future_id', CHAR(16), primary_key=True) # EM期货ID
    NAME = Column('name', CHAR(30), primary_key=True) # 期货名

class EmStockFutureDiff(Base):
    '''Choice股指期货基差'''

    __tablename__ = 'em_stock_future_diff'

    CODES = Column(CHAR(16), primary_key=True) # EM期货ID
    DATES = Column(DATE, primary_key=True) # 日期
    RESULT = Column(DOUBLE(asdecimal=False)) # 数值

class EmStockFutureDiffInfo(Base):
    '''Choice期货行情信息'''

    __tablename__ = 'em_stock_future_diff_info'

    codes = Column(CHAR(20), primary_key=True) # em_id
    name = Column(CHAR(60), primary_key=True) # 期货名

class EmBTCFromWeb(Base):
    '''新浪的btc'''

    __tablename__ = 'em_btc_from_web'

    codes = Column(CHAR(20), primary_key=True) # codes
    date = Column(DATE, primary_key=True) # 日期
    close = Column(DOUBLE(asdecimal=False)) # 数值

class HFFundNav(Base):
    '''私募基金数据'''

    __tablename__ = 'hf_fund_nav'

    fund_id = Column(CHAR(20), primary_key=True) # codes
    datetime = Column(DATE, primary_key=True) # 日期
    nav = Column(DOUBLE(asdecimal=False)) # 数值

class HFFundInfo(Base):
    '''私募基金信息'''

    __tablename__ = 'hf_fund_info'

    fund_id = Column(CHAR(15), primary_key=True) # 基金id
    begin_date = Column(DATE) # 私募开始年份
    stg_type = Column(CHAR(10)) # 策略类型
    desc_name = Column(CHAR(40)) # 基金名
    agency_id = Column(CHAR(10)) # 机构id
    agency_name = Column(CHAR(20)) # 机构名
    manager_name = Column(CHAR(20)) # 基金经理名
    source = Column(CHAR(20)) # 来源
    nav_source = Column(CHAR(10)) # 净值来源

class HFIndexPrice(Base):
    '''私募基金信息'''

    __tablename__ = 'hf_index_price'

    index_id = Column(CHAR(20), primary_key=True) # 指数id
    index_date = Column(DATE, primary_key=True) # 指数日期
    calcu_date = Column(DATE) # 指数数据计算时间
    close = Column(DOUBLE(asdecimal=False)) # 数值

class WindIndexPrice(Base):
    '''私募基金信息'''

    __tablename__ = 'wind_index_price'

    index_id = Column(CHAR(20), primary_key=True) # 指数id
    datetime = Column(DATE, primary_key=True) # 指数日期
    close = Column(DOUBLE(asdecimal=False)) # 数值

class WindIndexInfo(Base):
    '''私募基金信息'''

    __tablename__ = 'wind_index_info'

    index_id = Column(CHAR(20), primary_key=True) # 指数id
    desc_name = Column(CHAR(60))

class HFFundNavMiss(Base):
    '''私募基金净值缺失'''

    __tablename__ = 'hf_fund_nav_miss'

    fund_id = Column(CHAR(15), primary_key=True) # 基金id
    desc_name = Column(CHAR(40)) # 基金名

class EmOverseaIndexInfo(Base):
    '''Choice海外指数信息  明晟指数和全球知名指数'''

    __tablename__ = 'em_oversea_index_info'

    em_id = Column(CHAR(15), primary_key=True) # 指数东财代码
    index_full_name = Column(CHAR(64)) # 股票名字
    desc_name = Column(CHAR(64)) # 指数名字

class EmOverseaStockInfoUS(Base):
    '''Choice美股信息'''

    __tablename__ = 'em_oversea_stock_info_us'

    em_id = Column(CHAR(15), primary_key=True) # 股票代码
    desc_name = Column(CHAR(128)) # 股票简称
    isin_code = Column(CHAR(20)) # ISIN代码
    list_loc = Column(CHAR(20)) # 上市地
    currency = Column(CHAR(10)) # 交易币种
    market_loc = Column(CHAR(5)) # 证券所属交易市场
    market_name = Column(CHAR(64)) # 交易所中文名称
    market_short_name = Column(CHAR(20)) # 交易所英文简称
    stock_type = Column(CHAR(32)) # 证券类型
    stock_detail = Column(CHAR(64)) # 证券类型(细类)
    eng_name = Column(CHAR(128)) # 英文名称
    gics_indus_1 = Column(CHAR(64)) # 所属GICS行业1级
    gics_indus_2 = Column(CHAR(64)) # 所属GICS行业2级
    gics_indus_3 = Column(CHAR(64)) # 所属GICS行业3级
    gics_indus_4 = Column(CHAR(64)) # 所属GICS行业4级
    start_date = Column(DATE) # 成立日期

class EmOverseaStockInfoHK(Base):
    '''Choice港股信息'''

    __tablename__ = 'em_oversea_stock_info_hk'

    em_id = Column(CHAR(15), primary_key=True) # 股票代码
    desc_name = Column(CHAR(128)) # 股票简称
    isin_code = Column(CHAR(20)) # ISIN代码
    list_loc = Column(CHAR(20)) # 上市地
    currency = Column(CHAR(10)) # 交易币种
    market_loc = Column(CHAR(5)) # 证券所属交易市场
    market_name = Column(CHAR(64)) # 交易所中文名称
    market_short_name = Column(CHAR(20)) # 交易所英文简称
    stock_type = Column(CHAR(32)) # 证券类型
    stock_detail = Column(CHAR(64)) # 证券类型(细类)
    eng_name = Column(CHAR(128)) # 英文名称
    gics_indus_1 = Column(CHAR(64)) # 所属GICS行业1级
    gics_indus_2 = Column(CHAR(64)) # 所属GICS行业2级
    gics_indus_3 = Column(CHAR(64)) # 所属GICS行业3级
    gics_indus_4 = Column(CHAR(64)) # 所属GICS行业4级
    start_date = Column(DATE) # 成立日期

class EmOverseaStockInfoUK(Base):
    '''Choice港股信息'''

    __tablename__ = 'em_oversea_stock_info_uk'

    em_id = Column(CHAR(15), primary_key=True) # 证券代码
    desc_name = Column(CHAR(128)) # 股票简称
    isin_code = Column(CHAR(20)) # ISIN代码
    currency = Column(CHAR(10)) # 交易币种
    stock_detail = Column(CHAR(64)) # 证券类型(细类)
    company_name = Column(CHAR(128)) # 公司名称
    registered_location = Column(CHAR(64)) # 注册地所在国家或地区
    currency = Column(CHAR(10)) # 交易币种
    stock_type = Column(CHAR(32)) # 证券类型
    market_name = Column(CHAR(64)) # 交易所中文名称
    market_short_name = Column(CHAR(20)) # 交易所英文简称
    stock_detail = Column(CHAR(64)) # 证券类型(细类)
    start_date = Column(DATE) # 成立日期

class EmOverseaEmIndexPrice(Base):
    '''Choice海外指数数据'''
    
    __tablename__ = 'em_oversea_index_price'
    
    CODES = Column(CHAR(15), primary_key=True) # 指数代码
    DATES = Column(DATE, primary_key=True) # 日期
    CLOSE = Column(DOUBLE(asdecimal=False), nullable=False) # 收盘价

class EmOverseaEmStockPriceUS(Base):
    '''Choice海外指数数据'''
    
    __tablename__ = 'em_oversea_stock_price_us'
    
    CODES = Column(CHAR(15), primary_key=True) # 股票代码
    DATES = Column(DATE, primary_key=True) # 日期
    CLOSE = Column(DOUBLE(asdecimal=False), nullable=False) # 收盘价

class EmOverseaEmStockPriceHK(Base):
    '''Choice港股数据'''
    
    __tablename__ = 'em_oversea_stock_price_hk'
    
    CODES = Column(CHAR(15), primary_key=True) # 股票代码
    DATES = Column(DATE, primary_key=True) # 日期
    CLOSE = Column(DOUBLE(asdecimal=False), nullable=False) # 收盘价


class EmOverseaStockFinFac(Base):
    '''Choice港股美股财务数据'''

    __tablename__ = 'em_oversea_stock_fin_fac'

    stock_code = Column(CHAR(20), primary_key=True) # 证券代码 
    report_date = Column(CHAR(20), primary_key=True) # report_date 
    desc_name = Column(TEXT) # 证券名称 
    indicator_1 = Column(DOUBLE(asdecimal=False)) # 已发行普通股 
    indicator_2 = Column(DOUBLE(asdecimal=False)) # 年度分红 
    indicator_3 = Column(DOUBLE(asdecimal=False)) # 归属母公司净利润(TTM) 
    indicator_4 = Column(DOUBLE(asdecimal=False)) # 每股净资产 
    indicator_5 = Column(DOUBLE(asdecimal=False)) # 每股净资产(最新股本摊薄) 
    indicator_6 = Column(DOUBLE(asdecimal=False)) # 每股收益EPS(基本) 
    indicator_7 = Column(DOUBLE(asdecimal=False)) # 每股收益EPS(稀释) 
    indicator_8 = Column(DOUBLE(asdecimal=False)) # 每股收益EPS(调整股本数) 
    indicator_9 = Column(DOUBLE(asdecimal=False)) # 每股派息 
    indicator_10 = Column(DOUBLE(asdecimal=False)) # 每股现金流量净额 
    indicator_11 = Column(DOUBLE(asdecimal=False)) # 每股现金流量净额(TTM) 
    indicator_12 = Column(DOUBLE(asdecimal=False)) # 每股经营现金净流量 
    indicator_13 = Column(DOUBLE(asdecimal=False)) # 每股经营现金净流量(TTM) 
    indicator_14 = Column(DOUBLE(asdecimal=False)) # 每股营业收入 
    indicator_15 = Column(DOUBLE(asdecimal=False)) # 稀释每股收益 
    indicator_16 = Column(DOUBLE(asdecimal=False)) # 经营活动产生的现金 
    indicator_17 = Column(DOUBLE(asdecimal=False)) # 营业收入 
    indicator_18 = Column(DOUBLE(asdecimal=False)) # 总市值

class QSOverseaFundCurMdd(Base):
    '''青石基金当前回撤'''

    __tablename__ = 'qs_oversea_fund_cur_mdd'
    
    codes = Column(CHAR(15), primary_key=True) # 基金代码
    datetime = Column(DATE, primary_key=True) # 日期
    current_mdd = Column(DOUBLE(asdecimal=False), nullable=False) # 当前回撤

class QSOverseaFundMonthlyRet(Base):
    '''青石基金月度收益'''

    __tablename__ = 'qs_oversea_fund_monthly_ret'
    
    codes = Column(CHAR(15), primary_key=True) # 基金代码
    datetime = Column(DATE, primary_key=True) # 日期
    monthly_ret = Column(DOUBLE(asdecimal=False), nullable=False) # 月度收益

class QSOverseaFundIndicator(Base):
    '''青石基金指标'''

    __tablename__ = 'qs_oversea_fund_indicator'

    codes = Column(CHAR(15), primary_key=True) # 基金代码
    datetime = Column(DATE, primary_key=True) # 日期 
    data_cycle = Column(Integer, primary_key=True) # 因子计算时长
    trade_year = Column(DOUBLE(asdecimal=False), nullable=False) # 交易年限
    last_unit_nav = Column(DOUBLE(asdecimal=False), nullable=False) # 最后净值
    cumu_ret = Column(DOUBLE(asdecimal=False), nullable=False) # 累计收益
    annual_ret = Column(DOUBLE(asdecimal=False), nullable=False) # 年化收益
    annual_vol = Column(DOUBLE(asdecimal=False), nullable=False) # 年化波动
    sharpe = Column(DOUBLE(asdecimal=False), nullable=False) # 夏普
    recent_1w_ret = Column(DOUBLE(asdecimal=False), nullable=False) # 最近一个周收益
    recent_1m_ret = Column(DOUBLE(asdecimal=False), nullable=False) # 最近一个月收益 
    recent_3m_ret = Column(DOUBLE(asdecimal=False), nullable=False) # 最近三个月收益
    recent_6m_ret = Column(DOUBLE(asdecimal=False), nullable=False) # 最近六个月收益
    recent_1y_ret = Column(DOUBLE(asdecimal=False), nullable=False) # 最近一年收益
    recent_3y_ret = Column(DOUBLE(asdecimal=False), nullable=False) # 最近三年收益
    recent_5y_ret = Column(DOUBLE(asdecimal=False), nullable=False) # 最近五年收益
    worst_3m_ret = Column(DOUBLE(asdecimal=False), nullable=False) # 最差三个月收益
    worst_6m_ret = Column(DOUBLE(asdecimal=False), nullable=False) # 最差六个月收益
    last_mv_diff = Column(DOUBLE(asdecimal=False), nullable=False) # 最新涨跌幅
    last_increase_rate = Column(DOUBLE(asdecimal=False), nullable=False) # 最新涨跌
    recent_drawdown = Column(DOUBLE(asdecimal=False), nullable=False) # 当前回撤
    recent_mdd_date1 = Column(DATE) # 当前回撤开始时间
    recent_mdd_lens = Column(DOUBLE(asdecimal=False), nullable=False) # 当前回撤持续天数
    mdd = Column(DOUBLE(asdecimal=False), nullable=False) # 最大回撤
    mdd_date1 = Column(DATE) # 最大回撤开始日
    mdd_date2 = Column(DATE) # 最大回撤结束日
    mdd_lens = Column(DOUBLE(asdecimal=False), nullable=False) # 最大回撤持续天数
    calmar = Column(DOUBLE(asdecimal=False), nullable=False) # 卡玛比率
    downside_risk = Column(DOUBLE(asdecimal=False), nullable=False) # 下行风险
    sortino = Column(DOUBLE(asdecimal=False), nullable=False) # 索提诺
    var = Column(DOUBLE(asdecimal=False), nullable=False) # 风险价值
    ervar = Column(DOUBLE(asdecimal=False), nullable=False) # 风险价值调整比
    skew = Column(DOUBLE(asdecimal=False), nullable=False) # 偏度
    kurtosis = Column(DOUBLE(asdecimal=False), nullable=False) # 峰度
    alpha_cl = Column(DOUBLE(asdecimal=False), nullable=False) # cl alpha
    beta_cl = Column(DOUBLE(asdecimal=False), nullable=False) # cl beta
    beta_bear = Column(DOUBLE(asdecimal=False), nullable=False) # 熊市beta 已做负号处理
    beta_bull = Column(DOUBLE(asdecimal=False), nullable=False) # 牛市beta
    alpha_hm = Column(DOUBLE(asdecimal=False), nullable=False) # hm alpha
    beta_hm = Column(DOUBLE(asdecimal=False), nullable=False) # hm beta
    excess_ret = Column(DOUBLE(asdecimal=False), nullable=False) # 相对收益
    win_rate = Column(DOUBLE(asdecimal=False), nullable=False) # 胜率
    corr = Column(DOUBLE(asdecimal=False), nullable=False) # 相关性
    track_err = Column(DOUBLE(asdecimal=False), nullable=False) # 跟踪误差
    info = Column(DOUBLE(asdecimal=False), nullable=False) # 信息比率
    alpha = Column(DOUBLE(asdecimal=False), nullable=False) # alpha
    beta = Column(DOUBLE(asdecimal=False), nullable=False) # beta
    treynor = Column(DOUBLE(asdecimal=False), nullable=False) # 特雷诺
    not_system_risk = Column(DOUBLE(asdecimal=False), nullable=False) # 非系统性风险
    cvar = Column(DOUBLE(asdecimal=False), nullable=False) # cvar
    up_capture = Column(DOUBLE(asdecimal=False), nullable=False) # 上行捕捉率
    down_capture = Column(DOUBLE(asdecimal=False), nullable=False) # 下行捕捉率
    excess_ret_cotinue = Column(DOUBLE(asdecimal=False), nullable=False) # 超额收益持续性
    continue_value_m = Column(DOUBLE(asdecimal=False), nullable=False) # 业绩持续性

class QSOverseaFundRadarScore(Base):
    '''青石基金雷达图'''

    __tablename__ = 'qs_oversea_fund_radar_score'

    codes = Column(CHAR(15), primary_key=True) # 基金代码
    datetime = Column(DATE, primary_key=True) # 日期
    ret_ability = Column(DOUBLE(asdecimal=False), nullable=False) # 业绩
    risk_ability = Column(DOUBLE(asdecimal=False), nullable=False) # 波动管理
    bull_ability = Column(DOUBLE(asdecimal=False), nullable=False) # 牛市追踪
    bear_ability = Column(DOUBLE(asdecimal=False), nullable=False) # 熊市追踪
    alpha_ability = Column(DOUBLE(asdecimal=False), nullable=False) # 超越市场
    drawdown_ability = Column(DOUBLE(asdecimal=False), nullable=False) # 回撤管理
    total_score = Column(DOUBLE(asdecimal=False), nullable=False) # 总分
    fund_type = Column(CHAR(20)) # 基金类型

class QSOverseaFundPeriodRet(Base):
    '''青石基金阶段收益'''

    __tablename__ = 'qs_oversea_fund_period_ret'

    codes = Column(CHAR(15), primary_key=True) # 基金代码
    date = Column(Integer, primary_key=True) # 日期标签
    ret = Column(DOUBLE(asdecimal=False), nullable=False) # 收益

class QSFundStyleBox(Base):
    '''青石基金风格箱'''

    __tablename__ = 'qs_oversea_fund_style_box'

    codes = Column(CHAR(15), primary_key=True) # 基金代码
    datetime = Column(DATE, primary_key=True) # 日期标签
    x = Column(DOUBLE(asdecimal=False), nullable=False) # 风格
    y = Column(DOUBLE(asdecimal=False), nullable=False) # 规模

class QSFundRecentRet(Base):
    '''基金近期收益'''

    __tablename__ = 'qs_oversea_fund_recent_ret'

    codes = Column(CHAR(15), primary_key=True) # 基金代码
    datetime = Column(DATE, primary_key=True) # 日期标签
    recent_natural_year_ret = Column(DOUBLE(asdecimal=False)) # 最近自然年收益
    recent_1w_ret = Column(DOUBLE(asdecimal=False)) # 最近一周收益
    recent_1m_ret = Column(DOUBLE(asdecimal=False)) # 最近一月收益
    recent_3m_ret = Column(DOUBLE(asdecimal=False)) # 最近三月收益
    recent_6m_ret = Column(DOUBLE(asdecimal=False)) # 最近六月收益
    recent_1y_ret = Column(DOUBLE(asdecimal=False)) # 最近一年收益
    recent_2y_ret = Column(DOUBLE(asdecimal=False)) # 最近两年收益
    recent_3y_ret = Column(DOUBLE(asdecimal=False)) # 最近三年收益
    recent_4y_ret = Column(DOUBLE(asdecimal=False)) # 最近四年收益
    recent_5y_ret = Column(DOUBLE(asdecimal=False)) # 最近五年收益
    history_ret = Column(DOUBLE(asdecimal=False)) # 历史收益
    history_annual_ret = Column(DOUBLE(asdecimal=False)) # 历史年化收益

class EmFutureInfoDetail(Base):
    '''Choice期货信息'''

    __tablename__ = 'em_future_info_detail'

    EMCODE = Column('em_id', CHAR(20), primary_key=True) # 东财代码
    NAME = Column('desc_name', CHAR(40)) # 期货简称
    TRADINGCODE = Column('trading_code', CHAR(20)) # 交易代码  
    FTMKTSNAME = Column('mkt_name', CHAR(40)) # 交易所简称
    FTPRICELIMIT = Column('price_limit', DOUBLE(asdecimal=False)) # 涨跌幅限制
    FTTRANSMARGIN = Column('trans_margin', DOUBLE(asdecimal=False)) # 交易保证金
    FTDELIVMONTH = Column('deliv_month', Integer) # 交割月份
    FTQUTOBPRICE = Column('quote_price', DOUBLE(asdecimal=False)) # 挂牌基准价
    FTCONTRAENGSNAME =  Column('short_eng_name', CHAR(20)) # 合约英文简称
    FTCONTRAENGNAME = Column('eng_name', CHAR(40)) # 合约英文名称     
    DELIVERYDATE = Column('deliver_date', DATE) # 交割日期
    STARTTRADEDATE = Column('start_trade_date', DATE) # 开始交易日
    LASTTRADEDATE = Column('last_trade_date', DATE) # 最后交易日
    LONGMARGIN = Column('long_margin', Integer) # 多头交易保证金
    SHORTMARGIN = Column('short_margin', Integer) # 空头交易保证金
    PRICELIMITRANGE = Column('price_limit_range', DOUBLE(asdecimal=False)) # 涨跌停板幅度
    FTTRANSTYPE = Column('trans_type', CHAR(20)) # 交易品种
    FTTRANSUNIT = Column('trans_unit', CHAR(20)) # 交易单位
    CONTRACTMUL = Column('contract_mul', Integer) # 合约乘数
    FTPRICEUNIT = Column('price_unit', CHAR(40)) # 报价单位
    FTMINPRICECHG = Column('min_price_change', CHAR(20)) # 最小变动价位
    LISTDATE = Column('list_standard_date', DATE) # 标准合约上市日
    FTCONTRADATEINTRO = Column('contract_date_info', CHAR(20)) # 合约月份说明
    FTTRANSDATEINSTRO = Column('trans_date_info', CHAR(180)) # 交易时间说明
    FTLTRANSDATE = Column('last_trans_date', CHAR(40)) # 最后交易日说明
    FTDELIVDATEINTRO = Column('deliver_date_info', CHAR(80)) # 交割日期说明
    FTFIRSTTRANSMARGIN = Column('first_trans_margin', CHAR(40)) # 最低交易保证

class EmFuturePriceDetail(Base):
    '''Choice期货行情'''

    __tablename__ = 'em_future_price_detail'
    
    CODES = Column('em_id', CHAR(20), primary_key=True) # 东财代码 
    DATES = Column('datetime', DATE, primary_key=True) # 日期

    OPEN = Column('open', DOUBLE(asdecimal=False)) # 开盘价
    CLOSE = Column('close', DOUBLE(asdecimal=False)) # 收盘价
    HIGH = Column('high', DOUBLE(asdecimal=False)) # 最高价  
    LOW = Column('low', DOUBLE(asdecimal=False)) # 最低价
    PRECLOSE = Column('pre_close', DOUBLE(asdecimal=False)) # 前收盘价
    AVERAGE = Column('average_price', DOUBLE(asdecimal=False)) # 均价
    VOLUME =  Column('uni_volume', Integer) # 成交量
    AMOUNT = Column('uni_amount', DOUBLE(asdecimal=False)) # 成交金额      
    SPREAD = Column('spread', DOUBLE(asdecimal=False)) # 价差
    CLEAR = Column('clear', DOUBLE(asdecimal=False)) # 结算价
    PRECLEAR = Column('pre_clear', DOUBLE(asdecimal=False)) # 前结算价
    HQOI = Column('uni_oi', DOUBLE(asdecimal=False)) # 持仓量
    CHANGEOI = Column('uni_change_oi', DOUBLE(asdecimal=False)) # 持仓量变化 

class EmFuturePriceDetailDev(Base):
    '''Choice期货行情'''

    __tablename__ = 'em_future_price_detail_dev'
    
    CODES = Column('em_id', CHAR(20), primary_key=True) # 东财代码 
    DATES = Column('datetime', DATE, primary_key=True) # 日期
    
    OPEN = Column('open', DOUBLE(asdecimal=False)) # 开盘价
    CLOSE = Column('close', DOUBLE(asdecimal=False)) # 收盘价
    HIGH = Column('high', DOUBLE(asdecimal=False)) # 最高价  
    LOW = Column('low', DOUBLE(asdecimal=False)) # 最低价
    CLEAR = Column('clear', DOUBLE(asdecimal=False)) # 结算价
    PRECLEAR = Column('pre_clear', DOUBLE(asdecimal=False)) # 前结算价
    PRECLOSE = Column('pre_close', DOUBLE(asdecimal=False)) # 前收盘价
    AVGPRICE = Column('average_price', DOUBLE(asdecimal=False)) # 成交均价
    UNIOI = Column('uni_oi', DOUBLE(asdecimal=False)) # 持仓量(单边) 
    UNIOICHG = Column('uni_change_oi', DOUBLE(asdecimal=False)) # 持仓量变化(单边)
    UNIVOLUME =  Column('uni_volume', Integer) # 成交量(单边) 
    UNIAMOUNT = Column('uni_amount', DOUBLE(asdecimal=False)) # 成交额(单边)
    MAINFORCE = Column('mainforce', DOUBLE(asdecimal=False)) # 对应主力
    SPREAD = Column('spread', DOUBLE(asdecimal=False)) # 价差