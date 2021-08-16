import datetime

from sqlalchemy import CHAR, Column, Integer, Index, BOOLEAN, text, TEXT, Enum, VARCHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import DOUBLE, DATE, TINYINT, SMALLINT, DATETIME, MEDIUMTEXT, BIGINT, SMALLINT, DECIMAL
from sqlalchemy.sql.selectable import ScalarSelect

from ...constant import SectorType, IndexPriceSource, HoldingAssetType, FundStatus


class Base:
    _update_time = Column('_update_time', DATETIME, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  # 更新时间

# make this column at the end of every derived table
Base._update_time._creation_order = 9999
Base = declarative_base(cls=Base)



class PfundInstScaleAmac(Base):
    '''私募基金管理人规模'''

    __tablename__ = 'pfund_inst_scale_amac'
    
    party_id = Column(BIGINT, primary_key=True) # 机构内部编码
    
    party_full_name = Column(CHAR(300)) # 机构名称 
    main_fund_type = Column(CHAR(200)) # 管理基金主要类别 
    fund_types = Column(CHAR(200)) # 管理基金主要类别 # todo
    scale = Column(CHAR(50)) # 管理规模 
    inst_id = Column(CHAR(60)) # 源数据id 
    num = Column(Integer) # 变更次数 
    is_new = Column(Integer) # 是否最新
    fetch_time = Column(DATE) # 变动时间 
    update_time = Column(DATETIME) # 更新时间 
    

class PfundManagerInfo(Base):
    '''私募基金经理基本信息表'''

    __tablename__ = 'pfund_manager_info'
    
    person_id = Column(CHAR(60), primary_key=True) # 人员ID
    
    name = Column(CHAR(60)) # 姓名 
    gender = Column(CHAR(60)) # 性别 
    brithday = Column(CHAR(60)) # 生日 
    nationality_cd = Column(CHAR(60)) # 国籍 
    certificate = Column(CHAR(300)) # 证书 
    photo = Column(CHAR(200)) # 照片
    education = Column(Integer) # 最高学历 
    grad_univ = Column(CHAR(60)) # 毕业院校 
    major = Column(CHAR(60)) # 所学专业
    background_desc = Column(TEXT) # 简介
    background = Column(CHAR(60)) # 背景
    mf_to_pf = Column(TINYINT) # 是否公转私/私转公
    year = Column(DECIMAL(4,2)) # 投资年限
    awards_name = Column(CHAR(2000)) # 所获荣誉
    department = Column(CHAR(60)) # 所在部门
    position = Column(CHAR(500)) # 职务
    is_qual = Column(Integer) # 是否具备基金从业资格
    num_dura = Column(BIGINT) # 当前管理的基金数量
    dura_sec_id = Column(MEDIUMTEXT) # 当前管理的基金ID
    dura_sec_name = Column(MEDIUMTEXT) # 当前管理的基金
    party_id = Column(BIGINT) # 任职机构ID
    party_full_name = Column(CHAR(300)) # 任职机构
    rep_sec_id = Column(BIGINT) # 代表产品ID
    rep_sec_name = Column(CHAR(300)) # 代表产品
    return_man_a = Column(DECIMAL(18,10)) # 任职收益
    remark = Column(CHAR(300)) # 备注
    update_time = Column(DATETIME) # 更新时间

class PfundNav(Base):
    '''私募净值'''

    __tablename__ = 'pfund_nav'
    
    security_id = Column(BIGINT, primary_key=True) # 证券内部编码
    publish_date = Column(DATE, primary_key=True) # 数据发布日期 
    end_date = Column(DATE) # 净值日期 
    nav = Column(DECIMAL(19,4)) # 单位净值 
    accum_nav = Column(DECIMAL(19,4)) # 累计净值 
    update_time = Column(DATETIME) # 更新时间 
    adj_nav = Column(DECIMAL(19,4)) # 调整净值 
    nav_unit = Column(DECIMAL(19,4)) # 净值单位 
    return_rate = Column(DECIMAL(19,10)) # 净值收益 
    adj_return_rate = Column(DECIMAL(19,4)) # 调整净值收益 
    
class PfundInfo(Base):
    '''私募基本信息'''
        
    __tablename__ = 'pfund_info'
    
    security_id = Column(BIGINT, primary_key=True) # 证券内部编码 
    establish_date = Column(DATE) # 成立日期 
    pf_style = Column(CHAR(10)) # 产品类型 
    status = Column(CHAR(200)) # 运行状态 
    invest_strategy = Column(CHAR(10)) # 投资策略 
    invest_strategy_child = Column(CHAR(200)) # 子策略 
    duration = Column(Integer) # 存续期限 
    open_date_desc = Column(CHAR(500)) # 开放日 
    invest_consultant = Column(CHAR(50)) # 投资顾问 
    custodian = Column(CHAR(50)) # 托管人 
    issue_platform = Column(CHAR(100)) # 受托人 
    trading_broker = Column(CHAR(50)) # 交易经纪 
    subscription_start_point = Column(Integer) # 认购起点 
    scale_initial = Column(BIGINT) # 初始规模 
    issue_fee = Column(DECIMAL(19,10)) # 认购费率 
    redeem_fee = Column(DECIMAL(19,10)) # 赎回费率 
    management_fee = Column(DECIMAL(19,10)) # 管理费率 
    performanece_return = Column(DECIMAL(19,10)) # 业绩报酬 
    record_cd = Column(CHAR(50)) # 备案编码 
    update_time = Column(DATETIME) # 更新时间 
    record_date = Column(DATE) # 备案日期 
    end_date = Column(DATE) # 到期日 
    nav_freq = Column(CHAR(20)) # 净值发布频率 
    closing_dura_desc = Column(CHAR(200)) # 封闭期 
    issue_loc = Column(CHAR(200)) # 发行地 
    record_status = Column(CHAR(20)) # 备案状态 
    manage_type = Column(TINYINT(3)) # 管理类型 
    manager = Column(CHAR(500)) # 基金经理 
    min_add = Column(CHAR(200)) # 最低追加金额 
    stop_loss_line = Column(DECIMAL(19,4)) # 止损线 
    warn_line = Column(DECIMAL(19,4)) #  预警线
    futures_broker = Column(CHAR(50)) #  期货经纪
    amac_type = Column(CHAR(200)) #  协会公布类型
    apply_fee = Column(DECIMAL(19,4)) # 申购费
    custody_fee = Column(DECIMAL(19,4)) #  托管费
    is_quant = Column(TINYINT(3)) # 是否量化
    is_hedging = Column(TINYINT(3)) #  是否对冲

    
class PfundInstInfo(Base):
    '''投顾机构信息'''
        
    __tablename__ = 'pfund_inst_info'                        

    party_id = Column(BIGINT(20), primary_key=True) # 机构内部编码
    profile = Column(TEXT) # 公司简介
    idea_strategy= Column(TEXT) # 投资理念
    key_person= Column(TEXT) # 核心人物
    update_time= Column(DATETIME) # 更新时间
    record_date= Column(DATE) # 登记日期
    reg_cd= Column(CHAR(20)) # 登记编码
    legal_rep= Column(CHAR(100)) # 法定代表人/执行事务合伙人(委派代表)
    is_qualified= Column(TINYINT(3)) # 法人是否有从业资格
    qualify_way= Column(CHAR(20)) # 法人从业资格认定方式
    emp_num= Column(Integer) # 员工数量
    main_fund_type= Column(CHAR(100)) # 管理基金主要类别
    private_ind_scale= Column(CHAR(20)) # 私募证券基金自主发行规模
    private_con_scale= Column(CHAR(20)) # 私募证券基金顾问管理规模
    pe_scale= Column(CHAR(20)) # 私募股权基金规模
    vc_scale= Column(CHAR(20)) # 创业投资基金规模
    other_scale= Column(CHAR(20)) # 其他私募基金规模
    is_fund_mana= Column(BIGINT) # 是否公募基金管理人
    paa_scale= Column(CHAR(20)) # 私募资产配置基金规模
    record_status= Column(CHAR(20)) # 备案状态
    management_scale= Column(CHAR(100)) # 管理规模区间

class MdInstitution(Base):
    '''公司基本信息'''
        
    __tablename__ = 'md_institution'
    
    party_id = Column(Integer, primary_key=True) # 机构内部ID
    party_full_name = Column(CHAR(100)) # 机构全称 
    party_short_name = Column(CHAR(100)) # 机构简称 
    party_full_name_en = Column(CHAR(200)) # 机构英文全称 
    party_short_name_en = Column(CHAR(200)) # 机构英文简称 
    reg_date = Column(DATE) # 注册日期 
    reg_country_cd = Column(CHAR(3)) # 注册国家代码 
    reg_province = Column(CHAR(100)) # 注册省份 
    reg_city = Column(CHAR(100)) # 注册城市 
    reg_addr = Column(CHAR(200)) # 注册地址 
    reg_cap = Column(DECIMAL(18,4)) # 注册资金 
    reg_cap_curr_cd = Column(CHAR(3)) # 注册资金货币代码 
    office_addr = Column(CHAR(200)) # 办公地址 
    email = Column(CHAR(100)) # 联系邮箱 
    website = Column(CHAR(100)) # 机构网站 
    tel = Column(CHAR(50)) # 联系电话 
    fax = Column(CHAR(50)) # 联系传真 
    legal_entity_id = Column(CHAR(20)) # 工商登记号 
    prime_operating = Column(MEDIUMTEXT) # 主营业务 
    party_nature_cd = Column(CHAR(100)) # 公司性质 
    is_iss_bond = Column(CHAR(100)) # 是否发行债券 
    close_date = Column(DATE) # 机构终止日期 
    inst_status = Column(SMALLINT) # 是否运作 
    dy_use_flg = Column(BIGINT) # DY使用标识 
    update_time = Column(DATETIME) # 更新时间 
    profile = Column(TEXT) # 机构介绍 
    board_secry = Column(CHAR(50)) # 董事会秘书 
    legal_rep = Column(CHAR(50)) # 法定代表人 
    opa_scope = Column(MEDIUMTEXT) # 经营范围 
    gen_mana = Column(CHAR(50)) # 总经理 
    is_iss_mf = Column(Integer) # 是否发行公募基金 

class MdSecurity(Base):
    '''主编码及基本信息'''
        
    __tablename__ = 'md_security'
    
    security_id = Column(Integer, primary_key=True) # 证券内部ID
    ticker_symbol = Column(CHAR(50)) # 交易代码 
    exchange_cd = Column(CHAR(4)) # 交易市场代码 
    sec_full_name = Column(CHAR(100)) # 证券全称 
    sec_short_name = Column(CHAR(100)) # 证券简称 
    cn_spell = Column(CHAR(200)) # 简称拼音 
    sec_full_name_en = Column(CHAR(200)) # 证券英文全称 
    sec_short_name_en = Column(CHAR(200)) # 证券英文简称 
    dyid = Column(CHAR(50)) # 证券展示代码 
    ex_country_cd = Column(CHAR(3)) # 交易市场所属地区 
    trans_curr_cd = Column(CHAR(3)) # 交易货币代码 
    asset_class = Column(CHAR(4)) # 证券类型 
    list_status_cd = Column(CHAR(4)) # 上市状态 
    list_date = Column(DATE) # 上市日期 
    delist_date = Column(DATE) # 摘牌日期 
    party_id = Column(BIGINT) # 机构内部ID 
    dy_use_flg = Column(BIGINT) # DY使用标识 
    update_time = Column(DATETIME) # 更新时间 

