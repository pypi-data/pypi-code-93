from __future__ import annotations

from typing import TYPE_CHECKING, Collection, Mapping, Optional

from .._path_utils import PathLike, to_absolute_path
from . import DataSource

if TYPE_CHECKING:
    from .._java_api import JavaApi
    from ..table import Table


class ParquetDataSource(DataSource):
    """Parquet data source."""

    def __init__(self, java_api: JavaApi):
        """Init."""
        super().__init__(java_api, "PARQUET")

    def infer_parquet_types(
        self,
        *,
        path: PathLike,
        keys: Optional[Collection[str]],
        pattern: Optional[str],
        _parquet_column_name_to_table_column_name: Optional[Mapping[str, str]],
    ):
        """Infer Table types from a Parquet file."""
        return self._java_api.infer_table_types_from_source(
            source_key=self.source_key,
            keys=keys,
            source_params={
                "absolutePath": to_absolute_path(path),
                "globPattern": pattern,
                "parquetColumnNamesToStoreFieldNamesMapping": _parquet_column_name_to_table_column_name,
            },
        )

    def load_parquet_into_table(
        self,
        *,
        path: PathLike,
        table: Table,
        scenario_name: str,
        pattern: Optional[str] = None,
        _parquet_column_name_to_table_column_name: Optional[Mapping[str, str]] = None,
    ):
        """Load a Parquet into an existing table."""
        self.load_data_into_table(
            table.name,
            scenario_name=scenario_name,
            source_params={
                "absolutePath": to_absolute_path(path),
                "globPattern": pattern,
                "parquetColumnNamesToStoreFieldNamesMapping": _parquet_column_name_to_table_column_name,
            },
        )
