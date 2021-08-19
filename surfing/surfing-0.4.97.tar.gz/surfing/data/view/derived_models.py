
import datetime

from sqlalchemy import CHAR, Column, Integer, Index, BOOLEAN, text, TEXT, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import DOUBLE, DATE, DATETIME, SMALLINT
from sqlalchemy.sql.sqltypes import INTEGER

from ...constant import StockFactorType, IndClassType, HoldingAssetType


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


class IndexVolatility(Base):
    '''指数波动率'''

    __tablename__ = 'index_volatility'

    index_id = Column(CHAR(20), primary_key=True) # 指数ID
    datetime = Column(DATE, primary_key=True) # 日期
    w1_vol = Column(DOUBLE(asdecimal=False)) # 近一周波动率
    m1_vol = Column(DOUBLE(asdecimal=False)) # 近一月波动率
    m3_vol = Column(DOUBLE(asdecimal=False)) # 近三月波动率
    m6_vol = Column(DOUBLE(asdecimal=False)) # 近半年波动率
    y1_vol = Column(DOUBLE(asdecimal=False)) # 近一年波动率
    y3_vol = Column(DOUBLE(asdecimal=False)) # 近三年波动率
    y5_vol = Column(DOUBLE(asdecimal=False)) # 近五年波动率
    y10_vol = Column(DOUBLE(asdecimal=False)) # 近十年波动率
    this_y_vol = Column(DOUBLE(asdecimal=False)) # 今年以来波动率
    this_s_vol = Column(DOUBLE(asdecimal=False)) # 本季度以来波动率
    cumulative_vol = Column(DOUBLE(asdecimal=False)) # 成立至今波动率

    __table_args__ = (
        Index('idx_index_volatility_datetime', 'datetime'),
    )


class IndexReturn(Base):
    '''指数收益率'''

    __tablename__ = 'index_return'

    index_id = Column(CHAR(20), primary_key=True) # 指数ID
    datetime = Column(DATE, primary_key=True) # 日期
    w1_ret = Column(DOUBLE(asdecimal=False)) # 近一周收益率
    m1_ret = Column(DOUBLE(asdecimal=False)) # 近一月收益率
    m3_ret = Column(DOUBLE(asdecimal=False)) # 近三月收益率
    m6_ret = Column(DOUBLE(asdecimal=False)) # 近半年收益率
    y1_ret = Column(DOUBLE(asdecimal=False)) # 近一年收益率
    y3_ret = Column(DOUBLE(asdecimal=False)) # 近三年收益率
    y5_ret = Column(DOUBLE(asdecimal=False)) # 近五年收益率
    y10_ret = Column(DOUBLE(asdecimal=False)) # 近十年收益率
    this_y_ret = Column(DOUBLE(asdecimal=False)) # 今年以来收益率
    this_s_ret = Column(DOUBLE(asdecimal=False)) # 本季度以来收益率
    cumulative_ret = Column(DOUBLE(asdecimal=False)) # 成立至今收益率

    __table_args__ = (
        Index('idx_index_return_datetime', 'datetime'),
    )


class FundAlpha(Base):
    '''基金超额收益'''

    __tablename__ = 'fund_alpha'

    track_err = Column(DOUBLE(asdecimal=False)) # 跟踪误差
    this_y_alpha = Column(DOUBLE(asdecimal=False)) # 今年以来超额收益
    cumulative_alpha = Column(DOUBLE(asdecimal=False)) # 成立以来超额收益
    w1_alpha = Column(DOUBLE(asdecimal=False)) # 近一周收益率
    m1_alpha = Column(DOUBLE(asdecimal=False)) # 近一月超额收益
    m3_alpha = Column(DOUBLE(asdecimal=False)) # 近三月超额收益
    m6_alpha = Column(DOUBLE(asdecimal=False)) # 近半年超额收益
    y1_alpha = Column(DOUBLE(asdecimal=False)) # 近一年超额收益
    y3_alpha = Column(DOUBLE(asdecimal=False)) # 近三年超额收益
    y5_alpha = Column(DOUBLE(asdecimal=False)) # 近五年超额收益
    y10_alpha = Column(DOUBLE(asdecimal=False)) # 近十年超额收益
    fund_id = Column(CHAR(16), primary_key=True) # 基金ID
    datetime = Column(DATE, primary_key=True) # 日期

    __table_args__ = (
        Index('idx_fund_alpha_datetime', 'datetime'),
    )


class IndexValuationLongTerm(Base):
    '''指数估值'''

    __tablename__ = 'index_valuation_long_term'

    index_id = Column(CHAR(20), primary_key=True) #指数ID
    datetime = Column(DATE, primary_key=True) # 日期

    pb_mrq = Column(DOUBLE(asdecimal=False)) # 市净率-MRQ
    pe_ttm = Column(DOUBLE(asdecimal=False)) # 市盈率-MMT
    pe_ttm_nn = Column(DOUBLE(asdecimal=False)) # 市盈率PE(TTM)(剔除负值)
    roe = Column(DOUBLE(asdecimal=False)) # 净资产收益率
    ps_ttm = Column(DOUBLE(asdecimal=False)) # 市销率—MMT
    dy = Column(DOUBLE(asdecimal=False)) # 股息率
    pcf_ttm = Column(DOUBLE(asdecimal=False)) # 市现率-MMT
    peg_ttm = Column(DOUBLE(asdecimal=False)) # 市盈率相对盈利增长比率-MMT
    pe_pct = Column(DOUBLE(asdecimal=False)) # PE百分位(10/5年)
    pb_pct = Column(DOUBLE(asdecimal=False)) # PB百分位(10/5年)
    roe_pct = Column(DOUBLE(asdecimal=False)) # ROE百分位(10/5年)
    pe_pct_30 = Column(DOUBLE(asdecimal=False)) # PE百分位(10/5年) 30 分位
    pe_pct_70 = Column(DOUBLE(asdecimal=False)) # PE百分位(10/5年) 70 分位
    pb_pct_30 = Column(DOUBLE(asdecimal=False)) # PB百分位(10/5年) 30 分位
    pb_pct_70 = Column(DOUBLE(asdecimal=False)) # PB百分位(10/5年) 70 分位
    roe_pct_30 = Column(DOUBLE(asdecimal=False)) # ROE百分位(10/5年) 30 分位
    roe_pct_70 = Column(DOUBLE(asdecimal=False)) # ROE百分位(10/5年) 70 分位
    val_score = Column(DOUBLE(asdecimal=False)) # 估值评分(10/5年)
    eps_ttm = Column(DOUBLE(asdecimal=False)) # 每股收益—MMT
    ps_pct = Column(DOUBLE(asdecimal=False)) # PS百分位(10/5年)
    est_peg = Column(DOUBLE(asdecimal=False)) # 预测peg
    pe_pct_5_3 = Column(DOUBLE(asdecimal=False)) # PE百分位
    pb_pct_5_3 = Column(DOUBLE(asdecimal=False)) # PB百分位
    ps_pct_5_3 = Column(DOUBLE(asdecimal=False)) # PS百分位
    roe_pct_5_3 = Column(DOUBLE(asdecimal=False)) # ROE百分位
    mv = Column(DOUBLE(asdecimal=False)) # 总市值
    liqmv = Column(DOUBLE(asdecimal=False)) # 流通市值
    freeliqmv = Column(DOUBLE(asdecimal=False)) # 自由流通市值

    __table_args__ = (
        Index('idx_index_valuation_long_term_datetime', 'datetime'),
    )

