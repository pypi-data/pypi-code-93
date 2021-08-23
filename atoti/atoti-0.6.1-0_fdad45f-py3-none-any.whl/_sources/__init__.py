from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any, Mapping, Optional

if TYPE_CHECKING:
    from .._java_api import JavaApi
    from ..column import Column
    from ..type import DataType


class DataSource(ABC):
    """Abstract data source."""

    def __init__(self, java_api: JavaApi, source_key: str):
        """Initialise the source.

        Args:
            java_api: The Java API of the session.
            source_key: The key of the source.
        """
        self._java_api = java_api
        self.source_key = source_key

    def load_data_into_table(
        self,
        table_name: str,
        *,
        scenario_name: Optional[str],
        source_params: Mapping[str, Any],
    ):
        """Load the data into an existing table with a given source.

        Args:
            table_name: The name of the table to feed.
            scenario_name: The name of the scenario to feed.
            source_params: The parameters specific to the source.
        """
        self._java_api.load_data_into_table(
            table_name=table_name,
            source_key=self.source_key,
            scenario_name=scenario_name,
            source_params=source_params,
        )
