import math

from pandas import DataFrame

from cognite.well_model.models import TrajectoryData


class TrajectoryRows:
    """
    Custom data class for displaying trajectory data as data frames.
    """

    def __init__(self, data: TrajectoryData):
        self.sequence_external_id = data.source.sequence_external_id
        self.wellbore_asset_external_id = data.wellbore_asset_external_id
        self.source = data.source
        self.inclination_unit = data.inclination_unit
        self.azimuth_unit = data.azimuth_unit
        self.type = data.type
        self.measured_depth_unit = data.measured_depth_unit

        self.rows = data.rows

    def to_pandas(self) -> DataFrame:
        column_names = [
            "measured_depth",
            "true_vertical_depth",
            "northing",
            "easting",
            "azimuth",
            "inclination",
            "dogleg_severity",
        ]
        row_values = []
        for r in self.rows:
            row = [
                r.measured_depth,
                r.true_vertical_depth,
                r.northing,
                r.easting,
                r.azimuth,
                r.inclination,
                r.dogleg_severity,
            ]
            row_values.append(row)
        values = [[x if x is not None else math.nan for x in r] for r in row_values]
        return DataFrame(
            values,
            columns=column_names,
        )
