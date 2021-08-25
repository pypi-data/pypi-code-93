from dataclasses import dataclass
from datetime import datetime

from ctlml_commons.entity.execution_type import ExecutionType


@dataclass
class History:
    id: str
    execution_type: ExecutionType
    symbol: str
    shares: float
    purchase_price: float
    sell_price: float
    profit_loss: float
    notes: str
    time: datetime
