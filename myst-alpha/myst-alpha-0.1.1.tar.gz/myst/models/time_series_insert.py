from myst.models.base_model import BaseModel
from myst.models.time_dataset import TimeDataset


class TimeSeriesInsert(BaseModel):
    """Schema for time series insert requests."""

    time_dataset: TimeDataset
