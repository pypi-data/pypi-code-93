import pandas as pd
from typing import Dict, List, Optional

from .error import APIError
from pyrasgo import config
from pyrasgo import schemas as api
from pyrasgo.primitives import Collection, Feature, FeatureList, DataSource
from pyrasgo.utils import track_usage


class Read():
    
    def __init__(self):
        from . import Get
        from pyrasgo.storage import DataWarehouse, SnowflakeDataWarehouse
        
        self.data_warehouse: SnowflakeDataWarehouse = DataWarehouse.connect()
        self.get = Get()

    @track_usage
    def collection_data(self, 
                        id: int,
                        filters: Optional[Dict[str, str]] = None,
                        limit: Optional[int] = None) -> pd.DataFrame:
        """
        Constructs a pandas DataFrame from the specified Rasgo Collection

        :param id: int
        :param filters: dictionary providing columns as keys and the filtering values as values.
        :param limit: integer limit for number of rows returned
        :return: Dataframe containing feature data
        """
        collection = self.get.collection(id)
        if collection:
            try:
                table_metadata = collection._make_table_metadata()
                query, values = self.data_warehouse._make_select_statement(table_metadata, filters, limit)
                return self.data_warehouse.query_into_dataframe(query, values)
            except Exception as e:
                raise APIError(f"Collection table is not reachable: {e}")
        raise APIError("Collection does not exist")

    @track_usage
    def feature_data(self, 
                     id: int,
                     filters: Optional[Dict[str, str]] = None,
                     limit: Optional[int] = None) -> pd.DataFrame:
        """
        Constructs a pandas DataFrame from the specified Rasgo Feature data

        :param id: int
        :param filters: dictionary providing columns as keys and the filtering values as values.
        :param limit: integer limit for number of rows returned
        :return: Dataframe containing feature data
        """
        feature = self.get.feature(id)
        if feature.sourceTable:
            try:
                table_metadata = feature._make_table_metadata()
                #TODO: if we ever support multiple features, add them to this line -
                features = feature.columnName
                indices = ','.join(feature.indexFields)
                columns = indices +', '+features
                query, values = self.data_warehouse._make_select_statement(table_metadata, filters, limit, columns)
                return self.data_warehouse.query_into_dataframe(query, values)
            except Exception as e:
                raise APIError(f"Feature table is not reachable: {e}")
        raise APIError("Feature table does not exist")

    @track_usage
    def source_data(self, 
                    id: int,
                    filters: Optional[Dict[str, str]] = None,
                    limit: Optional[int] = None) -> pd.DataFrame:
        """
        Constructs a pandas DataFrame from the specified Rasgo DataSource

        :param id: int
        :param filters: dictionary providing columns as keys and the filtering values as values.
        :param limit: integer limit for number of rows returned
        :return: Dataframe containing feature data
        """
        data_source = self.get.data_source(id)
        if data_source:
            try:
                table_metadata = data_source._make_table_metadata()
                query, values = self.data_warehouse._make_select_statement(table_metadata, filters, limit)
                return self.data_warehouse.query_into_dataframe(query, values)
            except Exception as e:
                raise APIError(f"DataSource table is not reachable: {e}")
        raise APIError("DataSource does not exist")