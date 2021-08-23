from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
    ForeignKey,
)

from ...database import Base


class NDCDrugClassModel(Base):
    __tablename__ = "ndc_drug_class"

    id = Column(Integer, primary_key=True)
    product_ndc = Column(String(128), nullable=False, index=True)
    name = Column(String(128), nullable=True)
    rxcui = Column(String(128), nullable=False)
    drug_class = Column(
        Integer,
        ForeignKey('drug_class.id'),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("product_ndc", "rxcui", "drug_class"),)
