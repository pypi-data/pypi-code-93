from requests.exceptions import HTTPError
from typing import List, Optional, Union

from .error import APIError
from pyrasgo import schemas as api
from pyrasgo.primitives import Collection, Feature, FeatureList, FeatureSet, DataSource
from pyrasgo.schemas.enums import Granularity, ModelType
from pyrasgo.schemas.feature import featureImportanceStats, ColumnProfiles
from pyrasgo.utils import track_usage


class Create():

    def __init__(self):
        from .connection import Connection
        from pyrasgo.config import get_session_api_key

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)

    @track_usage
    def collection(self, name: str,
                   type: Union[str, ModelType],
                   granularity: Union[str, Granularity],
                   description: Optional[str] = None,
                   is_shared: Optional[bool] = False) -> Collection:
        try:
            # If not enum, convert to enum first.
            model_type = type.name
        except AttributeError:
            model_type = ModelType(type)

        try:
            # If not enum, convert to enum first.
            granularity = granularity.name
        except AttributeError:
            granularity = Granularity(granularity)

        content = {"name": name,
                   "type": model_type.value,
                   "granularities": [{"name": granularity.value}],
                   "isShared": is_shared
                   }
        if description:
            content["description"] = description
        response = self.api._post("/models", _json=content, api_version=1)
        return Collection(api_object=response.json())

    @track_usage
    def column(self, name: str,
               data_type: str,
               feature_set_id: int,
               dimension_id: int) -> api.Column:
        column = api.ColumnCreate(name=name, dataType=data_type,
                                  featureSetId=feature_set_id,
                                  dimensionId=dimension_id)
        response = self.api._post("/columns/", column.dict(exclude_unset=True), api_version=1).json()
        return api.Column(**response)

    @track_usage
    def data_source(self, table: str,
                    name: str,
                    source_type: str,
                    database: Optional[str] = None,
                    schema: Optional[str] = None,
                    source_code: Optional[str] = None,
                    domain: Optional[str] = None,
                    parent_source_id: Optional[int] = None) -> DataSource:
        data_source = api.DataSourceCreate(name=name,
                                           table=table,
                                           tableDatabase=database,
                                           tableSchema=schema,
                                           sourceCode=source_code,
                                           domain=domain,
                                           sourceType=source_type,
                                           parentId=parent_source_id)
        response = self.api._post("/data-source", data_source.dict(exclude_unset=True), api_version=1).json()
        return DataSource(api_object=response)

    @track_usage
    def dataframe(self, unique_id: str,
                  name: str = None,
                  shared_status: str = 'organization',
                  column_hash: Optional[str] = None,
                  update_date: str = None) -> api.Dataframe:
        shared_status = 'organization' if shared_status not in ['public', 'private'] else shared_status
        dataframe = api.DataframeCreate(uniqueId=unique_id,
                                        name=name,
                                        sharedStatus=shared_status,
                                        columnHash=column_hash,
                                        updatedDate=update_date)
        try:
            response = self.api._post("/dataframes", dataframe.dict(exclude_unset=True), api_version=1).json()
        except HTTPError as e:
            error_message = f"Failed to create dataframe {unique_id}."
            if e.response.status_code == 409:
                error_message += f" This id is already in use in your organization. Dataframe IDs must be unique."
            raise APIError(error_message)
        return api.Dataframe(**response)

    @track_usage
    def data_source_stats(self, data_source_id: int):
        """
        Sends an api request to build stats for a specified data source.
        """
        return self.api._post(f"/data-source/profile/{data_source_id}", api_version=1).json()

    @track_usage
    def dimensionality(self, granularity: str,
                       dimension_type: str) -> api.Dimensionality:
        """
        Creates a dimensionality record in a user's organization with format: DimensionType - Granularity
        """
        dimensionality = api.DimensionalityCreate(dimensionType=dimension_type,
                                                  granularity=granularity)
        response = self.api._post("/dimensionalities", dimensionality.dict(exclude_unset=True), api_version=1).json()
        return api.Dimensionality(**response)

    @track_usage
    def feature(self, feature_set_id: int,
                display_name: str,
                column_name: str,
                description: str,
                column_id: int,
                status: str,
                git_repo: str,
                tags: Optional[List[str]] = None) -> Feature:
        feature = api.FeatureCreate(name=display_name,
                                    code=column_name,
                                    description=description,
                                    featureSetId=feature_set_id,
                                    columnId=column_id,
                                    orchestrationStatus=status,
                                    tags=tags or [],
                                    gitRepo=git_repo)
        try:
            response = self.api._post("/features/", feature.dict(exclude_unset=True), api_version=1).json()
        except HTTPError as e:
            error_message = f"Failed to create Feature {display_name}."
            if e.response.status_code == 409:
                error_message += f" This name is already in use in your organization. Feature names must be unique."
            raise APIError(error_message)
        return Feature(api_object=response)

    @track_usage
    def feature_set(self, data_source_id: int,
                    name: str,
                    table_name: str,
                    file_path: Optional[str] = None,
                    source_code: Optional[str] = None) -> FeatureSet:
        feature_set = api.FeatureSetCreate(name=name,
                                           snowflakeTable=table_name,
                                           dataSourceId=data_source_id,
                                           rawFilePath=file_path,
                                           sourceCode=source_code)
        response = self.api._post("/feature-sets/", feature_set.dict(), api_version=0).json()
        return FeatureSet(api_object=response)

    @track_usage
    def feature_set_stats(self, feature_set_id: int):
        """
        Sends an api request to build feature stats for a specified feature.
        """
        return self.api._post(f"/feature-sets/{feature_set_id}/stats", api_version=1).json()

    @track_usage
    def feature_stats(self, feature_id: int):
        """
        Sends an api request to build feature stats for a specified feature.
        """
        return self.api._post(f"/features/{feature_id}/stats", api_version=1).json()

    @track_usage
    def feature_importance_stats(self, id: int, payload: featureImportanceStats):
        """
        Sends an api requrest to build feature importance stats for the specified model
        """
        return self.api._post(f"/models/{id}/stats/feature-importance", payload.dict(), api_version=1).json()

    @track_usage
    def column_importance_stats(self, id: str, payload: featureImportanceStats):
        """
        Sends a json payload of importance from a dataFrame to the API so it can render in the WebApp
        """
        return self.api._post(f"/dataframes/{id}/feature-importance", payload.dict(), api_version=1).json()

    @track_usage
    def dataframe_profile(self, id: str, payload: ColumnProfiles):
        """
        Send a json payload of a dataframe profile so it can render in the WebApp
        """
        return self.api._post(f"/dataframes/{id}/profile", payload.dict(), api_version=1).json()