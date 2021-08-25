from datetime import datetime
from typing import *

import numpy as np
import pandas
import pendulum
import pyspark
from pyspark.sql import DataFrame
from pyspark.sql.utils import AnalysisException

import tecton
from tecton import conf
from tecton._internals import data_frame_helper
from tecton._internals import errors
from tecton._internals import feature_retrieval_internal
from tecton._internals import metadata_service
from tecton._internals import utils
from tecton._internals.errors import FV_INVALID_MOCK_INPUTS
from tecton._internals.feature_packages import aggregations
from tecton._internals.sdk_decorators import sdk_public_method
from tecton.feature_services.query_helper import _QueryHelper
from tecton.interactive.data_frame import FeatureVector
from tecton.interactive.dataset import Dataset
from tecton.interactive.feature_definition import FeatureDefinition
from tecton.interactive.feature_set_config import FeatureDefinitionAndJoinConfig
from tecton.tecton_context import TectonContext
from tecton_proto.args.pipeline_pb2 import PipelineNode
from tecton_proto.data import feature_view_pb2
from tecton_proto.metadataservice.metadata_service_pb2 import GetFeatureViewRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetServingStatusRequest
from tecton_spark import pipeline_helper
from tecton_spark.feature_package_view import FeaturePackageOrView
from tecton_spark.id_helper import IdHelper
from tecton_spark.logger import get_logger
from tecton_spark.materialization_params import MaterializationParams
from tecton_spark.pipeline_helper import find_request_context
from tecton_spark.pipeline_helper import pipeline_to_dataframe
from tecton_spark.pipeline_helper import run_mock_pandas_pipeline
from tecton_spark.transformation import RequestContext

logger = get_logger("FeatureView")


__all__ = ["FeatureView", "get_feature_view"]


