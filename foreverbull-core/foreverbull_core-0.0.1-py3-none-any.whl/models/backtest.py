from foreverbull_core.models.socket import SocketConfig
from typing import List
from foreverbull_core.models.base import Base


class Session(Base):
    id: str


class BacktestSockets(Base):
    main: SocketConfig
    feed: SocketConfig
    broker: SocketConfig
    running: bool


class BacktestConfig(Base):
    start_date: str
    end_date: str
    timezone: str = "utc"
    benchmark: str
    assets: List[str]
