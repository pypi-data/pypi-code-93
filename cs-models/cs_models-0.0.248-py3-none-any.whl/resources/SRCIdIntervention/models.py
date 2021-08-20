from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    UniqueConstraint,
    ForeignKey,
    Boolean,
)

from ...database import Base


class SRCIdInterventionModel(Base):
    __tablename__ = "src_interventions"

    id = Column(Integer, primary_key=True)
    src_id = Column(String(128), nullable=False, index=True)
    src_type = Column(String(50), nullable=False, index=True)
    intervention_id = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=False,
    )
    narrow = Column(Boolean, nullable=False)
    group = Column(Integer, nullable=False)
    is_deleted = Column(Boolean, nullable=True)
    score = Column(Integer, nullable=True)
    final_mapping = Column(Boolean, nullable=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("src_id", "intervention_id"),)