class FeatureView(FeatureDefinition):
    """
    FeatureView class.

    To get a FeatureView instance, call :py:func:`tecton.get_feature_view`.
    """

    _proto: feature_view_pb2.FeatureView

    def __init__(self, proto):
        self._proto = proto

    @classmethod
    def _fco_type_name_singular_snake_case(cls) -> str:
        return "feature_view"

    @classmethod
    def _fco_type_name_plural_snake_case(cls) -> str:
        return "feature_views"

    def __str__(self):
        return f"FeatureView|{self.id}"

    def __repr__(self):
        return f"FeatureView(name='{self.name}')"

    @property  # type: ignore
    @sdk_public_method
    def features(self) -> List[str]:
        """
        Returns the names of the (output) features.
        """
        if self.is_temporal_aggregate:
            feature_names = [f.output_feature_name for f in self._proto.temporal_aggregate.features]
            return [f for f in feature_names if f != self.timestamp_key]

        return super().features

    def _online_transform_dataframe(
        self,
        spine: DataFrame,
        use_materialized_data: bool = True,
        namespace: Optional[str] = None,
    ) -> DataFrame:
        """
        Adds features from an OnDemandFeatureView to the spine.

        :param spine: Spark dataframe used to compute the on-demand features. Any dependent feature values must already be a part of the spine.
        :param use_materialized_data: (Optional) Use materialized data if materialization is enabled.

        :return: A spark dataframe containing the spine augmented with features. The features are prefixed by the namespace if it exists, or the FeatureView's name.
        """
        if not self.is_online:
            raise errors.TRANSFORMATION_DATAFRAME_ONLINE_ONLY

        df = pipeline_helper.dataframe_with_input(
            pipeline=self._proto.pipeline,
            spark=TectonContext.get_instance()._spark,
            input_df=spine,
            output_schema=self._materialization_schema.to_spark(),
            transformations=self._proto.enrichments.transformations,
            name=self.name,
            fv_id=self.id,
            namespace=namespace,
        )
        return df

    @sdk_public_method
    def run(self, **mock_inputs: Union[pandas.DataFrame, DataFrame]):
        """
        Runs the feature view against passed-in mock data rather than the actual data sources.

        :param mock_inputs: Dictionary with the same expected keys as the FeatureView's inputs parameter. Each input name maps to a Pandas DataFrame that should be evaluated for that node in the pipeline.
        """
        input_names = pipeline_helper.get_all_input_keys(self._proto.pipeline.root)
        if input_names != mock_inputs.keys():
            raise FV_INVALID_MOCK_INPUTS(mock_inputs.keys(), input_names)

        if self.is_online:
            return run_mock_pandas_pipeline(
                self._proto.pipeline, self._proto.enrichments.transformations, self.name, mock_inputs
            )
        else:
            tc = TectonContext.get_instance()
            spark = tc._spark
            return pipeline_to_dataframe(
                spark,
                pipeline=self._proto.pipeline,
                consume_streaming_data_sources=False,
                virtual_data_sources=[],
                transformations=self._proto.enrichments.transformations,
                feature_time_limits=None,
                schedule_interval=pendulum.Duration(
                    seconds=self._proto.materialization_params.schedule_interval.ToSeconds()
                ),
                mock_inputs=mock_inputs,
            )

    def _get_serving_status(self):
        request = GetServingStatusRequest()
        request.feature_package_id.CopyFrom(self._proto.feature_view_id)
        request.workspace = self.workspace
        return metadata_service.instance().GetServingStatus(request)

    @sdk_public_method
    def preview(self, limit=10, time_range: Optional[pendulum.Period] = None, use_materialized_data: bool = True):
        """
        Shows a preview of the FeatureView's features. Random, unique join_keys are chosen to showcase the features.

        :param limit: (Optional, default=10) The number of rows to preview
        :param time_range: (Optional) Time range to collect features from. Will default to recent data (past 2 days).
        :param use_materialized_data: (Optional) Use materialized data if materialization is enabled.
        :return: A Tecton :class:`DataFrame`.
        """
        if self.is_online:
            raise errors.FP_NOT_SUPPORTED_GET_FEATURE_DF

        try:
            pandas_df = (
                data_frame_helper._get_feature_dataframe_with_limits(
                    FeaturePackageOrView.of(self._proto),
                    spine=None,
                    spine_time_key=None,
                    spine_time_limits=time_range,
                    use_materialized_data=use_materialized_data,
                )
                .to_spark()
                .drop_duplicates(self.join_keys)
                .limit(limit)
                .toPandas()
            )
        except AnalysisException as e:
            if "Path does not exist:" in e.desc:
                raise errors.FD_PREVIEW_NO_MATERIALIZED_OFFLINE_DATA
            else:
                raise e

        if len(pandas_df) == 0:
            # spine_time_limits refers to the range of feature timestamps. Converting to the corresponding raw data time range.
            raw_data_time_limits = aggregations._get_time_limits(
                fpov=FeaturePackageOrView.of(self._proto), spine_df=None, spine_time_limits=time_range
            )
            time_range_type = "default" if time_range is None else "provided"
            logger.warn(
                f"No preview data could be generated because no data was found in the {time_range_type} "
                f"time range of {raw_data_time_limits}. To specify a different time range, set the parameter 'time_range'"
            )
        return tecton.interactive.data_frame.set_pandas_timezone_from_spark(pandas_df)

    def _assert_writes_to_offline_feature_store(self):
        if not self._writes_to_offline_feature_store:
            raise errors.FP_NEEDS_TO_BE_MATERIALIZED(self.name)

    def _should_infer_timestamp_of_spine(self, timestamp_key, spine):
        if timestamp_key is not None:
            return False
        if spine is None:
            return False
        if not self.is_online:
            return True
        # normally odfvs don't depend on a timestamp key except for when they have dependent fvs
        # in this case we want to infer the timestamp key of the spine
        if utils.get_num_dependent_fv(self._proto.pipeline.root, visited_inputs={}) > 0:
            return True
        return False

    @sdk_public_method
    def get_feature_dataframe(
        self,
        spine: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, None] = None,
        spine_time_key: str = None,
        use_materialized_data: bool = True,
        save: bool = None,
        save_as: str = None,
    ) -> "tecton.interactive.data_frame.DataFrame":
        """
        Returns a Tecton :class:`DataFrame` that contains the output Feature Transformation of the Feature View.

        :param spine: (Optional) The spine to join against, as a dataframe.
            If present, the returned data frame will contain rollups for all (join key, temporal key)
            combinations that are required to compute a full frame from the spine. If spine is not
            specified, it'll return a dataframe with sample feature vectors.
        :param spine_time_key: (Optional) Name of the time column in spine.
            If unspecified, will default to the time column of the spine if there is only one present.
        :param use_materialized_data: (Optional) Use materialized data if materialization is enabled
        :param save: (Optional) set to True to persist DataFrame as a Dataset object
        :param save_as: (Optional) name to save the DataFrame as. Not applicable when save=False.
            If unspecified and save=True, a name will be generated.
        :return: A Tecton :class:`DataFrame`.
        """
        from tecton.tecton_context import TectonContext
        from tecton.interactive.feature_set_config import FeatureSetConfig

        tc = TectonContext.get_instance()
        # TODO: be able to use self._get_feature_dataframe_with_limits directly
        # doing it this way for now to return timestamps provided by user rather than anchor times

        if self.is_online and spine is None:
            raise errors.FP_GET_FEATURE_DF_NO_SPINE

        if use_materialized_data and not self.is_online and not self._proto.materialization_enabled:
            raise errors.FD_GET_FEATURES_FROM_DISABLED_MATERIALIZATION(self.name, self.workspace)

        TectonContext.validate_spine_type(spine)

        timestamp_key = spine_time_key
        if self._should_infer_timestamp_of_spine(timestamp_key, spine):
            timestamp_key = utils.infer_timestamp(spine)

        fsc = FeatureSetConfig()
        fsc._add(FeaturePackageOrView.from_fv(self._proto))

        if self.is_online:
            inputs = _find_dependent_feature_set_items(
                self._proto.pipeline.root,
                visited_inputs={},
                fv_id=self.id,
            )
            fsc._definitions_and_configs = fsc._definitions_and_configs + inputs

        df = tc.execute(
            spine, feature_set_config=fsc, timestamp_key=timestamp_key, use_materialized_data=use_materialized_data
        )
        if save:
            return Dataset._create(
                df=df,
                save_as=save_as,
                feature_package_id=self.id,
                spine=spine,
                timestamp_key=timestamp_key,
            )
        return df

    @sdk_public_method
    def get_historical_features(
        self,
        spine: Optional[Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame]] = None,
        timestamp_key: str = None,
        start_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        end_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        entities: Optional[Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame]] = None,
        from_source: bool = False,
        save_dataset: bool = False,
        save_as: Optional[str] = None,
    ) -> "tecton.interactive.data_frame.DataFrame":
        """
        Returns a Tecton :class:`DataFrame` of historical values for this feature view.
        Either provide a spine to join against or set parameters start_time, end_time, and/or entities to specify which values to return.

        :param spine: (Optional) The spine to join against, as a dataframe.
            If present, the returned data frame will contain rollups for all (join key, temporal key)
            combinations that are required to compute a full frame from the spine. If spine is not
            specified, it'll return a dataframe of  feature values in the specified time range.
        :param timestamp_key: (Optional) Name of the time column in spine.
            If unspecified, will default to the time column of the spine if there is only one present.
        :param start_time: (Optional) The interval start time from when we want to retrieve features.
        :param end_time: (Optional) The interval end time until when we want to retrieve features.
        :param entities: (Optional) Filter feature data to a set of entity IDs.
            If specified, this DataFrame should only contain join key columns.
        :param from_source: Whether feature values should be recomputed from the original data source.
            If False, we will read the values from the materialized store.
        :param save_dataset: (Optional) set to True to persist DataFrame as a Dataset object.
        :param save_as: (Optional) name to save the DataFrame as. Not applicable when save=False.
            If unspecified and save=True, a name will be generated.
        :return: A Tecton :class:`DataFrame`.
        """
        return self._get_historical_features(
            spine, timestamp_key, start_time, end_time, entities, from_source, save_dataset, save_as
        )

    def _upload_df_spark(self, df_path: str, df: pyspark.sql.dataframe.DataFrame):
        df.write.parquet(df_path)

    @property
    def timestamp_key(self) -> Optional[str]:
        """
        Returns the timestamp_key column name of this FeatureView.
        """
        if self._proto.HasField("timestamp_key"):
            return self._proto.timestamp_key
        return None

    @property
    def is_temporal_aggregate(self):
        """
        Returns whether or not this FeatureView is of type TemporalAggregateFeatureView.
        """
        return self._proto.HasField("temporal_aggregate")

    @property
    def is_temporal(self):
        """
        Returns whether or not this FeatureView is of type TemporalFeatureView.
        """
        return self._proto.HasField("temporal")

    @property
    def is_online(self):
        """
        Returns whether or not this FeatureView is of type OnDemandFeatureView.
        """
        return self._proto.HasField("on_demand_feature_view")

    @property
    def _writes_to_offline_feature_store(self) -> bool:
        """
        Returns if the FeatureView materialization is enabled to write to the OfflineStore.
        Return value does not reflect the completion of any specific materialization job.
        """
        return self._proto.materialization_enabled and self._proto.materialization_params.writes_to_offline_store

    @property
    def _writes_to_online_feature_store(self) -> bool:
        """
        Returns if the FeatureView materialization is enabled to write to the OnlineStore.
        Return value does not reflect the completion of any specific materialization job.
        """
        return self._proto.materialization_enabled and self._proto.materialization_params.writes_to_online_store

    @property
    def _materialization_params(self) -> Optional[MaterializationParams]:
        return MaterializationParams.from_proto(self._proto)

    @property  # type: ignore
    @sdk_public_method
    def feature_start_time(self) -> Optional[pendulum.DateTime]:
        """
        This represents the time at which features are first available.
        """
        if not self._proto.HasField("materialization_params"):
            return None
        return pendulum.from_timestamp(self._proto.materialization_params.start_timestamp.ToSeconds())

    @property  # type: ignore
    @sdk_public_method
    def batch_materialization_schedule(self) -> Optional[pendulum.Duration]:
        """
        This represents how often we schedule batch materialization jobs.
        """
        if not self._proto.HasField("materialization_params"):
            return None
        # TODO: this should return a formatted duration, not a timestamp
        return pendulum.Duration(seconds=self._proto.materialization_params.schedule_interval.ToSeconds())

    @property  # type: ignore
    @sdk_public_method
    def schedule_offset(self) -> Optional[pendulum.Duration]:
        """
        If this attribute is non-empty, Tecton will schedule materialization jobs at an offset equal to this.
        """
        if not self._proto.HasField("materialization_params"):
            return None
        schedule_offset = pendulum.duration(
            seconds=self._proto.materialization_params.allowed_upstream_lateness.ToSeconds()
        )
        if not schedule_offset:
            return None
        return schedule_offset

    @property  # type: ignore
    @sdk_public_method
    def type(self):
        """
        Returns the FeatureView type.
        """
        if self.is_temporal:
            return "Temporal"
        elif self.is_temporal_aggregate:
            return "TemporalAggregate"
        elif self.is_online:
            return "OnDemand"
        else:
            # Should never happen
            raise errors.INTERNAL_ERROR(f"Invalid feature type for FeatureView {self.name}")

    @sdk_public_method
    def get_features(
        self,
        entities: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, None] = None,
        start_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        end_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        from_source: bool = False,
    ) -> "tecton.interactive.data_frame.DataFrame":
        """
        Returns all the feature values that are defined by this Feature View in the specified time range.

        :param entities: (Optional) Filter feature data to a set of entity IDs.
            If specified, this DataFrame should only contain join key columns.
        :param start_time: (Optional) The interval start time from when we want to retrieve features.
        :param end_time:  (Optional) The interval end time until when we want to retrieve features.
        :param from_source: Whether feature values should be recomputed from the original data source.
            If False, we will attempt to read the values from the materialized store.

        :return: A Tecton DataFrame with features values.
        """

        fpov = FeaturePackageOrView.of(self._proto)

        return feature_retrieval_internal.get_features(fpov, entities, start_time, end_time, from_source)

    @sdk_public_method
    def get_feature_vector(
        self,
        join_keys: Optional[Mapping[str, Union[int, np.int_, str, bytes]]] = None,
        include_join_keys_in_response: bool = False,
        request_context_map: Optional[Mapping[str, Union[int, np.int_, str, bytes, float]]] = None,
    ) -> FeatureVector:
        """
        Returns a single Tecton :class:`FeatureVector` from the Online Store.
        At least one of join_keys or request_context_map is required.

        :param join_keys: Join keys of the enclosed FeatureViews.
        :param include_join_keys_in_response: Whether to include join keys as part of the response FeatureVector.
        :param request_context_map: Dictionary of request context values.

        :return: A :class:`FeatureVector` of the results.
        """
        # doing checks here instead of get_online_features in order to provide the correct error messages
        if not self._writes_to_online_feature_store and not self.is_online:
            raise errors.UNSUPPORTED_OPERATION(
                "get_feature_vector", "online_serving_enabled is not set to True for this FeatureView."
            )
        if join_keys is None and request_context_map is None:
            raise errors.FS_GET_FEATURE_VECTOR_REQUIRED_ARGS
        return self.get_online_features(join_keys, include_join_keys_in_response, request_context_map)

    @sdk_public_method
    def get_online_features(
        self,
        join_keys: Optional[Mapping[str, Union[int, np.int_, str, bytes]]] = None,
        include_join_keys_in_response: bool = False,
        request_context_map: Optional[Mapping[str, Union[int, np.int_, str, bytes, float]]] = None,
    ) -> FeatureVector:
        """
        Returns a single Tecton :class:`FeatureVector` from the Online Store.
        At least one of join_keys or request_context_map is required.

        :param join_keys: Join keys of the enclosed FeatureViews.
        :param include_join_keys_in_response: Whether to include join keys as part of the response FeatureVector.
        :param request_context_map: Dictionary of request context values.

        :return: A :class:`FeatureVector` of the results.
        """
        if not self._writes_to_online_feature_store and not self.is_online:
            raise errors.UNSUPPORTED_OPERATION(
                "get_online_features", "online_serving_enabled is not set to True for this FeatureView."
            )
        if join_keys is None and request_context_map is None:
            raise errors.GET_ONLINE_FEATURES_REQUIRED_ARGS
        if join_keys is not None and not isinstance(join_keys, dict):
            raise errors.INVALID_JOIN_KEYS_TYPE(type(join_keys))
        if request_context_map is not None and not isinstance(request_context_map, dict):
            raise errors.INVALID_REQUEST_CONTEXT_TYPE(type(request_context_map))

        return _QueryHelper(self._proto.fco_metadata.workspace, feature_package_name=self.name).get_feature_vector(
            join_keys or {},
            include_join_keys_in_response,
            request_context_map or {},
            self._request_context,
        )

    @property
    def _request_context(self) -> Optional[RequestContext]:
        if self.is_online:
            rc = find_request_context(self._proto.pipeline.root)
            if rc is not None:
                return RequestContext._from_proto(rc)
            else:
                return RequestContext({})
        else:
            return RequestContext({})

    @property
    def _materialization_schema(self):
        from tecton_spark.schema import Schema

        return Schema(self._proto.schemas.materialization_schema)


