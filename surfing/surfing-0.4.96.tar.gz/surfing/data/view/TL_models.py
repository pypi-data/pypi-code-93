from sqlalchemy import CHAR, Column, Integer, TEXT, BOOLEAN, text, Index, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import DOUBLE, DATE, TINYINT, DATETIME, MEDIUMTEXT, YEAR, SMALLINT, BIGINT, DECIMAL, VARCHAR, TIMESTAMP

from ...constant import SectorType, IndexPriceSource, CodeFeeMode, IndClassType

class Base:
    pass
    #_update_time = Column('_update_time', DATETIME, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))  # 更新时间
# make this column at the end of every derived table
#Base._update_time._creation_order = 9999
Base = declarative_base(cls=Base)


class PfundInstScaleAmac(Base):
    '''私募基金管理人规模'''

    __tablename__ = 'pfund_inst_scale_amac'
    
    ID = Column(BIGINT, primary_key=True) # 信息编码
    PARTY_ID = Column(BIGINT) # 机构内部编码
    PARTY_FULL_NAME = Column(CHAR(300)) # 机构名称 
    MAIN_FUND_TYPE = Column(CHAR(200)) # 管理基金主要类别 
    SCALE = Column(CHAR(50)) # 管理规模 
    INST_ID = Column(CHAR(60)) # 源数据id 
    NUM = Column(Integer) # 变更次数 
    IS_NEW = Column(Integer) # 是否最新
    FETCH_DATE = Column(DATE) # 变动时间 
    UPDATE_TIME = Column(DATETIME) # 更新时间 
    TMSTAMP = Column(BIGINT) # 后台系统修改数据时间戳
    HERMESFIRSTTIME = Column(TIMESTAMP) # 记录数据首次写入时间
    HERMESUPTIME = Column(TIMESTAMP) # 记录数据更新时间
    

class PfundManagerInfo(Base):
    '''私募基金经理基本信息表'''

    __tablename__ = 'pfund_manager_info'
    
    ID = Column(BIGINT, primary_key=True) # 信息编码
    PERSON_ID = Column(CHAR(60)) # 人员ID
    NAME = Column(CHAR(60)) # 姓名 
    GENDER = Column(CHAR(60)) # 性别 
    BIRTHDAY = Column(CHAR(60)) # 生日 
    NATIONALITY_CD = Column(CHAR(60)) # 国籍 
    CERTIFICATE = Column(CHAR(300)) # 证书 
    PHOTO = Column(CHAR(200)) # 照片
    EDUCATION = Column(Integer) # 最高学历 
    GRAD_UNIV = Column(CHAR(60)) # 毕业院校 
    MAJOR = Column(CHAR(60)) # 所学专业
    BACKGROUND_DESC = Column(TEXT) # 简介
    BACKGROUND = Column(CHAR(60)) # 背景
    MF_TO_PF = Column(TINYINT) # 是否公转私/私转公
    YEAR = Column(DECIMAL(4,2)) # 投资年限
    AWARDS_NAME = Column(CHAR(2000)) # 所获荣誉
    DEPARTMENT = Column(CHAR(60)) # 所在部门
    POSITION = Column(CHAR(500)) # 职务
    IS_QUAL = Column(Integer) # 是否具备基金从业资格
    NUM_DURA = Column(BIGINT) # 当前管理的基金数量
    DURA_SEC_ID = Column(MEDIUMTEXT) # 当前管理的基金ID
    DURA_SEC_NAME = Column(MEDIUMTEXT) # 当前管理的基金
    PARTY_ID = Column(BIGINT) # 任职机构ID
    PARTY_FULL_NAME = Column(CHAR(300)) # 任职机构
    REP_SEC_ID = Column(BIGINT) # 代表产品ID
    REP_SEC_NAME = Column(CHAR(300)) # 代表产品
    RETURN_MAN_A = Column(DECIMAL(18,10)) # 任职收益
    REMARK = Column(CHAR(300)) # 备注
    UPDATE_TIME = Column(DATETIME) # 更新时间
    TMSTAMP = Column(BIGINT) # 后台系统修改数据时间戳
    HERMESFIRSTTIME = Column(TIMESTAMP) # 记录数据首次写入时间
    HERMESUPTIME = Column(TIMESTAMP) # 记录数据更新时间
    
    
