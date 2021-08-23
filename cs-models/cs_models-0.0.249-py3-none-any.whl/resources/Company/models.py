from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
)
from datetime import datetime

from ...database import Base


class CompanyModel(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)

    applicant_full_name = Column(String(190), unique=True, nullable=False)
    exchange = Column(String(100))
    parent_company = Column(String(255))
    ticker = Column(String(20))
    company_sec_id = Column(
        Integer,
        ForeignKey('companies_sec.id'),
        nullable=True,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