@sdk_public_method
def get_feature_view(fv_reference: str, workspace_name: Optional[str] = None) -> FeatureView:
    """
    Fetch an existing :class:`FeatureView` by name.

    :param fv_reference: Either a name or a hexadecimal Feature View ID.
    :returns: :class:`BatchFeatureView`, :class:`BatchWindowAggregateFeatureView`,
        :class:`StreamFeatureView`, :class:`StreamWindowAggregateFeatureView`,
        or :class:`OnDemandFeatureView`.
    """
    request = GetFeatureViewRequest()
    request.version_specifier = fv_reference
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")
    response = metadata_service.instance().GetFeatureView(request)
    if not response.HasField("feature_view"):
        raise errors.FCO_NOT_FOUND(FeatureView, fv_reference)

    if response.feature_view.HasField("feature_table"):
        raise errors.FCO_NOT_FOUND_WRONG_TYPE(FeatureView, fv_reference, "get_feature_table")

    return FeatureView(response.feature_view)


def _find_dependent_feature_set_items(
    node: PipelineNode, visited_inputs: Mapping[str, bool], fv_id: str
) -> List[FeatureDefinitionAndJoinConfig]:
    if node.HasField("feature_view_node"):
        if node.feature_view_node.input_name in visited_inputs:
            return []
        visited_inputs[node.feature_view_node.input_name] = True

        from tecton import get_feature_view
        from tecton_spark.feature_package_view import FVBackedFeaturePackageOrView

        fv = get_feature_view(IdHelper.to_string(node.feature_view_node.feature_view_id))

        fpov = FVBackedFeaturePackageOrView(fv._proto)
        join_keys = []
        overrides = {
            colpair.feature_column: colpair.spine_column
            for colpair in node.feature_view_node.feature_view.override_join_keys
        }
        for join_key in fv._proto.join_keys:
            potentially_overriden_key = overrides.get(join_key, join_key)
            join_keys.append((potentially_overriden_key, join_key))
        cfg = FeatureDefinitionAndJoinConfig(
            definition=fpov,
            name=fv.name,
            join_keys=join_keys,
            namespace=f"_udf_internal_{node.feature_view_node.input_name}_{fv_id}",
            features=node.feature_view_node.feature_view.features or fpov.features,
        )

        return [cfg]
    elif node.HasField("transformation_node"):
        ret: List[FeatureDefinitionAndJoinConfig] = []
        for child in node.transformation_node.inputs:
            ret = ret + _find_dependent_feature_set_items(child.node, visited_inputs, fv_id)
        return ret
    return []
