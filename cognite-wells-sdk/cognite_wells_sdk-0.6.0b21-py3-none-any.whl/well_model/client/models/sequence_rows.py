import math
from typing import Any, Dict, List, Optional

from pandas import DataFrame

from cognite.well_model.client.utils._auxiliary import to_camel_case
from cognite.well_model.models import BasicGetSequenceColumnInfo, SequenceGetData, SequenceRowDTO


class SequenceRows:
    """
    Custom data class for the data collected from surveys, so they can be displayed as dataframes correctly
    """

    def __init__(
        self,
        cdf_id: int,
        external_id: Optional[str],
        columns: List[BasicGetSequenceColumnInfo],
        rows: List[SequenceRowDTO],
    ):
        self.id = cdf_id
        self.external_id = external_id
        self.columns = columns
        self.rows = rows

    @staticmethod
    def from_sequence_data(survey_data: SequenceGetData):
        return SequenceRows(survey_data.id, survey_data.external_id, survey_data.columns, survey_data.rows)

    # Code for dump and to_pandas copied from sequences in cdf
    def dump(self, camel_case: bool = False) -> Dict[str, Any]:
        dumped = {
            "id": self.id,
            "external_id": self.external_id,
            "columns": self.columns,
            "rows": [
                {"rowNumber": r, "values": v}
                for r, v in zip([row.row_number for row in self.rows], [row.values for row in self.rows])
            ],
        }
        if camel_case:
            dumped = {to_camel_case(key): value for key, value in dumped.items()}
        return {key: value for key, value in dumped.items() if value is not None}

    def to_pandas(self, column_names: str = "columnExternalId") -> DataFrame:
        options = ["externalId", "id", "columnExternalId", "id|columnExternalId", "externalId|columnExternalId"]
        if column_names not in options:
            raise ValueError('Invalid column_names value, should be one of "%s"' % '", "'.join(options))

        column_names = (
            column_names.replace("columnExternalId", "{columnExternalId}")
            .replace("externalId", "{externalId}")
            .replace("id", "{id}")
        )
        df_columns = [
            column_names.format(id=str(self.id), externalId=str(self.external_id), columnExternalId=eid)
            for eid in [column.external_id for column in self.columns]
        ]

        row_values = [row.values for row in self.rows]
        row_numbers = [row.row_number for row in self.rows]
        return DataFrame(
            [[x if x is not None else math.nan for x in r] for r in row_values],
            index=row_numbers,
            columns=df_columns,
        )
