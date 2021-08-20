from sqlalchemy import (
    Column,
    String,
)

from ...database import Base


class SetIDICDCrossModel(Base):
    __tablename__ = "set_id_icd"

    set_id = Column(String(4000), nullable=False, primary_key=True)
    icd_code = Column(String(128), nullable=False, primary_key=True)
