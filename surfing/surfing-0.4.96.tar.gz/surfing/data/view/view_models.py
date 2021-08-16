from sqlalchemy import CHAR, Column, DATE, text, TEXT, Integer, BOOLEAN
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import DOUBLE, DATETIME, TINYINT


class Base():
    _update_time = Column('_update_time', DATETIME, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  # 更新时间


# make this column at the end of every derived table
Base._update_time._creation_order = 9999
Base = declarative_base(cls=Base)


class FundDailyCollection(Base):
    """基金信息日度收集"""

    __tablename__ = 'fund_daily_collection'

    fund_id = Column(CHAR(20), primary_key=True)  # 基金ID
    datetime = Column(CHAR(20), primary_key=True)  # 时间
    order_book_id = Column(CHAR(20))  # 基金代码

    # basic.fund_info
    risk_level = Column(CHAR(2))  # 风险等级
    full_name = Column(CHAR(255)) # 基金全名
    currency = Column(CHAR(20)) # 币种
    manage_fee = Column(DOUBLE(asdecimal=False)) # 管理费
    trustee_fee = Column(DOUBLE(asdecimal=False)) # 托管费
    purchase_fee = Column(DOUBLE(asdecimal=False)) # 申购费
    redeem_fee = Column(DOUBLE(asdecimal=False)) # 赎回费
    benchmark_1 = Column(CHAR(255)) # 业绩基准标的指数简称第一名
    benchmark_2 = Column(CHAR(255)) # 业绩基准标的指数简称第二名
    subscr_fee_detail = Column(TEXT) # 认购费率详情
    purchase_fee_detail = Column(TEXT) # 申购费率详情
    redeem_fee_detail = Column(TEXT) # 赎回费率详情
    service_fee = Column(TEXT) # 销售服务费率
    wind_class_I = Column(CHAR(64))  # Wind基金类型  (混合型基金 债券型基金 股票型基金 货币市场型基金 国际(QDII)基金 另类投资基金)
    wind_class_II = Column(CHAR(64))  # Wind基金二级类型
    institution_rating = Column(CHAR(20))  # 机构评级 暂无
    found_to_now = Column(DOUBLE(asdecimal=False))  # 成立年限
    exchange_status = Column(CHAR(20))  # 交易状态 basic.FundStatusLatest
    track_index = Column(CHAR(20)) # 跟踪指数 basic.FundInfo.track_index
    purch_status = Column(CHAR(16))  # 申购状态 basic.FundStatusLatest
    redem_status = Column(CHAR(16))  # 赎回状态 basic.FundStatusLatest
    fund_type = Column(CHAR(10))  # 基金人工大类 base on wind_class_II
    lp_limit = Column(DOUBLE(asdecimal=False))  # 暂停大额申购上限
    otc_lp_limit = Column(DOUBLE(asdecimal=False))  # 场外暂停大额申购上限
    otc_lp_limit_jg = Column(DOUBLE(asdecimal=False))  # 场外暂停大额申购上限(机构)
    otc_lp_limit_gr = Column(DOUBLE(asdecimal=False))  # 场外暂停大额申购上限(个人)
    first_benchmark_name = Column(CHAR(128)) # 根据benchmark 信息拆出来的基准名字

    # basic.FundNav
    unit_net_value = Column(DOUBLE(asdecimal=False))  # 单位净值
    acc_net_value = Column(DOUBLE(asdecimal=False))  # 累计单位净值
    adjusted_net_value = Column(DOUBLE(asdecimal=False))  # 复权净值
    change_rate = Column(DOUBLE(asdecimal=False))  # 日收益率
    found_date = Column(CHAR(20))  # 成立日期
    end_date = Column(CHAR(20))  # 关闭日期
    price_begin_date = Column(DATE)  # 净值开始时间
    price_end_date = Column(DATE)  # 净值开始时间

    # basic.FundRet
    annualized_returns = Column(DOUBLE(asdecimal=False))  # 成立以来年化收益率
    annualized_risk = Column(DOUBLE(asdecimal=False))  # 成立以来年化风险
    information_ratio = Column(DOUBLE(asdecimal=False))  # 成立以来信息比率
    last_month_return = Column(DOUBLE(asdecimal=False))  # 近一月收益率
    last_six_month_return = Column(DOUBLE(asdecimal=False)) #
    last_three_month_return = Column(DOUBLE(asdecimal=False))  # 近一季度收益率
    last_twelve_month_return = Column(DOUBLE(asdecimal=False))  # 近一年收益率
    last_week_return = Column(DOUBLE(asdecimal=False))  # 近一周收益率
    year_to_date_return = Column(DOUBLE(asdecimal=False))  # 今年以来收益率
    to_date_return = Column(DOUBLE(asdecimal=False))  # 成立至今收益率
    sharp_ratio = Column(DOUBLE(asdecimal=False))  # 成立至今夏普比率
    max_drop_down = Column(DOUBLE(asdecimal=False))  # 成立至今最大回撤
    y3_ret = Column(DOUBLE(asdecimal=False))  # 近三年收益率
    y5_ret = Column(DOUBLE(asdecimal=False))  # 近五年收益率
    vol = Column(DOUBLE(asdecimal=False))  # 波动率（成立以来）

    # based on basic.FundRet
    last_week_return_rank = Column(Integer)  # 近一周同类排名
    last_month_return_rank = Column(Integer)  # 近一月同类排名
    last_three_month_return_rank = Column(Integer)  # 近三月同类排名
    last_six_month_return_rank = Column(Integer)  # 近六月同类排名
    last_twelve_month_return_rank = Column(Integer)  # 近一年同类排名
    y3_ret_rank = Column(Integer)  # 近三年同类排名
    y5_ret_rank = Column(Integer)  # 近五年同类排名
    year_to_date_return_rank = Column(Integer)  # 年初至今同类排名
    to_date_return_rank = Column(Integer)  # 成立以来同类排名
    group_num = Column(Integer)  # 同类数量

    # derived.Derived.FundManagerInfo
    fund_manager = Column(CHAR(255))  # 基金经理
    fund_manager_id = Column(CHAR(127))  # 基金经理ID
    company_name = Column(CHAR(64))  # 基金公司
    symbol = Column(CHAR(64)) # 基金名称
    manager_profit = Column(DOUBLE(asdecimal=False)) # 基金经理任期收益

    # basic.FundBenchmark
    benchmark = Column(CHAR(255)) # 业绩基准  basic.FundInfo.benchmark
    benchmark_s = Column(CHAR(64)) # 跟踪标的id
    benchmark_name = Column(CHAR(64)) # 跟踪标的

    # basic.FundRate
    zs = Column(Integer)  # 招商评级
    sh3 = Column(Integer)  # 上海证券评级三年期
    sh5 = Column(Integer)  # 上海证券评级五年期
    jajx = Column(Integer)  # 济安金信评级
    mornstar_3y = Column(Integer)  # 晨星三年评级
    mornstar_5y = Column(Integer)  # 晨星五年评级

    # basic.FundAlpha
    track_err = Column(DOUBLE(asdecimal=False))  # 跟踪误差
    this_y_alpha = Column(DOUBLE(asdecimal=False))  # 今年以来超额收益
    cumulative_alpha = Column(DOUBLE(asdecimal=False))  # 成立以来超额收益
    w1_alpha = Column(DOUBLE(asdecimal=False))  # 近一周收益率
    m1_alpha = Column(DOUBLE(asdecimal=False))  # 近一月超额收益
    m3_alpha = Column(DOUBLE(asdecimal=False))  # 近三月超额收益
    m6_alpha = Column(DOUBLE(asdecimal=False))  # 近半年超额收益
    y1_alpha = Column(DOUBLE(asdecimal=False))  # 近一年超额收益
    y3_alpha = Column(DOUBLE(asdecimal=False))  # 近三年超额收益
    y5_alpha = Column(DOUBLE(asdecimal=False))  # 近五年超额收益
    y10_alpha = Column(DOUBLE(asdecimal=False))  # 近十年超额收益

    # basic.FundSize.latest_size
    latest_size = Column(DOUBLE(asdecimal=False)) # 最新规模

    # derived.FundIndicator
    beta = Column(DOUBLE(asdecimal=False))  # 风险指数
    alpha = Column(DOUBLE(asdecimal=False))  # 投资回报
    tag_track_err = Column(DOUBLE(asdecimal=False))  # 跟踪误差
    fee_rate = Column(DOUBLE(asdecimal=False))  # 费率
    info_ratio = Column(DOUBLE(asdecimal=False))  # 信息比率
    treynor = Column(DOUBLE(asdecimal=False))  # 特雷诺比率
    mdd = Column(DOUBLE(asdecimal=False))  # 净值最大回撤
    down_risk = Column(DOUBLE(asdecimal=False))  # 下行风险
    ret_over_period = Column(DOUBLE(asdecimal=False))  # 区间收益率
    annual_avg_daily_ret = Column(DOUBLE(asdecimal=False))  # 年化日均收益
    annual_vol = Column(DOUBLE(asdecimal=False))  # 年化波动率
    annual_ret = Column(DOUBLE(asdecimal=False))  # 年化收益率
    m_square = Column(DOUBLE(asdecimal=False))  # M平方测度 风险调整收益指标
    time_ret = Column(DOUBLE(asdecimal=False))  # 择时收益
    var = Column(DOUBLE(asdecimal=False))  # 资产在险值
    r_square = Column(DOUBLE(asdecimal=False))  # 决定系数R方
    sharpe = Column(DOUBLE(asdecimal=False))  # 夏普率
    downside_std = Column(DOUBLE(asdecimal=False))  # 下行风险
    continue_regress_v = Column(DOUBLE(asdecimal=False))  # 收益稳定性
    stock_cl_beta = Column(DOUBLE(asdecimal=False))  # 择时收益
    stock_cl_alpha = Column(DOUBLE(asdecimal=False))  # 选股收益
    prn_hold = Column(DOUBLE(asdecimal=False))  # 私人持有占比

    # derived.FundScoreNew
    tag_name = Column(CHAR(64)) # 基金类别
    #score = Column(DOUBLE(asdecimal=False)) # 评分

    return_score = Column(DOUBLE(asdecimal=False))  # 被动指数型、被动指数型债券(均为二级分类)基金为跟踪标的能力，其他为收益能力
    robust_score = Column(DOUBLE(asdecimal=False))  # 稳定性能力
    risk_score = Column(DOUBLE(asdecimal=False))  # 抗风险能力
    timing_score = Column(DOUBLE(asdecimal=False))  # 被动指数型、被动指数型债券(均为二级分类)基金和货基(一二级分类相同)为管理规模能力，其他为择时能力
    selection_score = Column(DOUBLE(asdecimal=False))  # 被动指数型、被动指数型债券(均为二级分类)基金和货基(一二级分类相同)为机构观点，其他为选证能力
    team_score = Column(DOUBLE(asdecimal=False))  # 基金公司团队能力
    total_score = Column(DOUBLE(asdecimal=False))  # 总分

    # fund recommend part
    sector_list = Column(TEXT) # 板块列表 需要json.loads
    sector_name = Column(TEXT) # 板块名字列表 需要json.loads
    index_list = Column(TEXT) # 指数列表 需要json.loads
    index_name = Column(TEXT) # 指数名字列表 需要json.loads
    top_mng_id = Column(CHAR(64)) # 头名基金经理ID
    top_mng_name = Column(CHAR(64)) # 头名基金经理名字
    top_manager_profit = Column(DOUBLE(asdecimal=False)) # 头名基金经理任期收益
    is_ipo_fund = Column(TINYINT(1)) # 是否是打新基金
    is_abs_ret_fund = Column(TINYINT(1)) # 是否是绝对收益基金 0 否， 1 是
    is_conv_bond_fund = Column(TINYINT(1)) # 是否是可转债基金 0 否， 1 是

    # derived.style_box
    fund_size_type = Column(CHAR(20)) # 基金规模类型
    fund_style_type = Column(CHAR(20)) # 基金风格类型

    # new
    fund_type_1 = Column(CHAR(64))  # 一级策略
    fund_type_2 = Column(CHAR(64))  # 二级策略
    nav_start_date = Column(DATE) # 开始时间
    nav_end_date = Column(DATE) # 截止时间
    nav_date = Column(CHAR(40)) # 净值日期
    nav_frequency = Column(CHAR(32)) # 净值周期
    fund_nav_completion = Column(DOUBLE(asdecimal=False))  # 净值完整度
    recent_3m_ret_annual = Column(DOUBLE(asdecimal=False))  # 近3月年化
    recent_6m_ret_annual = Column(DOUBLE(asdecimal=False))  # 近6月年年化
    this_y_ret_annual = Column(DOUBLE(asdecimal=False))  # 今年年化
    recent_2y_ret_annual = Column(DOUBLE(asdecimal=False))  # 近2年年化
    recent_2y_ret = Column(DOUBLE(asdecimal=False))  # 近1年以来收益
    this_y_mdd = Column(DOUBLE(asdecimal=False))   # 近年以来最大回撤
    recent_3m_mdd = Column(DOUBLE(asdecimal=False))  # 近三个月最大回撤
    recent_6m_mdd = Column(DOUBLE(asdecimal=False))  # 近六个月最大回撤
    recent_1y_mdd = Column(DOUBLE(asdecimal=False))  # 近一年最大回撤
    recent_2y_mdd = Column(DOUBLE(asdecimal=False))  # 近二年最大回撤
    calmar = Column(DOUBLE(asdecimal=False))  # 卡玛比率
    sortino = Column(DOUBLE(asdecimal=False))  # 索提诺

    @staticmethod
    def mul_fund_view_to_private_fund_view():
        # 公募对私募
        return {'fund_id': 'fund_id',
                'full_name': 'desc_name',
                'nav_start_date':'start_date',
                'nav_end_date':'end_date',
                'nav_date':'nav_date',
                'exchange_status':'status',
                'fund_type_1':'fund_type_1',
                'fund_type_2':'fund_type_2',
                'company_name':'company',
                'fund_manager':'manager',
                'nav_frequency':'nav_frequency',
                'fund_nav_completion':'fund_nav_completion',
                'unit_net_value':'unit_net_value',

                'to_date_return': 'history_ret',
                'annualized_returns': 'history_ret_annual',
                'recent_3m_ret_annual':'recent_3m_ret_annual',
                'recent_6m_ret_annual':'recent_6m_ret_annual',
                'this_y_ret_annual':'this_y_ret_annual',
                'recent_2y_ret_annual':'recent_2y_ret_annual',
                'year_to_date_return': 'this_y_ret',
                'last_three_month_return': 'recent_3m_ret',
                'last_six_month_return': 'recent_6m_ret',
                'last_twelve_month_return': 'recent_1y_ret',
                'recent_2y_ret':'recent_2y_ret',

                'annualized_risk':'history_vol',
                'max_drop_down': 'history_mdd',
                'this_y_mdd':'this_y_mdd',
                'recent_3m_mdd':'recent_3m_mdd',
                'recent_6m_mdd':'recent_6m_mdd',
                'recent_1y_mdd':'recent_1y_mdd',
                'recent_2y_mdd':'recent_2y_mdd',

                'sharp_ratio': 'sharpe',
                'var': 'var',
                'calmar':'calmar',
                'sortino':'sortino',
                'var':'var',
                }


    @staticmethod
    def trans_columns():
        return {
            'fund_id': '基金ID',
            'order_book_id': '基金代码',

            'wind_class_I': '基金类型',
            'wind_class_II': '二级分类',
            'symbol': '基金名称',
            'institution_rating': '机构评级',
            'found_to_now': '成立年限',
            'average_size': '基金规模',
            'track_index': '跟踪指数',
            'first_benchmark_name': '第一基准名',

            'exchange_status': '交易状态',
            'purch_status': '申购状态',
            'redem_status': '赎回状态',
            'lp_limit': '暂停大额申购上限',
            'otc_lp_limit': '场外暂停大额申购上限',
            'otc_lp_limit_jg': '场外暂停大额申购上限(机构)',
            'otc_lp_limit_gr': '场外暂停大额申购上限(个人)',
            'price_begin_date':'净值开始时间',
            'price_end_date':'净值结束时间',

            'adjusted_net_value': '复权净值',
            'unit_net_value': '净值',
            'acc_net_value': '累计净值',
            'change_rate': '日收益率',
            'found_date': '成立日期',
            'end_date': '关闭日期',
            'annualized_returns': '年化收益',
            'annualized_risk': '成立以来年化风险',
            'information_ratio': '成立以来信息比率',
            'last_week_return': '近1周',
            'last_month_return': '近1月',
            'last_three_month_return': '近3月',
            'last_six_month_return': '近半年',
            'last_twelve_month_return': '近1年',
            'year_to_date_return': '年初至今',
            'to_date_return': '成立至今',
            'sharp_ratio': '夏普比率',
            'y3_ret': '近3年',
            'y5_ret': '近5年',
            'vol': '成立以来波动率',
            'max_drop_down': '最大回撤',
            'fund_manager': '基金经理',
            'fund_manager_id': '基金经理ID',
            'company_name': '基金公司',
            'benchmark': '业绩基准',
            'benchmark_s': '跟踪标的ID',
            'benchmark_name': '跟踪标的',

            'last_week_return_rank': '近一周同类排名',
            'last_month_return_rank': '近一月同类排名',
            'last_three_month_return_rank': '近三月同类排名',
            'last_six_month_return_rank': '近六月同类排名',
            'last_twelve_month_return_rank': '近一年同类排名',
            'y3_ret_rank': '近三年同类排名',
            'y5_ret_rank': '近五年同类排名',
            'year_to_date_return_rank': '年初至今同类排名',
            'to_date_return_rank': '成立以来同类排名',
            'group_num': '同类数量',
            'manager_profit':'基金经理任期收益',

            'zs': '招商评级',
            'sh3': '上证三年评级',
            'sh5': '上证五年评级',
            'jajx': '济安评级',
            'mornstar_3y': '晨星三年评级',
            'mornstar_5y': '晨星五年评级',

            'track_err': '跟踪误差',
            'this_y_alpha': '今年以来超额收益',
            'cumulative_alpha': '成立以来超额收益',
            'w1_alpha': '近一周超额收益',
            'm1_alpha': '近一月超额收益',
            'm3_alpha': '近三月超额收益',
            'm6_alpha': '近半年超额收益',
            'y1_alpha': '近一年超额收益',
            'y3_alpha': '近三年超额收益',
            'y5_alpha': '近五年超额收益',
            'y10_alpha': '近十年超额收益',
            'latest_size': '最新规模',

            'beta': 'beta',
            'alpha': 'alpha',
            'tag_track_err': 'tag跟踪误差',
            'fee_rate': '费率',
            'info_ratio': '_信息比率',
            'treynor': '_特雷诺比率',
            'mdd': '_净值最大回撤',
            'down_risk': '_下行风险',
            'ret_over_period': '_区间收益率',
            'annual_avg_daily_ret': '_年化日均收益',
            'annual_vol': '_年化波动率',
            'annual_ret': '_年化收益率',
            'm_square': '_M平方测度',
            'time_ret': '_择时收益',
            'var': '_资产在险值',
            'r_square': '_决定系数R方',
            'sharpe': '_夏普率',
            'downside_std':'下行风险',
            'continue_regress_v':'收益稳定性',
            'stock_cl_beta':'择时收益',
            'stock_cl_alpha':'选股收益',
            'prn_hold':'私人持有占比',

            'tag_name': '基金类别',
            'fund_size_type':'基金规模类别',
            'fund_style_type':'基金风格类别',

            'return_score': '收益能力',
            'robust_score': '稳定性能力',
            'risk_score': '抗风险能力',
            'timing_score': '择时能力',
            'selection_score': '选证能力',
            'team_score': '团队能力',
            'total_score': '总分',

            'sector_list': '板块列表',
            'sector_name': '板块名字列表',
            'index_list': '指数列表',
            'index_name': '指数名字列表',
            'top_mng_id': '头名基金经理ID',
            'top_mng_name': '头名基金经理名字',
            'top_manager_profit':'头名基金经理任期收益',
            'is_abs_ret_fund': '是否是绝对收益基金',
            'is_conv_bond_fund': '是否是可转债基金',
            'is_ipo_fund': '是否是打新基金',
            'fund_type': '基金大类类型',
            'risk_level':'风险等级',
            'full_name':'基金全名',
            'currency':'币种',
            'manage_fee':'管理费',
            'trustee_fee':'托管费',
            'purchase_fee':'申购费',
            'redeem_fee':'赎回费',
            'benchmark_1':'业绩基准标的指数简称第一名',
            'benchmark_2':'业绩基准标的指数简称第二名',
            'subscr_fee_detail':'认购费率详情',
            'purchase_fee_detail':'申购费率详情',
            'redeem_fee_detail':'赎回费率详情',
            'service_fee':'销售服务费率',

            'fund_type_1':'一级策略',
            'fund_type_2':'二级策略',
            'nav_start_date':'开始时间',
            'nav_end_date':'截止时间',
            'nav_date':'净值日期',
            'nav_frequency':'净值周期',
            'fund_nav_completion':'净值完整度',
            'recent_3m_ret_annual':'近3月年化',
            'recent_6m_ret_annual':'近6月年年化',
            'this_y_ret_annual':'今年年化',
            'recent_2y_ret_annual ':'近2年年化',
            'recent_2y_ret':'近1年以来收益',
            'this_y_mdd':'近年以来最大回撤',
            'recent_3m_mdd':'近三个月最大回撤',
            'recent_6m_mdd':'近六个月最大回撤',
            'recent_1y_mdd':'近一年最大回撤',
            'recent_2y_mdd':'近二年最大回撤',
            'calmar':'卡玛比率',
            'sortino':'索提诺',
        }


class IndexDailyCollection(Base):
    """基金信息日度收集"""

    __tablename__ = 'index_daily_collection'

    # derived.IndexValuationLongTerm
    index_id = Column(CHAR(20), primary_key=True)  # 指数ID
    datetime = Column(DATE, primary_key=True)  # 日期
    pb_mrq = Column(DOUBLE(asdecimal=False))  # 市净率-MRQ
    pe_ttm = Column(DOUBLE(asdecimal=False))  # 市盈率-MMT
    peg_ttm = Column(DOUBLE(asdecimal=False))  # PEG-MMT
    est_peg = Column(DOUBLE(asdecimal=False))  # 预测peg
    roe = Column(DOUBLE(asdecimal=False))  # 净资产收益率-MMT
    dy = Column(DOUBLE(asdecimal=False))  # 股息率-MMT
    pe_pct = Column(DOUBLE(asdecimal=False))  # PE百分位
    pb_pct = Column(DOUBLE(asdecimal=False))  # PB百分位
    ps_pct = Column(DOUBLE(asdecimal=False))  # PS百分位
    val_score = Column(DOUBLE(asdecimal=False))  # 估值评分
    liqmv = Column(DOUBLE(asdecimal=False))  # 流通市值

    # calc based on derived.IndexValuationLongTerm pe_ttm pb_mrq
    pe_0_percentile = Column(DOUBLE(asdecimal=False))  # pe0分位
    pe_30_percentile = Column(DOUBLE(asdecimal=False))  # pe30分位
    pe_70_percentile = Column(DOUBLE(asdecimal=False))  # pe70分位
    pe_100_percentile = Column(DOUBLE(asdecimal=False))  # pe100分位
    pb_0_percentile = Column(DOUBLE(asdecimal=False))  # pb0分位
    pb_30_percentile = Column(DOUBLE(asdecimal=False))  # pb30分位
    pb_70_percentile = Column(DOUBLE(asdecimal=False))  # pb70分位
    pb_100_percentile = Column(DOUBLE(asdecimal=False))  # pb100分位

    # derived.IndexVolatility
    vol_datetime = Column(DATE)  # 日期
    w1_vol = Column(DOUBLE(asdecimal=False))  # 近一周波动率
    m1_vol = Column(DOUBLE(asdecimal=False))  # 近一月波动率
    m3_vol = Column(DOUBLE(asdecimal=False))  # 近三月波动率
    m6_vol = Column(DOUBLE(asdecimal=False))  # 近半年波动率
    y1_vol = Column(DOUBLE(asdecimal=False))  # 近一年波动率
    y3_vol = Column(DOUBLE(asdecimal=False))  # 近三年波动率
    y5_vol = Column(DOUBLE(asdecimal=False))  # 近五年波动率
    y10_vol = Column(DOUBLE(asdecimal=False))  # 近十年波动率
    this_y_vol = Column(DOUBLE(asdecimal=False))  # 今年以来波动率
    cumulative_vol = Column(DOUBLE(asdecimal=False))  # 成立至今波动率

    # derived.IndexReturn
    ret_datetime = Column(DATE)  # 日期
    w1_ret = Column(DOUBLE(asdecimal=False))  # 近一周收益率
    m1_ret = Column(DOUBLE(asdecimal=False))  # 近一月收益率
    m3_ret = Column(DOUBLE(asdecimal=False))  # 近三月收益率
    m6_ret = Column(DOUBLE(asdecimal=False))  # 近半年收益率
    y1_ret = Column(DOUBLE(asdecimal=False))  # 近一年收益率
    y3_ret = Column(DOUBLE(asdecimal=False))  # 近三年收益率
    y5_ret = Column(DOUBLE(asdecimal=False))  # 近五年收益率
    y10_ret = Column(DOUBLE(asdecimal=False))  # 近十年收益率
    this_y_ret = Column(DOUBLE(asdecimal=False))  # 今年以来收益率
    cumulative_ret = Column(DOUBLE(asdecimal=False))  # 成立至今收益率

    # basic.IndexPrice
    price_datetime = Column(DATE)  # 日期
    volume = Column(DOUBLE(asdecimal=False))  # 交易量
    low = Column(DOUBLE(asdecimal=False))  # 最低价
    close = Column(DOUBLE(asdecimal=False))  # 收盘价
    high = Column(DOUBLE(asdecimal=False))  # 最高价
    open = Column(DOUBLE(asdecimal=False))  # 开盘价
    total_turnover = Column(DOUBLE(asdecimal=False))  # 成交额
    ret = Column(DOUBLE(asdecimal=False))  # 收益率
    yest_close = Column(DOUBLE(asdecimal=False))  # 前收盘价
    price_begin_date = Column(DATE)  # 净值开始时间
    price_end_date = Column(DATE)  # 净值结束时间

    # basic.IndexInfo
    order_book_id = Column(CHAR(20))  # 米筐ID
    industry_tag = Column(CHAR(64))  # 行业标签
    tag_method = Column(CHAR(64))  # 估值评分采用方法
    desc_name = Column(CHAR(64))  # 名称
    id_cat = Column(CHAR(64), nullable=False)  # 所属类型
    is_select = Column(BOOLEAN, nullable=False)  # 是否属于精选
    val_level = Column(CHAR(10))  # 指数估值水平

    @staticmethod
    def trans_columns():
        return {
            'index_id': '指数ID',
            'datetime': '日期',
            'w1_vol': '近一周波动率',
            'm1_vol': '近一月波动率',
            'm3_vol': '近三月波动率',
            'm6_vol': '近半年波动率',
            'y1_vol': '近一年波动率',
            'y3_vol': '近三年波动率',
            'y5_vol': '近五年波动率',
            'y10_vol': '近十年波动率',
            'this_y_vol': '今年以来波动率',
            'cumulative_vol': '成立至今波动率',

            'ret_datetime': 'ret日期',
            'w1_ret': '近一周收益率',
            'm1_ret': '近一月收益率',
            'm3_ret': '近三月收益率',
            'm6_ret': '近半年收益率',
            'y1_ret': '近一年收益率',
            'y3_ret': '近三年收益率',
            'y5_ret': '近五年收益率',
            'y10_ret': '近十年收益率',
            'this_y_ret': '今年以来收益率',
            'cumulative_ret': '成立至今收益率',

            'pb_mrq': 'PB',
            'pe_ttm': 'PE',
            'peg_ttm': 'PEG-TTM',
            'est_peg': '预测PEG',
            'roe': 'ROE',
            'dy': '股息率',
            'pe_pct': 'PE百分位',
            'pb_pct': 'PB百分位',
            'ps_pct': 'PS百分位',
            'val_score': '估值评分',
            'alpha_datetime': 'alpha日期',
            'liqmv': '流通市值',

            'pe_0_percentile': 'pe0分位',
            'pe_30_percentile': 'pe30分位',
            'pe_70_percentile': 'pe70分位',
            'pe_100_percentile': 'pe100分位',
            'pb_0_percentile': 'pb0分位',
            'pb_30_percentile': 'pb30分位',
            'pb_70_percentile': 'pb70分位',
            'pb_100_percentile': 'pb100分位',

            'price_datetime': '价格日期',
            'volume': '交易量',
            'low': '最低价',
            'close': '收盘价',
            'high': '最高价',
            'open': '开盘价',
            'total_turnover': '成交额',
            'ret': '收益率',
            'yest_close': '前收盘价',
            'price_begin_date':'净值开始时间',
            'price_end_date':'净值结束时间',

            'order_book_id': '指数代码',
            'industry_tag': '行业标签',
            'tag_method': '估值评分采用方法',
            'desc_name': '指数名称',
            'id_cat': '所属类型',
            'is_select': '精选指数',
            'val_level': '估值水平',
        }


class TianData(Base):

    __tablename__ = 'tian_data_collection'

    CODES = Column('stock_id', CHAR(10), primary_key=True)  # EM股票ID
    NAME = Column('name', TEXT, nullable=False)  # 股票简称
    CLOSE = Column('close', DOUBLE(asdecimal=False), nullable=False)  # 收盘价
    TOTALSHARE = Column('total_share', DOUBLE(asdecimal=False), nullable=False)  # 总股本
    HOLDFROZENAMTACCUMRATIO = Column('hold_frozen_amt_accum_ratio', DOUBLE(asdecimal=False))  # 控股股东累计质押数量占持股比例
    PNITTMR = Column('pni_ttmr', DOUBLE(asdecimal=False))  # 归属母公司股东的净利润TTM(报告期)
    PERFORMANCEEXPRESSPARENTNI = Column('performance_express_parent_ni', DOUBLE(asdecimal=False))  # 业绩快报.归属母公司股东的净利润
    ASSETMRQ = Column('asset_mrq', DOUBLE(asdecimal=False))  # 资产总计(MRQ)
    EQUITYMRQ = Column('equity_mrq', DOUBLE(asdecimal=False))  # 归属母公司股东的权益(MRQ)(净资产)
    PETTMDEDUCTED = Column('pe_ttm_deducted', DOUBLE(asdecimal=False))  # 市盈率TTM(扣除非经常性损益)
    PBLYRN = Column('pb_lyr_n', DOUBLE(asdecimal=False))  # 市净率(PB，LYR)(按公告日)
    PSTTM = Column('ps_ttm', DOUBLE(asdecimal=False))  # 市销率(PS，TTM)
    AHOLDER = Column('a_holder', DOUBLE(asdecimal=False))  # 实际控制人
    MBSALESCONS = Column('mb_sales_cons_lyr', DOUBLE(asdecimal=False))  # 主营收入构成(最近一期年报LYR)
    GPMARGIN = Column('gp_margin_lyr', DOUBLE(asdecimal=False))  # 销售毛利率(最近一期年报LYR)
    NPMARGIN = Column('np_margin', DOUBLE(asdecimal=False))  # 销售净利率(营业收入/净利润)(最近三年一期)
    INVTURNRATIO = Column('inv_turn_ratio_lyr', DOUBLE(asdecimal=False))  # 存货周转率(最近一期年报LYR)
    ARTURNRATIO = Column('ar_turn_ratio_lyr', DOUBLE(asdecimal=False))  # 应收账款周转率(含应收票据)(最近一期年报LYR)
    EXPENSETOOR = Column('expense_toor', DOUBLE(asdecimal=False)) # 销售期间费用率
    ROEAVG = Column('row_avg', DOUBLE(asdecimal=False)) # 净资产收益率ROE(平均)
    ROEWA = Column('row_wa', DOUBLE(asdecimal=False)) # 净资产收益率ROE(加权)
    EPSBASIC = Column('eps_basic', DOUBLE(asdecimal=False)) # 每股收益EPS(基本)
    EPSDILUTED = Column('eps_diluted', DOUBLE(asdecimal=False)) # 每股收益EPS(稀释)
    BPS = Column('bps', DOUBLE(asdecimal=False)) # 每股净资产
    BALANCESTATEMENT_25 = Column('balance_statement_25', DOUBLE(asdecimal=False)) # 流动资产合计
    BALANCESTATEMENT_46 = Column('balance_statement_46', DOUBLE(asdecimal=False)) # 非流动资产合计
    BALANCESTATEMENT_93 = Column('balance_statement_93', DOUBLE(asdecimal=False)) # 流动负债合计
    BALANCESTATEMENT_103 = Column('balance_statement_103', DOUBLE(asdecimal=False)) # 非流动负债合计
    BALANCESTATEMENT_141 = Column('balance_statement_141', DOUBLE(asdecimal=False)) # 股东权益合计
    BALANCESTATEMENT_140 = Column('balance_statement_140', DOUBLE(asdecimal=False)) # 归属于母公司股东权益合计
    INCOMESTATEMENT_9 = Column('income_statement_9', DOUBLE(asdecimal=False)) # 营业收入
    INCOMESTATEMENT_48 = Column('income_statement_48', DOUBLE(asdecimal=False)) # 营业利润
    INCOMESTATEMENT_60 = Column('income_statement_60', DOUBLE(asdecimal=False)) # 净利润
    INCOMESTATEMENT_61 = Column('income_statement_61', DOUBLE(asdecimal=False)) # 归属于母公司股东的净利润
    INCOMESTATEMENT_85 = Column('income_statement_85', DOUBLE(asdecimal=False)) # 其他业务收入
    INCOMESTATEMENT_127 = Column('income_statement_127', DOUBLE(asdecimal=False)) # 利息费用
    INCOMESTATEMENT_14 = Column('income_statement_14', DOUBLE(asdecimal=False)) # 财务费用
    CASHFLOWSTATEMENT_39 = Column('cashflow_statement_39', DOUBLE(asdecimal=False)) # 经营活动产生的现金流量净额
    CASHFLOWSTATEMENT_59 = Column('cashflow_statement_59', DOUBLE(asdecimal=False)) # 投资活动产生的现金流量净额
    CASHFLOWSTATEMENT_77 = Column('cashflow_statement_77', DOUBLE(asdecimal=False)) # 筹资活动产生的现金流量净额
    CASHFLOWSTATEMENT_82 = Column('cashflow_statement_82', DOUBLE(asdecimal=False)) # 现金及现金等价物净增加额
    CASHFLOWSTATEMENT_86 = Column('cashflow_statement_86', DOUBLE(asdecimal=False)) # 资产减值准备
    long_term_libility_to_asset = Column(DOUBLE(asdecimal=False))  # 长期资产负债率
    current_ratio = Column(DOUBLE(asdecimal=False))  # 流动比率
    quick_ratio = Column(DOUBLE(asdecimal=False))  # 速动比率


class AutomaticInvestmentCollection(Base):
    """定投收益收集"""

    __tablename__ = 'automatic_investment_collection'

    # derived.FundAIC
    fund_id = Column(CHAR(20), primary_key=True)  # 基金ID
    price_time = Column(CHAR(20), primary_key=True)  # 时间
    y1_ret = Column(DOUBLE(asdecimal=False))  # 普通定投一年收益
    y3_ret = Column(DOUBLE(asdecimal=False))  # 普通定投三年收益
    y5_ret = Column(DOUBLE(asdecimal=False))  # 普通定投五年收益
    intel_y1_ret = Column(DOUBLE(asdecimal=False))  # 智能定投一年收益
    intel_y3_ret = Column(DOUBLE(asdecimal=False))  # 智能定投三年收益
    intel_y5_ret = Column(DOUBLE(asdecimal=False))  # 智能定投五年收益

    @staticmethod
    def trans_columns():
        return {
            'fund_id': '基金ID',
            'price_time': '定投收益日期',
            'y1_ret': '普通定投一年收益',
            'y3_ret': '普通定投三年收益',
            'y5_ret': '普通定投五年收益',
            'intel_y1_ret': '智能定投一年收益',
            'intel_y3_ret': '智能定投三年收益',
            'intel_y5_ret': '智能定投五年收益',
        }


class FundRecommendationCollection(Base):
    """基金推荐月度收集"""

    __tablename__ = 'fund_recommendation_collection'

    fund_id = Column(CHAR(10), primary_key=True) # 基金ID
    order_book_id = Column(CHAR(10)) # 基金代码
    desc_name = Column(CHAR(64)) # 基金名称
    company_id = Column(CHAR(64)) # 基金公司
    wind_class_1 = Column(CHAR(64)) # Wind基金类型
    wind_class_2 = Column(CHAR(64)) # Wind基金二级类型
    risk_level = Column(CHAR(2))  # 风险等级
    is_ipo_fund = Column(TINYINT(1)) # 是否是打新基金
    sector_list = Column(TEXT) # 板块列表 需要json.loads
    sector_name = Column(TEXT) # 板块名字列表 需要json.loads
    index_list = Column(TEXT) # 指数列表 需要json.loads
    index_name = Column(TEXT) # 指数名字列表 需要json.loads
    mdd = Column(DOUBLE(asdecimal=False)) # 最大回撤
    annual_ret = Column(DOUBLE(asdecimal=False)) # 年化收益
    ret_ability = Column(DOUBLE(asdecimal=False)) # 收益能力
    risk_ability = Column(DOUBLE(asdecimal=False)) # 风险能力
    stable_ability = Column(DOUBLE(asdecimal=False)) # 稳定能力
    select_time = Column(DOUBLE(asdecimal=False)) # 择时能力
    select_stock = Column(DOUBLE(asdecimal=False)) # 择股能力
    mng_score = Column(DOUBLE(asdecimal=False)) # 团队能力
    total_score = Column(DOUBLE(asdecimal=False)) # 总分
    mng_id = Column(CHAR(64)) # 基金经理id
    mng_name = Column(CHAR(64)) # 基金经理名字
    fund_type = Column(CHAR(64)) # 基金大类类型
    is_abs_ret_fund = Column(TINYINT(1)) # 是否是绝对收益基金 0 否， 1 是
    is_conv_bond_fund = Column(TINYINT(1)) # 是否是可转债基金 0 否， 1 是

    @staticmethod
    def trans_columns():
        return {
            'fund_id': '基金ID',
            'order_book_id': '基金代码',
            'desc_name': '基金名称',
            'company_id': '基金公司名字',
            'wind_class_1': '基金类型一',
            'wind_class_2': '基金类型二',
            'risk_level': '基金风险等级',
            'is_ipo_fund': '是否是打新基金',
            'sector_list': '板块列表',
            'sector_name': '板块名字列表',
            'index_list': '指数列表',
            'index_name': '指数名字列表',
            'mdd': '最大回撤',
            'annual_ret': '年化收益',
            'ret_ability': '基金收益能力',
            'risk_ability': '基金风险能力',
            'stable_ability': '基金稳定能力',
            'select_time': '基金择时能力',
            'select_stock': '基金择股能力',
            'mng_score': '基金团队能力',
            'total_score': '基金总分',
            'mng_id': '基金经理id',
            'mng_name': '基金经理名字',
            'is_abs_ret_fund': '是否是绝对收益基金',
            'is_conv_bond_fund': '是否是可转债基金',
            'fund_type': '基金大类类型',
        }


class ManagerInfoCollection(Base):
    """基金经理评价"""

    __tablename__ = 'manager_info_collection'

    mng_id = Column(CHAR(10), primary_key=True) # 经理ID
    mng_name = Column(CHAR(30)) # 经理名
    introduction = Column(TEXT) # 介绍
    fund_type = Column(CHAR(64)) # 基金大类类型


class StockIpoCollection(Base):
    """股票打新数据"""

    __tablename__ = 'stock_ipo_collection'

    stock_code = Column(CHAR(10), primary_key=True) # 股票ID
    stock_name = Column(CHAR(30)) # 股票名
    trade_market = Column(CHAR(40)) # 交易板块
    list_date = Column(DATE) # 上市日期
    ipo_price = Column(DOUBLE(asdecimal=False)) # 发行价
    latest_price = Column(DOUBLE(asdecimal=False)) # 最新价
    latest_rate = Column(DOUBLE(asdecimal=False)) # 涨跌幅
    cumulate_rate = Column(DOUBLE(asdecimal=False)) # 累计涨幅
    first_date_rate = Column(DOUBLE(asdecimal=False)) # 首日涨幅
    continue_limited_rise = Column(DOUBLE(asdecimal=False)) # 连续涨停
    earn_per_stick = Column(DOUBLE(asdecimal=False)) # 每签获利

    @staticmethod
    def trans_columns():
        return {
            'stock_code': '股票ID',
            'stock_name': '股票名',
            'trade_market': '交易板块',
            'list_date': '上市日期',
            'ipo_price': '发行价',
            'latest_price': '最新价',
            'latest_rate': '涨跌幅',
            'cumulate_rate': '累计涨幅',
            'first_date_rate': '首日涨幅',
            'continue_limited_rise': '连续涨停',
            'earn_per_stick': '每签获利',
        }

class ConvBondIpoCollection(Base):
    '''可转债券打新数据'''

    __tablename__ = 'conv_bond_collection'

    bond_id = Column(CHAR(10), primary_key=True) # 可债ID
    bond_name = Column(CHAR(30)) # 债券名字
    list_date = Column(DATE) # 上市日期
    ipo_price = Column(DOUBLE(asdecimal=False)) # 发行价
    trade_market = Column(CHAR(5)) # 市场名字
    new_price = Column(DOUBLE(asdecimal=False)) # 最新价
    total_ret = Column(DOUBLE(asdecimal=False)) # 累计涨幅
    first_open = Column(DOUBLE(asdecimal=False)) # 首日开盘价
    earn_per_account = Column(DOUBLE(asdecimal=False)) # 单账户收益
    earn_per_stick = Column(DOUBLE(asdecimal=False)) # 单签收益
    first_date_rate = Column(DOUBLE(asdecimal=False)) # 首日涨幅
    rate = Column(DOUBLE(asdecimal=False)) # 中签率
    limit_num = Column(DOUBLE(asdecimal=False)) # 认购数量上限

    @staticmethod
    def trans_columns():
        return {
            'bond_id': '可转债ID',
            'bond_name': '债券名字',
            'list_date': '上市日期',
            'ipo_price': '发行价',
            'trade_market': '市场代码',
            'new_price':'最新价',
            'total_ret': '累计涨幅',
            'first_open': '首日开盘价',
            'first_date_rate': '首日涨幅',
            'earn_per_account': '单账户收益',
            'earn_per_stick': '每签获利',
            'rate':'中签率',
            'limit_num':'认购数量上限',
        }


class FundManagerDailyCollection(Base):
    """基金经理数据"""

    __tablename__ = 'fund_manager_daily_collection'

    
    mng_id = Column(CHAR(10), primary_key=True) # 基金经理id
    fund_type = Column(CHAR(20), primary_key=True) # 基金类型
    name = Column(CHAR(25)) # 姓名
    mdd_history_daily = Column(DOUBLE(asdecimal=False)) # 历史最大回撤
    annual_ret_history_m = Column(DOUBLE(asdecimal=False)) # 历史年化收益
    total_score = Column(DOUBLE(asdecimal=False)) # 经理总分
    ret_ability = Column(DOUBLE(asdecimal=False)) # 收益能力
    risk_ability = Column(DOUBLE(asdecimal=False)) # 抗风险能力
    select_time = Column(DOUBLE(asdecimal=False)) # 择时能力
    select_stock = Column(DOUBLE(asdecimal=False)) # 选股能力
    stable_ability = Column(DOUBLE(asdecimal=False)) # 稳定能力
    experience = Column(DOUBLE(asdecimal=False)) # 经验能力
    mdd_5y_m = Column(DOUBLE(asdecimal=False)) # 近五年最大回撤
    annual_ret_5y_m = Column(DOUBLE(asdecimal=False)) # 近五年年化收益
    mdd_3y_m = Column(DOUBLE(asdecimal=False)) # 近三年最大回撤
    annual_ret_3y_m = Column(DOUBLE(asdecimal=False)) # 近三年年化收益
    mdd_1y_m = Column(DOUBLE(asdecimal=False)) # 近一年最大回撤
    annual_ret_1y_m = Column(DOUBLE(asdecimal=False)) # 近一年年化收益
    trading_days = Column(Integer) # 从业天数
    best_fund = Column(CHAR(10)) # 代表作品
    company_id = Column(CHAR(64)) # 基金公司


    @staticmethod
    def trans_columns():
        return {
            'mng_id':'基金经理id',
            'name':'姓名',
            'fund_type':'基金类型',
            'mdd_history_daily':'历史最大回撤',
            'annual_ret_history_m':'历史年化收益',
            'total_score':'经理总分',
            'ret_ability':'收益能力',
            'risk_ability':'抗风险能力',
            'select_time':'择时能力',
            'select_stock':'选股能力',
            'stable_ability':'稳定能力',
            'experience':'经验能力',
            'mdd_5y_m':'近五年最大回撤',
            'annual_ret_5y_m':'近五年年化收益',
            'mdd_3y_m':'近三年最大回撤',
            'annual_ret_3y_m':'近三年年化收益',
            'mdd_1y_m':'近一年最大回撤',
            'annual_ret_1y_m':'近一年年化收益',
            'trading_days':'从业天数',
            'best_fund':'代表作品',
            'company_id':'基金公司',
        }

class HFFundDailyCollection(Base):
    """基金信息日度收集"""

    __tablename__ = 'hf_fund_daily_collection'

    fund_id = Column(CHAR(20), primary_key=True)  # 基金ID
    begin_date = Column(CHAR(20), primary_key=True)  # 时间
    stg_type = Column(CHAR(20))  # 基金代码
    desc_name = Column(CHAR(40)) # 基金名
    agency_id = Column(CHAR(10)) # 机构id
    agency_name = Column(CHAR(20)) # 机构名
    manager_name = Column(CHAR(20)) # 基金经理名
    source = Column(CHAR(20)) # 来源
    nav_source = Column(CHAR(10)) # 净值来源

    annual_ret = Column(DOUBLE(asdecimal=False))  # 成立以来年化收益率
    annual_vol = Column(DOUBLE(asdecimal=False))  # 成立以来年化波动率
    sharpe_ratio = Column(DOUBLE(asdecimal=False))  # 成立以来夏普比率
    price_begin_date = Column(DATE)  # 净值开始时间
    price_end_date = Column(DATE)  # 净值开始时间

class PFFundDailyCollection(Base):
    """私募信息日度收集"""

    __tablename__ = 'pf_fund_daily_collection'

    fund_id = Column(CHAR(20), primary_key=True)  # 基金ID
    desc_name = Column(CHAR(40)) # 基金名
    start_date = Column(DATE) # 开始时间
    end_date = Column(DATE) # 截止时间
    nav_date = Column(CHAR(40)) # 净值日期
    status = Column(CHAR(40)) # 运行状态
    fund_type_1 = Column(CHAR(40)) # 一级策略
    fund_type_2 = Column(CHAR(40)) # 二级策略
    company = Column(CHAR(80)) # 投资顾问
    manager = Column(CHAR(80)) # 基金经理
    nav_frequency = Column(CHAR(32)) # 净值周期
    fund_nav_completion = Column(DOUBLE(asdecimal=False))  # 净值完整度
    unit_net_value = Column(DOUBLE(asdecimal=False))  # 单位净值

    # 收益
    history_ret = Column(DOUBLE(asdecimal=False))  # 成立以来收益
    history_ret_annual = Column(DOUBLE(asdecimal=False))  # 成立以来年化
    recent_3m_ret_annual = Column(DOUBLE(asdecimal=False))  # 近3月年化
    recent_6m_ret_annual = Column(DOUBLE(asdecimal=False))  # 近6月年年化
    this_y_ret_annual = Column(DOUBLE(asdecimal=False))  # 今年年化
    recent_2y_ret_annual = Column(DOUBLE(asdecimal=False))  # 近2年年化
    this_y_ret = Column(DOUBLE(asdecimal=False))  # 今年以来收益
    recent_3m_ret = Column(DOUBLE(asdecimal=False))  # 近3月年以来收益    
    recent_6m_ret = Column(DOUBLE(asdecimal=False))  # 近6月以来收益
    recent_1y_ret = Column(DOUBLE(asdecimal=False))  # 近1年以来收益    
    recent_2y_ret = Column(DOUBLE(asdecimal=False))  # 近2年以来收益
    
    # 风险
    history_vol = Column(DOUBLE(asdecimal=False))  # 成立以来波动
    history_mdd = Column(DOUBLE(asdecimal=False))  # 成立以来最大回撤
    this_y_mdd = Column(DOUBLE(asdecimal=False))   # 近年以来最大回撤
    recent_3m_mdd = Column(DOUBLE(asdecimal=False))  # 近三个月最大回撤
    recent_6m_mdd = Column(DOUBLE(asdecimal=False))  # 近六个月最大回撤
    recent_1y_mdd = Column(DOUBLE(asdecimal=False))  # 近一年最大回撤
    recent_2y_mdd = Column(DOUBLE(asdecimal=False))  # 近二年最大回撤
    
    # 综合
    sharpe = Column(DOUBLE(asdecimal=False))  # 夏普
    calmar = Column(DOUBLE(asdecimal=False))  # 卡玛比率
    sortino = Column(DOUBLE(asdecimal=False))  # 索提诺
    var = Column(DOUBLE(asdecimal=False))  # VaR
    

    @staticmethod
    def trans_columns():
        return {
            'fund_id':'基金ID',
            'desc_name':'基金名',
            'start_date':'开始时间',
            'end_date':'截止时间',
            'nav_date':'净值日期',
            'status':'运行状态',
            'fund_type_1':'一级策略',
            'fund_type_2':'二级策略',
            'company':'投资顾问',
            'manager':'基金经理',
            'nav_frequency':'净值周期',
            'fund_nav_completion':'净值完整度',
            'unit_net_value':'单位净值',

            'history_ret':'成立以来收益',
            'history_ret_annual':'成立以来年化',
            'recent_3m_ret_annual':'近3月年化',
            'recent_6m_ret_annual':'近6月年化',
            'this_y_ret_annual':'今年年化',
            'recent_2y_ret_annual':'近2年年化',
            'this_y_ret':'今年以来收益',
            'recent_3m_ret':'近3月年以来收益',   
            'recent_6m_ret':'近6月以来收益',
            'recent_1y_ret':'近1年以来收益',
            'recent_2y_ret':'近1年以来收益',
            
            'history_vol':'成立以来波动',
            'history_mdd':'成立以来最大回撤',
            'this_y_mdd':'近年以来最大回撤',
            'recent_3m_mdd':'近三个月最大回撤',
            'recent_6m_mdd':'近六个月最大回撤',
            'recent_1y_mdd':'近一年最大回撤',
            'recent_2y_mdd':'近二年最大回撤',
            
            'sharpe':'夏普',
            'calmar':'卡玛比率',
            'sortino':'索提诺',
            'var':'VaR',
        }
