from typing import Dict, List, Optional, Union

import pandas as pd
import time
from tqdm import tqdm

from pyrasgo.api.connection import Connection
from pyrasgo.schemas import data_source as schema
from pyrasgo.utils import naming, track_usage

class DataSource(Connection):
    """
    Stores a Rasgo DataSource
    """

    def __init__(self, api_object, **kwargs):
        super().__init__(**kwargs)
        self._fields = schema.DataSource(**api_object)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"Source(id={self.id}, name={self.name}, sourceType={self.sourceType}, table={naming.make_fqtn(self.table, self.tableDatabase, self.tableSchema)})"

    def __getattr__(self, item):
        try:
            return self._fields.__getattribute__(item)
        except KeyError:
            self.refresh()
        try:
            return self._fields.__getattribute__(item)
        except KeyError:
            raise AttributeError(f"No attribute named {item}")

# ----------
# Properties
# ----------
    @property
    @track_usage
    def columns(self) -> List[schema.DataSourceColumn]:
        """
        Returns columns in the DataSource table
        """
        response = self._get(f"/data-source/columns/{self.id}", api_version=1).json()
        return [schema.DataSourceColumn(**column) for column in response['columns']]

# -------
# Methods
#--------
    @track_usage
    def display_source_code(self):
        """
        Convenience function to display the sourceCode property
        """
        return self._fields.sourceCode

    @track_usage
    def read_into_df(self,
                     filters: Optional[Dict[str, str]] = None,
                     limit: Optional[int] = None) -> pd.DataFrame:
        """
        Pull Source data from DataWarehouse into a pandas Dataframe
        """
        from pyrasgo.api.read import Read
        return Read().source_data(id=self.id, filters=filters, limit=limit)

    @track_usage
    def rebuild_from_source_code(self):
        """
        Rebuild the Source using the source code
        """
        raise NotImplementedError()

    @track_usage
    def refresh(self):
        """
        Updates the Soure's attributes from the API
        """
        self._fields = schema.DataSource(**self._get(f"/data-source/{self.id}", api_version=1).json())

    @track_usage
    def rename(self, new_name: str):
        """
        Updates a DataSource's display name
        """
        print(f"Renaming DataSource {self.id} from {self.name} to {new_name}")
        source = schema.DataSourceUpdate(id=self.id, name=new_name)
        self._fields = schema.DataSource(**self._patch(f"/data-source/{self.id}",
                                                    api_version=1, _json=source.dict(exclude_unset=True, exclude_none=True)).json())

    def _make_table_metadata(self):
        organization = self._get_profile().get("organization")
        metadata = {
            "database": self._fields.tableDatabase or organization.get("database"),
            "schema": self._fields.tableSchema or organization.get("schema"),
            "table": self._fields.table,
        }
        return metadata