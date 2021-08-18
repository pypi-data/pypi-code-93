from typing import List, Optional

from .error import APIError
from pyrasgo import schemas as api
from pyrasgo.primitives import Collection, Feature, FeatureList, FeatureSet, DataSource
from pyrasgo.schemas.enums import Granularity, ModelType
from pyrasgo.utils import track_usage


class Match():

    def __init__(self):
        from .connection import Connection
        from pyrasgo.config import get_session_api_key

        api_key = get_session_api_key()
        self.api = Connection(api_key=api_key)

    @track_usage
    def data_source(self, fqtn: str) -> DataSource:
        """
        Returns the first Data Source that matches the specified name
        """
        try:
            response = self.api._get(f"/data-source", {"table": fqtn}, api_version=1).json()
            return DataSource(api_object=response[0])
        except:
            return None

    @track_usage
    def dataframe(self, name: str = None, unique_id: str = None) -> api.Dataframe:
        """
        Returns the first Dataframe that matches the specified name or uid
        """
        try:
            if name:
                response = self.api._get(f"/dataframes", {"name": name}, api_version=1).json()
                return api.Dataframe(**response[0])
            elif unique_id:
                response = self.api._get(f"/dataframes/{unique_id}", api_version=1).json()
                return api.Dataframe(**response)
        except:
            return None
        return None

    @track_usage
    def dimensionality(self, granularity: str) -> api.Dimensionality:
        """
        Returns the first community or private Dimensionality that matches the specified granularity
        """
        try:
            response = self.api._get(f"/dimensionalities/granularity/{granularity}", api_version=1).json()
            return api.Dimensionality(**response)
        except:
            return None

    @track_usage
    def column(self, name: str, feature_set_id: int) -> Optional[api.Column]:
        """
        Returns the first Column matching the specidied name in the specified featureset
        """
        try:
            cols = self.api._get(f"/columns/by-featureset/{feature_set_id}", api_version=1).json()
            for c in cols:
                if name == c["name"]:
                    return api.Column(**c)
            return None
        except:
            return None

    @track_usage
    def feature(self, code: str, feature_set_id: int) -> Optional[Feature]:
        """
        Returns the first Feature matching the specified name in the specified featureset
        """
        try:
            features = self.api._get(f"/features/by-featureset/{feature_set_id}", api_version=1).json()
            for f in features:
                if code == f["code"]:
                    return Feature(api_object=f)
            return None
        except:
            return None

    @track_usage
    def feature_set(self, table_name: Optional[str] = None, source_id: int = None) -> Optional[FeatureSet]:
        """
        Returns the first FeatureSet matching the specified table name
        """
        try:
            if table_name:
                fs = self.api._get(f"/feature-sets/", {"source_table": table_name}, api_version=1).json()
            elif source_id:
                fs = self.api._get(f"/feature-sets/", {"source_id": source_id}, api_version=1).json()
            return FeatureSet(api_object=fs[0])
        except:
            return None