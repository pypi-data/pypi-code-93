from __future__ import annotations

import pathlib
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Dict, Mapping, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd

from ._bitwise_operators_only import IdentityElement
from ._docs_utils import (
    CSV_KWARGS,
    HEAD_DOC,
    PARQUET_KWARGS,
    TABLE_APPEND_DOC,
    TABLE_IADD_DOC,
    doc,
)
from ._file_utils import _split_path_and_pattern
from ._ipython_utils import ipython_key_completions_for_mapping
from ._java_api import JavaApi
from ._plugins import MissingPluginError
from ._repr_utils import ReprJson, ReprJsonable
from ._scenario_utils import BASE_SCENARIO_NAME
from ._sources.csv import CsvDataSource
from ._sources.parquet import ParquetDataSource
from ._spark_utils import spark_to_temporary_parquet
from ._type_utils import typecheck
from .column import Column
from .report import TableReport
from .type import DataType

if TYPE_CHECKING:
    from pyspark.sql import DataFrame as SparkDataFrame

# Type for table rows
Row = Union[Tuple[Any, ...], Mapping[str, Any]]

_DOC_KWARGS = {"what": "table"}


@dataclass(frozen=True)
class _LoadParquetPrivateParameters:
    _parquet_column_name_to_table_column_name: Optional[Any] = None