class FundIndicator(Base):
    '''基金评价指标'''

    __tablename__ = 'fund_indicator'
    fund_id = Column(CHAR(10), primary_key=True) # 基金ID
    datetime = Column(DATE, primary_key=True) # 日期
    beta = Column(DOUBLE(asdecimal=False)) # 风险指数
    alpha = Column(DOUBLE(asdecimal=False)) # 投资回报
    track_err = Column(DOUBLE(asdecimal=False)) # 跟踪误差
    timespan = Column(DOUBLE(asdecimal=False)) # 历史数据跨度(年)
    fee_rate = Column(DOUBLE(asdecimal=False)) # 费率
    info_ratio = Column(DOUBLE(asdecimal=False)) # 信息比率
    treynor = Column(DOUBLE(asdecimal=False)) # 特雷诺比率
    mdd = Column(DOUBLE(asdecimal=False)) #净值最大回撤
    down_risk = Column(DOUBLE(asdecimal=False)) #下行风险
    ret_over_period = Column(DOUBLE(asdecimal=False)) #区间收益率
    annual_avg_daily_ret = Column(DOUBLE(asdecimal=False)) #年化日均收益
    annual_vol = Column(DOUBLE(asdecimal=False)) #年化波动率
    annual_ret = Column(DOUBLE(asdecimal=False)) #年化收益
    m_square = Column(DOUBLE(asdecimal=False)) #M平方测度 风险调整收益指标
    time_ret = Column(DOUBLE(asdecimal=False)) #择时收益
    var = Column(DOUBLE(asdecimal=False)) #资产在险值
    r_square = Column(DOUBLE(asdecimal=False)) #决定系数R方
    sharpe = Column(DOUBLE(asdecimal=False)) #夏普率
    year_length = Column(DOUBLE(asdecimal=False)) #成立年限
    alpha_bond = Column(DOUBLE(asdecimal=False)) #alpha 债
    beta_bond = Column(DOUBLE(asdecimal=False)) #beta 债
    alpha_hs300 = Column(DOUBLE(asdecimal=False)) #alpha hs300
    beta_hs300 = Column(DOUBLE(asdecimal=False)) #beta hs300

    __table_args__ = (
        Index('idx_fund_indicator_datetime', 'datetime'),
    )


class FundIndicatorWeekly(Base):
    '''基金评价指标'''

    __tablename__ = 'fund_indicator_weekly'
    fund_id = Column(CHAR(10), primary_key=True) # 基金ID
    datetime = Column(DATE, primary_key=True) # 日期
    beta_w = Column(DOUBLE(asdecimal=False)) # 风险指数
    alpha_w = Column(DOUBLE(asdecimal=False)) # 投资回报
    track_err_w = Column(DOUBLE(asdecimal=False)) # 跟踪误差

    __table_args__ = (
        Index('idx_fund_indicator_datetime_weekly', 'datetime'),
    )

class FundIndicatorMonthly(Base):
    '''基金评价指标（月度）'''

    __tablename__ = 'fund_indicator_monthly'

    fund_id = Column(CHAR(10), primary_key=True)  # 基金ID
    datetime = Column(DATE, primary_key=True)  # 日期
    beta_m = Column(DOUBLE(asdecimal=False), nullable=False)  # beta
    sharpe_ratio_m = Column(DOUBLE(asdecimal=False))  # 夏普比率
    treynor_ratio_m = Column(DOUBLE(asdecimal=False))  # 特雷诺比率
    information_ratio_m = Column(DOUBLE(asdecimal=False))  # 信息比率
    jensen_alpha_m = Column(DOUBLE(asdecimal=False), nullable=False)  # 詹森指数
    calmar_ratio_m = Column(DOUBLE(asdecimal=False))  # 卡玛比率

    __table_args__ = (
        Index('idx_fund_indicator_monthly_datetime_monthly', 'datetime'),
    )


class FundIndicatorAnnual(Base):
    '''基金年度指标'''

    __tablename__ = 'fund_indicator_annual'

    fund_id = Column(CHAR(16), primary_key=True)  # 基金ID
    datetime = Column(DATE, primary_key=True)  # 日期
    beta_annual = Column(DOUBLE(asdecimal=False))  # beta
    alpha_annual = Column(DOUBLE(asdecimal=False))  # alpha
    excess_return_annual = Column(DOUBLE(asdecimal=False))  # 超额收益

    __table_args__ = (
        Index('idx_fund_indicator_datetime_annual', 'datetime'),
    )


class FundIndicatorGroup(Base):
    '''基金评价指标'''

    __tablename__ = 'fund_indicator_group'

    fund_id = Column(CHAR(10), primary_key=True)  # 基金ID
    datetime = Column(DATE, primary_key=True)  # 日期
    data_cycle = Column(CHAR(3), primary_key=True)  # 使用多长时间的数据来计算
    scale = Column(DOUBLE(asdecimal=False))  # 规模
    beta = Column(DOUBLE(asdecimal=False))
    alpha = Column(DOUBLE(asdecimal=False))
    track_err = Column(DOUBLE(asdecimal=False))  # 跟踪误差
    info_ratio = Column(DOUBLE(asdecimal=False))  # 信息比率
    info_ratio_hs300 = Column(DOUBLE(asdecimal=False))  # 相对沪深300的信息比率
    treynor = Column(DOUBLE(asdecimal=False))  # 特雷诺比率
    mdd = Column(DOUBLE(asdecimal=False))  # 净值最大回撤
    mdd_len = Column(DOUBLE(asdecimal=False))  # 最大回撤持续时间
    winning_rate = Column(DOUBLE(asdecimal=False))  # 和mmf的相对胜率
    VaR = Column(DOUBLE(asdecimal=False))  # Value at Risk
    CVaR = Column(DOUBLE(asdecimal=False))  # Expected Shortfall
    ins_holds = Column(DOUBLE(asdecimal=False))  # 机构持有者占比
    hold_num = Column(DOUBLE(asdecimal=False))  # 持有人数量
    leverage = Column(DOUBLE(asdecimal=False))  # 杠杆
    ptm = Column(DOUBLE(asdecimal=False))  # 到期期限
    annual_vol = Column(DOUBLE(asdecimal=False))  # 年化波动率
    annual_ret = Column(DOUBLE(asdecimal=False))  # 年化收益
    sharpe = Column(DOUBLE(asdecimal=False))
    calma_ratio = Column(DOUBLE(asdecimal=False))
    stutzer = Column(DOUBLE(asdecimal=False))
    continue_regress_v = Column(DOUBLE(asdecimal=False))  # 业绩持续性回归系数
    continue_regress_t = Column(DOUBLE(asdecimal=False))  # 业绩持续性回归T值
    continue_stats_v = Column(DOUBLE(asdecimal=False))  # 业绩持续性回归计算值
    stock_cl_alpha = Column(DOUBLE(asdecimal=False))  # cl alpha
    stock_cl_alpha_t = Column(DOUBLE(asdecimal=False))  # cl alpha t值
    stock_cl_alpha_p = Column(DOUBLE(asdecimal=False))  # cl alpha p值
    stock_cl_beta = Column(DOUBLE(asdecimal=False))  # cl beta
    stock_cl_beta_t = Column(DOUBLE(asdecimal=False))  # cl beta t值
    stock_cl_beta_p = Column(DOUBLE(asdecimal=False))  # cl beta p值
    stock_tm_alpha = Column(DOUBLE(asdecimal=False))  # tm alpha
    stock_tm_alpha_t = Column(DOUBLE(asdecimal=False))  # tm alpha t值
    stock_tm_alpha_p = Column(DOUBLE(asdecimal=False))  # tm alpha p值
    stock_tm_beta = Column(DOUBLE(asdecimal=False))  # tm beta
    stock_tm_beta_t = Column(DOUBLE(asdecimal=False))  # tm beta t值
    stock_tm_beta_p = Column(DOUBLE(asdecimal=False))  # tm beta p值
    stock_hm_alpha = Column(DOUBLE(asdecimal=False))  # hm alpha
    stock_hm_alpha_t = Column(DOUBLE(asdecimal=False))  # hm alpha t值
    stock_hm_alpha_p = Column(DOUBLE(asdecimal=False))  # hm alpha p值
    stock_hm_beta = Column(DOUBLE(asdecimal=False))  # hm beta
    stock_hm_beta_t = Column(DOUBLE(asdecimal=False))  # hm beta t值
    stock_hm_beta_p = Column(DOUBLE(asdecimal=False))  # hm beta p值
    abnormal_reason = Column(CHAR(60)) # 未计算因子 异常原因
    __table_args__ = (
        Index('idx_fund_indicator_group_datetime_data_cycle', 'datetime', 'data_cycle'),
    )

