from __future__ import annotations

from typing import TYPE_CHECKING, Any, Collection, Dict, Mapping, Optional

from .._path_utils import PathLike, to_absolute_path
from . import DataSource

if TYPE_CHECKING:
    from .._java_api import JavaApi
    from ..table import Table


def create_csv_params(
    *,
    path: PathLike,
    separator: Optional[str],
    encoding: str,
    process_quotes: Optional[bool],
    array_separator: Optional[str],
    pattern: Optional[str],
    date_patterns: Optional[Mapping[str, str]],
) -> Dict[str, Any]:
    """Create the CSV specific parameters."""
    return {
        "absolutePath": to_absolute_path(path),
        "separator": separator,
        "encoding": encoding,
        "processQuotes": process_quotes,
        "arraySeparator": array_separator,
        "globPattern": pattern,
        "datePatterns": date_patterns,
    }


class CsvDataSource(DataSource):
    """CSV data source."""

    def __init__(self, java_api: JavaApi):
        """Init."""
        super().__init__(java_api, "CSV")

    def infer_csv_types(
        self,
        path: PathLike,
        *,
        keys: Optional[Collection[str]],
        separator: Optional[str],
        encoding: str,
        process_quotes: Optional[bool],
        array_separator: Optional[str],
        pattern: Optional[str],
        date_patterns: Optional[Mapping[str, str]],
    ):
        """Infer Table types from a CSV file or directory."""
        source_params = create_csv_params(
            path=path,
            separator=separator,
            encoding=encoding,
            process_quotes=process_quotes,
            array_separator=array_separator,
            pattern=pattern,
            date_patterns=date_patterns,
        )
        return self._java_api.infer_table_types_from_source(
            source_key=self.source_key,
            keys=keys,
            source_params=source_params,
        )

    def load_csv_into_table(
        self,
        path: PathLike,
        table: Table,
        *,
        scenario_name: str,
        separator: Optional[str],
        encoding: str,
        process_quotes: bool,
        array_separator: Optional[str],
        pattern: Optional[str],
        date_patterns: Optional[Mapping[str, str]],
    ):
        """Load a csv into an existing table."""
        source_params = create_csv_params(
            path=path,
            separator=separator,
            encoding=encoding,
            process_quotes=process_quotes,
            array_separator=array_separator,
            pattern=pattern,
            date_patterns=date_patterns,
        )
        self.load_data_into_table(
            table.name,
            scenario_name=scenario_name,
            source_params=source_params,
        )
