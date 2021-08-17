from typing import Optional
from uuid import UUID

from typing_extensions import Literal

from myst.core.time.time import Time
from myst.models.base_model import BaseModel
from myst.models.time_dataset import TimeDataset


class TimeSeriesQueryResult(BaseModel):
    """Time series query result schema."""

    object: Literal["Result"] = "Result"
    uuid: UUID
    create_time: Time
    type: Literal["TimeSeriesQueryResult"] = "TimeSeriesQueryResult"
    node: UUID
    time_dataset: TimeDataset
    update_time: Optional[Time] = None