class FundScoreExtended(Base):
    '''新基金评分v1'''

    __tablename__ = 'fund_score_extended'

    fund_id = Column(CHAR(16), primary_key=True)  # 基金代码
    datetime = Column(DATE, primary_key=True)  # 日期
    data_cycle = Column(CHAR(3), primary_key=True)  # 使用多长时间的数据来计算
    wind_class_1 = Column(CHAR(16))  # Wind基金一级类型
    ret = Column(DOUBLE(asdecimal=False))  # ret
    vol = Column(DOUBLE(asdecimal=False))  # volatility
    sr = Column(DOUBLE(asdecimal=False))  # sharpe ratio
    ir = Column(DOUBLE(asdecimal=False))  # information ratio
    beta = Column(DOUBLE(asdecimal=False))  # beta
    alpha = Column(DOUBLE(asdecimal=False))  # alpha
    treynor_ratio = Column(DOUBLE(asdecimal=False))  # treynor_ratio
    mdd = Column(DOUBLE(asdecimal=False))  # max drawdown
    timing = Column(DOUBLE(asdecimal=False))  # timing
    ret_score = Column(DOUBLE(asdecimal=False))  # score of ret
    vol_score = Column(DOUBLE(asdecimal=False))  # score of volatility
    sr_score = Column(DOUBLE(asdecimal=False))  # score of sharpe ratio
    ir_score = Column(DOUBLE(asdecimal=False))  # score of information ratio
    beta_score = Column(DOUBLE(asdecimal=False))  # score of beta
    alpha_score = Column(DOUBLE(asdecimal=False))  # score of alpha
    treynor_ratio_score = Column(DOUBLE(asdecimal=False))  # score of treynor_ratio
    mdd_score = Column(DOUBLE(asdecimal=False))  # score of max drawdown
    return_score = Column(DOUBLE(asdecimal=False))  # score of return
    robust_score = Column(DOUBLE(asdecimal=False))  # score of robust
    timing_score = Column(DOUBLE(asdecimal=False))  # score of timing
    selection_score = Column(DOUBLE(asdecimal=False))  # score of selection
    allocation_score = Column(DOUBLE(asdecimal=False))  # score of allocation
    interaction_score = Column(DOUBLE(asdecimal=False))  # score of interaction
    return_rank = Column(DOUBLE(asdecimal=False))  # rank of return
    robust_rank = Column(DOUBLE(asdecimal=False))  # rank of robust
    timing_rank = Column(DOUBLE(asdecimal=False))  # rank of timing
    selection_rank = Column(DOUBLE(asdecimal=False))  # rank of selection
    allocation_rank = Column(DOUBLE(asdecimal=False))  # rank of allocation
    interaction_rank = Column(DOUBLE(asdecimal=False))  # rank of interaction
    total_score = Column(DOUBLE(asdecimal=False), nullable=False)  # score of total
    total_rank = Column(DOUBLE(asdecimal=False))  # rank of total

    __table_args__ = (
        Index('idx_fund_score_extended_datetime_data_cycle', 'datetime', 'data_cycle'),
    )

class FundScoreNew(Base):
    '''新基金评分v2'''

    __tablename__ = 'fund_score_new'

    fund_id = Column(CHAR(16), primary_key=True)  # 基金代码
    datetime = Column(DATE, primary_key=True)  # 日期
    data_cycle = Column(CHAR(3), primary_key=True)  # 使用多长时间的数据来计算
    wind_class_1 = Column(CHAR(16))  # Wind基金一级类型
    return_score = Column(DOUBLE(asdecimal=False))  # 被动指数型、被动指数型债券(均为二级分类)基金为跟踪标的能力，其他为收益能力
    robust_score = Column(DOUBLE(asdecimal=False))  # 稳定性能力
    risk_score = Column(DOUBLE(asdecimal=False))  # 抗风险能力
    timing_score = Column(DOUBLE(asdecimal=False))  # 被动指数型、被动指数型债券(均为二级分类)基金和货基(一二级分类相同)为管理规模能力，其他为择时能力
    selection_score = Column(DOUBLE(asdecimal=False))  # 被动指数型、被动指数型债券(均为二级分类)基金和货基(一二级分类相同)为机构观点，其他为选证能力
    team_score = Column(DOUBLE(asdecimal=False))  # 基金公司团队能力
    total_score = Column(DOUBLE(asdecimal=False), nullable=False)  # 总分
    abnormal_reason = Column(CHAR(60)) # 未计算因子 异常原因

    __table_args__ = (
        Index('idx_fund_score_new_data_cycle', 'data_cycle'),
    )

class AssetAllocationInfo(Base):
    '''十档大类资产组合'''

    __tablename__ = 'asset_allocation_info'
    allocation_id = Column(Integer, primary_key=True) # 组合id
    version = Column(Integer, primary_key=True) # 版本号

    hs300 =  Column(DOUBLE(asdecimal=False)) # 沪深300权重
    csi500 =  Column(DOUBLE(asdecimal=False)) # 中证500权重
    gem =  Column(DOUBLE(asdecimal=False)) # 创业板权重
    sp500rmb =  Column(DOUBLE(asdecimal=False)) # 标普500人民币权重
    national_debt = Column(DOUBLE(asdecimal=False)) # 国债权重
    gold =  Column(DOUBLE(asdecimal=False)) # 黄金权重
    credit_debt =  Column(DOUBLE(asdecimal=False)) # 信用债权重
    dax30rmb = Column(DOUBLE(asdecimal=False)) # 德国dax30权重
    real_state = Column(DOUBLE(asdecimal=False)) # 房地产权重 拼错了
    oil = Column(DOUBLE(asdecimal=False)) # 原油权重
    n225rmb = Column(DOUBLE(asdecimal=False)) # 日经225权重
    cash = Column(DOUBLE(asdecimal=False)) # 现金权重
    mdd = Column(DOUBLE(asdecimal=False)) # 最大回撤
    annual_ret = Column(DOUBLE(asdecimal=False)) # 年化收益
    sharpe = Column(DOUBLE(asdecimal=False)) # 夏普率
    recent_y5_ret = Column(DOUBLE(asdecimal=False)) # 最近五年收益
    annual_vol = Column(DOUBLE(asdecimal=False)) # 年化波动率
    mdd_d1 = Column(DATE) # 最大回撤开始时间
    mdd_d2 = Column(DATE) # 最大回撤结束时间
    start_date = Column(DATE) # 回测开始时间
    end_date = Column(DATE) # 回测结束时间