@dataclass
class Table(ReprJsonable):
    """Represents a single table."""

    _name: str
    _java_api: JavaApi = field(repr=False)
    _scenario: str = field(default=BASE_SCENARIO_NAME)
    _columns: Dict[str, Column] = field(default_factory=dict)

    def __post_init__(self):
        """Finish initialization."""
        for col in self._java_api.get_table_schema(self):
            self._columns[col.name] = Column(col.name, col.data_type, self)

    @property
    def name(self) -> str:
        """Name of the table."""
        return self._name

    @property
    def keys(self) -> Sequence[str]:
        """Names of the key columns of the table."""
        return self._java_api.get_key_columns(self)

    @property
    def scenario(self) -> str:
        """Scenario on which the table is."""
        return self._scenario

    @property
    def columns(self) -> Sequence[str]:
        """Columns of the table."""
        return list(self._columns.keys())

    @property
    def _types(self) -> Mapping[str, DataType]:
        """Columns and their types."""
        return {name: col.data_type for name, col in self._columns.items()}

    @property
    def _partitioning(self) -> str:
        """Table partitioning."""
        return self._java_api.get_table_partitioning(self)

    def join(
        self,
        other: Table,
        *,
        mapping: Optional[Mapping[str, str]] = None,
    ):
        """Define a reference between this table and another.

        There are two different possible situations when creating references:

        * All the key columns of the *other* table are mapped: this is a normal reference.
        * Only some of the key columns of the *other* table are mapped: this is a partial reference:

            * The columns from the base table used in the mapping must be attached to hierarchies.
            * The un-mapped key columns of the *other* table will be converted into hierarchies.

        Depending on the cube creation mode, the join will also generate different hierarchies and measures:

        * ``manual``: The un-mapped keys of the *other* table will become hierarchies.
        * ``no_measures``: All of the key columns and non-numeric columns from the *other* table will be converted into hierarchies.
          No measures will be created in this mode.
        * ``auto``: The same hierarchies will be created as in the ``no_measures`` mode.
          Additionally, columns of the base table containing numeric values (including arrays), except for columns which are keys, will be converted into measures.
          Columns of the *other* table with these types will not be converted into measures.

        Args:
            other: The other table to reference.
            mapping: The column mapping of the reference.
                Defaults to the columns with the same names in the two tables.
        """
        self._java_api.create_join(
            self,
            other,
            mappings=mapping,
        )
        self._java_api.refresh()

    @property
    def scenarios(self) -> TableScenarios:
        """All the scenarios the table can be on."""
        if self.scenario != BASE_SCENARIO_NAME:
            raise Exception("You can only create a new scenario from the base scenario")
        return TableScenarios(self._java_api, self)

    @property
    def loading_report(self) -> TableReport:
        """Table loading report."""
        reports = self._java_api.get_loading_report(self)
        return TableReport(self.name, reports)

    def __getitem__(self, key: str) -> Column:
        """Return the column with the given name."""
        return self._columns[key]

    def __len__(self) -> int:
        """Return the number of rows in the table."""
        return self._java_api.get_table_size(self)

    def _ipython_key_completions_(self):
        return ipython_key_completions_for_mapping(self._columns)

    @doc(TABLE_APPEND_DOC, **_DOC_KWARGS)
    def append(self, *rows: Row):
        rows_df = pd.DataFrame(rows, columns=self.columns)
        self.load_pandas(rows_df)

    @doc(TABLE_IADD_DOC, **_DOC_KWARGS)
    def __iadd__(self, row: Row) -> Table:
        """Add a single row to the table."""
        self._java_api.insert_in_table(table=self, scenario_name=self.scenario, row=row)
        return self

    def drop(self, *coordinates: Mapping[str, Any]):
        """Delete rows where the values for each column match those specified.

        Each set of coordinates can only contain one value for each column.
        To specify multiple values for one column, multiple mappings must be passed.

        Args:
            coordinates: Mappings between table columns and values.
                Rows matching the provided mappings will be deleted from the table.
                If ``None``, all the rows of the table will be deleted.


        Example:
            >>> df = pd.DataFrame(
            ...     columns=["City", "Price"],
            ...     data=[
            ...         ("London", 240.0),
            ...         ("New York", 270.0),
            ...         ("Paris", 200.0),
            ...     ],
            ... )
            >>> table = session.read_pandas(df, keys=["City"], table_name="Cities")
            >>> table.head()
                      Price
            City
            London    240.0
            New York  270.0
            Paris     200.0
            >>> table.drop({"City": "Paris"})
            >>> table.head()
                      Price
            City
            London    240.0
            New York  270.0
            >>> table.drop()
            >>> table.head()
            Empty DataFrame
            Columns: [Price]
            Index: []
        """
        self._java_api.delete_rows_from_table(
            table=self,
            scenario_name=self.scenario,
            coordinates=coordinates,
        )

    def _repr_json_(self) -> ReprJson:
        key_cols = self.keys
        schema = {
            column.name: {
                "key": column.name in key_cols,
                "nullable": column.data_type.nullable,
                "type": column.data_type.java_type,
            }
            for column in list(self._columns.values())
        }
        return schema, {"expanded": True, "root": self.name}

    @doc(HEAD_DOC, **_DOC_KWARGS)
    def head(self, n: int = 5) -> pd.DataFrame:
        if n < 1:
            raise ValueError("n must be at least 1.")

        return self._java_api.get_table_dataframe(
            self, n, scenario_name=self.scenario, keys=self.keys
        )

    @doc(**CSV_KWARGS)
    def load_csv(
        self,
        path: Union[pathlib.Path, str],
        *,
        separator: Optional[str] = None,
        encoding: str = "utf-8",
        process_quotes: bool = True,
        array_separator: Optional[str] = None,
        date_patterns: Optional[Mapping[str, str]] = None,
    ):
        """Load a CSV into this scenario.

        Args:
            {path}
            {separator}
            {encoding}
            {process_quotes}
            {array_separator}
            {date_patterns}
        """
        path, pattern = _split_path_and_pattern(path, ".csv")

        CsvDataSource(self._java_api).load_csv_into_table(
            path,
            self,
            scenario_name=self.scenario,
            separator=separator,
            encoding=encoding,
            process_quotes=process_quotes,
            array_separator=array_separator,
            pattern=pattern,
            date_patterns=date_patterns,
        )

    def load_pandas(
        self,
        dataframe: pd.DataFrame,  # type: ignore
    ):
        """Load a pandas DataFrame into this scenario.

        Args:
            dataframe: The DataFrame to load.
        """
        from ._pandas_utils import pandas_to_temporary_parquet

        # Save DataFrame as Parquet then read it
        (
            parquet_path,
            parquet_column_name_to_table_column_name,
        ) = pandas_to_temporary_parquet(dataframe, types=self._types)
        self.load_parquet(
            parquet_path,
            _parquet_column_name_to_table_column_name=parquet_column_name_to_table_column_name,
        )

    def load_numpy(
        self,
        array: np.ndarray,  # type: ignore
    ):
        """Load a NumPy 2D array into this scenario.

        Args:
            array: The 2D array to load.
        """
        dataframe = pd.DataFrame(array, columns=self.columns)
        self.load_pandas(dataframe)

    @doc(**PARQUET_KWARGS)
    def load_parquet(
        self,
        path: Union[pathlib.Path, str],
        **kwargs: Any,
    ):
        """Load a Parquet file into this scenario.

        Args:
            {path}
        """
        private_parameters = _LoadParquetPrivateParameters(**kwargs)
        path, pattern = _split_path_and_pattern(path, ".parquet")
        ParquetDataSource(self._java_api).load_parquet_into_table(
            path=path,
            table=self,
            scenario_name=self.scenario,
            pattern=pattern,
            _parquet_column_name_to_table_column_name=private_parameters._parquet_column_name_to_table_column_name,
        )

    @typecheck(ignored_params=["dataframe"])
    def load_spark(
        self,
        dataframe: SparkDataFrame,  # type: ignore
    ):
        """Load a Spark DataFrame into this scenario.

        Args:
            dataframe: The dataframe to load.
        """
        parquet_file = spark_to_temporary_parquet(dataframe)
        self.load_parquet(
            parquet_file,
        )

    def load_kafka(  # pylint: disable=no-self-use
        self, *args: Any, **kwargs: Any
    ) -> Any:
        raise MissingPluginError("kafka")

    def load_sql(self, *args: Any, **kwargs: Any) -> Any:  # pylint: disable=no-self-use
        raise MissingPluginError("sql")

    def _identity(self) -> Tuple[IdentityElement, ...]:
        identity = (self._name, self._scenario)
        for name, column in self._columns.items():
            identity += (name,) + column._identity()
        return identity


def _create_table(java_api: JavaApi, name: str) -> Table:
    """Create a table and refresh the session.

    Args:
        java_api: The Java API.
        name: The name of the table.
    """
    table = Table(name, java_api)
    return table


@dataclass(frozen=True)
class TableScenarios:
    """Scenarios of a table."""

    _java_api: JavaApi = field(repr=False)
    _table: Table = field(repr=False)

    def __getitem__(self, key: str) -> Table:
        """Get the scenario or create it if it does not exist.

        Args:
            key: the name of the scenario

        """
        return Table(self._table.name, self._java_api, key)

    def __delitem__(self, key: str) -> None:
        """Override base del method to throw an error."""
        raise Exception(
            "You cannot delete a scenario from a table since they are shared between all tables."
            "Use the Session.delete_scenario() method instead."
        )
