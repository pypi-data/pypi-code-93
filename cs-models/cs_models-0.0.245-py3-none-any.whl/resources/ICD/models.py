from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    Boolean
)

from ...database import Base


class ICDModel(Base):
    __tablename__ = "icd"

    id = Column(Integer, primary_key=True)
    icd_code = Column(String(128), nullable=False, index=True)
    description = Column(Text, nullable=True)
    class_kind = Column(String(50), nullable=True)
    is_leaf = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )
