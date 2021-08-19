from datetime import datetime
from datetime import timezone
from io import BytesIO
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pandas
import pendulum
import pyspark
import requests
from pyspark.sql.types import StructType
from pyspark.sql.utils import AnalysisException

import tecton.interactive.data_frame
from tecton import conf
from tecton._internals import data_frame_helper
from tecton._internals import errors
from tecton._internals import feature_retrieval_internal
from tecton._internals import metadata_service
from tecton._internals import utils
from tecton._internals.display import Displayable
from tecton._internals.feature_packages import aggregations
from tecton._internals.sdk_decorators import sdk_public_method
from tecton.fco import Fco
from tecton.feature_packages.aggregations import TrailingTimeWindowAggregationBuilder
from tecton.feature_packages.feature_package_args import FeatureAggregation
from tecton.feature_packages.temporal import Temporal
from tecton.feature_services.query_helper import _QueryHelper
from tecton.interactive.data_frame import FeatureVector
from tecton.interactive.dataset import Dataset
from tecton.interactive.transformation import Transformation
from tecton.tecton_context import TectonContext
from tecton_proto.common import column_type_pb2
from tecton_proto.data import feature_package_pb2
from tecton_proto.data.feature_package_pb2 import FeatureTransformation
from tecton_proto.data.materialization_status_pb2 import MaterializationStatus
from tecton_proto.metadataservice.metadata_service_pb2 import GetFeaturePackageRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetFeaturePackageSummaryRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetMaterializationStatusRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetNewIngestDataframeInfoRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetServingStatusRequest
from tecton_proto.metadataservice.metadata_service_pb2 import IngestDataframeRequest
from tecton_spark import feature_package_utils
from tecton_spark.feature_package_view import FeaturePackageOrView
from tecton_spark.id_helper import IdHelper
from tecton_spark.logger import get_logger
from tecton_spark.materialization_params import MaterializationParams
from tecton_spark.online_serving_index import OnlineServingIndex
from tecton_spark.schema import Schema
from tecton_spark.transformation import RequestContext

logger = get_logger("FeaturePackage")

__all__ = ["FeaturePackage", "get_feature_package"]

"""
NOTE: much of the code here is duplicated between this and feature_view.py, please change both.
"""