class PfundNav(Base):
    '''私募净值'''

    __tablename__ = 'pfund_nav'
    
    ID = Column(BIGINT, primary_key=True) # 自增ID
    SECURITY_ID = Column(BIGINT) # 证券内部编码
    PUBLISH_DATE = Column(DATE) # 数据发布日期 
    END_DATE = Column(DATE) # 净值日期 
    NAV = Column(DECIMAL(19,4)) # 单位净值 
    ACCUM_NAV = Column(DECIMAL(19,4)) # 累计净值 
    UPDATE_TIME = Column(DATETIME) # 更新时间 
    TMSTAMP = Column(BIGINT) # 后台系统修改数据时间戳
    ADJ_NAV = Column(DECIMAL(19,4)) # 调整净值 
    NAV_UNIT = Column(DECIMAL(19,4)) # 净值单位 
    RETURN_RATE = Column(DECIMAL(19,10)) # 净值收益 
    ADJ_RETURN_RATE = Column(DECIMAL(19,4)) # 调整净值收益 
    HERMESFIRSTTIME = Column(TIMESTAMP) # 记录数据首次写入时间
    HERMESUPTIME = Column(TIMESTAMP) # 记录数据更新时间


class SysCode(Base):
    '''参数集合'''

    __tablename__ = 'sys_code'
    
    ID = Column(BIGINT, primary_key=True) # 自增ID
    CODE_TYPE_ID = Column(Integer) # 参数ID
    CODE_TYPE_NAME = Column(CHAR(100)) # 参数名称 
    CODE_TYPE_NAME_EN = Column(CHAR(100)) # 参数英文名称 
    VALUE_NO = Column(SMALLINT) # 参数值序列 
    VALUE_EN_CD = Column(CHAR(50)) # 参数值字母编码 
    VALUE_NUM_CD = Column(CHAR(20)) # 参数值数字编码 
    VALUE_NAME_CN = Column(CHAR(100)) # 参数值中文名称 
    VALUE_NAME_EN = Column(CHAR(100)) # 参数值英文缩写 
    REMARK = Column(CHAR(500)) # 备注 
    TMSTAMP = Column(BIGINT) #  后台系统修改数据时间戳
    UPDATE_TIME = Column(DATETIME) # 更新时间
    HERMESFIRSTTIME = Column(TIMESTAMP) # 记录数据首次写入时间
    HERMESUPTIME = Column(TIMESTAMP) # 记录数据更新时间

class MdInstitution(Base):
    '''公司基本信息'''
        
    __tablename__ = 'md_institution'
    
    PARTY_ID = Column(Integer, primary_key=True) # 机构内部ID
    PARTY_FULL_NAME = Column(CHAR(100)) # 机构全称 
    PARTY_SHORT_NAME = Column(CHAR(100)) # 机构简称 
    PARTY_FULL_NAME_EN = Column(CHAR(200)) # 机构英文全称 
    PARTY_SHORT_NAME_EN = Column(CHAR(200)) # 机构英文简称 
    REG_DATE = Column(DATE) # 注册日期 
    REG_COUNTRY_CD = Column(CHAR(3)) # 注册国家代码 
    REG_PROVINCE = Column(CHAR(100)) # 注册省份 
    REG_CITY = Column(CHAR(100)) # 注册城市 
    REG_ADDR = Column(CHAR(200)) # 注册地址 
    REG_CAP = Column(DECIMAL(18,4)) # 注册资金 
    REG_CAP_CURR_CD = Column(CHAR(3)) # 注册资金货币代码 
    OFFICE_ADDR = Column(CHAR(200)) # 办公地址 
    EMAIL = Column(CHAR(100)) # 联系邮箱 
    WEBSITE = Column(CHAR(100)) # 机构网站 
    TEL = Column(CHAR(50)) # 联系电话 
    FAX = Column(CHAR(50)) # 联系传真 
    LEGAL_ENTITY_ID = Column(CHAR(20)) # 工商登记号 
    PRIME_OPERATING = Column(MEDIUMTEXT) # 主营业务 
    PARTY_NATURE_CD = Column(CHAR(100)) # 公司性质 
    IS_ISS_BOND = Column(CHAR(100)) # 是否发行债券 
    CLOSE_DATE = Column(DATE) # 机构终止日期 
    INST_STATUS = Column(SMALLINT) # 是否运作 
    DY_USE_FLG = Column(BIGINT) # DY使用标识 
    UPDATE_TIME = Column(DATETIME) # 更新时间 
    TMSTAMP = Column(BIGINT) #  后台系统修改数据时间戳
    PROFILE = Column(TEXT) # 机构介绍 
    BOARD_SECRY = Column(CHAR(50)) # 董事会秘书 
    LEGAL_REP = Column(CHAR(50)) # 法定代表人 
    OPA_SCOPE = Column(MEDIUMTEXT) # 经营范围 
    GEN_MANA = Column(CHAR(50)) # 总经理 
    IS_ISS_MF = Column(Integer) # 是否发行公募基金 
    HERMESFIRSTTIME = Column(TIMESTAMP) #  记录数据首次写入时间
    HERMESUPTIME = Column(TIMESTAMP) #  记录数据更新时间
    

