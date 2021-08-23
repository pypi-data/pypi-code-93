from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
)

from ...database import Base


class PharmacologicModel(Base):
    __tablename__ = "pharmacologic"

    id = Column(Integer, primary_key=True)
    pharma_set_id = Column(String(128), nullable=False, index=True)
    unii_code = Column(String(128), nullable=True)
    unii_name = Column(String(128), nullable=True)
    nui = Column(String(128), nullable=True, index=True)
    code_system = Column(String(128), nullable=True)
    class_name = Column(String(128), nullable=True, index=True)
    class_type = Column(String(128), nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