class StyleAnalysisFactorReturn(Base):
    '''风格分析因子收益'''

    __tablename__ = 'style_analysis_factor_return'

    universe_index = Column(CHAR(20), primary_key=True)  # universe, 全市场股票时值为all
    datetime = Column(DATE, primary_key=True)  # 日期
    latest_size = Column(DOUBLE(asdecimal=False))  # 规模
    bp = Column(DOUBLE(asdecimal=False))  # 价值
    short_term_momentum = Column(DOUBLE(asdecimal=False))  # 短期动量
    long_term_momentum = Column(DOUBLE(asdecimal=False))  # 长期动量
    high_low = Column(DOUBLE(asdecimal=False))  # 波动率
    const = Column(DOUBLE(asdecimal=False))  # 常数项

class BarraCNE5FactorReturn(Base):
    '''Barra CNE5因子收益'''

    __tablename__ = 'barra_cne5_factor_return'

    datetime = Column(DATE, primary_key=True)  # 日期
    market = Column(DOUBLE(asdecimal=False))
    leverage = Column(DOUBLE(asdecimal=False))
    cap = Column(DOUBLE(asdecimal=False))
    momentum = Column(DOUBLE(asdecimal=False))
    bp = Column(DOUBLE(asdecimal=False))
    earning = Column(DOUBLE(asdecimal=False))
    liquidity = Column(DOUBLE(asdecimal=False))
    growth = Column(DOUBLE(asdecimal=False))
    vol = Column(DOUBLE(asdecimal=False))

class AllocationDistribution(Base):
    '''有效前沿下各mdd最优策略'''

    __tablename__ = 'allocation_distribution'

    ef_id = Column(CHAR(8), primary_key=True)  # 有效前沿id
    version = Column(Integer, primary_key=True) # 版本号
    annual_ret = Column(DOUBLE(asdecimal=False)) #年化收益
    csi500 = Column(DOUBLE(asdecimal=False)) # 中证500权重
    gem = Column(DOUBLE(asdecimal=False)) #创业板权重
    gold = Column(DOUBLE(asdecimal=False)) #黄金权重
    hs300 = Column(DOUBLE(asdecimal=False)) #沪深300权重
    mdd = Column(DOUBLE(asdecimal=False)) # 最大回撤
    mdd_up_limit = Column(DOUBLE(asdecimal=False)) #最大回测档位上限
    mmf = Column(DOUBLE(asdecimal=False)) # 货币基金权重
    national_debt = Column(DOUBLE(asdecimal=False)) #国债权重
    sp500rmb = Column(DOUBLE(asdecimal=False)) #标普500权重
    cash = Column(DOUBLE(asdecimal=False)) #现金权重

class FundAIC(Base):
    '''基金定投收益收集'''

    __tablename__ = 'fund_aic'

    fund_id = Column(CHAR(20), primary_key=True)  # 基金ID
    datetime = Column(CHAR(20), primary_key=True)  # 时间
    y1_ret = Column(DOUBLE(asdecimal=False))  # 普通定投一年收益
    y3_ret = Column(DOUBLE(asdecimal=False))  # 普通定投三年收益
    y5_ret = Column(DOUBLE(asdecimal=False))  # 普通定投五年收益
    intel_y1_ret = Column(DOUBLE(asdecimal=False))  # 智能定投一年收益
    intel_y3_ret = Column(DOUBLE(asdecimal=False))  # 智能定投三年收益
    intel_y5_ret = Column(DOUBLE(asdecimal=False))  # 智能定投五年收益

class StyleBox(Base):
    '''基金风格九宫格评分'''

    __tablename__ = 'fund_style_box'

    fund_id = Column(CHAR(20), primary_key=True)  # 基金ID
    datetime = Column(DATE, primary_key=True)  # 时间
    x = Column(DOUBLE(asdecimal=False))  # 价值-平衡-成长维度
    y = Column(DOUBLE(asdecimal=False))  # 小盘-中盘-大盘维度

    __table_args__ = (
        Index('idx_fund_style_box_datetime', 'datetime'),
    )

class StyleReg(Base):
    '''Style 因子收益'''

    __tablename__ = 'style_reg_factor_return'

    datetime = Column(DATE, primary_key=True)  # 日期
    large_g= Column(DOUBLE(asdecimal=False))
    large_v = Column(DOUBLE(asdecimal=False))
    mid_g = Column(DOUBLE(asdecimal=False))
    mid_v = Column(DOUBLE(asdecimal=False))
    small_g = Column(DOUBLE(asdecimal=False))
    small_v = Column(DOUBLE(asdecimal=False))

class FundManagerIndex(Base):
    '''基金经理指数'''

    __tablename__ = 'fund_manager_index'

    manager_id = Column(CHAR(16), primary_key=True)  # 基金经理ID
    datetime = Column(DATE, primary_key=True)  # 日期
    fund_type = Column(CHAR(8), primary_key=True)  # 所管理基金类型
    manager_index = Column(DOUBLE(asdecimal=False))  # 基金经理指数

class FundManagerScore(Base):
    '''基金经理评分以及因子'''

    __tablename__ = 'fund_manager_score'

    manager_id = Column(CHAR(16), primary_key=True)  # 基金经理ID
    datetime = Column(DATE, primary_key=True)  # 日期
    fund_type = Column(CHAR(8), primary_key=True)  # 所管理基金类型
    trade_year = Column(DOUBLE(asdecimal=False))
    annualized_ret = Column(DOUBLE(asdecimal=False))
    annualized_vol = Column(DOUBLE(asdecimal=False))
    sharpe = Column(DOUBLE(asdecimal=False))
    mdd = Column(DOUBLE(asdecimal=False))
    alpha = Column(DOUBLE(asdecimal=False))
    beta = Column(DOUBLE(asdecimal=False))
    track_err = Column(DOUBLE(asdecimal=False))
    fund_size = Column(DOUBLE(asdecimal=False))
    model_alpha = Column(DOUBLE(asdecimal=False))
    model_beta = Column(DOUBLE(asdecimal=False))
    now_comp_year = Column(DOUBLE(asdecimal=False)) # 在当前基金公司时间
    year_ret_std =  Column(DOUBLE(asdecimal=False)) # 每年收益波动率
    score = Column(DOUBLE(asdecimal=False))

    __table_args__ = (
        Index('idx_fund_manager_score_datetime', 'datetime'),
    )

class FundManagerInfo(Base):
    '''基金经理信息'''
    __tablename__ = 'manager_info'

    mng_id = Column(CHAR(10), primary_key=True) # 基金经理id
    start_date = Column(DATE, primary_key=True) # 基金经理任职时间
    fund_id = Column(CHAR(10), primary_key=True) # 代码
    mng_name = Column(CHAR(25)) # 基金经理
    gender = Column(CHAR(2)) # 性别
    birth_year = Column(CHAR(4)) # 出生年份
    education = Column(CHAR(4)) # 学历
    nationality = Column(CHAR(10)) # 国籍
    resume = Column(TEXT) # 简历
    end_date = Column(DATE) # 基金经理离职时间
    company_id = Column(CHAR(64)) # 基金公司
    profit = Column(DOUBLE)     # 任期基金收益

class FundManagerFundRank(Base):
    '''基金经理基金排名'''
    __tablename__ = 'manager_fund_rank'

    mng_id = Column(CHAR(10), primary_key=True) # 基金经理id
    datetime = Column(DATE, primary_key=True) # 时间
    fund_list = Column(TEXT)

class ManagerFundDetail(Base):
    '''基金经理基金排名'''
    __tablename__ = 'manager_fund_detail'

    mng_id = Column(CHAR(10), primary_key=True) # 基金经理id
    datetime = Column(DATE, primary_key=True) # 时间
    stock_fund_list = Column(TEXT)
    # bond_fund_list = Column(TEXT)
    # mmf_fund_list = Column(TEXT)
    # qdii_fund_list = Column(TEXT)
    # mix_fund_list = Column(TEXT)

class NewShareFundRank(Base):
    """打新基金榜单"""
    __tablename__ = 'fund_rank_new_share'

    fund_id = Column(CHAR(10), primary_key=True)        # 基金ID
    final_score = Column(DOUBLE(asdecimal=False))       # 最终分数


class AbsReturnFundRank(Base):
    """绝对收益基金榜单"""
    __tablename__ = 'fund_rank_abs_return'

    fund_id = Column(CHAR(10), primary_key=True)        # 基金ID
    final_score = Column(DOUBLE(asdecimal=False))       # 最终分数


class ConvertibleBondFundRank(Base):
    """可转债基金榜单"""
    __tablename__ = 'fund_rank_convertible_bonds'

    fund_id = Column(CHAR(10), primary_key=True)        # 基金ID
    final_score = Column(DOUBLE(asdecimal=False))       # 最终分数


class ThirdPartyPortfolioInfo(Base):
    '''组合基本信息表'''

    __tablename__ = 'third_party_portfolio_info'

    po_id = Column(CHAR(16), primary_key=True)  # 组合ID
    po_src = Column(SMALLINT, nullable=False)  # 组合来源 详见constant.SourceType
    po_name = Column(TEXT, nullable=False)  # 组合名称
    po_desc = Column(TEXT)  # 组合描述
    manager_name = Column(TEXT) # 主理人名称
    rich_desc = Column(TEXT)  # 详细描述
    benchmarks = Column(TEXT) # 业绩比较基准
    start_date = Column(DATE, nullable=False)  # 组合开始日期
    risk_level = Column(CHAR(6))  # 风险级别
    can_aip = Column(BOOLEAN)  # 是否可定投


class ThirdPartyPortfolioTrade(Base):
    '''组合调仓记录表'''

    __tablename__ = 'third_party_portfolio_trade'

    po_id = Column(CHAR(16), primary_key=True)  # 组合ID
    datetime = Column(DATE, primary_key=True)  # 日期
    po_src = Column(SMALLINT, nullable=False)  # 组合来源 详见constant.SourceType
    details = Column(TEXT, nullable=False)  # 调仓详情
    comment = Column(TEXT)


class ThirdPartyPortfolioPositionLatest(Base):
    '''组合最新持仓表'''

    __tablename__ = 'third_party_portfolio_position_latest'

    po_id = Column(CHAR(16), primary_key=True)  # 组合ID
    datetime = Column(DATE, primary_key=True)  # 日期
    po_src = Column(SMALLINT, nullable=False)  # 组合来源 详见constant.SourceType
    position = Column(TEXT, nullable=False)  # 持仓

    __table_args__ = (
        Index('idx_third_party_portfolio_position_latest_po_src', 'po_src'),
    )

class ThirdPartyPortfolioIndicator(Base):
    '''组合最新因子表'''

    __tablename__ = 'third_party_portfolio_indicator'

    po_id = Column(CHAR(16), primary_key=True)  # 组合ID
    datetime = Column(DATE, primary_key=True)  # 日期
    po_src = Column(SMALLINT, nullable=False)  # 组合来源 详见constant.SourceType
    nav = Column(DOUBLE(asdecimal=False), nullable=False)  # 净值（累计复权净值计算得出）
    sharpe_ratio = Column(DOUBLE(asdecimal=False))  # 夏普比率
    mdd = Column(DOUBLE(asdecimal=False), nullable=False)  # 最大回撤
    annual_compounded_ret = Column(DOUBLE(asdecimal=False), nullable=False)  # 年化复合收益率
    daily_ret = Column(DOUBLE(asdecimal=False), nullable=False)  # 最近一天收益率
    weekly_ret = Column(DOUBLE(asdecimal=False))  # 最近一周收益率
    monthly_ret = Column(DOUBLE(asdecimal=False))  # 最近一月收益率
    quarterly_ret = Column(DOUBLE(asdecimal=False))  # 最近一季收益率
    half_yearly_ret = Column(DOUBLE(asdecimal=False))  # 最近半年收益率
    yearly_ret = Column(DOUBLE(asdecimal=False))  # 最近一年收益率
    from_setup_ret = Column(DOUBLE(asdecimal=False), nullable=False)  # 成立以来收益率
    vol_by_day = Column(DOUBLE(asdecimal=False))  # 年化日波动率
    vol_by_week = Column(DOUBLE(asdecimal=False))  # 年化周波动率
    vol_by_month = Column(DOUBLE(asdecimal=False))  # 年化月波动率
    annual_ret = Column(DOUBLE(asdecimal=False), nullable=False)  # 年化收益
    mdd_d1 = Column(DATE, nullable=False)  # 回撤区间高点日期
    mdd_d2 = Column(DATE, nullable=False)  # 回撤区间低点日期
    total_commission = Column(DOUBLE(asdecimal=False), nullable=False)  # 总手续费
    rebalance_times = Column(DOUBLE(asdecimal=False), nullable=False)  # 调仓次数