class MdSecurity(Base):
    '''主编码及基本信息'''
        
    __tablename__ = 'md_security'
    
    SECURITY_ID = Column(Integer, primary_key=True) # 证券内部ID
    TICKER_SYMBOL = Column(CHAR(50)) # 交易代码 
    EXCHANGE_CD = Column(CHAR(4)) # 交易市场代码 
    SEC_FULL_NAME = Column(CHAR(100)) # 证券全称 
    SEC_SHORT_NAME = Column(CHAR(100)) # 证券简称 
    CN_SPELL = Column(CHAR(200)) # 简称拼音 
    SEC_FULL_NAME_EN = Column(CHAR(200)) # 证券英文全称 
    SEC_SHORT_NAME_EN = Column(CHAR(200)) # 证券英文简称 
    DYID = Column(CHAR(50)) # 证券展示代码 
    EX_COUNTRY_CD = Column(CHAR(3)) # 交易市场所属地区 
    TRANS_CURR_CD = Column(CHAR(3)) # 交易货币代码 
    ASSET_CLASS = Column(CHAR(4)) # 证券类型 
    LIST_STATUS_CD = Column(CHAR(4)) # 上市状态 
    LIST_DATE = Column(DATE) # 上市日期 
    DELIST_DATE = Column(DATE) # 摘牌日期 
    PARTY_ID = Column(BIGINT) # 机构内部ID 
    DY_USE_FLG = Column(BIGINT) # DY使用标识 
    UPDATE_TIME = Column(DATETIME) # 更新时间 
    TMSTAMP = Column(BIGINT) #  后台系统修改数据时间戳
    HERMESFIRSTTIME = Column(TIMESTAMP) #  记录数据首次写入时间
    HERMESUPTIME = Column(TIMESTAMP) #  记录数据更新时间
     
                  
