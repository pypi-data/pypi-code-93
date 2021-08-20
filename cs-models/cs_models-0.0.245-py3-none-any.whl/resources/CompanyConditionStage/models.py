from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
    Text,
)

from ...database import Base


class CompanyConditionStageModel(Base):
    __tablename__ = "company_condition_stage"

    id = Column(Integer, primary_key=True)
    src_condition_id = Column(String(128), nullable=False, index=True)
    stage = Column(Text)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("src_condition_id"),)
