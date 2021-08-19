
import datetime

from sqlalchemy import CHAR, Column, Integer, Index, BOOLEAN, text, TEXT, Enum, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import DOUBLE, DATE, TINYINT, SMALLINT, DATETIME, MEDIUMTEXT, BIGINT, SMALLINT, DECIMAL
from sqlalchemy.sql.selectable import ScalarSelect

from ...constant import SectorType, IndexPriceSource, HoldingAssetType, FundStatus


class Base:
    _update_time = Column('_update_time', DATETIME, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  # 更新时间


class FOFBase:
    create_time = Column(DATETIME, nullable=False, server_default=text('CURRENT_TIMESTAMP'))  # 创建时间
    update_time = Column(DATETIME, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  # 更新时间
    is_deleted = Column(BOOLEAN, nullable=False, server_default=text('FALSE'))  # 是否删除 默认不删除


# make this column at the end of every derived table
Base._update_time._creation_order = 9999
Base = declarative_base(cls=Base)

FOFBase.create_time._creation_order = 9997
FOFBase.update_time._creation_order = 9998
FOFBase.is_deleted._creation_order = 9999
FOFBase = declarative_base(cls=FOFBase)


class SectorInfo(Base):
    '''板块信息表'''

    __tablename__ = 'sector_info'

    sector_id = Column(CHAR(64), primary_key=True)  # 板块ID
    sector_type = Column(Enum(SectorType), nullable=False)  # 板块类型 industry-行业 topic-主题
    sector_desc = Column(TEXT, nullable=False)  # 板块描述
    sector_name = Column(CHAR(16), nullable=False, unique=True)  # 板块名称
    main_index_id = Column(CHAR(16), nullable=False)  # 板块代表指数
    main_fund_id = Column(CHAR(16))  # 板块代表基金


class SectorFunds(Base):
    '''板块基金表'''

    __tablename__ = 'sector_funds'

    id = Column(Integer, primary_key=True)

    sector_id = Column(CHAR(64), nullable=False)  # 板块ID
    csi_index_id = Column(CHAR(16), nullable=False)  # Choice指数ID
    index_id = Column(CHAR(20), nullable=False)  # 指数ID
    em_fund_id = Column(CHAR(16))  # Choice基金ID
    fund_id = Column(CHAR(16))  # 基金ID


class IndexInfo(Base):
    '''指数信息表'''

    __tablename__ = 'index_info'
    index_id = Column(CHAR(20), primary_key=True)
    is_deleted = Column(BOOLEAN, default=False)  # 是否删除

    order_book_id = Column(CHAR(20))  # 米筐ID
    # web_id= Column(CHAR(20)) # 数据所在网页ID
    industry_tag = Column(CHAR(64))  # 行业标签
    tag_method = Column(CHAR(64))  # 估值评分采用方法
    desc_name = Column(CHAR(64), nullable=False, unique=True)  # 名称
    maker_name = Column(CHAR(32), nullable=False)  # 编制机构
    # publish_date = Column(DATE, nullable=False)  # 发布日期
    is_select = Column(BOOLEAN, nullable=False)  # 是否属于精选
    is_stock_factor_universe = Column(BOOLEAN)  # 是否是股票因子universe
    em_id = Column(CHAR(20))  # ChoiceID
    em_plate_id = Column(CHAR(20))  # Choice板块ID
    index_profile = Column(TEXT)  # 指数概况
    price_source = Column(Enum(IndexPriceSource), nullable=False)  # 指数价格来源标记


class IndexComponent(Base):

    __tablename__ = 'index_component'

    index_id = Column(CHAR(20), primary_key=True)
    datetime = Column(DATE, primary_key=True)  # 日期
    num = Column(Integer, nullable=False)  # 成分股数量
    id_cat = Column(Enum(SectorType), nullable=False)  # 所属类型 industry-行业 topic-主题
    sector = Column(TEXT, nullable=False)  # 所属板块
    top10 = Column(TEXT, nullable=False)  # 前10成分及权重
    related_funds = Column(TEXT)  # 相关产品
    all_constitu = Column(MEDIUMTEXT, nullable=False)  # 所有成分及权重(from Choice)


class StockInfo(Base):
    '''股票信息表'''

    __tablename__ = 'stock_info'
    stock_id = Column(CHAR(20), primary_key=True) # 股票ID
    rq_id = Column(CHAR(20)) # 米筐ID


class FundSize(Base):
    '''基金最新规模'''

    __tablename__ = 'fund_size'

    fund_id = Column(CHAR(10), primary_key=True) # 基金id
    latest_size = Column(DOUBLE(asdecimal=False)) # 最新规模


class FundStatusLatest(Base):
    '''
    基金状态表 包含基金申赎状态等
    '''

    __tablename__ = 'fund_status_latest'

    fund_id = Column(CHAR(10), primary_key=True)  # 基金ID

    PURCHSTATUS = Column('purch_status', CHAR(16))  # 申购状态
    REDEMSTATUS = Column('redem_status', CHAR(16))  # 赎回状态
    LPLIMIT = Column('lp_limit', DOUBLE(asdecimal=False))  # 暂停大额申购上限
    OTCLPLIMITJG = Column('otc_lp_limit_jg', DOUBLE(asdecimal=False))  # 场外暂停大额申购上限(机构)
    OTCLPLIMITGR = Column('otc_lp_limit_gr', DOUBLE(asdecimal=False))  # 场外暂停大额申购上限(个人)
    TRADESTATUS = Column('trade_status', CHAR(16))  # 交易状态
    PCHMINAMT = Column('pch_min_amt', DOUBLE(asdecimal=False))  # 申购金额下限
    REDMMINAMT = Column('redm_min_amt', DOUBLE(asdecimal=False))  # 单笔赎回份额下限


class FundInfo(Base):
    '''基金信息表'''

    __tablename__ = 'fund_info'
    fund_id = Column(CHAR(10), primary_key=True) # 基金ID

    wind_id = Column(CHAR(20), unique=True) # Wind基金ID
    transition = Column(Integer) # 基金变更次数
    order_book_id = Column(CHAR(10)) # RiceQuant基金ID
    desc_name = Column(CHAR(64)) # 基金名称
    start_date = Column(DATE) # 成立日期
    end_date = Column(DATE) # 关闭日期
    wind_class_1 = Column(CHAR(64)) # Wind基金类型
    wind_class_2 = Column(CHAR(64)) # Wind基金二级类型
    risk_level = Column(CHAR(2))  # 风险等级
    manager_id = Column(TEXT) # 基金经理
    company_id = Column(CHAR(64)) # 基金公司
    benchmark = Column(CHAR(255)) # 业绩基准
    full_name = Column(CHAR(255)) # 基金全名
    currency = Column(CHAR(20)) # 币种
    base_fund_id = Column(CHAR(20)) # 分级基金基础基金代号
    is_structured = Column(TINYINT(1)) # 是否为分级基金
    is_open = Column(TINYINT(1)) # 是否为日常开放申赎的基金 1是 0否， 排除掉封闭基金和定期开放基金
    is_regular_open_ended = Column(TINYINT(1)) # 是否为定期开放式基金 1是 0否
    is_closed_ended = Column(TINYINT(1)) # 是否为封闭基金 1是 0 否
    structure_type = Column(TINYINT(1))  # 是否为分级子基金  0/nan非   1母   2分级A  3 分级B 4 其他
    is_etf = Column(TINYINT(1)) # 是否是etf  0 非  1 etf
    asset_type = Column(CHAR(32)) # 资产类别
    tt_purchase_fee = Column(DOUBLE(asdecimal=False)) # 天天基金优惠申购费
    manage_fee = Column(DOUBLE(asdecimal=False)) # 管理费
    trustee_fee = Column(DOUBLE(asdecimal=False)) # 托管费
    purchase_fee = Column(DOUBLE(asdecimal=False)) # 申购费
    redeem_fee = Column(DOUBLE(asdecimal=False)) # 赎回费
    note = Column(CHAR(64)) # 附加信息
    track_index = Column(CHAR(20)) # 跟踪指数
    benchmark_1 = Column(CHAR(255)) # 业绩基准标的指数简称第一名
    benchmark_2 = Column(CHAR(255)) # 业绩基准标的指数简称第二名
    index_id = Column(CHAR(20)) # 基于第一业绩标准所标注的指数ID
    is_c =  Column("is_c", BOOLEAN)  #是否是etf  0 非  1 c
    is_a = Column("is_a", BOOLEAN)  #是否是etf  0 非  1 a
    ac_filter = Column("ac_filter", BOOLEAN) #是否ac均有要排除的a 0 排除  1 保留
    is_selected_mmf = Column(TINYINT(1)) # 是否基金规模最大的前50只货币基金(10年前有两只存在)  0 非  1 是
    national_debt_extension = Column(TINYINT(1)) # 纯债tag  0 非  1 是
    index_id_new = Column(CHAR(20)) # 基于第一业绩标准所标注的指数ID新
    subscr_fee_detail = Column(TEXT) # 认购费率详情
    purchase_fee_detail = Column(TEXT) # 申购费率详情
    redeem_fee_detail = Column(TEXT) # 赎回费率详情
    service_fee = Column(TEXT) # 销售服务费率
    fund_manager = Column(TEXT)  # 基金经理(现任)
    pre_fund_manager = Column(TEXT)  # 基金经理(历任)
    custodian_bank = Column(CHAR(64))  # 基金托管人
    foreign_custodian = Column(CHAR(64))  # 境外托管人
    frontend_fee_code = Column(CHAR(12))   # 前端收费代码
    backend_fee_code = Column(CHAR(12))  # 后端收费代码
    ar_code_in = Column(CHAR(12))  # 场内申赎代码


class FundBenchmark(Base):
    '''基金业绩比较基准表'''

    __tablename__ = 'fund_benchmark'

    em_id = Column(CHAR(16), primary_key=True)  # 基金代码
    fund_id = Column(CHAR(16))  # 内部基金代码
    # datetime = Column(DATE, primary_key=True)  # 日期
    index_text = Column(TEXT, nullable=False)  # 业绩比较基准
    benchmark = Column(TEXT, nullable=False)  # 解析出来的业绩比较基准
    benchmark_s = Column(TEXT, nullable=False)  # index转换后的业绩比较基准
    benchmark_s_raw = Column(TEXT, nullable=False)  # index转换后的业绩比较基准(原始)
    assets = Column(CHAR(32))  # 追踪的标的
    industry = Column(CHAR(64))  # 行业分类

    __table_args__ = (
        Index('idx_fund_benchmark_fund_id', 'fund_id'),
    )


class TradingDayList(Base):
    '''交易日列表'''

    __tablename__ = 'trading_day_list'
    datetime = Column(DATE, primary_key=True)


class FundNav(Base):
    '''基金净值表'''

    __tablename__ = 'fund_nav'
    fund_id = Column(CHAR(20), primary_key=True) # 合约代码
    datetime = Column(DATE, primary_key=True) # 日期

    unit_net_value = Column(DOUBLE(asdecimal=False)) # 单位净值
    acc_net_value = Column(DOUBLE(asdecimal=False)) # 累计单位净值 基金公司公告发布的原始数据 单位净值 + 单位累计分红
    adjusted_net_value = Column(DOUBLE(asdecimal=False)) # 复权净值 考虑分红再投资后调整的单位净值
    change_rate = Column(DOUBLE(asdecimal=False)) # 涨跌幅
    daily_profit = Column(DOUBLE(asdecimal=False)) # 每万元收益（日结型货币基金专用）
    weekly_yield = Column(DOUBLE(asdecimal=False)) # 7日年化收益率（日结型货币基金专用）
    redeem_status = Column(Integer) # 赎回状态，开放 - Open, 暂停 - Suspended, 限制大额申赎 - Limited, 封闭期 - Close
    subscribe_status = Column(Integer) # 订阅状态，开放 - Open, 暂停 - Suspended, 限制大额申赎 - Limited, 封闭期 - Close
    fund_size = Column(DOUBLE(asdecimal=False)) # 基金规模

    __table_args__ = (
        Index('idx_fund_nav_datetime', 'datetime'),
    )


class IndexPrice(Base):
    '''指数价格表'''

    __tablename__ = 'index_price'
    index_id = Column(CHAR(20), primary_key=True) # 指数id
    datetime = Column(DATE, primary_key=True) # 日期

    volume = Column(DOUBLE(asdecimal=False)) # 交易量
    low = Column(DOUBLE(asdecimal=False)) # 最低价
    close = Column(DOUBLE(asdecimal=False)) # 收盘价
    high = Column(DOUBLE(asdecimal=False)) # 最高价
    open = Column(DOUBLE(asdecimal=False)) # 开盘价
    total_turnover = Column(DOUBLE(asdecimal=False)) # 成交额
    ret = Column(DOUBLE(asdecimal=False)) # 日收益

    __table_args__ = (
        Index('idx_index_price_datetime', 'datetime'),
    )

class StockPrice(Base):
    '''股票价格表'''

    __tablename__ = 'stock_price'
    stock_id = Column(CHAR(20), primary_key=True) # 指数id
    datetime = Column(DATE, primary_key=True) # 日期

    open = Column(DOUBLE(asdecimal=False)) # 开盘价
    close = Column(DOUBLE(asdecimal=False)) # 收盘价
    high = Column(DOUBLE(asdecimal=False)) # 最高价
    low = Column(DOUBLE(asdecimal=False)) # 最低价
    limit_up = Column(DOUBLE(asdecimal=False)) # 涨停价
    limit_down = Column(DOUBLE(asdecimal=False)) # 跌停价
    total_turnover = Column(DOUBLE(asdecimal=False)) # 交易额
    volume = Column(DOUBLE(asdecimal=False)) # 交易量
    num_trades = Column(DOUBLE(asdecimal=False)) # 交易笔数
    adj_close = Column(DOUBLE(asdecimal=False)) # 后复权价格
    post_adj_factor = Column(DOUBLE(asdecimal=False)) # 后复权因子

    __table_args__ = (
        Index('idx_stock_price_datetime', 'datetime'),
    )


class FundRet(Base):
    '''基金历史收益'''

    __tablename__ = 'fund_ret'

    fund_id = Column(CHAR(10), primary_key=True) # 原始基金ID
    datetime = Column(DATE, primary_key=True) # 日期

    w1_ret = Column(DOUBLE(asdecimal=False)) # 近一周收益率
    m1_ret = Column(DOUBLE(asdecimal=False)) # 近一月收益率
    m3_ret = Column(DOUBLE(asdecimal=False)) # 近一季度收益率
    m6_ret = Column(DOUBLE(asdecimal=False)) # 近半年收益率
    y1_ret = Column(DOUBLE(asdecimal=False)) # 近一年收益率
    y3_ret = Column(DOUBLE(asdecimal=False)) # 近三年收益率
    y5_ret = Column(DOUBLE(asdecimal=False)) # 近五年收益率
    to_date_ret = Column(DOUBLE(asdecimal=False)) # 成立至今收益率
    mdd = Column(DOUBLE(asdecimal=False)) # 最大回撤（成立以来）
    annual_ret = Column(DOUBLE(asdecimal=False)) # 年化收益（成立以来）
    avg_size = Column(DOUBLE(asdecimal=False)) # 平均规模（成立以来）
    sharpe_ratio = Column(DOUBLE(asdecimal=False)) # 夏普率（成立以来）
    vol = Column(DOUBLE(asdecimal=False)) # 波动率（成立以来）
    info_ratio = Column(DOUBLE(asdecimal=False)) # 信息比率（成立以来）
    recent_y_ret = Column(DOUBLE(asdecimal=False)) # 年初至今收益率

class FundRatingLatest(Base):
    '''基金最新评级'''

    __tablename__ = 'fund_rating_latest'

    fund_id = Column(CHAR(10), primary_key=True)  # 基金id
    zs = Column(DOUBLE(asdecimal=False))  # 招商评级
    sh3 = Column(DOUBLE(asdecimal=False))  # 上海证券评级三年期
    sh5 = Column(DOUBLE(asdecimal=False))  # 上海证券评级五年期
    jajx = Column(DOUBLE(asdecimal=False))  # 济安金信评级
    update_time = Column(DATE)  # 更新日期

    __table_args__ = (
        Index('idx_fund_rating_latest_datetime', 'update_time'),
    )


class StyleAnalysisStockFactor(Base):
    '''风格分析股票因子'''

    __tablename__ = 'style_analysis_stock_factor'

    stock_id = Column(CHAR(10), primary_key=True)  # EM股票ID
    datetime = Column(DATE, primary_key=True)  # 日期
    rate_of_return = Column(DOUBLE(asdecimal=False), nullable=False)  # 收益率
    latest_size = Column(DOUBLE(asdecimal=False))  # 规模
    bp = Column(DOUBLE(asdecimal=False))  # 价值
    short_term_momentum = Column(DOUBLE(asdecimal=False))  # 短期动量
    long_term_momentum = Column(DOUBLE(asdecimal=False))  # 长期动量
    high_low = Column(DOUBLE(asdecimal=False))  # 波动率

    __table_args__ = (
        Index('idx_style_analysis_stock_factor_datetime', 'datetime'),
    )

class BarraCNE5RiskFactor(Base):
    '''Barra CNE5风险因子'''

    __tablename__ = 'barra_cne5_risk_factor'

    stock_id = Column(CHAR(10), primary_key=True)  # EM股票ID
    datetime = Column(DATE, primary_key=True)  # 日期
    ret = Column(DOUBLE(asdecimal=False))
    leverage = Column(DOUBLE(asdecimal=False))
    logsize = Column(DOUBLE(asdecimal=False))
    momentum = Column(DOUBLE(asdecimal=False))
    book_price = Column(DOUBLE(asdecimal=False))
    earning_yields = Column(DOUBLE(asdecimal=False))
    liquidity = Column(DOUBLE(asdecimal=False))
    growth = Column(DOUBLE(asdecimal=False))
    resvol = Column(DOUBLE(asdecimal=False))

    __table_args__ = (
        Index('idx_barra_cne5_risk_factor_datetime', 'datetime'),
    )

class Fund_size_and_hold_rate(Base):
    '''基金规模和持有人比例'''

    __tablename__ = 'fund_size_and_hold_rate'

    fund_id = Column(CHAR(10), primary_key=True)  # 基金id
    datetime = Column(DATE, primary_key=True)  # 日期
    size = Column(DOUBLE(asdecimal=False)) # 最新规模
    unit_total = Column(DOUBLE(asdecimal=False))  # 基金份额
    personal_holds = Column(DOUBLE(asdecimal=False)) # 个人持有比例 单位百分比
    institution_holds = Column(DOUBLE(asdecimal=False)) # 机构持有比例 单位百分比
    hold_num = Column(DOUBLE(asdecimal=False))  # 基金份额持有人户数

    __table_args__ = (
        Index('idx_fund_size_and_hold_rate_datetime', 'datetime'),
    )

class FundRate(Base):
    '''基金评级'''

    __tablename__ = 'fund_rate'

    fund_id = Column(CHAR(10), primary_key=True)  # 基金id
    datetime = Column(DATE, primary_key=True)  # 日期
    mkt_3y_comp = Column(CHAR(5)) # 市场综合3年评级
    mornstar_3y =  Column(CHAR(5)) # 晨星3年评级
    mornstar_5y =  Column(CHAR(5)) # 晨星5年评级
    merchant_3y = Column(CHAR(5)) # 招商3年评级
    tx_comp = Column(CHAR(5)) # 天相投顾综合评级
    sh_3y_comp = Column(CHAR(5)) #上海证券3年评级(综合评级)
    sh_3y_stock = Column(CHAR(5)) #上海证券3年评级(选股能力)
    sh_3y_timeret = Column(CHAR(5)) #上海证券3年评级(择时能力)
    sh_3y_sharpe = Column(CHAR(5)) #上海证券3年评级(夏普比率)
    sh_5y_comp = Column(CHAR(5)) #上海证券5年评级(综合评级)
    sh_5y_stock = Column(CHAR(5)) #上海证券5年评级(选股能力)
    sh_5y_timeret = Column(CHAR(5)) #上海证券5年评级(择时能力)
    sh_5y_sharpe = Column(CHAR(5)) #上海证券5年评级(夏普比率)
    jian_comp = Column(CHAR(5)) #济安金信基金评级(综合评级)
    jian_earn = Column(CHAR(5)) #济安金信基金评级(盈利能力)
    jian_stable = Column(CHAR(5)) #济安金信基金评级(业绩稳定性)
    jian_risk = Column(CHAR(5)) #济安金信基金评级(抗风险能力)
    jian_stock = Column(CHAR(5)) #济安金信基金评级(选股能力)
    jian_timeret = Column(CHAR(5)) #济安金信基金评级(择时能力)
    jian_track = Column(CHAR(5)) #济安金信基金评级(基准跟踪能力)
    jian_alpha = Column(CHAR(5)) #济安金信基金评级(超额收益能力)
    jian_fee = Column(CHAR(5)) #济安金信基金评级(整体费用)

class FundHoldAsset(Base):
    '''基金持仓资产比例'''

    __tablename__ = 'fund_hold_asset'

    fund_id = Column(CHAR(10), primary_key=True)  # 基金id
    datetime = Column(DATE, primary_key=True)  # 日期
    stock_nav_ratio = Column(DOUBLE(asdecimal=False)) # 股票市值占基金资产净值比
    bond_nav_ratio = Column(DOUBLE(asdecimal=False)) # 债券市值占基金资产净值比
    fund_nav_ratio = Column(DOUBLE(asdecimal=False)) # 基金市值占基金资产净值比
    cash_nav_ratio = Column(DOUBLE(asdecimal=False)) # 银行存款占基金资产净值比
    other_nav_ratio = Column(DOUBLE(asdecimal=False)) # 其他资产占基金资产净值比
    first_repo_to_nav = Column(DOUBLE(asdecimal=False))  # 报告期内债券回购融资余额占基金资产净值比例
    avg_ptm = Column(DOUBLE(asdecimal=False))  # 报告期末投资组合平均剩余期限

    __table_args__ = (
        Index('idx_fund_hold_asset_datetime', 'datetime'),
    )

class FundHoldIndustry(Base):
    '''基金持仓前三行业'''

    __tablename__ = 'fund_hold_industry'

    fund_id = Column(CHAR(10), primary_key=True) # 基金ID
    datetime = Column(DATE, primary_key=True) # 日期
    rank1_indname = Column(CHAR(50)) #第一排名行业名称
    rank1_indweight = Column(DOUBLE(asdecimal=False)) #第一排名行业市值占基金资产总值比
    rank2_indname = Column(CHAR(50)) #第二排名行业名称
    rank2_indweight = Column(DOUBLE(asdecimal=False)) #第二排名行业市值占基金资产总值比
    rank3_indname = Column(CHAR(50)) #第三排名行业名称
    rank3_indweight = Column(DOUBLE(asdecimal=False)) #第三排名行业市值占基金资产总值比

class FundHoldStock(Base):
    '''基金持仓前十股票'''

    __tablename__ = 'fund_hold_stock'

    fund_id = Column(CHAR(10), primary_key=True) # 基金ID
    datetime = Column(DATE, primary_key=True) # 日期
    rank1_stock = Column(TEXT) #股票名
    rank1_stock_code = Column(TEXT)  # 股票ID
    rank1_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank1_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank2_stock = Column(TEXT) #股票名
    rank2_stock_code = Column(TEXT)  # 股票ID
    rank2_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank2_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank3_stock = Column(TEXT) #股票名
    rank3_stock_code = Column(TEXT)  # 股票ID
    rank3_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank3_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank4_stock = Column(TEXT) #股票名
    rank4_stock_code = Column(TEXT)  # 股票ID
    rank4_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank4_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank5_stock = Column(TEXT) #股票名
    rank5_stock_code = Column(TEXT)  # 股票ID
    rank5_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank5_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank6_stock = Column(TEXT) #股票名
    rank6_stock_code = Column(TEXT)  # 股票ID
    rank6_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank6_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank7_stock = Column(TEXT) #股票名
    rank7_stock_code = Column(TEXT)  # 股票ID
    rank7_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank7_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank8_stock = Column(TEXT) #股票名
    rank8_stock_code = Column(TEXT)  # 股票ID
    rank8_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank8_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank9_stock = Column(TEXT) #股票名
    rank9_stock_code = Column(TEXT)  # 股票ID
    rank9_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank9_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank10_stock = Column(TEXT) #股票名
    rank10_stock_code = Column(TEXT)  # 股票ID
    rank10_stockval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank10_stockweight = Column(DOUBLE(asdecimal=False)) #持仓权重

class FundHoldBond(Base):
    '''东财基金重仓债'''

    __tablename__ = 'fund_hold_bond'
    fund_id = Column(CHAR(20), primary_key=True) # 基金ID
    datetime = Column(DATE, primary_key=True) # 日期
    rank1_bond = Column(CHAR(60)) #债券名
    rank1_bond_code =  Column(CHAR(60)) # 债券id
    rank1_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank1_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank2_bond = Column(CHAR(60)) #债券名
    rank2_bond_code =  Column(CHAR(60)) # 债券id
    rank2_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank2_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank3_bond = Column(CHAR(60)) #债券名
    rank3_bond_code =  Column(CHAR(60)) # 债券id
    rank3_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank3_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank4_bond = Column(CHAR(60)) #债券名
    rank4_bond_code =  Column(CHAR(60)) # 债券id
    rank4_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank4_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank5_bond = Column(CHAR(60)) #债券名
    rank5_bond_code =  Column(CHAR(60)) # 债券id
    rank5_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank5_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank6_bond = Column(CHAR(60)) #债券名
    rank6_bond_code =  Column(CHAR(60)) # 债券id
    rank6_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank6_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank7_bond = Column(CHAR(60)) #债券名
    rank7_bond_code =  Column(CHAR(60)) # 债券id
    rank7_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank7_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank8_bond = Column(CHAR(60)) #债券名
    rank8_bond_code =  Column(CHAR(60)) # 债券id
    rank8_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank8_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank9_bond = Column(CHAR(60)) #债券名
    rank9_bond_code =  Column(CHAR(60)) # 债券id
    rank9_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank9_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重
    rank10_bond = Column(CHAR(60)) #债券名
    rank10_bond_code =  Column(CHAR(60)) # 债券id
    rank10_bondval = Column(DOUBLE(asdecimal=False)) #持仓市值
    rank10_bondweight = Column(DOUBLE(asdecimal=False)) #持仓权重

class FundStockPortfolio(Base):
    '''基金的股票全部持仓'''

    __tablename__ = 'fund_stock_portfolio'

    fund_id = Column(CHAR(10), primary_key=True)  # 基金代码
    datetime = Column(DATE, primary_key=True)  # 报告期
    stock_id = Column(CHAR(10), primary_key=True)  # 股票代码
    hold_number = Column(DOUBLE(asdecimal=True), nullable=False)  # 持股数量(万股)
    semi_change = Column(DOUBLE(asdecimal=True))  # 半年度持股变动(万股)
    stock_mv = Column(DOUBLE(asdecimal=True))  # 持股市值(万元)
    net_asset_ratio = Column(DOUBLE(asdecimal=True))  # 占净值比(%)
    mv_ratio = Column(DOUBLE(asdecimal=True))  # 占股票投资市值比(%)

class MngInfo(Base):
    '''基金经理信息表'''

    __tablename__ = 'mng_info'

    start_mng_date = Column(DATE, primary_key=True) # 最早任职基金经理日期
    mng_name = Column(CHAR(25), primary_key=True) # 基金经理
    fund_id = Column(CHAR(10), primary_key=True) # 代码
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
        Index('idx_mng_info_fund_id', 'fund_id'),
    )

class FundMngChange(Base):
    '''基金经理变更表'''

    __tablename__ = 'fund_mng_change'

    fund_id = Column(CHAR(10), primary_key=True) # 代码
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

class FundCompMngChange(Base):
    '''基金公司经理变更表'''

    __tablename__ = 'fund_comp_mng_change'

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
    
class FundCompCoreMng(Base):
    '''基金公司核心人员稳定性'''

    __tablename__ = 'fund_comp_core_mng'

    fund_id = Column(CHAR(10), primary_key=True) # 代码
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

class AssetInfo(Base):
    '''大类资产对应信息'''

    __tablename__ = 'asset_info'

    asset_id = Column(CHAR(40), primary_key=True) # 代码
    real_id = Column(CHAR(20), primary_key=True) # 真实代码
    asset_name = Column(CHAR(15)) # 资产名
    real_name = Column(CHAR(40)) # 真实名字
    asset_type = Column(CHAR(10)) # 资产名

class FundIPOStats(Base):
    '''基金打新收益率统计'''

    __tablename__ = 'fund_ipo_stats'

    fund_id = Column(CHAR(10), primary_key=True) # 代码
    end_date = Column(DATE, primary_key=True) # 结束统计日
    ipo_allocation_num = Column(Integer) # 打中新股数量
    ipo_allocation_share_num = Column(DOUBLE(asdecimal=False)) # 累计获配股数(万股)
    ipo_allocation_amount = Column(DOUBLE(asdecimal=False)) # 累计获配金额(万元)
    ipo_allocation_ret = Column(DOUBLE(asdecimal=False)) # 打新收益率(%)
    start_date = Column(DATE)  # 开始统计日期
    size = Column(DOUBLE(asdecimal=False)) # 基金规模
    ipo_allocation_weight = Column(DOUBLE(asdecimal=False)) # 基金打新比例

class FundConvStats(Base):
    '''基金可转债比例'''

    __tablename__ = 'fund_conv_stats'

    fund_id = Column(CHAR(10), primary_key=True) # 代码
    datetime = Column(DATE, primary_key=True) # 日期
    conv_weights = Column(DOUBLE(asdecimal=False)) # 可转债权重

class FundOpenInfo(Base):
    '''基金定开信息'''

    __tablename__ = 'fund_open_info'

    fund_id = Column(CHAR(10), primary_key=True) # 代码
    desc_name = Column(CHAR(64)) # 基金名称

class StockInFund(Base):
    '''基金重仓股'''

    __tablename__ = 'stock_in_fund'

    fund_id = Column(CHAR(10), primary_key=True)  # 基金代码
    stock_id = Column(CHAR(10), primary_key=True) # 股票代码
    datetime = Column(DATE, primary_key=True) # 日期
    stock_name = Column(CHAR(64)) # 股票名称
    stock_weight = Column(DOUBLE(asdecimal=False)) # 股票在基金权重
    fund_name = Column(CHAR(64)) # 基金名称

class BondInFund(Base):
    '''基金重仓债'''

    __tablename__ = 'bond_in_fund'

    fund_id = Column(CHAR(10), primary_key=True)  # 基金代码
    bond_id = Column(CHAR(10), primary_key=True) # 债券代码
    datetime = Column(DATE, primary_key=True) # 日期
    bond_name = Column(CHAR(64)) # 债券名称
    bond_weight = Column(DOUBLE(asdecimal=False)) # 债券在基金权重
    fund_name = Column(CHAR(64)) # 基金名称
    
class OverseaFundInfo(Base):
    '''海外基金信息表'''

    __tablename__ = 'oversea_fund_info'

    codes = Column(CHAR(25), primary_key=True)  # 基金id
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

class OverseaFundNav(Base):
    '''海外基金信息表'''

    __tablename__ = 'oversea_fund_nav'

    codes = Column(CHAR(25), primary_key=True)  # 基金id
    datetime = Column(DATE, primary_key=True) # 日期
    nav = Column(DOUBLE(asdecimal=False)) # 净值

class ETFInfo(Base):

    __tablename__ = 'etf_info'

    fund_id = Column(CHAR(10), primary_key=True)  # 基金代码
    desc_name = Column(CHAR(64)) # 基金名称
    wind_class_1 = Column(CHAR(64)) # Wind基金类型
    wind_class_2 = Column(CHAR(64)) # Wind基金二级类型
    index_id = Column(CHAR(20)) # 指数id
    company_id = Column(CHAR(64)) # 基金公司
    etf_type = Column(CHAR(10)) # 场内场外类型
    index_name = Column(CHAR(64)) # 指数名称

class StockTag(Base):

    __tablename__ = 'stock_tag'

    tag_id = Column(CHAR(32), primary_key=True)  #标签id
    stock_id = Column(CHAR(10), primary_key=True) # 股票id
    tag_group_id = Column(CHAR(32), primary_key=True) # 标签组名 source_type_ymd
    tag_name = Column(CHAR(64)) # 标签名

class FundTag(Base):

    __tablename__ = 'fund_tag'

    tag_id = Column(CHAR(32), primary_key=True)  #标签id
    fund_id = Column(CHAR(10), primary_key=True) # 基金id
    tag_group_id = Column(CHAR(32), primary_key=True) # 标签组名 source_type_ymd
    tag_name = Column(CHAR(64)) # 标签名


class HedgeFundAlias(FOFBase):
    '''私募基金别名'''

    __tablename__ = 'hedge_fund_alias'

    fund_id_alias = Column(CHAR(16), primary_key=True)  # 私募基金ID别名
    manager_id = Column(CHAR(32), primary_key=True)  # 管理端ID
    fund_id = Column(CHAR(16))  # 基金ID


class HedgeFundNAV(FOFBase):
    '''私募基金净值'''

    __tablename__ = 'hedge_fund_nav'

    fund_id = Column(CHAR(16), primary_key=True)  # 基金ID
    datetime = Column(DATE, primary_key=True)  # 日期
    insert_time = Column(DATETIME, primary_key=True)  # 插入时间
    calc_date = Column(DATE)  # 计算日期
    net_asset_value = Column(DOUBLE(asdecimal=False))  # 单位净值
    acc_unit_value = Column(DOUBLE(asdecimal=False))  # 累计净值
    adjusted_net_value = Column(DOUBLE(asdecimal=False)) # 复权净值
    v_net_value = Column(DOUBLE(asdecimal=False))  # 单位净值的虚拟后净值
    change_rate = Column(DOUBLE(asdecimal=False))   # 涨跌幅
    ta_factor = Column(DOUBLE(asdecimal=False))   # 复权因子

    # 不能加这个 会影响fof backend项目
    # __table_args__ = (
    #     Index('idx_hedge_fund_nav_datetime', 'datetime'),
    # )


class HedgeFundInfo(FOFBase):
    '''私募基金信息'''

    __tablename__ = 'hedge_fund_info'

    fund_id = Column(CHAR(16), primary_key=True)  # 基金ID
    fund_name = Column(TEXT, nullable=False)  # 基金名称
    brief_name = Column(TEXT, nullable=False)  # 基金简称
    company = Column(VARCHAR(256))                                                   # 公司名称
    net_asset_value = Column(DOUBLE(asdecimal=False))                                # 单位净值
    acc_unit_value = Column(DOUBLE(asdecimal=False))                                 # 累计净值
    adjusted_net_value = Column(DOUBLE(asdecimal=False))                             # 复权净值
    invest_strategy = Column(VARCHAR(256))                                           # 投资策略
    manager_id = Column(CHAR(16), nullable=False)  # 私募基金公司ID
    incentive_fee_mode = Column(TEXT)  # 业绩报酬计提方法
    incentive_fee_ratio = Column(DOUBLE(asdecimal=False))  # 业绩计提比例
    incentive_fee_type = Column(VARCHAR(31))                                          # 业绩提取方式
    incentive_fee_str = Column(VARCHAR(255))                                          # 业绩提取细则
    incentive_fee_date = Column(CHAR(20))                                          # 业绩提取日期
    v_nav_decimals = Column(SMALLINT, nullable=False)  # 虚拟净值精度
    size = Column(DOUBLE(asdecimal=False))  # 基金规模
    manager = Column(TEXT)  # 私募基金经理
    stars = Column(Integer, server_default=text('1'))  # 星级
    lock_in_period = Column(Integer)                                                    # 封闭期
    found_date = Column(DATE)                                                           # 成立时间
    fund_adviser = Column(VARCHAR(31))                                                  # 投资顾问
    records_no = Column(VARCHAR(127))                                                   # 备案编号
    records_date = Column(CHAR(20))                                                     # 备案日期
    deposit_security = Column(VARCHAR(63))                                              # 托管券商
    open_date = Column(CHAR(20))                                                        # 开放日
    warning_line = Column(DOUBLE(asdecimal=False))                                      # 预警线
    closeout_line = Column(DOUBLE(asdecimal=False))                                     # 平仓线
    management_fee = Column(DOUBLE(asdecimal=False))                                    # 管理费率
    custodian_fee = Column(DOUBLE(asdecimal=False))                                     # 托管费率
    administrative_fee = Column(DOUBLE(asdecimal=False))                                # 行政管理费率
    purchase_fee = Column(DOUBLE(asdecimal=False))                                      # 申购费
    redeem_fee = Column(DOUBLE(asdecimal=False))                                        # 赎回费
    purchase_confirmed = Column(Integer)                                                # 申购确认
    purchase_done = Column(Integer)                                                     # 申购交收
    redeem_confirmed = Column(Integer)                                                  # 赎回确认
    redeem_done = Column(Integer)                                                       # 赎回交收
    latest_cal_date = Column(DATETIME)                                                  # 最新净值日
    mdd = Column(DOUBLE(asdecimal=False))                                               # 最大回撤
    ret = Column(DOUBLE(asdecimal=False))                                               # 成立以来收益率
    year_to_now_ret = Column(DOUBLE(asdecimal=False))                                   # 今年以来收益率
    ann_ret = Column(DOUBLE(asdecimal=False))                                           # 年化收益率


# class HedgeFundMgrInfo(Base):
#     '''私募基金公司信息'''

#     __tablename__ = 'hedge_fund_mgr_info'

#     manager_id = Column(CHAR(16), primary_key=True) # 私募基金公司ID
#     manager_name = Column(TEXT, nullable=False)  # 私募基金公司名称


class FOFInfo(FOFBase):
    '''fof产品信息'''

    __tablename__ = 'fof_info'

    fof_id = Column(CHAR(16), primary_key=True)             # 产品ID
    desc_id = Column(CHAR(31))                              # 展示ID
    manager_id = Column(VARCHAR(32), primary_key=True)      # 管理端ID
    datetime = Column(CHAR(16))                             # 数据日期（以支持更新操作）
    fof_name = Column(TEXT, nullable=False)                 # 产品名称
    desc_name = Column(CHAR(31))                            # 简称
    admin = Column(TEXT)                                    # 管理人
    established_date = Column(DATE)                         # 成立日期
    running_start_date = Column(DATE)                       # 实际运作起始日期
    fof_status = Column(CHAR(16))                           # 申赎状态等
    subscription_fee = Column(TEXT)                         # 认购费率
    purchase_fee = Column(TEXT)                             # 申购费率
    redemption_fee = Column(TEXT)                           # 赎回费率
    sale_proxy_fee = Column(TEXT)                           # 代销费率
    management_fee = Column(DOUBLE(asdecimal=False))        # 管理费率
    custodian_fee = Column(DOUBLE(asdecimal=False))         # 托管费率
    min_custodian_fee_amt = Column(DOUBLE(asdecimal=False)) # 托管费率最小金额
    administrative_fee = Column(DOUBLE(asdecimal=False))    # 行政管理费率
    min_admin_fee_amt = Column(DOUBLE(asdecimal=False))     # 行政管理费率最小金额
    lock_up_period = Column(TEXT)                           # 锁定期
    stop_loss = Column(TEXT)                                # 预警/止损配置
    incentive_fee_mode = Column(Integer)                    # 业绩报酬计提方法
    incentive_fee_type = Column(VARCHAR(31))                # 业绩报酬计提类型
    incentive_fee_str = Column(VARCHAR(255))                # 业绩报酬提取规则
    incentive_fee_time = Column(TEXT)                       # 业绩报酬提取时点
    current_deposit_rate = Column(DOUBLE(asdecimal=False))  # 银行活期存款利率
    purchase_redeem_appointment = Column(TEXT)              # 预约申赎机制
    force_redemption = Column(TEXT)                         # 违约赎回机制
    huge_redemption_thres = Column(DOUBLE(asdecimal=False)) # 巨额赎回认定比例
    dividend_distribution = Column(TEXT)                    # 分红分配方式
    initial_raised_fv = Column(DOUBLE(asdecimal=False))     # 初始募集面值
    initial_net_value = Column(DOUBLE(asdecimal=False))     # 期初总资产净值
    total_volume = Column(DOUBLE(asdecimal=False))          # 总资产份额
    total_amount = Column(DOUBLE(asdecimal=False))          # 资产总额
    net_asset_value = Column(DOUBLE(asdecimal=False))       # 单位净值
    acc_unit_value = Column(DOUBLE(asdecimal=False))        # 累计净值
    adjusted_net_value = Column(DOUBLE(asdecimal=False))    # 复权净值
    ret_year_to_now = Column(DOUBLE(asdecimal=False))       # 今年以来收益率
    ret_total = Column(DOUBLE(asdecimal=False))             # 总收益率
    ret_ann = Column(DOUBLE(asdecimal=False))               # 总收益率年化
    mdd = Column(DOUBLE(asdecimal=False))                   # 最大回撤
    sharpe = Column(DOUBLE(asdecimal=False))                # 夏普比率
    vol = Column(DOUBLE(asdecimal=False))                   # 波动率
    is_calculating = Column(BOOLEAN, default=False)         # 是否正在计算
    latest_cal_date = Column(DATE)                          # 最新净值日
    strategy_type = Column(Integer)                         # 策略类型
    sub_strategy_type = Column(VARCHAR(31))                 # 子策略类型
    risk_type = Column(Integer)                             # 风险等级
    is_on_sale = Column(BOOLEAN, default=False)             # 是否上架
    is_fof = Column(BOOLEAN, default=False)                 # 是否为fof计算产品
    is_top = Column(BOOLEAN, default=False)                 # 是否置顶
    benchmark = Column(VARCHAR(63))                         # 默认业绩基准
    asset_type = Column(VARCHAR(63))                        # 产品类型
    nav_decimals = Column(SMALLINT)                         # 净值精度
    nav_freq = Column(VARCHAR(31))                          # 净值频率
    fund_no = Column(CHAR(6))                               # 基金编号
    management_ids = Column(VARCHAR(255))                   # 所属机构ID
    filing_date = Column(DATE)                              # 备案时间
    filing_stage = Column(VARCHAR(16))                      # 基金备案阶段
    fund_type = Column(VARCHAR(16))                         # 基金类型
    currency_type = Column(VARCHAR(16))                     # 币种
    management_type = Column(VARCHAR(16))                   # 管理类型
    custodian_name = Column(VARCHAR(128))                   # 托管人名称
    fund_status = Column(VARCHAR(16))                       # 运作状态
    fof_manager = Column(VARCHAR(16))                       # 基金经理
    benchmark_index = Column(VARCHAR(127))                  # 基准指数
    open_date = Column(CHAR(63))                            # 开放日
    temp_open_times = Column(TEXT)                          # 临时开放次数
    stars = Column(Integer, server_default=text('1'))       # 星级
    is_structured = Column(BOOLEAN, default=False)          # 是否是分级基金
    main_fof_id = Column(VARCHAR(32))                       # 主ID
    last_increase_rate = Column(DOUBLE(asdecimal=False))    # 涨跌幅
    last_before_date = Column(DATE)                         # 前净值日
    has_nav = Column(BOOLEAN, default=False)                # 是否存在净值


class FOFScaleAlteration(FOFBase):
    '''fof规模变动记录'''

    __tablename__ = 'fof_scale_alteration'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fof_id = Column(CHAR(16), primary_key=True)  # 产品ID
    manager_id = Column(VARCHAR(32))  # 管理端ID
    datetime = Column(DATE, primary_key=True)  # 确认日期
    investor_id = Column(CHAR(16), nullable=False)  # 投资人ID
    applied_date = Column(DATE)  # 申请日期
    deposited_date = Column(DATE)  # 交割日期
    amount = Column(DOUBLE(asdecimal=False))  # 被申购金额
    share = Column(DOUBLE(asdecimal=False))  # 被赎回份额
    nav = Column(DOUBLE(asdecimal=False))  # 交易净值
    status = Column(Integer, nullable=False)  # 状态：在途/完成
    event_type = Column(Integer)                            # 交易类型
    asset_type = Column(Enum(HoldingAssetType), nullable=False)  # 资产类型


class FOFAssetAllocation(FOFBase):
    '''fof资产配置记录'''

    __tablename__ = 'fof_asset_allocation'

    fof_id = Column(CHAR(16), primary_key=True)                     # 产品ID
    manager_id = Column(CHAR(32), primary_key=True)                 # 管理端ID
    datetime = Column(DATE, primary_key=True)                       # 日期
    fund_id = Column(CHAR(16), primary_key=True, nullable=False)    # 申购/赎回基金ID
    id = Column(Integer, primary_key=True, autoincrement=True)
    trade_num = Column(VARCHAR(255))                                # 备案编号
    asset_type = Column(Enum(HoldingAssetType), nullable=False)     # 资产类型
    amount = Column(DOUBLE(asdecimal=False))                        # 交易金额
    share = Column(DOUBLE(asdecimal=False))                         # 交易份额
    nav = Column(DOUBLE(asdecimal=False))                           # 交易净值
    acc_net_value = Column(DOUBLE(asdecimal=False))                 # 累计净值
    status = Column(Enum(FundStatus), nullable=False)               # 状态：在途/完成
    confirmed_date = Column(DATE)                                   # 确认日期
    deposited_date = Column(DATE)                                   # 交割日期
    event_type = Column(Integer)                                    # 事件类型
    water_line = Column(DOUBLE(asdecimal=False))                    # 水位线(一般是累计净值; 但整体高水位法下与累计净值可能不同)
    remark = Column(VARCHAR(255))                                   # 备注


class FOFManually(FOFBase):
    '''fof手工校正数据'''

    __tablename__ = 'fof_manually'

    fof_id = Column(CHAR(16), primary_key=True)  # 产品ID
    datetime = Column(DATE, primary_key=True)  # 日期
    fee_transfer = Column(DOUBLE(asdecimal=False))  # 费用划拨
    cd_interest_transfer = Column(DOUBLE(asdecimal=False))  # 银行活期存款利息扣除
    other_fees = Column(DOUBLE(asdecimal=False))  # 其他费用划拨
    management_fee_error = Column(DOUBLE(asdecimal=False))  # 管理费误差
    custodian_fee_error = Column(DOUBLE(asdecimal=False))  # 托管费误差
    admin_service_fee_error = Column(DOUBLE(asdecimal=False))  # 行政服务费误差


class FOFInvestorInfo(Base):
    '''fof投资人信息'''

    __tablename__ = 'fof_investor_info'

    investor_id = Column(CHAR(16), primary_key=True)  # 客户合同号(投资人ID)
    manager_id = Column(VARCHAR(32))  # 管理端ID
    investor_name = Column(CHAR(8), nullable=False)  # 姓名


class FOFInvestorPosition(FOFBase):
    '''fof投资人持仓信息(最新快照)'''

    __tablename__ = 'fof_investor_position'

    investor_id = Column(CHAR(16), primary_key=True)  # 投资人ID
    manager_id = Column(CHAR(32), primary_key=True)  # 管理端ID
    fof_id = Column(CHAR(16), primary_key=True)  # 产品ID
    datetime = Column(DATE, nullable=False)  # 日期
    v_nav = Column(DOUBLE(asdecimal=False))  # 对应到投资人的虚拟净值
    cost_nav = Column(DOUBLE(asdecimal=False))  # 投资人的平均成本
    mv = Column(DOUBLE(asdecimal=False))  # 总市值
    amount = Column(DOUBLE(asdecimal=False))  # 总投资额
    shares = Column(DOUBLE(asdecimal=False))  # 总份额
    total_ret = Column(DOUBLE(asdecimal=False))  # 累计收益
    details = Column(TEXT)  # 持仓详细信息


class FOFInvestorPositionSummary(FOFBase):
    '''fof投资人持仓信息'''

    __tablename__ = 'fof_investor_position_summary'

    investor_id = Column(CHAR(16), primary_key=True)  # 投资人ID
    manager_id = Column(CHAR(32), primary_key=True)  # 管理端ID
    datetime = Column(DATE, primary_key=True)  # 日期
    mv = Column(DOUBLE(asdecimal=False))  # 总市值(总资产)
    amount = Column(DOUBLE(asdecimal=False))  # 总投资额(总本金)
    left_amount = Column(DOUBLE(asdecimal=False))  # 剩余本金
    shares = Column(DOUBLE(asdecimal=False))  # 总份额
    left_shares = Column(DOUBLE(asdecimal=False))  # 剩余份额
    total_ret = Column(DOUBLE(asdecimal=False))  # 累计收益
    total_rr = Column(DOUBLE(asdecimal=False))  # 累计收益率


class FOFIncidentalStatement(FOFBase):

    """杂项流水记录"""

    __tablename__ = 'fof_incidental_statement'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fof_id = Column(CHAR(16), primary_key=True)                     # 产品ID
    manager_id = Column(CHAR(32), primary_key=True)                 # 管理端ID
    datetime = Column(DATE)                                         # 日期
    trade_num = Column(CHAR(128))                                   # 流水编号
    event_type = Column(Integer)                                    # 事件类型
    amount = Column(DOUBLE(asdecimal=False))                        # 金额
    remark = Column(VARCHAR(255))                                   # 备注


class FOFAccountStatement(FOFBase):

    """账户流水"""

    __tablename__ = 'fof_account_statement'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fof_id = Column(CHAR(16), primary_key=True)                     # 产品ID
    manager_id = Column(CHAR(32), primary_key=True)                 # 管理端ID
    datetime = Column(DATE)                                         # 日期
    trade_num = Column(CHAR(128))                                   # 流水编号
    event_type = Column(Integer)                                    # 事件类型
    amount = Column(DOUBLE(asdecimal=False))                        # 金额
    remain_cash = Column(DOUBLE(asdecimal=False))                   # 账户余额
    remark = Column(VARCHAR(255))                                   # 备注


class FOFTransitMoney(FOFBase):
    """在途资金"""
    __tablename__ = 'fof_transit_money'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fof_id = Column(CHAR(16), primary_key=True)                             # 产品ID
    fund_id = Column(CHAR(20))                                              # 基金ID
    confirmed_datetime = Column(DATE)                                       # 确认时间
    event_type = Column(Integer)                                            # 事件类型
    amount = Column(DOUBLE(asdecimal=False))                                # 金额
    transit_cash = Column(DOUBLE(asdecimal=False))                          # 在途资金总额
    remark = Column(VARCHAR(255))                                           # 备注


class FOFEstimateInterest(FOFBase):
    """预估利息"""

    __tablename__ = 'fof_estimate_interest'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fof_id = Column(CHAR(16), primary_key=True)                 # 产品ID
    manager_id = Column(CHAR(32), primary_key=True)             # 管理端ID
    date = Column(DATE)                                         # 日期
    remain_cash = Column(DOUBLE(asdecimal=False))               # 当日余额
    interest = Column(DOUBLE(asdecimal=False))                  # 利息
    remark = Column(VARCHAR(255))                               # 备注
    total_interest = Column(DOUBLE(asdecimal=False))            # 总利息


class FOFEstimateFee(FOFBase):
    """预估计提费"""
    __tablename__ = 'fof_estimate_fee'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fof_id = Column(CHAR(16), primary_key=True)  # 产品ID
    date = Column(DATE)  # 日期
    pre_market_value = Column(DOUBLE(asdecimal=False))          # 前一日净资产总额
    management_fee = Column(DOUBLE(asdecimal=False))            # 管理费
    total_management_fee = Column(DOUBLE(asdecimal=False))      # 累计管理费
    custodian_fee = Column(DOUBLE(asdecimal=False))             # 托管费
    total_custodian_fee = Column(DOUBLE(asdecimal=False))       # 累计管理费
    administrative_fee = Column(DOUBLE(asdecimal=False))        # 行政管理费
    total_administrative_fee = Column(DOUBLE(asdecimal=False))  # 累计行政管理费
    is_down = Column(BOOLEAN, default=False)                    # 是否结算
    remark = Column(VARCHAR(255))                               # 备注


class FOFRealAccountStatement(FOFBase):
    """账户流水"""
    __tablename__ = 'fof_account_statement_real'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fof_id = Column(CHAR(16), primary_key=True)                     # 产品ID
    datetime = Column(DATETIME)                                     # 时间
    trade_num = Column(CHAR(128))                                   # 流水编号
    event_type = Column(Integer)                                    # 事件类型
    amount = Column(DOUBLE(asdecimal=False))                        # 金额
    remain_cash = Column(DOUBLE(asdecimal=False))                   # 账户余额
    remark = Column(VARCHAR(255))                                   # 备注


class FOFRealTransitMoney(FOFBase):
    """在途资金"""
    __tablename__ = 'fof_transit_money_real'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fof_id = Column(CHAR(16), primary_key=True)                             # 产品ID
    fund_id = Column(CHAR(20))                                              # 基金ID
    confirmed_datetime = Column(DATE)                                       # 确认时间
    event_type = Column(Integer)                                            # 事件类型
    amount = Column(DOUBLE(asdecimal=False))                                # 金额
    transit_cash = Column(DOUBLE(asdecimal=False))                          # 在途资金总额
    remark = Column(VARCHAR(255))                                           # 备注


class FOFRealEstimateInterest(FOFBase):
    """预估利息"""

    __tablename__ = 'fof_estimate_interest_real'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fof_id = Column(CHAR(16), primary_key=True)                 # 产品ID
    date = Column(DATE)                                         # 日期
    remain_cash = Column(DOUBLE(asdecimal=False))               # 当日余额
    interest = Column(DOUBLE(asdecimal=False))                  # 利息
    remark = Column(VARCHAR(255))                               # 备注
    total_interest = Column(DOUBLE(asdecimal=False))            # 总利息


class FOFRealEstimateFee(FOFBase):
    """预估计提费"""
    __tablename__ = 'fof_estimate_fee_real'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fof_id = Column(CHAR(16), primary_key=True)  # 产品ID
    date = Column(DATE)  # 日期
    pre_market_value = Column(DOUBLE(asdecimal=False))          # 前一日净资产总额
    management_fee = Column(DOUBLE(asdecimal=False))            # 管理费
    total_management_fee = Column(DOUBLE(asdecimal=False))      # 累计管理费
    custodian_fee = Column(DOUBLE(asdecimal=False))             # 托管费
    total_custodian_fee = Column(DOUBLE(asdecimal=False))       # 累计管理费
    administrative_fee = Column(DOUBLE(asdecimal=False))        # 行政管理费
    total_administrative_fee = Column(DOUBLE(asdecimal=False))  # 累计行政管理费
    is_down = Column(BOOLEAN, default=False)                    # 是否结算
    remark = Column(VARCHAR(255))                               # 备注


class FOFOtherRecord(FOFBase):
    """其他记录"""
    __tablename__ = 'fof_other_record'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fof_id = Column(CHAR(16), primary_key=True)                     # 产品ID
    date = Column(DATE)                                             # 日期
    event_type = Column(Integer)                                    # 事件类型
    amount = Column(DOUBLE(asdecimal=False))                        # 金额
    remark = Column(VARCHAR(255))                                   # 备注


class FOFAssertCorrect(FOFBase):
    """净资产修正"""
    __tablename__ = 'fof_assert_correct'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fof_id = Column(CHAR(16), primary_key=True)                     # 产品ID
    manager_id = Column(CHAR(32), primary_key=True)                 # 管理端ID
    date = Column(DATE)                                             # 日期
    amount = Column(DOUBLE(asdecimal=False))                        # 金额
    remark = Column(VARCHAR(255))                                   # 备注


class EMailParserInfo(FOFBase):
    ''' parser 信息表'''

    __tablename__ = 'email_parser_info'

    id = Column(Integer, primary_key=True, autoincrement=True)  # parser ID
    manager_id = Column(CHAR(32))  # 管理端ID
    p_name = Column(TEXT)                      # parser name
    p_desc = Column(TEXT)                      # parser 描述
    p_type = Column(Integer, nullable=False)                   # parser 类型


class EMailParserCode(FOFBase):
    ''' parser 代码表'''

    __tablename__ = 'email_parser_code'

    id = Column(Integer, primary_key=True, autoincrement=True)  # parser ID
    manager_id = Column(CHAR(32))  # 管理端ID
    p_code = Column(TEXT, nullable=False)                            # parser 代码


class EMailParserExec(FOFBase):
    ''' parser 执行信息'''

    __tablename__ = 'email_parser_exec'

    id = Column(Integer, primary_key=True, autoincrement=True)  # parser ID
    manager_id = Column(CHAR(32), unique=True)  # 管理端ID
    p_priority_info = Column(TEXT, nullable=False)                   # parser 优先级信息 JSON 格式


class HedgeFundEmailRaw(FOFBase):
    '''私募基金(净值)邮件原始数据'''

    __tablename__ = 'hedge_fund_email_raw'

    manager_id = Column(CHAR(32), primary_key=True)  # 管理端ID
    fof_id = Column(CHAR(16), primary_key=True)  # FOF ID
    fund_id = Column(CHAR(16), primary_key=True)  # 基金ID
    datetime = Column(DATE, primary_key=True)  # 日期
    nav = Column(DOUBLE(asdecimal=False))  # 单位净值
    acc_net_value = Column(DOUBLE(asdecimal=False))  # 累计净值
    v_nav = Column(DOUBLE(asdecimal=False))  # 单位净值的虚拟后净值
