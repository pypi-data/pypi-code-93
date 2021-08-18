import pandas as pd
from typing import List, Optional

from .error import APIError
from pyrasgo import schemas as api
from pyrasgo.primitives import Collection, Feature, FeatureList, FeatureSet, DataSource
from pyrasgo.utils import track_usage


class Get():
    
    def __init__(self):
        from .connection import Connection
        from pyrasgo.config import get_session_api_key
        from pyrasgo.storage import DataWarehouse, SnowflakeDataWarehouse

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)
        self.data_warehouse: SnowflakeDataWarehouse = DataWarehouse.connect()

    @track_usage
    def collection(self, id: int) -> Collection:
        """
        Returns a Rasgo Collection (set of joined Features) matching the specified id
        """
        try:
            return Collection(api_object=self.api._get(f"/models/{id}", api_version=1).json())
        except:
            raise APIError(f"Collection {id} does not exist or this API key does not have access.")

    @track_usage
    def collection_attributes(self, id: int) -> api.CollectionAttributes:
        """
        Returns a dict of attributes for a collection
        """
        try:
            response = self.api._get(f"/models/{id}/attributes", api_version=1).json()
            dict_out = {}
            for kv in response:
                dict_out[kv['key']] = kv['value']
            return api.CollectionAttributes(collectionId=id, attributes=dict_out)
        except:
            raise APIError(f"Collection {id} does not exist or this API key does not have access.")

    @track_usage
    def collections(self, include_shared: bool=False) -> List[Collection]:
        """
        Returns all Rasgo Collections (set of joined Features) that I have author access to. Add an include_shared 
        parameter to return all Rasgo Collections that I have any access to (author or shared access)
        :param include_shared: Boolean value indicating if the return should include all accessible collections
        """
        try:
            return [Collection(api_object=entry) for entry in self.api._get(f"/models", {"include_shared": include_shared}, api_version=1).json()]
        except:
            raise APIError("Collections do not exist or this API key does not have access.")

    @track_usage
    def collections_by_attribute(self, key: str, value: str = None) -> List[Collection]:
        """
        Returns a list of Rasgo Collections that match an attribute
        """
        try:
            params = {"key": key}
            if value:
                params.update({"value": value})
            return self.api._get(f"/models/attributes/models", params=params, api_version=1).json()
        except:
            raise APIError(f"Key {key}: {value or 'Any'} does not exist or this API key does not have access.")

    @track_usage
    def column(self, id: int) -> api.Column:
        """
        Returns a Column with the specified id
        """
        try:
            response = self.api._get(f"/columns/{id}", api_version=1).json()
            return api.Column(**response)
        except:
            raise APIError(f"Column {id} does not exist or this API key does not have access.")

    @track_usage
    def columns_by_featureset(self, id: int) -> List[api.Column]:
        """
        Returns all Columns in the specified FeatureSet
        """
        try:
            response = self.api._get(f"/columns/by-featureset/{id}", api_version=1).json()
            return [api.Column(**entry) for entry in response]
        except:
            raise APIError(f"FeatureSet {id} does not exist or this API key does not have access.")

    @track_usage
    def data_sources(self) -> List[DataSource]:
        """
        Returns all DataSources available in your organization or Rasgo Community
        """
        try:
            response = self.api._get("/data-source", api_version=1).json()
            return [DataSource(api_object=entry) for entry in response]
        except:
            raise APIError("Data Sources do not exist or this API key does not have access.")

    @track_usage
    def data_source(self, id: int) -> DataSource:
        """
        Returns the DataSource with the specified id
        """
        try:
            response = self.api._get(f"/data-source/{id}", api_version=1).json()
            return DataSource(api_object=response)
        except:
            raise APIError(f"Data Source {id} does not exist or this API key does not have access.")

    @track_usage
    def data_source_columns(self, id: int) -> List[api.DataSourceColumn]:
        """
        Returns columns in the DataSource with the specified id
        """
        try:
            response = self.api._get(f"/data-source/columns/{id}", api_version=1).json()
            return [api.DataSourceColumn(**column) for column in response['columns']]
        except:
            raise APIError(f"Data Source {id} does not exist or this API key does not have access.")

    @track_usage
    def data_source_stats(self, id: int):
        """
        Returns the stats profile of the specificed data source
        """
        try:
            return self.api._get(f"/data-source/profile/{id}", api_version=1).json()
        except:
            raise APIError(f"Stats do not exist for DataSource {id}")

    @track_usage
    def dataframes(self) -> List[api.Dataframe]:
        """
        Returns all Dataframes available in your organization or Rasgo Community
        """
        try:
            response = self.api._get("/dataframes", api_version=1).json()
            return [api.Dataframe(**entry) for entry in response]
        except:
            raise APIError("Dataframes do not exist or this API key does not have access.")

    @track_usage
    def dataframe(self, unique_id: str) -> api.Dataframe:
        """
        Returns the Dataframe with the specified id
        """
        try:
            response = self.api._get(f"/dataframes/{unique_id}", api_version=1).json()
            return api.Dataframe(**response)
        except:
            raise APIError(f"Dataframe {unique_id} does not exist or this API key does not have access.")

    @track_usage
    def dimensionalities(self) -> List[api.Dimensionality]:
        """
        Returns all Dimensionalities available in your organization or Rasgo Community
        """
        try:
            response = self.api._get("/dimensionalities", api_version=1).json()
            return [api.Dimensionality(**entry) for entry in response]
        except:
            raise APIError("Dimensionalities do not exist or this API key does not have access.")
    
    @track_usage
    def feature(self, id: int) -> Feature:
        """
        Returns the Feature with the specified id
        """
        try:
            return Feature(api_object=self.api._get(f"/features/{id}", api_version=1).json())
        except:
            raise APIError(f"Feature {id} does not exist or this API key does not have access.")
    
    @track_usage
    def feature_attributes(self, id: int) -> api.FeatureAttributes:
        """
        Returns a dict of attributes for a feature
        """
        try:
            response = self.api._get(f"/features/{id}/attributes", api_version=1).json()
            dict_out = {}
            for kv in response:
                dict_out[kv['key']] = kv['value']
            return api.FeatureAttributes(featureId=id, attributes=dict_out)
        except:
            raise APIError(f"Feature {id} does not exist or this API key does not have access.")

    @track_usage
    def feature_attributes_log(self, id: int) -> tuple:
        """
        Returns a list of all attributes values logged to a feature over time
        """
        try:
            response = self.api._get(f"/features/{id}/attributes/log", api_version=1).json()
            lst_out = []
            for kv in response:
                dict_item={}
                dict_item[kv['key']] = kv.get('value', None)
                dict_item['updatedBy'] = kv.get('recordAuthorId', None)
                dict_item['updated'] = kv.get('recordTimestamp', None)
                lst_out.append(dict_item)
            return api.FeatureAttributesLog(featureId=id, attributes=lst_out)
        except:
            raise APIError(f"Feature {id} does not exist or this API key does not have access.")

    @track_usage
    def feature_set(self, id: int) -> FeatureSet:
        """
        Returns the FeatureSet (set of Fetures) with the specified id
        """
        try:
            response = self.api._get(f"/feature-sets/{id}", api_version=1).json()
            return FeatureSet(api_object=response)
        except:
            raise APIError(f"FeatureSet {id} does not exist or this API key does not have access.")

    @track_usage
    def feature_set_yml(self, id: int) -> FeatureSet:
        """
        Returns the FeatureSet (set of Fetures) with the specified id
        """
        try:
            response = self.api._get(f"/feature-sets/{id}", api_version=1).json()
            return api.FeatureSetYML(**response)
        except:
            raise APIError(f"FeatureSet {id} does not exist or this API key does not have access.")

    @track_usage
    def feature_sets(self) -> List[FeatureSet]:
        """
        Returns a list of FeatureSets (set of Features) available in your organization or Rasgo Community
        """
        try:
            response = self.api._get("/feature-sets", api_version=1).json()
            return [FeatureSet(api_object=entry) for entry in response]
        except:
            raise APIError("FeatureSets do not exist or this API key does not have access.")

    @track_usage
    def feature_stats(self, id: int) -> Optional[api.FeatureStats]:
        """
        Returns the stats profile for the specified Feature
        """
        try:
            stats_json = self.api._get(f"/features/{id}/stats", api_version=1).json()
            return api.FeatureStats(**stats_json["featureStats"])
        except:
            raise APIError(f"Stats do not exist yet for feature {id}.")
    
    @track_usage
    def features(self) -> FeatureList:
        """
        Returns a list of Features available in your organization or Rasgo Community
        """
        try:
            return FeatureList(api_object=self.api._get("/features", api_version=1).json())
        except:
            raise APIError("Features do not exist or this API key does not have access.")

    @track_usage
    def features_by_attribute(self, key: str, value: str = None) -> List[Feature]:
        """
        Returns a list of features that match an attribute
        """
        try:
            params = {"key": key}
            if value:
                params.update({"value": value})
            return FeatureList(api_object=self.api._get(f"/features/attributes/features", params=params, api_version=1).json())
        except:
            raise APIError(f"Key {key}: {value or 'Any'} does not exist or this API key does not have access.")

    @track_usage
    def features_by_featureset(self, id: int) -> FeatureList:
        """
        Returns a list of Features in the specific FeatureSet
        """
        try:
            response = self.api._get(f"/features/by-featureset/{id}", api_version=1)
            return FeatureList(api_object=response.json())
        except:
            raise APIError(f"FeatureSet {id} does not exist or this API key does not have access.")

    @track_usage
    def shared_collections(self) -> List[Collection]:
        """
        Returns all Rasgo Collections (set of joined Features) shared in my organization or in Rasgo community
        """
        try:
            return [Collection(api_object=entry) for entry in self.api._get(f"/models/shared", api_version=1).json()]
        except:
            raise APIError("Shared Collections do not exist or this API key does not have access.")

    @track_usage
    def source_columns(self, table: Optional[str] = None, database: Optional[str] = None, schema: Optional[str] = None, data_type: Optional[str] = None) -> pd.DataFrame:
        """
        Returns a DataFrame of columns in Snowflake tables and views that are queryable as feature sources
        """
        return self.data_warehouse.get_source_columns(table=table, database=database, schema=schema, data_type=data_type)

    @track_usage
    def source_tables(self, database: Optional[str] = None, schema: Optional[str] = None) -> pd.DataFrame:
        """
        Return a DataFrame of Snowflake tables and views that are queryable as feature sources
        """
        return self.data_warehouse.get_source_tables(database=database, schema=schema)

    @track_usage
    def transform_list(self) -> dict:
        """
        Returns json of all available transforms
        """
        return self.api._get("/features/transforms2", api_version=1).json()

    @track_usage
    def user(self):
        return self.api._get("/users/me", api_version=1).json()