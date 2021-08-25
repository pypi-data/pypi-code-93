from abc import abstractmethod
from datetime import datetime
from datetime import timezone
from typing import List
from typing import Optional
from typing import Union

import pandas as pd
import pendulum
from pyspark.sql import DataFrame as pysparkDF

from tecton._internals import data_frame_helper
from tecton._internals import errors
from tecton._internals import metadata_service
from tecton._internals import utils
from tecton._internals.display import Displayable
from tecton._internals.feature_retrieval_internal import get_features
from tecton._internals.sdk_decorators import sdk_public_method
from tecton.fco import Fco
from tecton.interactive.data_frame import DataFrame
from tecton.interactive.dataset import Dataset
from tecton.interactive.feature_set_config import FeatureSetConfig
from tecton.tecton_context import TectonContext
from tecton_proto.data.materialization_status_pb2 import MaterializationStatus
from tecton_proto.metadataservice.metadata_service_pb2 import GetFeatureViewSummaryRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetMaterializationStatusRequest
from tecton_spark.feature_package_view import FeaturePackageOrView
from tecton_spark.feature_package_view import FVBackedFeaturePackageOrView
from tecton_spark.id_helper import IdHelper
from tecton_spark.online_serving_index import OnlineServingIndex
from tecton_spark.schema import Schema


