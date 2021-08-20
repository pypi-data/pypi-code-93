from sqlalchemy import (
    Column,
    String,
)

from ...database import Base


class NCTIdICDCrossModel(Base):
    __tablename__ = "nct_id_icd"

    nct_id = Column(String(128), nullable=False, primary_key=True)
    icd_code = Column(String(128), nullable=False, primary_key=True)
