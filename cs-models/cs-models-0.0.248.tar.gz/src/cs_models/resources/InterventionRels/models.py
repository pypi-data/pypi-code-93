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


class InterventionRelsModel(Base):
    __tablename__ = "intervention_rels"

    id = Column(Integer, primary_key=True)
    nct_id = Column(String(128), nullable=False, index=True)
    intervention_id_1 = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=False,
    )
    intervention_id_2 = Column(
        Integer,
        ForeignKey('interventions.id'),
        nullable=False,
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        # https://stackoverflow.com/questions/58776476/why-doesnt-freezegun-work-with-sqlalchemy-default-values
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
    )

    __table_args__ = (UniqueConstraint("nct_id", "intervention_id_1", "intervention_id_2"),)
