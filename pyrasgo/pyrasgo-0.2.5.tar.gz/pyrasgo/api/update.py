from typing import List, Optional

from .error import APIError
from pyrasgo import schemas as api
from pyrasgo.primitives import Collection, Feature, FeatureList, FeatureSet, DataSource
from pyrasgo.schemas.enums import Granularity, ModelType
from pyrasgo.utils import track_usage


class Update():

    def __init__(self):
        from .connection import Connection
        from pyrasgo.config import get_session_api_key

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)

    @track_usage
    def collection_attributes(self,
                              id: int,
                              attributes: List[dict]):
        """
        Create or update attributes on a Rasgo Collection

        param attributes: dict [{"key": "value"}, {"key": "value"}]
        """
        msg = 'attributes parameter must be passed in as a list of k:v pairs. Example: [{"key": "value"}, {"key": "value"}]'
        if not isinstance(attributes, list):
            raise APIError(msg)
        attr = []
        for kv in attributes:
            if not isinstance(kv, dict):
                raise APIError(msg)
            for k, v in kv.items():
                attr.append(api.Attribute(key=k, value=v))
        attr_in = api.CollectionAttributeBulkCreate(collectionId = id, attributes=attr)
        return self.api._put(f"/models/{id}/attributes", attr_in.dict(exclude_unset=True), api_version=1).json()

    @track_usage
    def column(self,
               id: int,
               name: Optional[str] = None,
               data_type: Optional[str] = None,
               feature_set_id: Optional[int] = None,
               dimension_id: Optional[int] = None) -> api.Column:
        column = api.ColumnUpdate(id=id,
                                  name=name, dataType=data_type,
                                  featureSetId=feature_set_id,
                                  dimensionId=dimension_id)
        response = self.api._patch(f"/columns/{id}", column.dict(exclude_unset=True, exclude_none=True), api_version=1).json()
        return api.Column(**response)

    @track_usage
    def data_source(self,
                    id: int,
                    name: Optional[str] = None,
                    domain: Optional[str] = None,
                    source_type: Optional[str] = None,
                    table: Optional[str] = None,
                    database: Optional[str] = None,
                    schema: Optional[str] = None,
                    source_code: Optional[str] = None,
                    table_status: Optional[str] = None,
                    parent_source_id: Optional[int] = None):
        data_source = api.DataSourceUpdate(id=id,
                                           name=name,
                                           domain=domain,
                                           table=table,
                                           tableDatabase=database,
                                           tableSchema=schema,
                                           sourceCode=source_code,
                                           tableStatus=table_status,
                                           sourceType=source_type,
                                           parentId=parent_source_id)
        response = self.api._patch(f"/data-source/{id}", data_source.dict(exclude_unset=True, exclude_none=True), api_version=1).json()
        return DataSource(api_object=response)

    @track_usage
    def dataframe(self,
                  unique_id: str,
                  name: Optional[str] = None,
                  shared_status: str = None,
                  column_hash: str = None,
                  update_date: str = None) -> api.Dataframe:
        if shared_status not in [None, 'private', 'organization', 'public']:
            raise APIError("Valid values for shared_status are ['private', 'organization', 'public']")
        dataframe = api.DataframeUpdate(name=name,
                                        uniqueId=unique_id,
                                        sharedStatus=shared_status,
                                        columnHash=column_hash,
                                        updatedDate = update_date)
        response = self.api._patch(f"/dataframes/{unique_id}", dataframe.dict(exclude_unset=True, exclude_none=True), api_version=1).json()
        return api.Dataframe(**response)

    @track_usage
    def feature(self,
                id: int,
                display_name: Optional[str] = None,
                column_name: Optional[str] = None,
                description: Optional[str] = None,
                status: Optional[str] = None,
                tags: Optional[List[str]] = None,
                git_repo: Optional[str] = None) -> Feature:
        feature = api.FeatureUpdate(id=id,
                                    name=display_name,
                                    code=column_name,
                                    description=description,
                                    orchestrationStatus=status,
                                    tags=tags,
                                    gitRepo=git_repo)
        response = self.api._patch(f"/features/{id}", feature.dict(exclude_unset=True, exclude_none=True), api_version=1).json()
        return Feature(api_object=response)

    @track_usage
    def feature_attributes(self,
                           id: int,
                           attributes: List[dict]):
        """
        Create or update attributes on a feature

        param attributes: dict [{"key": "value"}, {"key": "value"}]
        """
        msg = 'attributes parameter must be passed in as a list of k:v pairs. Example: [{"key": "value"}, {"key": "value"}]'
        if not isinstance(attributes, list):
            raise APIError(msg)
        attr = []
        for kv in attributes:
            if not isinstance(kv, dict):
                raise APIError(msg)
            for k, v in kv.items():
                attr.append(api.Attribute(key=k, value=v))
        attr_in = api.FeatureAttributeBulkCreate(featureId = id,
                                             attributes=attr)
        return self.api._put(f"/features/{id}/attributes", attr_in.dict(exclude_unset=True), api_version=1).json()

    @track_usage
    def feature_set(self,
                    id: int,
                    name: Optional[str] = None,
                    data_source_id: Optional[int] = None,
                    table_name: Optional[str] = None,
                    file_path: Optional[str] = None,
                    source_code: Optional[str] = None) -> FeatureSet:
        feature_set = api.FeatureSetUpdate(id=id,
                                           name=name,
                                           snowflakeTable=table_name,
                                           dataSourceId=data_source_id,
                                           rawFilePath=file_path,
                                           sourceCode=source_code)
        response = self.api._patch(f"/feature-sets/{id}", feature_set.dict(exclude_unset=True, exclude_none=True), api_version=0).json()
        return FeatureSet(api_object=response)