class FeaturePackage(Fco):
    """
    FeaturePackage class.

    To get a FeaturePackage instance, call :py:func:`tecton.get_feature_package`.
    """

    _feature_package: feature_package_pb2.FeaturePackage

    def __init__(self):
        """ Do not call this directly. Use :py:func:`tecton.get_feature_package` """

    def _init_with_proto(self, proto: feature_package_pb2.FeaturePackage):
        self._feature_package = proto
        self._proto = proto

    @classmethod
    def _from_proto(cls, fp_proto: feature_package_pb2.FeaturePackage) -> "FeaturePackage":
        feature_type = feature_package_utils.get_feature_type(fp_proto.feature_transformation)
        if feature_type:
            obj = FeaturePackage.__new__(cls)
            obj._init_with_proto(fp_proto)
            return obj
        else:
            raise errors.INTERNAL_ERROR(f"No feature type for FeaturePackage {fp_proto.fco_metadata.name}")

    @classmethod
    def _fco_type_name_singular_snake_case(cls) -> str:
        return "feature_package"

    @classmethod
    def _fco_type_name_plural_snake_case(cls) -> str:
        return "feature_packages"

    @property
    def _fco_metadata(self):
        return self._feature_package.fco_metadata

    @classmethod
    def _get_feature_store_start_time_from_materialization_start_time(
        cls,
        materialization_start_time: pendulum.DateTime,
        is_temporal_aggregate: bool,
        feature_transformation: FeatureTransformation,
    ) -> pendulum.DateTime:
        if is_temporal_aggregate:
            max_aggregation_window = pendulum.duration(
                seconds=feature_package_utils.get_max_aggregation_window(feature_transformation).ToSeconds()
            )
            return materialization_start_time + max_aggregation_window
        else:
            return materialization_start_time

    def __str__(self):
        return f"FeaturePackage|{self.id}"

    def __repr__(self):
        return f"FeaturePackage(name='{self.name}')"

    @property  # type: ignore
    @sdk_public_method
    def features(self) -> List[str]:
        """
        Returns the names of the (output) features of this feature package.
        """
        if self.is_temporal_aggregate and self._trailing_time_window_aggregation is not None:
            return self._trailing_time_window_aggregation.features
        elif self.is_online:
            return self._view_schema.column_names()
        return self._raw_features

    # Return 'raw' features coming out of view_sql
    @property
    def _raw_features(self):
        return FeaturePackage._raw_features_from_schema(self._view_schema, self.join_keys, self.timestamp_key)

    @staticmethod
    def _raw_features_from_schema(view_schema, join_keys, timestamp_key):
        return feature_package_utils.get_input_feature_columns(view_schema.to_proto(), join_keys, timestamp_key)

    def summary(self):
        """
        Returns various information about this FeaturePackage, including the most critical metadata such
        as the FeaturePackage's name, owner, features, etc.
        """
        request = GetFeaturePackageSummaryRequest()
        request.fco_locator.id.CopyFrom(self._feature_package.feature_package_id)
        request.fco_locator.workspace = self.workspace

        response = metadata_service.instance().GetFeaturePackageSummary(request)

        def value_formatter(key, value):
            if key == "featureStartTimeSeconds":
                t = datetime.fromtimestamp(int(value))
                return t.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
            return value

        return Displayable.from_fco_summary(response.fco_summary, value_formatter=value_formatter)

    def _get_serving_status(self):
        request = GetServingStatusRequest()
        request.feature_package_id.CopyFrom(self._feature_package.feature_package_id)
        request.workspace = self.workspace
        return metadata_service.instance().GetServingStatus(request)

    @sdk_public_method
    def materialization_status(
        self, verbose: bool = False, limit: int = 1000, sort_columns: Optional[str] = None, errors_only: bool = False
    ):
        """
        Displays materialization information for the FeaturePackage, which may include past and scheduled jobs,
        and job failures.

        This method returns different information depending on the type of FeaturePackage. It is not currently
        supported by class ``PushFeaturePackage`` or ``OnlineFeaturePackage``, as neither is materialized.

        :param verbose: If set to true, method will display additional low level materialization information,
            useful for debugging.
        :param sort_columns: A comma-seperated list of column names by which to sort the rows
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
        Returns MaterializationStatus proto for the FeaturePackage.
        """
        request = GetMaterializationStatusRequest()
        request.feature_package_id.CopyFrom(self._feature_package.feature_package_id)

        response = metadata_service.instance().GetMaterializationStatus(request)
        return response.materialization_status

    @sdk_public_method
    def preview(
        self, limit: int = 10, time_range: Optional[pendulum.Period] = None, use_materialized_data: bool = True
    ):
        """
        Shows a preview of the FeaturePackage's features. Random, unique join_keys are chosen to showcase the features.

        :param limit: (Optional, default=10) The number of rows to preview
        :param time_range: (Optional) Time range to collect features from. Will default to recent data (past 2 days).
        :param use_materialized_data: (Optional) Use materialized data if materialization is enabled
        :return: A Tecton :class:`DataFrame`.
        """

        if self.is_online:
            raise errors.FP_NOT_SUPPORTED_GET_FEATURE_DF

        try:
            pandas_df = (
                self._get_feature_dataframe_with_limits(
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
                fpov=FeaturePackageOrView.of(self._feature_package), spine_df=None, spine_time_limits=time_range
            )
            time_range_type = "default" if time_range is None else "provided"
            logger.warn(
                f"No preview data could be generated because no data was found in the {time_range_type} "
                f"time range of {raw_data_time_limits}. To specify a different time range, set the parameter 'time_range'"
            )
        return tecton.interactive.data_frame.set_pandas_timezone_from_spark(pandas_df)

    def _validate_and_return_use_materialized_data(self, use_materialized_data):
        if self.is_online:
            return False

        if use_materialized_data and not self._writes_to_offline_feature_store:
            logger.warning(
                "Calculating features from raw data source(s) since materialization to offline feature store is not enabled. This may "
                "result in slow feature computations."
            )
            if self._feature_package.fco_metadata.workspace in ["", "prod"]:
                logger.warning("Consider enabling materialization for faster feature computations")
            else:
                logger.warning("This is a non-production workspace where materialization is not supported")
            use_materialized_data = False

        return use_materialized_data

    def _assert_writes_to_offline_feature_store(self):
        if not self._writes_to_offline_feature_store:
            raise errors.FP_NEEDS_TO_BE_MATERIALIZED(self.name)

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
        Returns a Tecton :class:`DataFrame` that contains the output Feature Transformation of the package.

        :param spine: (Optional) The spine to join against, as a dataframe.
            If present, the returned data frame will contain rollups for all (join key, temporal key)
            combinations that are required to compute a full frame from the spine. If spine is not
            specified, it'll return a dataframe with sample feature vectors.
        :param spine_time_key: (Optional) Name of the time column in spine.
            If unspecified, will default to the name of the timestamp key of the feature package.
        :param use_materialized_data: (Optional) Use materialized data if materialization is enabled
        :param save: (Optional) set to True to persist DataFrame as a Dataset object
        :param save_as: (Optional) name to save the DataFrame as. not applicable when save=False.
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

        TectonContext.validate_spine_type(spine)

        timestamp_key = spine_time_key
        if timestamp_key is None and spine is not None and not self.is_online:
            timestamp_key = utils.infer_timestamp(spine)

        fsc = FeatureSetConfig()
        fsc._add(FeaturePackageOrView.from_fp(self._feature_package))

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

    def _get_feature_dataframe_with_limits(
        self,
        *,
        spine: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, None],
        spine_time_key: Optional[str],
        spine_time_limits: Optional[pendulum.Period],
        use_materialized_data: bool,
        wildcard_key_not_in_spine: bool = False,
        validate_time_key=True,
    ) -> "tecton.interactive.data_frame.DataFrame":
        """
        Returns a Tecton DataFrame that contains the output Feature Transformation of the package.

        :param spine: (Optional) The spine to join against, either as SQL string or a dataframe.
            If present, the returned data frame will contain rollups for all (join key, temporal key)
            combinations that are required to compute a full frame from the spine.
        :param spine_time_key: (Optional) Name of the time column in spine.
            If unspecified, will default to the time column of the spine if there is only one present.
        :param spine_time_limits: (Optional) Spine Time Bounds, precomputed by the caller.
        :param wildcard_key_not_in_spine: Whether or not the wildcard join_key is present in the spine.
            Defaults to False if spine is not specified or if FeaturePackage has no wildcard join_key.
        :return: A Tecton DataFrame.
        """
        return data_frame_helper._get_feature_dataframe_with_limits(
            FeaturePackageOrView.of(self._feature_package),
            spine=spine,
            spine_time_key=spine_time_key,
            spine_time_limits=spine_time_limits,
            use_materialized_data=use_materialized_data,
            wildcard_key_not_in_spine=wildcard_key_not_in_spine,
            validate_time_key=validate_time_key,
        )

    @sdk_public_method
    def ingest(self, df: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame]):
        """
        Ingests a Dataframe into a Push Feature Package. The method is not supported for other Feature Package types.

        :param df: The Dataframe to be ingested. Has to conform to the Feature Package schema.
        """
        if not self.is_push:
            raise errors.FP_PUSH_ONLY_METHOD

        get_upload_info_request = GetNewIngestDataframeInfoRequest()
        get_upload_info_request.feature_definition_id.CopyFrom(self._id_proto)
        upload_info_response = metadata_service.instance().GetNewIngestDataframeInfo(get_upload_info_request)
        df_path = upload_info_response.df_path
        upload_url = upload_info_response.signed_url_for_df_upload

        # We write in the native format and avoid converting Pandas <-> Spark due to partially incompatible
        # type system, in specifically missing Int in Pandas
        if isinstance(df, pyspark.sql.dataframe.DataFrame):
            self._upload_df_spark(df_path, df)
        else:
            self._check_types_and_upload_df_pandas(upload_url, df_path, df)

        ingest_request = IngestDataframeRequest()
        ingest_request.workspace = self.workspace
        ingest_request.feature_definition_id.CopyFrom(self._id_proto)
        ingest_request.df_path = df_path
        response = metadata_service.instance().IngestDataframe(ingest_request)

    def _check_types_and_upload_df_pandas(self, upload_url: str, df_path: str, df: pandas.DataFrame):
        """
        Since Pandas doesn't have Integer type, only Long, we automatically cast Long columns
        to Ints (when FP schema has the same column as Integer), while leaving rest of the types in place.
        """
        tc = TectonContext.get_instance()
        spark = tc._spark
        spark_df = spark.createDataFrame(df)
        df_columns = Schema.from_spark(spark_df.schema).column_name_types()
        fp_columns = self._view_schema.column_name_types()
        converted_columns = []
        converted_df_schema = StructType()
        for df_column in df_columns:
            if df_column[1] == "long" and (df_column[0], "integer") in fp_columns:
                converted_columns.append(df_column[0])
                converted_df_schema.add(df_column[0], "integer")
            else:
                converted_df_schema.add(df_column[0], df_column[1])

        if converted_columns:
            logger.warning(
                f"Tecton is casting field(s) {', '.join(converted_columns)} to type Integer (was type Long). "
                f"To remove this warning, use a Long type in the FeaturePackage schema."
            )
            converted_df = spark.createDataFrame(df, schema=converted_df_schema)
            self._upload_df_spark(df_path, converted_df)
        else:
            self._upload_df_pandas(upload_url, df)

    def _upload_df_pandas(self, upload_url: str, df: pandas.DataFrame):
        out_buffer = BytesIO()
        df.to_parquet(out_buffer, index=False)

        # Maximum 1GB per ingestion
        if out_buffer.__sizeof__() > 1000000000:
            raise errors.FP_PUSH_DF_TOO_LARGE

        r = requests.put(upload_url, data=out_buffer.getvalue())
        if r.status_code != 200:
            raise errors.FP_PUSH_UPLOAD_FAILED(r.reason)

    def _upload_df_spark(self, df_path: str, df: pyspark.sql.dataframe.DataFrame):
        df.write.parquet(df_path)

    @property
    def _view_schema(self):
        return Schema(self._feature_package.schemas.view_schema)

    @property
    def _materialization_schema(self):
        return Schema(self._feature_package.schemas.materialization_schema)

    @classmethod
    def _validate(cls, feature_transformation, view_schema: Schema):
        """Runs validity checks on the package definition, raising an error if any fail."""
        for join_key in feature_transformation.join_keys:
            column_type = view_schema.tecton_type(join_key)
            if column_type == column_type_pb2.COLUMN_TYPE_DOUBLE:
                raise errors.FLOATING_POINT_JOIN_KEY(join_key)

        for feature in FeaturePackage._raw_features_from_schema(
            view_schema,
            feature_transformation.join_keys,
            feature_package_utils.get_timestamp_key(feature_transformation.feature_type),
        ):
            column_type = view_schema.tecton_type(feature)

    @property  # type: ignore
    @sdk_public_method
    def entity_names(self) -> List[str]:
        """
        Returns a list of entity names for this feature package.
        """
        return [entity.fco_metadata.name for entity in self._feature_package.enrichments.entities]

    @property  # type: ignore
    @sdk_public_method
    def created_at(self) -> str:
        """
        Returns the creation date of the package.
        """
        return self._feature_package.fco_metadata.created_at.ToDatetime().strftime("%Y-%m-%d %H:%M:%S")

    @property
    def timestamp_key(self) -> str:
        """
        Returns the timestamp_key column name of this feature package
        """
        feature_type = feature_package_utils.get_feature_type(self._feature_package.feature_transformation)
        if feature_type:
            return feature_package_utils.get_timestamp_key(feature_type)
        else:
            raise ValueError("Unknown feature type; could not infer timestamp key")

    @property
    def is_temporal_aggregate(self):
        """
        Returns whether or not this FeaturePackage is of type TemporalAggregateFeaturePackage.
        """
        feature_type = feature_package_utils.get_feature_type(self._feature_package.feature_transformation)
        if feature_type:
            return feature_package_utils.is_temporal_aggregate(feature_type)
        else:
            return False

    @property
    def is_temporal(self):
        """
        Returns whether or not this FeaturePackage is of type TemporalFeaturePackage.
        """
        feature_type = feature_package_utils.get_feature_type(self._feature_package.feature_transformation)
        if feature_type:
            return feature_package_utils.is_temporal(feature_type)
        else:
            return False

    @property
    def is_online(self):
        """
        Returns whether or not this FeaturePackage is of type OnlineFeaturePackage.
        """
        feature_type = feature_package_utils.get_feature_type(self._feature_package.feature_transformation)
        return feature_package_utils.is_online(feature_type)

    @property
    def is_push(self):
        """
        Returns whether or not this FeaturePackage is of type PushFeaturePackage.
        """
        feature_type = feature_package_utils.get_feature_type(self._feature_package.feature_transformation)
        return feature_package_utils.is_push(feature_type)

    @property
    def _writes_to_offline_feature_store(self) -> bool:
        """
        Returns if the FeaturePackage materialization is enabled to write to the OfflineStore.
        Return value does not reflect the completion of any specific materialization job.
        """
        return (
            self._feature_package.materialization_enabled
            and self._feature_package.materialization_params.writes_to_offline_store
        )

    @property
    def _writes_to_online_feature_store(self) -> bool:
        """
        Returns if the FeaturePackage materialization is enabled to write to the OnlineStore.
        Return value does not reflect the completion of any specific materialization job.
        """
        return (
            self._feature_package.materialization_enabled
            and self._feature_package.materialization_params.writes_to_online_store
        )

    @property
    def join_keys(self) -> List[str]:
        """
        Returns the join key column names of this feature package
        """
        return list(self._feature_package.feature_transformation.join_keys)

    @property
    def wildcard_join_key(self) -> Optional[str]:
        """
        Returns a wildcard join key column name for the feature package if it exists;
        Otherwise returns None.
        """
        online_serving_index = self.online_serving_index
        wildcard_keys = [join_key for join_key in self.join_keys if join_key not in online_serving_index.join_keys]
        return wildcard_keys[0] if wildcard_keys else None

    @property
    def _materialization_params(self) -> Optional[MaterializationParams]:
        return MaterializationParams.from_proto(self._feature_package)

    @property
    def serving_ttl(self) -> Optional[pendulum.Duration]:
        """
        The duration that feature values will remain eligible for serving the offline store. This duration is respected in offline joins as well.
        """
        feature_type = feature_package_utils.get_feature_type(self._feature_package.feature_transformation)
        serving_ttl_proto = feature_package_utils.get_serving_ttl(feature_type)
        return pendulum.Duration(seconds=serving_ttl_proto.ToSeconds())

    @property
    def data_lookback(self) -> Optional[pendulum.Duration]:
        """
        The duration that Tecton will filter back in time when processing raw data.
        """
        if not self.is_temporal or self._temporal is None:
            return None
        return self._temporal.data_lookback

    @property
    def _trailing_time_window_aggregation(self) -> Optional[TrailingTimeWindowAggregationBuilder]:
        feature_type = feature_package_utils.get_feature_type(self._feature_package.feature_transformation)
        if feature_type is None or feature_package_utils.get_temporal_aggregation(feature_type) is None:
            return None
        return TrailingTimeWindowAggregationBuilder._from_feature_type_proto(feature_type)

    @property
    def _temporal(self) -> Optional[Temporal]:
        feature_type = feature_package_utils.get_feature_type(self._feature_package.feature_transformation)
        if feature_type is None or feature_package_utils.get_temporal(feature_type) is None:
            return None
        return Temporal._from_feature_type_proto(feature_type)

    @property  # type: ignore
    @sdk_public_method
    def id(self) -> str:
        """
        Returns the id of this feature package
        """
        return IdHelper.to_string(self._id_proto)

    @property
    def _id_proto(self):
        return self._feature_package.feature_package_id

    @property  # type: ignore
    @sdk_public_method
    def view_sql(self) -> Optional[str]:
        """
        Returns the SQL statement of this feature package.
        """
        if self._feature_package.feature_transformation.HasField("view_sql"):
            return self._feature_package.feature_transformation.view_sql
        else:
            return None

    @property  # type: ignore
    @sdk_public_method
    def aggregations(self) -> List[FeatureAggregation]:
        """
        Returns the list of all aggregations of this feature package.
        """
        feature_type = feature_package_utils.get_feature_type(self._feature_package.feature_transformation)
        temporal_aggregation = feature_package_utils.get_temporal_aggregation(feature_type)
        if not temporal_aggregation:
            return []
        result = []
        for feature in temporal_aggregation.features:
            feature_aggregation = FeatureAggregation(
                feature.input_feature_name,
                TrailingTimeWindowAggregationBuilder._get_aggregation_function_name(feature.function),
                str(pendulum.duration(seconds=feature.window.seconds)),
            )
            result.append(feature_aggregation)
        return result

    @property  # type: ignore
    @sdk_public_method
    def aggregation_slide_period(self) -> Optional[str]:
        """
        Frequency of Tecton updating the aggregations with new data.
        """
        feature_type = feature_package_utils.get_feature_type(self._feature_package.feature_transformation)
        temporal_aggregation = feature_package_utils.get_temporal_aggregation(feature_type)
        if not temporal_aggregation:
            return None
        return str(pendulum.duration(seconds=temporal_aggregation.aggregation_slide_period.seconds))

    @property  # type: ignore
    @sdk_public_method
    def feature_start_time(self) -> Optional[pendulum.DateTime]:
        if not self._feature_package.HasField("materialization_params"):
            return None
        return pendulum.from_timestamp(self._feature_package.materialization_params.start_timestamp.ToSeconds())

    @property  # type: ignore
    @sdk_public_method
    def feature_store_start_time(self) -> Optional[str]:
        """
        Legacy attribute. This represents the existing parameter ``feature_start_time``.
        """
        if not self._feature_package.HasField("materialization_params"):
            return None
        feature_store_start_time = self._get_feature_store_start_time_from_materialization_start_time(
            materialization_start_time=pendulum.from_timestamp(
                self._feature_package.materialization_params.start_timestamp.ToSeconds()
            ),
            is_temporal_aggregate=self.is_temporal_aggregate,
            feature_transformation=self._feature_package.feature_transformation,
        )
        return str(feature_store_start_time)

    @property  # type: ignore
    @sdk_public_method
    def batch_materialization_schedule(self) -> Optional[str]:
        """
        Legacy attribute. This represents the existing parameter ``schedule_interval``.
        """
        if not self._feature_package.HasField("materialization_params"):
            return None
        if self.is_temporal_aggregate:
            if not self._feature_package.materialization_params.HasField("batch_materialization_schedule"):
                feature_type = self._feature_package.feature_transformation.feature_type
                return str(
                    pendulum.duration(
                        seconds=feature_type.trailing_time_window_aggregation.aggregation_slide_period.ToSeconds()
                    )
                )
            else:
                batch_materialization_schedule = pendulum.duration(
                    seconds=self._feature_package.materialization_params.batch_materialization_schedule.ToSeconds()
                )
                return str(batch_materialization_schedule)
        elif self.is_temporal:
            batch_materialization_schedule = pendulum.duration(
                seconds=self._feature_package.materialization_params.batch_materialization_schedule.ToSeconds()
            )
            return str(batch_materialization_schedule)

        return None

    @property  # type: ignore
    @sdk_public_method
    def schedule_offset(self) -> Optional[str]:
        """
        If this attribute exists, Tecton will schedule materialization jobs at an offset equal to this.
        """
        if not self._feature_package.HasField("materialization_params"):
            return None
        schedule_offset = pendulum.duration(
            seconds=self._feature_package.materialization_params.allowed_upstream_lateness.ToSeconds()
        )
        if not schedule_offset:
            return None
        return str(schedule_offset)

    @property  # type: ignore
    @sdk_public_method
    def online_serving_index(self) -> OnlineServingIndex:
        """
        Returns Defines the set of join keys that will be indexed and queryable during online serving.
        Defaults to the complete join key.
        """
        return OnlineServingIndex.from_proto(self._feature_package.online_serving_index)

    @property  # type: ignore
    @sdk_public_method
    def final_transformation(self) -> Optional[Transformation]:
        """
        Returns the final Transformation associated with this FeaturePackage.
        """
        if not self._feature_package.feature_transformation.HasField("final_transformation_id"):
            return None

        return Transformation._from_proto_and_deps(
            self._feature_package.feature_transformation.final_transformation_id,
            self._feature_package.enrichments.transformations,
            self._feature_package.enrichments.virtual_data_sources,
        )

    @property  # type: ignore
    @sdk_public_method
    def type(self) -> str:
        """
        Returns the FeaturePackage type.
        """
        feature_type = feature_package_utils.get_feature_type(self._feature_package.feature_transformation)
        if feature_type is not None:
            if feature_package_utils.is_temporal(feature_type):
                return "Temporal"
            if feature_package_utils.is_temporal_aggregate(feature_type):
                return "TemporalAggregate"
            if feature_package_utils.is_online(feature_type):
                return "Online"
            if feature_package_utils.is_push(feature_type):
                return "Push"
        # Should never happen
        raise errors.INTERNAL_ERROR(f"Invalid feature type for FeaturePackage {self.name}")

    @property  # type: ignore
    @sdk_public_method
    def url(self) -> str:
        """
        Returns a link to the Tecton Web UI for this FeaturePackage.
        """
        return self._feature_package.enrichments.web_url

    @sdk_public_method
    def get_features(
        self,
        entities: Union[pyspark.sql.dataframe.DataFrame, pandas.DataFrame, None] = None,
        start_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        end_time: Optional[Union[pendulum.DateTime, datetime]] = None,
        from_source: bool = False,
    ) -> "tecton.interactive.data_frame.DataFrame":
        """
        Gets all features that are defined by this Feature Package. These features are read from the offline store,
        or using offline feature computation.

        :param entities: (Optional) A DataFrame that used to filter down FeatureValues.
            If specified, this DataFrame if specified should only contain join key columns.
        :param start_time: (Optional) The interval start time from when we want to retrieve features.
        :param end_time:  (Optional) The interval end time until when we want to retrieve features
        :param from_source: Whether we should compute feature values on the fly from data sources.
            If False, we will attempt to read the values from the materialized store.

        :return: A Tecton DataFrame with features values.
        """

        from_source = not self._validate_and_return_use_materialized_data(not from_source)
        fpov = FeaturePackageOrView.of(self._feature_package)

        return feature_retrieval_internal.get_features(fpov, entities, start_time, end_time, from_source)

    @sdk_public_method
    def get_feature_vector(
        self,
        join_keys: Optional[Dict[str, Union[int, str, bytes]]] = None,
        include_join_keys_in_response: bool = False,
        request_context_map: Optional[Dict[str, Union[int, str, bytes, float]]] = None,
    ) -> FeatureVector:
        """
        Returns a single Tecton :class:`FeatureVector` from the Online Store.
        At least one of join_keys or request_context_map is required.

        :param join_keys: Join keys of the enclosed FeaturePackages.
        :param include_join_keys_in_response: Whether to include join keys as part of the response FeatureVector.
        :param request_context_map: Dictionary of request context values.

        :return: A :class:`FeatureVector` of the results.
        """
        if not self._feature_package.materialization_params.writes_to_online_store and not self.is_online:
            raise errors.UNSUPPORTED_OPERATION(
                "get_feature_vector", "online_serving_enabled was not defined for this Feature Package."
            )
        if join_keys is None and request_context_map is None:
            raise errors.FS_GET_FEATURE_VECTOR_REQUIRED_ARGS
        if join_keys is not None and not isinstance(join_keys, dict):
            raise errors.INVALID_JOIN_KEYS_TYPE(type(join_keys))
        if request_context_map is not None and not isinstance(request_context_map, dict):
            raise errors.INVALID_REQUEST_CONTEXT_TYPE(type(request_context_map))

        if not self._feature_package.feature_transformation.final_transformation_id:
            raise errors.UNSUPPORTED_OPERATION(
                "get_feature_vector", "No Feature Transformation was defined for this Feature Package."
            )
        return _QueryHelper(
            self._feature_package.fco_metadata.workspace, feature_package_name=self.name
        ).get_feature_vector(
            join_keys or {},
            include_join_keys_in_response,
            request_context_map or {},
            self._request_context,
        )

    @property
    def _request_context(self):
        if self.is_online:
            return RequestContext._from_proto(self.final_transformation._transformation_proto.request_context)
        else:
            return None


@sdk_public_method
def get_feature_package(package_reference: str, workspace_name: Optional[str] = None) -> FeaturePackage:
    """
    Fetch an existing :class:`FeaturePackage` by name.

    :param package_reference: Either a name or a hexadecimal feature package ID.
    :returns: :class:`TemporalFeaturePackage`, :class:`TemporalAggregateFeaturePackage`, or :class:`OnlineFeaturePackage`.
    """
    request = GetFeaturePackageRequest()
    request.version_specifier = package_reference
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")
    response = metadata_service.instance().GetFeaturePackage(request)
    if not response.HasField("feature_package"):
        raise errors.FCO_NOT_FOUND(FeaturePackage, package_reference)

    return FeaturePackage._from_proto(response.feature_package)