class FeatureDefinition(Fco):
    @property
    def _fco_metadata(self):
        return self._proto.fco_metadata

    @property
    def _view_schema(self):
        return Schema(self._proto.schemas.view_schema)

    @property
    def _materialization_schema(self):
        return Schema(self._proto.schemas.materialization_schema)

    @property
    def _id_proto(self):
        return self._proto.feature_view_id

    @property  # type: ignore
    @sdk_public_method
    def id(self) -> str:
        """
        Returns the id of this object
        """
        return IdHelper.to_string(self._id_proto)

    @property
    def join_keys(self) -> List[str]:
        """
        Returns the join key column names
        """
        return list(self._proto.join_keys)

    @property  # type: ignore
    @sdk_public_method
    def online_serving_index(self) -> OnlineServingIndex:
        """
        Returns Defines the set of join keys that will be indexed and queryable during online serving.
        Defaults to the complete join key.
        """
        return OnlineServingIndex.from_proto(self._proto.online_serving_index)

    @property
    def wildcard_join_key(self) -> Optional[str]:
        """
        Returns a wildcard join key column name if it exists;
        Otherwise returns None.
        """
        online_serving_index = self.online_serving_index
        wildcard_keys = [join_key for join_key in self.join_keys if join_key not in online_serving_index.join_keys]
        return wildcard_keys[0] if wildcard_keys else None

    @property  # type: ignore
    @sdk_public_method
    def entity_names(self) -> List[str]:
        """
        Returns a list of entity names.
        """
        return [entity.fco_metadata.name for entity in self._proto.enrichments.entities]

    @property  # type: ignore
    @sdk_public_method
    def features(self) -> List[str]:
        """
        Returns the names of the (output) features.
        """
        join_keys = self.join_keys
        timestamp_key = self.timestamp_key
        return [
            col_name
            for col_name in self._view_schema.column_names()
            if col_name not in join_keys and col_name != timestamp_key
        ]

    @property  # type: ignore
    @sdk_public_method
    @abstractmethod
    def type(self):
        """
        Returns the feature definition type.
        """
        raise NotImplementedError()

    @property  # type: ignore
    @sdk_public_method
    def url(self) -> str:
        """
        Returns a link to the Tecton Web UI.
        """
        return self._proto.enrichments.web_url

    @sdk_public_method
    def summary(self) -> Displayable:
        """
        Returns various information about this feature definition, including the most critical metadata such
        as the name, owner, features, etc.
        """
        request = GetFeatureViewSummaryRequest()
        request.fco_locator.id.CopyFrom(self._id_proto)
        request.fco_locator.workspace = self.workspace

        response = metadata_service.instance().GetFeatureViewSummary(request)

        def value_formatter(key, value):
            if key == "featureStartTimeSeconds":
                t = datetime.fromtimestamp(int(value))
                return t.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
            return value

        return Displayable.from_fco_summary(response.fco_summary, value_formatter=value_formatter)

    def _point_in_time_join(
        self, spine: Union[pysparkDF, pd.DataFrame], timestamp_key: str, from_source: bool
    ) -> DataFrame:
        if (
            not from_source
            and not self._proto.HasField("on_demand_feature_view")
            and not self._proto.materialization_enabled
        ):
            raise errors.FD_GET_FEATURES_FROM_DISABLED_MATERIALIZATION(self.name, self.workspace)

        spark = TectonContext.get_instance()._spark
        if isinstance(spine, pd.DataFrame):
            spine = spark.createDataFrame(spine)
        utils.validate_spine_dataframe(spine, timestamp_key)

        feature_set_config = FeatureSetConfig()
        feature_set_config._add(FVBackedFeaturePackageOrView(self._proto))

        df = data_frame_helper.get_features_for_spine(
            spark, spine, feature_set_config, timestamp_key=timestamp_key, from_source=from_source
        )
        return DataFrame._create(df)

    def _get_historical_features(
        self,
        spine: Optional[Union[pysparkDF, pd.DataFrame]],
        timestamp_key: Optional[str],
        start_time: Optional[Union[pendulum.DateTime, datetime]],
        end_time: Optional[Union[pendulum.DateTime, datetime]],
        entities: Optional[Union[pysparkDF, pd.DataFrame]],
        from_source: bool,
        save_dataset: bool,
        save_as: Optional[str],
    ) -> DataFrame:
        has_point_in_time_join_params = spine is not None
        has_get_features_params = start_time is not None or end_time is not None or entities is not None

        if has_point_in_time_join_params:
            if has_get_features_params:
                raise errors.GET_HISTORICAL_FEATURES_WRONG_PARAMS(
                    ["start_time", "end_time", "entities"], "the spine parameter is provided"
                )
            timestamp_key = timestamp_key or utils.infer_timestamp(spine)
            df = self._point_in_time_join(spine, timestamp_key, from_source)
        else:
            if timestamp_key is not None:
                raise errors.GET_HISTORICAL_FEATURES_WRONG_PARAMS(
                    ["timestamp_key"], "the spine parameter is not provided"
                )
            fpov = FeaturePackageOrView.of(self._proto)
            df = get_features(
                fpov,
                start_time=start_time,
                end_time=end_time,
                entities=entities,
                from_source=from_source,
                is_read_api=True,
            )

        if save_dataset:
            return Dataset._create(
                df=df,
                save_as=save_as,
                feature_package_id=self.id,
                spine=spine,
                timestamp_key=timestamp_key,
            )
        return df

    @sdk_public_method
    def materialization_status(self, verbose=False, limit=1000, sort_columns=None, errors_only=False):
        """
        Displays materialization information for the FeatureView, which may include past jobs, scheduled jobs,
        and job failures.

        This method returns different information depending on the type of FeatureView. It is not currently
        supported by :class:`OnDemandFeatureView`, as it does not involve materialization.

        :param verbose: If set to true, method will display additional low level materialization information,
            useful for debugging.
        :param sort_columns: A comma-separated list of column names by which to sort the rows
        """
        materialization_attempts = self._get_materialization_status().materialization_attempts
        column_names, materialization_status_rows = utils.format_materialization_attempts(
            materialization_attempts, verbose, limit, sort_columns, errors_only
        )

        print("All the displayed times are in UTC time zone")

        # Setting `max_width=0` creates a table with an unlimited width.
        table = Displayable.from_items(headings=column_names, items=materialization_status_rows, max_width=0)
        # Align columns in the middle horizontally
        table._text_table.set_cols_align(["c" for _ in range(len(column_names))])

        return table

    def _get_materialization_status(self) -> MaterializationStatus:
        """
        Returns MaterializationStatus proto for the FeatureView.
        """
        request = GetMaterializationStatusRequest()
        request.feature_package_id.CopyFrom(self._id_proto)

        response = metadata_service.instance().GetMaterializationStatus(request)
        return response.materialization_status
