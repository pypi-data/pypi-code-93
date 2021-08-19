from sqlalchemy import CHAR, Column, Integer, TEXT, BOOLEAN, text, Index, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import DOUBLE, DATE, TINYINT, DATETIME, MEDIUMTEXT, YEAR, SMALLINT, BIGINT, DECIMAL, VARCHAR

from ...constant import SectorType, IndexPriceSource, CodeFeeMode, IndClassType


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

# test库主要是测试库，使用没问题后，转正

class PfIndexInfo(Base):
    '''私募指数信息'''

    __tablename__ = 'pf_index_info'

    index_id = Column(CHAR(20), primary_key=True) # 指数id
    desc_name = Column(CHAR(40)) # 指数中文
    start_date = Column(DATE) # 指数开始日期
    desc = Column(CHAR(255)) # 指数说明

class PfIndexComponent(Base):
    '''私募指数权重表'''

    __tablename__ = 'pf_index_component'

    index_id = Column(CHAR(20), primary_key=True) # 指数id
    datetime = Column(DATE, primary_key=True) # 开始日期
    desc_name = Column(CHAR(128), primary_key=True) # 私募基金名
    wgt = Column(DOUBLE(asdecimal=False)) # 权重

class PfIndexPrice(Base):
    '''私募指数净值表'''

    __tablename__ = 'pf_index_price'

    index_id = Column(CHAR(20), primary_key=True) # 指数id
    datetime = Column(DATE, primary_key=True) # 开始日期
    close = Column(DOUBLE(asdecimal=False)) # 收盘价
    ret = Column(DOUBLE(asdecimal=False)) # 收益率