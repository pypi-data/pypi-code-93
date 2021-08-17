from typing import Optional
from uuid import UUID

from typing_extensions import Literal

from myst import get_client
from myst.core.data.time_array import TimeArray
from myst.core.time.time import Time
from myst.core.time.time_delta import TimeDelta
from myst.models.base_model import BaseModel
from myst.models.deploy_status import DeployStatus
from myst.models.time_dataset import TimeDataset, TimeDatasetRow
from myst.models.time_series_insert import TimeSeriesInsert
from myst.models.time_series_insert_result import TimeSeriesInsertResult
from myst.models.time_series_query_result import TimeSeriesQueryResult
from myst.models.types import AxisLabels, CoordinateLabels, Shape, UUIDOrStr


class TimeSeries(BaseModel):
    """The core time series API resource.

    A `TimeSeries` is a queryable, shareable node containing fixed-frequency, arbitrarily dimensioned time series data.
    It combines data from multiple layers into a single stream.

    In addition to queries, a time series also supports inserts, which take precedence over data flowing through the
    input layers.
    """

    object: Literal["Node"] = "Node"
    uuid: UUID
    create_time: Time
    update_time: Optional[Time]
    organization: UUID
    owner: UUID
    type: Literal["TimeSeries"] = "TimeSeries"
    title: str
    description: Optional[str]
    project: UUID
    creator: UUID
    deploy_status: DeployStatus
    sample_period: TimeDelta
    cell_shape: Shape
    coordinate_labels: CoordinateLabels
    axis_labels: AxisLabels

    @classmethod
    def get(cls, uuid: UUIDOrStr) -> "TimeSeries":
        """Returns the time series identified by the given UUID."""
        return get_client().request(method="GET", path=f"/time_series/{uuid}", response_class=TimeSeries)

    def insert_time_array(self, time_array: TimeArray) -> None:
        """Inserts data from a `TimeArray` into this time series.

        Args:
            time_array: the array of data to be inserted
        """
        time_dataset_row = TimeDatasetRow(
            start_time=time_array.start_time,
            end_time=time_array.end_time,
            as_of_time=time_array.as_of_time,
            values=time_array.values,
            mask=time_array.mask,
        )

        time_dataset = TimeDataset(
            cell_shape=time_array.cell_shape,
            sample_period=time_array.sample_period,
            data=[time_dataset_row],
            coordinate_labels=time_array.coordinate_labels,
            axis_labels=time_array.axis_labels,
        )

        get_client().request(
            method="POST",
            path=f"/time_series/{self.uuid}:insert",
            request_model=TimeSeriesInsert(time_dataset=time_dataset),
            response_class=TimeSeriesInsertResult,
        )

    def query_time_array(self, start_time: Time, end_time: Time, as_of_time: Time) -> TimeArray:
        """Queries this time series for data according to the given parameters.

        Args:
            start_time: the beginning of the natural time range to query over, inclusive
            end_time: the end of the natural time range to query over, exclusive
            as_of_time: the precise as of time to query

        Returns:
            a time array containing data for the specified time range and as of time
        """
        query_result = get_client().request(
            method="GET",
            path=f"/time_series/{self.uuid}:query",
            params=dict(
                start_time=start_time.to_iso_string(),
                end_time=end_time.to_iso_string(),
                as_of_time=as_of_time.to_iso_string(),
            ),
            response_class=TimeSeriesQueryResult,
        )

        time_arrays = query_result.time_dataset.to_time_arrays()

        # Without offering the user the ability to control flattening behavior, we just throw up our hands instead.
        if len(time_arrays) != 1:
            raise NotImplementedError()

        return time_arrays[0]
