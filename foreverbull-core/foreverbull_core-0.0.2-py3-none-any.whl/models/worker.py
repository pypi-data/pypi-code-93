from typing import List, Optional

from foreverbull_core.models.base import Base


class Database(Base):
    user: str
    password: str
    hostname: str
    port: int
    db_name: str
    dialect: str


class Parameter(Base):
    key: str
    value: int
    default: int


class WorkerConfig(Base):
    session_id: str
    database: Optional[Database]
    parameters: Optional[List[Parameter]]
