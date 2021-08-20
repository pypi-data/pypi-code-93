from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
)

from ...database import Base


class ConceptNormModel(Base):
    __tablename__ = "concept_norm"

    id = Column(Integer, primary_key=True)
    cui = Column(String(50), nullable=False, index=True)
    norm_cui = Column(String(50), nullable=False, index=True)
    norm_cui_name = Column(String(191), nullable=False)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("cui", "norm_cui"),)
