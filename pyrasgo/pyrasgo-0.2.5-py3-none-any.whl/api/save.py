import pandas as pd
from typing import Dict, List, Optional

from .error import APIError
from pyrasgo.primitives import Feature, FeatureList, FeatureSet, DataSource
from pyrasgo import schemas as api
from pyrasgo.utils import ingestion, naming, track_usage


class Save():

    def __init__(self):
        from . import Get, Create, Match, Update
        from pyrasgo.storage import DataWarehouse, SnowflakeDataWarehouse

        self.data_warehouse: SnowflakeDataWarehouse = DataWarehouse.connect()
        self.get = Get()
        self.match = Match()
        self.create = Create()
        self.update = Update()

    @track_usage
    def data_source(self, table: str,
                    name: str = None,
                    database: Optional[str] = None,
                    schema: Optional[str] = None,
                    source_code: Optional[str] = None,
                    domain: Optional[str] = None,
                    source_type: Optional[str] = None,
                    parent_source_id: Optional[int] = None,
                    if_exists: str = 'return') -> DataSource:
        """
        Creates or returns a DataSource depending on of the defined parameters

        if_exists:  return - returns the source without operating on it
                    edit - edits the existing source
                    new - creates a new source
        """
        fqtn = naming.make_fqtn(table=table, database=database, schema=schema)
        ds = self.match.data_source(fqtn=fqtn)
        if ds:
            if if_exists == 'return':
                return ds
            elif if_exists in ['edit', 'replace', 'append']:
                return self.update.data_source(id=ds.id, name=name, table=table, database=database, schema=schema, source_code=source_code, domain=domain, source_type=source_type, parent_source_id=parent_source_id)
            else:
                raise APIError(f"Table {fqtn} is already registered as Data Source {ds.id}")
        return self.create.data_source(name=name, table=table, database=database, schema=schema, source_code=source_code, domain=domain, source_type=source_type, parent_source_id=parent_source_id)

    @track_usage
    def dataframe(self, unique_id: str,
                  name: str = None,
                  shared_status: str = None,
                  column_hash: Optional[str] = None,
                  update_date: str = None,
                  if_exists: str = 'return') -> api.Dataframe:
        """
        Creates or returns a Dataframe depending on of the defined parameters

        if_exists:  return - returns the source without operating on it
                    edit - edits the existing source
                    new - creates a new source
        """
        df = self.match.dataframe(unique_id=unique_id)
        if df:
            if if_exists == 'return':
                return df
            elif if_exists in ['edit', 'replace', 'append']:
                return self.update.dataframe(df.uniqueId, name, shared_status, column_hash, update_date)
            else:
                raise APIError(f"ID {unique_id} is already registered as DataFrame {df.id}")
        return self.create.dataframe(unique_id, name, shared_status, column_hash, update_date)

    @track_usage
    def dimension(self, feature_set_id: int,
                  column_name: str,
                  data_type: str,
                  display_name: Optional[str] = None,
                  dimension_type: Optional[str] = None,
                  granularity: Optional[str] = None,
                  if_exists: str = 'return') ->api.Column:
        """
        Creates or updates a dimension depending on existence of the defined parameters

        if_exists:  return - returns the source without operating on it
                    edit - edits the existing source
                    new - creates a new source
        """
        dimensionality = self.dimensionality(dimension_type=dimension_type, granularity=granularity)
        dim = self.match.column(name=column_name, feature_set_id=feature_set_id)
        if dim:
            if if_exists == 'return':
                return dim
            elif if_exists in ['edit', 'replace', 'append']:
                return self.update.column(id=dim.id, name=column_name, data_type=data_type, feature_set_id=feature_set_id, dimension_id=dimensionality.id)
            else:
                raise APIError(f"Column {column_name} is already registered in FeatureSet {feature_set_id} as Dimension {dim.id}")
        return self.create.column(name=column_name, data_type=data_type, feature_set_id=feature_set_id, dimension_id=dimensionality.id)

    @track_usage
    def dimensionality(self, granularity: str,
                       dimension_type: Optional[str] = None,
                       if_exists: str = 'return') -> api.Dimensionality:
        """
        Creates or returns a dimensionality depending on existence of the defined parameters

        Dimensionality is a named pairing of a datatype and a granularity. Note in some cases the
        granularity is actually a data type.
        """
        # TODO: We should move this mapping to the Granularity enum class or behind an API
        if dimension_type is None:
            if granularity.lower() in ["second", "minute", "hour", "day", "week", "month", "quarter", "year"]:
                dimension_type = "DateTime"
            elif granularity.lower() in ["latlong", "zipcode", "fips", "dma", "city", "cbg", "county", "state",
                                         "country"]:
                dimension_type = "Geolocation"
            else:
                dimension_type = "Custom"
        elif dimension_type.lower() == "datetime":
            dimension_type = "DateTime"
        elif dimension_type.lower() in ["geo", "geoloc", "geolocation"]:
            dimension_type = "Geolocation"
        else:
            dimension_type = dimension_type.title()

        dimensionality = self.match.dimensionality(granularity)
        # No edit path for dimensionality for now...
        if dimensionality:
            if if_exists in ['return', 'edit']:
                return dimensionality
            else:
                raise APIError(f"Dimensionality {granularity} is already registered as Dimensionality {dimensionality.id}")
        return self.create.dimensionality(dimension_type=dimension_type, granularity=granularity)

    @track_usage
    def feature(self, feature_set_id: int,
                column_name: str,
                display_name: str,
                data_type: str,
                description: Optional[str] = None,
                granularity: Optional[str] = None,
                status: Optional[str] = None,
                tags: Optional[List[str]] = None,
                git_repo: Optional[str] = None,
                if_exists: str = 'return') -> Feature:
        """
        Creates or updates a feature depending on existence of the defined parameters

        if_exists:  return - returns the source without operating on it
                    edit - edits the existing source
                    new - creates a new source
        """
        column_name = column_name or display_name
        description = description or f"Feature that contains {display_name} data"
        status = status or "Sandboxed"
        dimension_id = None if granularity is None else self.dimensionality(dimension_type=None, granularity=granularity).id

        ft = self.match.feature(code=column_name, feature_set_id=feature_set_id)
        if ft:
            if if_exists == 'return':
                return ft
            elif if_exists in ['edit', 'replace', 'append']:
                self.update.column(id=ft.columnId, name=column_name, data_type=data_type, feature_set_id=feature_set_id, dimension_id=dimension_id)
                return self.update.feature(id=ft.id, display_name=display_name, column_name=column_name, description=description, status=status, tags=tags or [], git_repo=git_repo)
            else:
                raise APIError(f"Column {column_name} is already registered in FeatureSet {feature_set_id} as Feature {ft.id}")
        column = self.create.column(name=column_name, data_type=data_type, feature_set_id=feature_set_id, dimension_id=dimension_id)
        return self.create.feature(feature_set_id=feature_set_id, display_name=display_name, column_name=column_name, description=description, column_id=column.id, status=status, git_repo=git_repo, tags=tags or [])

    @track_usage
    def feature_set(self, data_source_id: int,
                    table_name: str,
                    name: str,
                    file_path: Optional[str] = None,
                    source_code: Optional[str] = None,
                    if_exists: str = 'return') -> FeatureSet:
        """
        Creates or updates a featureset depending on existence of the defined parameters

        if_exists:  return - returns the source without operating on it
                    edit - edits the existing source
                    new - creates a new source
        """
        fs = self.match.feature_set(table_name=table_name)
        if fs:
            if if_exists == 'return':
                return fs
            elif if_exists in ['edit', 'replace', 'append']:
                return self.update.feature_set(id=fs.id, name=name, data_source_id=data_source_id, table_name=table_name, file_path=file_path, source_code=source_code)
            else:
                raise APIError(f"Table {table_name} is already registered as FeatureSet {fs.id}")
        return self.create.feature_set(name=name, data_source_id=data_source_id, table_name=table_name, file_path=file_path, source_code=source_code)

    @track_usage
    def feature_set_dict(self, feature_set_dict: dict,
                         trigger_stats: bool = True) -> FeatureSet:
        """
        Creates or updates a featureset based on values in a dict
        """
        if not ingestion._confirm_valid_dict(dict_in=feature_set_dict):
            raise APIError("Not a valid dict")
        source_table = feature_set_dict.get("sourceTable")
        ds = feature_set_dict.get("datasource")
        ds_name = ds.get("name", source_table) if ds else source_table
        data_source = self.data_source(name=ds_name, table=source_table, source_type="Table")
        featureset_name = feature_set_dict.get("name", source_table)
        tags = []
        if feature_set_dict.get("tags"):
            for t in feature_set_dict.get("tags"):
                tags.append(t)
        attributes = []
        if feature_set_dict.get("attributes"):
            for a in feature_set_dict.get("attributes"):
                for k, v in a.items():
                    attributes.append({k: v})
        source_code = feature_set_dict.get("sourceCode")
        featureset = self.feature_set(name=featureset_name, data_source_id=data_source.id, table_name=source_table, source_code=source_code, if_exists='edit')

        # publish dimensions
        for dim in feature_set_dict["dimensions"]:
            column_name = dim.get("columnName")
            display_name = dim.get("displayName")
            data_type = dim.get("dataType")
            # if we get an enum, convert it to str so pydantic doesn't get mad
            if isinstance(data_type, api.DataType):
                data_type = data_type.value
            dim_granularity = dim.get("granularity")
            self.dimension(feature_set_id=featureset.id, column_name=column_name, display_name=display_name, data_type=data_type, granularity=dim_granularity, if_exists='edit')

        # publish features
        for feature in feature_set_dict["features"]:
            display_name = feature.get("displayName")
            column_name = feature.get("columnName")
            data_type = feature.get("dataType")
            # if we get an enum, convert it to str so pydantic doesn't get mad
            if isinstance(data_type, api.DataType):
                data_type = data_type.value
            description = feature.get("description", f"Feature that contains {display_name} data")
            # apply featureset tags to all features...
            feature_tags = tags
            # ...and add feature-specific tags
            if feature.get("tags"):
                for t in feature.get("tags"):
                    feature_tags.append(t)
            feature_attributes = attributes
            if feature.get("attributes"):
                for a in feature.get("attributes"):
                    for k, v in a.items():
                        feature_attributes.append({k: v})
            status = "Sandboxed" if feature_set_dict.get("status") == "Sandboxed" else "Productionized"
            f = self.feature(feature_set_id=featureset.id, display_name=display_name, data_type=data_type, column_name=column_name, description=description, status=status, tags=feature_tags, if_exists='edit')
            self.update.feature_attributes(f.id, feature_attributes)

        # Post stats for features
        if trigger_stats:
            self.create.feature_set_stats(featureset.id)
        return self.get.feature_set(featureset.id)

    @track_usage
    def column_importance_stats(self, id: str, payload: api.feature.featureImportanceStats):
        """
        Sends a json payload of importance from a dataFrame to the API so it can render in the WebApp
        """
        # First update timestamp on the DF object
        self.dataframe(unique_id=id, update_date=payload.timestamp, if_exists='edit')
        return self.create.column_importance_stats(id, payload)

    @track_usage
    def feature_importance_stats(self, id: int, payload: api.feature.featureImportanceStats):
        """
        sends a JSON payload of importance from a collection to the API so it can store and render stats later
        """
        return self.create.feature_importance_stats(id=id, payload=payload)

    @track_usage
    def dataframe_profile(self, id: str, payload: api.feature.ColumnProfiles):
        """
        Send a json payload of a dataframe profile so it can render in the WebApp
        """
        # First update timestamp on the DF object
        self.dataframe(unique_id=id, update_date=payload.timestamp, if_exists='edit')
        return self.create.dataframe_profile(id, payload)