class FundIndicatorIPOConv(Base):
    '''基金评价指标'''

    __tablename__ = 'fund_indicator_ipo_conv'
    fund_id = Column(CHAR(10), primary_key=True) # 基金ID
    datetime = Column(DATE, primary_key=True) # 日期
    beta = Column(DOUBLE(asdecimal=False)) # 风险指数
    alpha = Column(DOUBLE(asdecimal=False)) # 投资回报
    track_err = Column(DOUBLE(asdecimal=False)) # 跟踪误差
    timespan = Column(DOUBLE(asdecimal=False)) # 历史数据跨度(年)
    fee_rate = Column(DOUBLE(asdecimal=False)) # 费率
    info_ratio = Column(DOUBLE(asdecimal=False)) # 信息比率
    treynor = Column(DOUBLE(asdecimal=False)) # 特雷诺比率
    mdd = Column(DOUBLE(asdecimal=False)) #净值最大回撤
    down_risk = Column(DOUBLE(asdecimal=False)) #下行风险
    ret_over_period = Column(DOUBLE(asdecimal=False)) #区间收益率
    annual_avg_daily_ret = Column(DOUBLE(asdecimal=False)) #年化日均收益
    annual_vol = Column(DOUBLE(asdecimal=False)) #年化波动率
    annual_ret = Column(DOUBLE(asdecimal=False)) #年化收益
    m_square = Column(DOUBLE(asdecimal=False)) #M平方测度 风险调整收益指标
    time_ret = Column(DOUBLE(asdecimal=False)) #择时收益
    var = Column(DOUBLE(asdecimal=False)) #资产在险值
    r_square = Column(DOUBLE(asdecimal=False)) #决定系数R方
    sharpe = Column(DOUBLE(asdecimal=False)) #夏普率
    year_length = Column(DOUBLE(asdecimal=False)) #成立年限

    __table_args__ = (
        Index('idx_fund_indicator_ipo_conv_datetime', 'datetime'),
    )

class TopManagerFunds(Base):
    '''基金经理选基'''

    __tablename__ = 'top_manager_funds'
    datetime = Column(DATE, primary_key=True) # 日期
    top_1 = Column(CHAR(10))  # 第一名基金
    top_2 = Column(CHAR(10))  # 第二名基金
    top_3 = Column(CHAR(10))  # 第三名基金
    top_4 = Column(CHAR(10))  # 第四名基金
    top_5 = Column(CHAR(10))  # 第五名基金
    top_6 = Column(CHAR(10))  # 第六名基金
    top_7 = Column(CHAR(10))  # 第七名基金
    top_8 = Column(CHAR(10))  # 第八名基金
    top_9 = Column(CHAR(10))  # 第九名基金
    top_10 = Column(CHAR(10)) # 第十名基金

class StockFactorInfo(Base):
    '''因子信息表'''

    __tablename__ = 'stock_factor_info'

    f_id = Column(CHAR(16), primary_key=True)  # 因子ID
    f_type = Column(Enum(StockFactorType), nullable=False)  # 因子所属分类
    f_name = Column(TEXT, nullable=False)  # 因子名称
    is_selected_by_default = Column(BOOLEAN, nullable=False)  # 是否默认被选中
    f_desc = Column(TEXT)  # 因子简介

class FundIndustryExposure(Base):
    '''基金行业暴露'''

    __tablename__ = 'fund_industry_exposure'

    fund_id = Column(CHAR(10), primary_key=True) # 基金ID
    datetime = Column(DATE, primary_key=True) # 日期
    ind_class_type = Column(Enum(IndClassType), nullable=False)  # 行业分类类型
    value = Column(TEXT, nullable=False)  # JSON格式的行业暴露数据


class FOFNav(FOFBase):
    '''fof净值数据'''

    __tablename__ = 'fof_nav'

    fof_id = Column(CHAR(16), primary_key=True)             # 产品ID
    manager_id = Column(CHAR(32), primary_key=True)         # 管理端ID
    datetime = Column(DATE, primary_key=True)               # 日期
    nav = Column(DOUBLE(asdecimal=False), nullable=False)   # 单位净值
    acc_net_value = Column(DOUBLE(asdecimal=False))         # 累计净值
    adjusted_nav = Column(DOUBLE(asdecimal=False))          # 复权净值
    ta_factor = Column(DOUBLE(asdecimal=False))             # 复权因子
    volume = Column(DOUBLE(asdecimal=False))                # 份额
    mv = Column(DOUBLE(asdecimal=False))                    # 市值
    ret = Column(DOUBLE(asdecimal=False))                   # 累计收益率


class FOFUnconfirmedNav(FOFBase):
    '''fof未确认净值数据'''

    __tablename__ = 'fof_nav_unconfirmed'

    fof_id = Column(CHAR(16), primary_key=True)             # 产品ID
    manager_id = Column(CHAR(32), primary_key=True)         # 管理端ID
    datetime = Column(DATE, primary_key=True)               # 日期
    nav = Column(DOUBLE(asdecimal=False), nullable=False)   # 单位净值
    acc_net_value = Column(DOUBLE(asdecimal=False))         # 累计净值
    v_nav = Column(DOUBLE(asdecimal=False))                 # 虚拟净值


class FOFNavPublic(FOFBase):
    '''fof净值数据发布表'''

    __tablename__ = 'fof_nav_public'

    fof_id = Column(CHAR(16), primary_key=True)             # 产品ID
    datetime = Column(DATE, primary_key=True)               # 日期
    nav = Column(DOUBLE(asdecimal=False), nullable=False)   # 单位净值
    acc_net_value = Column(DOUBLE(asdecimal=False))         # 累计净值
    adjusted_nav = Column(DOUBLE(asdecimal=False))          # 复权净值
    volume = Column(DOUBLE(asdecimal=False))                # 份额
    mv = Column(DOUBLE(asdecimal=False))                    # 市值
    ret = Column(DOUBLE(asdecimal=False))                   # 累计收益率


class FOFNavCalc(FOFBase):
    '''fof净值数据表(计算)'''

    __tablename__ = 'fof_nav_calc'

    fof_id = Column(CHAR(16), primary_key=True)             # 产品ID
    manager_id = Column(CHAR(32), primary_key=True)         # 管理端ID
    datetime = Column(DATE, primary_key=True)               # 日期
    nav = Column(DOUBLE(asdecimal=False), nullable=False)   # 单位净值
    acc_net_value = Column(DOUBLE(asdecimal=False))         # 累计净值
    adjusted_nav = Column(DOUBLE(asdecimal=False))          # 复权净值
    ta_factor = Column(DOUBLE(asdecimal=False))             # 复权因子
    volume = Column(DOUBLE(asdecimal=False))                # 总份额
    mv = Column(DOUBLE(asdecimal=False))                    # 总市值(净资产)
    interest = Column(DOUBLE(asdecimal=False))              # 当日利息
    management_fee = Column(DOUBLE(asdecimal=False))        # 当日管理费
    custodian_fee = Column(DOUBLE(asdecimal=False))         # 当日托管费
    administrative_fee = Column(DOUBLE(asdecimal=False))    # 当日行政服务费
    ret = Column(DOUBLE(asdecimal=False))                   # 累计收益率
    dy_per_share = Column(DOUBLE(asdecimal=False))          # 每股分红


class FOFPosition(FOFBase):
    '''fof持仓汇总数据'''

    __tablename__ = 'fof_position'

    fof_id = Column(CHAR(16), primary_key=True)  # 产品ID
    manager_id = Column(CHAR(32), primary_key=True)  # 管理端ID
    datetime = Column(DATE, primary_key=True)  # 日期
    position = Column(TEXT, nullable=False)  # 持仓信息
    total_current = Column(DOUBLE(asdecimal=False))  # 流动性资产及负债总计
    other_assets = Column(DOUBLE(asdecimal=False))  # 其他资产
    deposit_in_bank = Column(DOUBLE(asdecimal=False))  # 银行存款