class Pfund(Base):
    '''私募基本信息'''
        
    __tablename__ = 'pfund'
    
    ID = Column(BIGINT, primary_key=True) # 自增ID

    SECURITY_ID = Column(BIGINT) # 证券内部编码 
    ESTABLISH_DATE = Column(DATE) # 成立日期 
    PF_STYLE = Column(CHAR(10)) # 产品类型 
    STATUS = Column(CHAR(200)) # 运行状态 
    INVEST_STRATEGY = Column(CHAR(10)) # 投资策略 
    INVEST_STRATEGY_CHILD = Column(CHAR(200)) # 子策略 
    DURATION = Column(Integer) # 存续期限 
    OPEN_DATE_DESC = Column(CHAR(500)) # 开放日 
    INVEST_CONSULTANT = Column(CHAR(50)) # 投资顾问 
    CUSTODIAN = Column(CHAR(50)) # 托管人 
    ISSUE_PLATFORM = Column(CHAR(100)) # 受托人 
    TRADING_BROKER = Column(CHAR(50)) # 交易经纪 
    SUBSCRIPTION_START_POINT = Column(Integer) # 认购起点 
    SCALE_INITIAL = Column(BIGINT) # 初始规模 
    ISSUE_FEE = Column(DECIMAL(19,10)) # 认购费率 
    REDEEM_FEE = Column(DECIMAL(19,10)) # 赎回费率 
    MANAGEMENT_FEE = Column(DECIMAL(19,10)) # 管理费率 
    PERFORMANECE_RETURN = Column(DECIMAL(19,10)) # 业绩报酬 
    RECORD_CD = Column(CHAR(50)) # 备案编码 
    UPDATE_TIME = Column(DATETIME) # 更新时间 
    TMSTAMP = Column(BIGINT) #  后台系统修改数据时间戳
    RECORD_DATE = Column(DATE) # 备案日期 
    END_DATE = Column(DATE) # 到期日 
    NAV_FREQ = Column(CHAR(20)) # 净值发布频率 
    CLOSING_DURA_DESC = Column(CHAR(200)) # 封闭期 
    ISSUE_LOC = Column(CHAR(200)) # 发行地 
    RECORD_STATUS = Column(CHAR(20)) # 备案状态 
    MANAGE_TYPE = Column(TINYINT(3)) # 管理类型 
    MANAGER = Column(CHAR(500)) # 基金经理 
    MIN_ADD = Column(CHAR(200)) # 最低追加金额 
    STOP_LOSS_LINE = Column(DECIMAL(19,4)) # 止损线 
    WARN_LINE = Column(DECIMAL(19,4)) #  预警线
    FUTURES_BROKER = Column(CHAR(50)) #  期货经纪
    AMAC_TYPE = Column(CHAR(200)) #  协会公布类型
    APPLY_FEE = Column(DECIMAL(19,4)) # 申购费
    CUSTODY_FEE = Column(DECIMAL(19,4)) #  托管费
    IS_QUANT = Column(TINYINT(3)) # 是否量化
    IS_HEDGING = Column(TINYINT(3)) #  是否对冲
    HERMESFIRSTTIME = Column(TIMESTAMP) # 记录数据首次写入时间
    HERMESUPTIME = Column(TIMESTAMP) # 记录数据更新时间
    

class PfundInstInfo(Base):
    '''投顾机构信息'''
        
    __tablename__ = 'pfund_inst_info'                        

    ID = Column(BIGINT, primary_key=True) # 信息编码

    PARTY_ID = Column(BIGINT(20)) # 机构内部编码
    PROFILE = Column(TEXT) # 公司简介
    IDEA_STRATEGY= Column(TEXT) # 投资理念
    KEY_PERSON= Column(TEXT) # 核心人物
    UPDATE_TIME= Column(DATETIME) # 更新时间
    TMSTAMP= Column(BIGINT(20)) # 后台系统修改数据时间戳
    RECORD_DATE= Column(DATE) # 登记日期
    REG_CD= Column(CHAR(20)) # 登记编码
    LEGAL_REP= Column(CHAR(100)) # 法定代表人/执行事务合伙人(委派代表)
    IS_QUALIFIED= Column(TINYINT(3)) # 法人是否有从业资格
    QUALIFY_WAY= Column(CHAR(20)) # 法人从业资格认定方式
    EMP_NUM= Column(Integer) # 员工数量
    MAIN_FUND_TYPE= Column(CHAR(100)) # 管理基金主要类别
    PRIVATE_IND_SCALE= Column(CHAR(20)) # 私募证券基金自主发行规模
    PRIVATE_CON_SCALE= Column(CHAR(20)) # 私募证券基金顾问管理规模
    PE_SCALE= Column(CHAR(20)) # 私募股权基金规模
    VC_SCALE= Column(CHAR(20)) # 创业投资基金规模
    OTHER_SCALE= Column(CHAR(20)) # 其他私募基金规模
    IS_FUND_MANA= Column(BIGINT) # 是否公募基金管理人
    PAA_SCALE= Column(CHAR(20)) # 私募资产配置基金规模
    RECORD_STATUS= Column(CHAR(20)) # 备案状态
    MANAGEMENT_SCALE= Column(CHAR(100)) # 管理规模区间
    HERMESFIRSTTIME= Column(TIMESTAMP) # 记录数据首次写入时间
    HERMESUPTIME= Column(TIMESTAMP) # 记录数据更新时间
