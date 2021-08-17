from typing import Optional
from uuid import UUID

from typing_extensions import Literal

from myst.core.time.time import Time
from myst.models.base_model import BaseModel


class TimeSeriesInsertResult(BaseModel):
    """Time series insert result schema."""

    object: Literal["Result"] = "Result"
    uuid: UUID
    create_time: Time
    type: Literal["TimeSeriesInsertResult"] = "TimeSeriesInsertResult"
    node: UUID
    update_time: Optional[Time] = None