class FOFInvestorData(FOFBase):
    '''fof投资人数据'''

    __tablename__ = 'fof_investor_data'

    fof_id = Column(CHAR(16), primary_key=True)  # 产品ID
    investor_id = Column(CHAR(16), primary_key=True)  # 客户合同号(投资人ID)
    manager_id = Column(CHAR(32))  # 管理端ID
    total_investment = Column(DOUBLE(asdecimal=False))  # 总投资额


class FOFPositionDetail(FOFBase):
    '''fof持仓详细数据'''

    __tablename__ = 'fof_position_detail'

    fof_id = Column(CHAR(16), primary_key=True)  # 产品ID
    manager_id = Column(CHAR(32), primary_key=True)  # 管理端ID
    datetime = Column(DATE, primary_key=True)  # 日期
    fund_id = Column(CHAR(10), primary_key=True) # 基金ID
    asset_type = Column(Enum(HoldingAssetType), nullable=False)  # 资产类型
    confirmed_nav = Column(TEXT, nullable=False)  # 确认日净值列表
    water_line = Column(TEXT, nullable=False)  # 水位线列表(累计净值)
    nav = Column(DOUBLE(asdecimal=False), nullable=False)  # 单位净值
    v_nav = Column(DOUBLE(asdecimal=False))  # 虚拟净值
    acc_nav = Column(DOUBLE(asdecimal=False), nullable=False)  # 累计净值
    total_shares = Column(DOUBLE(asdecimal=False), nullable=False)  # 总份额
    total_cost = Column(DOUBLE(asdecimal=False), nullable=False)  # 投资成本
    latest_mv = Column(DOUBLE(asdecimal=False), nullable=False)  # 当日市值
    total_ret = Column(DOUBLE(asdecimal=False), nullable=False)  # 累计收益
    total_rr = Column(DOUBLE(asdecimal=False), nullable=False)  # 累计收益率


class HedgeFundInvestorPurAndRedemp(FOFBase):
    '''私募客户申赎数据'''

    __tablename__ = 'hedge_fund_investor_pur_redemp'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fof_id = Column(CHAR(16), primary_key=True)  # 产品ID
    manager_id = Column(CHAR(32), primary_key=True)  # 管理端ID
    datetime = Column(DATE, primary_key=True)  # 交易日期
    applied_date = Column(DATE)  # 申请日期
    deposited_date = Column(DATE)  # 交割日期
    event_type = Column(Integer, nullable=False)  # 交易类型
    investor_id = Column(CHAR(16), nullable=False)  # 客户合同号(投资人ID)
    net_asset_value = Column(DOUBLE(asdecimal=False), nullable=False)  # 单位净值
    acc_unit_value = Column(DOUBLE(asdecimal=False), nullable=False)  # 累计净值
    water_line = Column(DOUBLE(asdecimal=False), nullable=False)  # 水位线(一般是累计净值; 但整体高水位法下与累计净值可能不同)
    purchase_amount = Column(DOUBLE(asdecimal=False))  # 申认购金额(元)
    redemp_confirmed_amount = Column(DOUBLE(asdecimal=False))  # 赎回确认金额(元)
    raising_interest = Column(DOUBLE(asdecimal=False))  # 募集期利息(元)
    redemp_fee = Column(DOUBLE(asdecimal=False))  # 赎回费(元)
    carry_amount = Column(DOUBLE(asdecimal=False))  # 业绩报酬金额(元)
    share_changed = Column(DOUBLE(asdecimal=False), nullable=False)  # 份额变更
    share_after_trans = Column(DOUBLE(asdecimal=False), nullable=False)  # 交易后份额


class HedgeFundInvestorPurAndRedempSub(FOFBase):
    """私募客户申赎数据附表"""

    __tablename__ = 'hedge_fund_investor_pur_redemp_sub'

    id = Column(Integer, primary_key=True, autoincrement=True)
    main_id = Column(Integer)
    trade_confirm_url = Column(CHAR(127))                       # 交易确认单
    trade_apply_url = Column(CHAR(127))                         # 交易申请表
    remark = Column(CHAR(255))                                  # 备注


class HedgeFundInvestorDivAndCarry(FOFBase):
    '''私募客户分红/业绩计提数据'''

    __tablename__ = 'hedge_fund_investor_div_carry'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fof_id = Column(CHAR(16), primary_key=True)  # 产品ID
    manager_id = Column(CHAR(32), primary_key=True)  # 管理端ID
    datetime = Column(DATE, primary_key=True)  # 交易日期
    applied_date = Column(DATE)  # 申请日期
    deposited_date = Column(DATE)  # 交割日期
    event_type = Column(Integer, nullable=False)  # 交易类型
    investor_id = Column(CHAR(16), nullable=False)  # 客户合同号(投资人ID)
    net_asset_value = Column(DOUBLE(asdecimal=False), nullable=False)  # 单位净值
    acc_unit_value = Column(DOUBLE(asdecimal=False), nullable=False)  # 累计净值
    water_line = Column(DOUBLE(asdecimal=False), nullable=False)  # 水位线(一般是累计净值; 但整体高水位法下与累计净值可能不同)
    total_dividend = Column(DOUBLE(asdecimal=False))  # 红利总额(元)
    cash_dividend = Column(DOUBLE(asdecimal=False))  # 现金分红金额(元)
    reinvest_amount = Column(DOUBLE(asdecimal=False))  # 再投资金额(元)
    carry_amount = Column(DOUBLE(asdecimal=False))  # 业绩报酬金额(元)
    share_changed = Column(DOUBLE(asdecimal=False), nullable=False)  # 份额变更
    share_after_trans = Column(DOUBLE(asdecimal=False), nullable=False)  # 交易后份额


class HedgeFundCustodianData(FOFBase):
    '''私募基金托管人数据'''

    __tablename__ = 'hedge_fund_custodian_data'

    id = Column(Integer, primary_key=True, autoincrement=True)
    fof_id = Column(CHAR(16), primary_key=True)  # 产品ID
    manager_id = Column(CHAR(32), primary_key=True)  # 管理端ID
    datetime = Column(DATE, primary_key=True)  # 交易日期
    nav = Column(DOUBLE(asdecimal=False), nullable=False)  # 单位净值
    equity = Column(DOUBLE(asdecimal=False), nullable=False)  # 资产净值(元)
    total_shares = Column(DOUBLE(asdecimal=False), nullable=False)  # 总份额
    other_assets = Column(DOUBLE(asdecimal=False), nullable=False)  # 其他资产
    deposit_in_bank = Column(DOUBLE(asdecimal=False))  # 银行存款
    interest_receivable = Column(DOUBLE(asdecimal=False))  # 应收利息
    pur_amt_receivable = Column(DOUBLE(asdecimal=False))  # 应收申购款
    sec_clearing_fund = Column(DOUBLE(asdecimal=False))  # 证券清算款
    dividends_receivable = Column(DOUBLE(asdecimal=False))  # 应收股利
    payable_to_managers = Column(DOUBLE(asdecimal=False))  # 应付管理人报酬
    payable_to_custodian = Column(DOUBLE(asdecimal=False))  # 应付托管费
    payable_to_admin_service = Column(DOUBLE(asdecimal=False))  # 应付行政服务费
    mutual_funds_data = Column(TEXT)  # 持仓公募信息
    hedge_funds_data = Column(TEXT)  # 持仓私募信息
    url = Column(CHAR(127))  # 

