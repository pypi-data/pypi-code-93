from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
)

from ...database import Base


class DrugClassModel(Base):
    __tablename__ = "drug_class"

    id = Column(Integer, primary_key=True)
    disease_id = Column(String(128), nullable=False)
    disease_name = Column(String(256), nullable=False)
    moa = Column(String(256), nullable=True)
    moa_id = Column(String(128), nullable=False)
    epc = Column(String(256), nullable=True)
    epc_id = Column(String(128), nullable=False)
    struct = Column(String(256), nullable=True)
    struct_id = Column(String(128), nullable=True)
    pe = Column(String(256), nullable=True)
    pe_id = Column(String(128), nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("disease_id", "moa_id", "epc_id"),)
