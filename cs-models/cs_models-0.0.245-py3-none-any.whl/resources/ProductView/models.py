from sqlalchemy import (
    Column,
    Integer,
    Text,
    String,
    DateTime,
    ForeignKey,
    Boolean,
)
from datetime import datetime

from ...database import Base


class ProductViewModel(Base):
    __tablename__ = 'product_view'

    id = Column(Integer, primary_key=True)
    intervention_name = Column(String(128), nullable=False, index=True)
    intervention_type = Column(String(50), nullable=True)
    synonyms = Column(Text, nullable=True)
    condition_id = Column(
        Integer,
        ForeignKey('conditions.id'),
        nullable=True,
    )
    disease_name = Column(String(128), nullable=True)
    approved_condition = Column(Boolean, nullable=True)
    pharm_actions = Column(Text, nullable=True)
    company_sec_id = Column(
        Integer,
        ForeignKey('companies_sec.id'),
        nullable=True,
    )
    company_ous_id = Column(
        Integer,
        ForeignKey('companies_ous.id'),
        nullable=True,
    )
    isonmarket = Column(Boolean, nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