class PfIndicator(Base):
    '''基金评价指标'''

    __tablename__ = 'pf_indicator'
    pf_id = Column(CHAR(10), primary_key=True) # 基金ID
    datetime = Column(DATE, primary_key=True) # 日期
    period = Column(CHAR(10), primary_key=True) # 因子计算时间范围

    start_date =Column(DATE) # 开始日
    last_unit_nav = Column(DOUBLE(asdecimal=False)) # 末期单位净值
    annualized_ret = Column(DOUBLE(asdecimal=False)) # 年化收益
    trade_year = Column(DOUBLE(asdecimal=False)) # 成立年限
    cumu_ret = Column(DOUBLE(asdecimal=False)) # 累计收益
    annualized_vol = Column(DOUBLE(asdecimal=False)) # 年化波动率
    sharpe = Column(DOUBLE(asdecimal=False)) # 夏普率
    recent_year_ret = Column(DOUBLE(asdecimal=False)) # 最近自然年收益
    recent_1w_ret = Column(DOUBLE(asdecimal=False)) # 最近1周收益
    recent_1m_ret = Column(DOUBLE(asdecimal=False)) # 最近1月收益
    recent_4w_ret = Column(DOUBLE(asdecimal=False)) # 最近4周收益
    recent_3m_ret = Column(DOUBLE(asdecimal=False)) # 最近3月收益
    recent_6m_ret = Column(DOUBLE(asdecimal=False)) # 最近6月收益
    y_2020_ret = Column(DOUBLE(asdecimal=False)) # 2020年收益
    last_year_ret = Column(DOUBLE(asdecimal=False)) # 去年收益
    recent_y1_ret = Column(DOUBLE(asdecimal=False)) # 近一年收益
    recent_y3_ret = Column(DOUBLE(asdecimal=False)) # 近三年收益
    recent_y5_ret = Column(DOUBLE(asdecimal=False)) # 近五年收益
    mdd = Column(DOUBLE(asdecimal=False)) # 最大回撤
    mdd_date1 = Column(DATE) # 最大回撤开始时间
    mdd_date2 = Column(DATE) # 最大回撤结束时间
    mdd_lens = Column(Integer) # 最大回撤区间持续时间
    ret_over_mdd = Column(DOUBLE(asdecimal=False)) # Calmar 年化收益除以最大回撤
    last_mv_diff = Column(DOUBLE(asdecimal=False)) # 末期市值增量
    last_increase_rate = Column(DOUBLE(asdecimal=False)) # 末期涨幅
    worst_3m_ret = Column(DOUBLE(asdecimal=False)) # 最差三月收益
    worst_6m_ret = Column(DOUBLE(asdecimal=False)) # 最差六月收益
    recent_drawdown = Column(DOUBLE(asdecimal=False)) # 最近回撤
    recent_mdd_date1 = Column(DATE) # 最近回撤开始时间
    downside_std = Column(DOUBLE(asdecimal=False)) # 下行风险
    var = Column(DOUBLE(asdecimal=False)) # 风险价值VaR
    cvar = Column(DOUBLE(asdecimal=False)) # 条件风险价值 CVaR
    raise_month_num = Column(Integer) # 上涨月份数
    drop_month_num = Column(Integer) # 下跌月份数
    mdd_recover = Column(DOUBLE(asdecimal=False)) # 最大回撤恢复
    mdd_recover_date1 = Column(DATE) # 最大回撤恢复开始时间
    mdd_recover_date2 = Column(DATE) # 最大回测恢复结束时间
    mdd_recover_lens = Column(Integer) # 最大回测哈恢复天数
    win_rate_0_period = Column(DOUBLE(asdecimal=False)) # 设定周期对零胜率
    nav_density = Column(DOUBLE(asdecimal=False)) # 净值密度
    nav_type = Column(CHAR(20)) # 净值类型
    w1_end_date = Column(DATE) # 近一周结束时间
    w1_begin_date = Column(DATE) # 近一周开始时间

class PfIndicatorWithBenchmark(Base):
    '''基金评价指标'''

    __tablename__ = 'pf_indicator_with_benchmark'
    pf_id = Column(CHAR(10), primary_key=True) # 基金ID
    datetime = Column(DATE, primary_key=True) # 日期
    period = Column(Integer, primary_key=True) # 因子计算时间范围
    index_id = Column(CHAR(10), primary_key=True) # 指数ID

    alpha = Column(DOUBLE(asdecimal=False)) # 超额收益
    beta = Column(DOUBLE(asdecimal=False)) # 风险暴露
    track_err = Column(DOUBLE(asdecimal=False)) # 跟踪误差
    ir = Column(DOUBLE(asdecimal=False)) # 信息比率
    alpha_cl = Column(DOUBLE(asdecimal=False)) # 择股收益
    beta_cl = Column(DOUBLE(asdecimal=False)) # 择时收益
    treynor = Column(DOUBLE(asdecimal=False)) # 特雷诺
    win_rate = Column(DOUBLE(asdecimal=False)) # 对基准胜率
    win_rate_0 = Column(DOUBLE(asdecimal=False)) # 对零胜率
    continue_value = Column(DOUBLE(asdecimal=False)) # 业绩持续性
    win_rate_weekly = Column(DOUBLE(asdecimal=False)) # 周度对基准胜率
    win_rate_0_weekly = Column(DOUBLE(asdecimal=False)) # 周度对零胜率
    win_rate_monthly = Column(DOUBLE(asdecimal=False)) # 月度对基准胜率
    win_rate_0_monthly = Column(DOUBLE(asdecimal=False)) # 月度对零胜率
    excess_mdd = Column(DOUBLE(asdecimal=False)) # 超额收益最大回撤
    excess_mdd_date1 = Column(DATE) # 超额收益最大回撤开始日
    excess_mdd_date2 = Column(DATE) # 超额收益最大回撤结束日
    excess_mdd_lens = Column(Integer) # 超额收益最大回撤持续时间
    up_capture = Column(DOUBLE(asdecimal=False)) # 向上捕捉率
    down_capture = Column(DOUBLE(asdecimal=False)) # 向下捕捉率
    not_system_risk = Column(DOUBLE(asdecimal=False)) # 非系统性风险
    corr = Column(DOUBLE(asdecimal=False)) # 相关性
    sortino = Column(DOUBLE(asdecimal=False)) # 索提诺
    skew = Column(DOUBLE(asdecimal=False)) # 偏度
    kurtosis = Column(DOUBLE(asdecimal=False)) # 峰度
    total_relative_ret = Column(DOUBLE(asdecimal=False)) # 相对全部收益

class FundTypeClassification(Base):
    '''基金类型分类'''

    __tablename__ = 'fund_type_classification'
    
    fund_type = Column(CHAR(10), primary_key=True) # 公募基金或者私募基金
    fund_class_1_ori = Column(CHAR(10), primary_key=True) # 基金一级分类
    fund_class_2_ori = Column(CHAR(40), primary_key=True) # 基金二级分类
    fund_class_1 = Column(CHAR(10)) # 合并一级分类
    fund_class_2 = Column(CHAR(40)) # 合并二级分类