from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Boolean,
)

from ...database import Base


class NCTMetamapModel(Base):
    __tablename__ = "nct_metamap"

    id = Column(Integer, primary_key=True)
    nct_id = Column(String(128), nullable=False, index=True)
    cui = Column(String(50), nullable=False)
    preferred_name = Column(String(256), nullable=False)
    type = Column(String(128), nullable=False)
    score = Column(Integer, nullable=True)
    note = Column(Text, nullable=True)
    final_mapping = Column(Boolean, nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
