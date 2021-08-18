from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import attr
import pendulum
from pyspark.sql import DataFrame
from pyspark.sql import functions
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import BooleanType

from tecton_proto.args.pipeline_pb2 import Pipeline
from tecton_proto.data.feature_package_pb2 import FeaturePackage
from tecton_proto.data.feature_package_pb2 import FeatureTransformation
from tecton_proto.data.feature_view_pb2 import FeatureView
from tecton_proto.data.feature_view_pb2 import NewTemporalAggregate
from tecton_proto.data.new_transformation_pb2 import NewTransformation
from tecton_proto.data.transformation_pb2 import Transformation
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource
from tecton_spark import data_source_helper
from tecton_spark import feature_package_utils
from tecton_spark import schema
from tecton_spark import time_utils
from tecton_spark import transformation_helper
from tecton_spark.errors import TectonFeatureTimeError
from tecton_spark.feature_package_view import FeaturePackageOrView
from tecton_spark.feature_package_view import FPBackedFeaturePackageOrView
from tecton_spark.materialization_common import MaterializationContext
from tecton_spark.partial_aggregations import construct_partial_time_aggregation_df
from tecton_spark.partial_aggregations import TEMPORAL_ANCHOR_COLUMN_NAME
from tecton_spark.pipeline_helper import pipeline_to_dataframe
from tecton_spark.time_utils import convert_timedelta_for_version
from tecton_spark.time_utils import convert_timestamp_to_epoch
from tecton_spark.transformation import TransformationDataProtoDAG

MATERIALIZED_RAW_DATA_END_TIME = "_materialized_raw_data_end_time"


@attr.s(auto_attribs=True)
class MaterializationPlan(object):
    offline_store_data_frame: Optional[DataFrame]
    online_store_data_frame: Optional[DataFrame]
    # should be the most recent ancestor of both online and offline so we can cache both of them easily
    base_data_frame: Optional[DataFrame]
    coalesce: int


def get_batch_materialization_plan(
    *,
    spark: SparkSession,
    feature_package_or_view: FeaturePackageOrView,
    raw_data_time_limits: Optional[pendulum.Period],
    coalesce: int,
    vds_proto_map: Dict[str, VirtualDataSource],
    transformation_id2proto: Dict[str, Transformation],
    called_for_online_feature_store: bool = False,
    called_for_schema_computation: bool = False,
    new_transformations: Optional[List[NewTransformation]] = None,
    schedule_interval: Optional[pendulum.Duration] = None,
    # TODO(FV3-cleanup): Remove after the migration
    DO_NOT_USE_vds_df_override_for_fv: Optional[DataFrame] = None,
) -> MaterializationPlan:
    """
    NOTE: We rely on Spark's lazy evaluation model to infer partially materialized tile Schema during FeaturePackage
    creation time without actually performing any materialization.
    Please make sure to not perform any Spark operations under this function's code path that will actually execute
    the Spark query (e.g: df.count(), df.show(), etc.).
    """

    if feature_package_or_view.is_feature_view:
        if feature_package_or_view.is_temporal_aggregate:
            return _get_batch_materialization_plan_for_aggregate_feature_view(
                spark,
                feature_package_or_view,
                False,
                raw_data_time_limits,
                list(vds_proto_map.values()),
                new_transformations or [],
                coalesce,
                called_for_schema_computation,
                schedule_interval=schedule_interval,
                DO_NOT_USE_vds_df_override_for_fv=DO_NOT_USE_vds_df_override_for_fv,
            )
        elif feature_package_or_view.is_temporal:
            assert raw_data_time_limits is not None
            return _get_batch_materialization_plan_for_temporal_feature_view(
                spark,
                feature_package_or_view,
                False,
                raw_data_time_limits,
                list(vds_proto_map.values()),
                new_transformations or [],
                coalesce,
                called_for_online_feature_store,
                called_for_schema_computation,
                schedule_interval=schedule_interval,
                DO_NOT_USE_vds_df_override_for_fv=DO_NOT_USE_vds_df_override_for_fv,
            )
        else:
            raise ValueError(f"Unhandled feature view: {feature_package_or_view.fv}")
    else:
        # We're dealing with feature packages
        is_temporal_aggregate = feature_package_or_view.is_temporal_aggregate
        feature_package = feature_package_or_view.fp
        if is_temporal_aggregate:
            return _get_batch_materialization_plan_for_TAFP(
                spark, feature_package, raw_data_time_limits, coalesce, vds_proto_map, transformation_id2proto
            )
        else:
            return _get_batch_materialization_plan_for_TFP(
                spark,
                feature_package,
                raw_data_time_limits,
                coalesce,
                vds_proto_map,
                transformation_id2proto,
                called_for_online_feature_store,
                called_for_schema_computation,
            )


def _get_batch_materialization_plan_for_aggregate_feature_view(
    spark: SparkSession,
    feature_package_or_view: FeaturePackageOrView,
    consume_streaming_data_sources: bool,
    raw_data_time_limits: Optional[pendulum.Period],
    virtual_data_sources: List[VirtualDataSource],
    transformations: List[NewTransformation],
    coalesce: int,
    called_for_schema_computation: bool,
    schedule_interval: Optional[pendulum.Duration] = None,
    DO_NOT_USE_vds_df_override_for_fv: Optional[DataFrame] = None,
) -> MaterializationPlan:
    df = pipeline_to_dataframe(
        spark,
        feature_package_or_view.fv.pipeline,
        consume_streaming_data_sources,
        virtual_data_sources,
        transformations,
        feature_time_limits=raw_data_time_limits,
        schedule_interval=schedule_interval,
        DO_NOT_USE_vds_df_override=DO_NOT_USE_vds_df_override_for_fv,
        called_for_schema_computation=called_for_schema_computation,
    )
    vds_proto_map = data_source_helper.get_vds_proto_map(virtual_data_sources)
    timestamp_key = feature_package_or_view.timestamp_key
    spark_df = _possibly_apply_feature_time_limits(df, raw_data_time_limits, vds_proto_map, timestamp_key, True)

    trailing_time_window_aggregation = feature_package_or_view.trailing_time_window_aggregation
    online_store_df = offline_store_df = underlying_df = construct_partial_time_aggregation_df(
        spark_df,
        list(feature_package_or_view.join_keys),
        trailing_time_window_aggregation,
        feature_package_or_view.get_feature_store_format_version,
    )

    return MaterializationPlan(offline_store_df, online_store_df, underlying_df, coalesce)


def _get_batch_materialization_plan_for_temporal_feature_view(
    spark: SparkSession,
    fpov: FeaturePackageOrView,
    consume_streaming_data_sources: bool,
    raw_data_time_limits: pendulum.Period,
    virtual_data_sources: List[VirtualDataSource],
    transformations: List[NewTransformation],
    coalesce: int,
    called_for_online_feature_store: bool,
    called_for_schema_computation: bool,
    schedule_interval: Optional[pendulum.Duration] = None,
    DO_NOT_USE_vds_df_override_for_fv: Optional[DataFrame] = None,
):
    vds_proto_map = data_source_helper.get_vds_proto_map(virtual_data_sources)

    offline_store_df, online_store_df, underlying_df = _materialize_interval_for_temporal_feature_view(
        spark,
        fpov,
        raw_data_time_limits,
        vds_proto_map,
        transformations,
        called_for_online_feature_store,
        consume_streaming_data_sources,
        called_for_schema_computation,
        schedule_interval=schedule_interval,
        DO_NOT_USE_vds_df_override_for_fv=DO_NOT_USE_vds_df_override_for_fv,
    )

    return MaterializationPlan(offline_store_df, online_store_df, underlying_df, coalesce)


def _get_batch_materialization_plan_for_TAFP(
    spark: SparkSession,
    feature_package: FeaturePackage,
    raw_data_time_limits: Optional[pendulum.Period],
    coalesce: int,
    vds_proto_map: Dict[str, VirtualDataSource],
    transformation_id2proto: Dict[str, Transformation],
) -> MaterializationPlan:
    feature_transformation = feature_package.feature_transformation
    if feature_transformation.HasField("final_transformation_id"):
        vds_id2proto = data_source_helper.get_vds_id2proto_map(vds_proto_map.values())
        spark_df = _transformation_dag_to_df(
            spark, MaterializationContext.default(), feature_transformation, transformation_id2proto, vds_id2proto
        )
    else:
        # Deprecated! SQLTransformation should be used in view_sql.
        spark_df = spark.sql(feature_transformation.view_sql)

    feature_type = feature_package_utils.get_feature_type(feature_transformation)
    timestamp_key = feature_package_utils.get_timestamp_key(feature_type)
    spark_df = _possibly_apply_feature_time_limits(spark_df, raw_data_time_limits, vds_proto_map, timestamp_key, False)

    online_store_df = offline_store_df = construct_partial_time_aggregation_df(
        spark_df,
        list(feature_transformation.join_keys),
        feature_package_utils.get_temporal_aggregation(feature_type),
        feature_package_utils.get_feature_store_format_version(feature_package),
    )

    return MaterializationPlan(offline_store_df, online_store_df, None, coalesce)


def _get_batch_materialization_plan_for_TFP(
    spark: SparkSession,
    feature_package: FeaturePackage,
    raw_data_time_limits: Optional[pendulum.Period],
    coalesce: int,
    vds_proto_map: Dict[str, VirtualDataSource],
    transformation_id2proto: Dict[str, Transformation],
    called_for_online_feature_store: bool,
    called_for_schema_computation: bool,
) -> MaterializationPlan:
    """
    TODO: For TFPs with only row level transformations, we can materialize multiple tiles
    using a single global temp view and Spark Window-ing function, as long as we validate in SDK that
    those TFPs are not depended on `context` parameter.
    """

    assert (
        called_for_schema_computation or raw_data_time_limits is not None
    ), "Specifying `raw_data_time_limits` is required for generating materialization query"

    tile_count = _get_tile_count_for_TFP(feature_package, raw_data_time_limits)

    if called_for_schema_computation or tile_count <= 1:
        offline_store_df, online_store_df = _materialize_single_tile_for_TFP(
            spark,
            feature_package,
            raw_data_time_limits,
            vds_proto_map,
            transformation_id2proto,
            called_for_online_feature_store,
        )
    else:
        offline_store_df, online_store_df = _materialize_multiple_tiles_for_TFP(
            spark,
            feature_package,
            raw_data_time_limits,
            tile_count,
            vds_proto_map,
            transformation_id2proto,
            called_for_online_feature_store,
        )

    return MaterializationPlan(offline_store_df, online_store_df, None, coalesce)


def _get_tile_count_for_TFP(feature_package: FeaturePackage, raw_data_time_limits: Optional[pendulum.Period]) -> int:
    if raw_data_time_limits is None:
        return 0

    tile_length_secs = feature_package_utils.get_tile_interval(feature_package).seconds
    batch_schedule_secs = feature_package_utils.get_batch_materialization_schedule(feature_package).seconds
    raw_data_range_secs = raw_data_time_limits.in_seconds()

    if (raw_data_range_secs - tile_length_secs) % batch_schedule_secs != 0:
        raise RuntimeError(
            f"`raw_data_range_secs - tile_length` ({raw_data_range_secs} - {tile_length_secs}) "
            f"must be divisible by the `batch_schedule_secs` ({batch_schedule_secs})."
        )
    if raw_data_time_limits.end.int_timestamp % batch_schedule_secs != 0:
        raise RuntimeError(
            f"`raw_data_time_limits.end.int_timestamp` ({raw_data_time_limits.end.int_timestamp}) "
            f"must be divisible by the `batch_schedule_secs` ({batch_schedule_secs})."
        )

    return int((raw_data_range_secs - tile_length_secs) / batch_schedule_secs) + 1


def _materialize_multiple_tiles_for_TFP(
    spark: SparkSession,
    feature_package: FeaturePackage,
    raw_data_time_limits: pendulum.Period,
    tile_count: int,
    vds_proto_map: Dict[str, VirtualDataSource],
    transformation_id2proto: Dict[str, Transformation],
    called_for_online_feature_store: bool,
):
    """
    To materialize multiple tiles, we:
      1. Register temp views based on tile's start and end times for each VDS's batch DS.
      2. Construct feature DataFrame for the tile for both offline and online feature stores.
      3. Concatenate features resulted from each tile's materialization.
    """
    # Cache raw data dataframe for each batch DS because to re-reading raw data for each (possibly overlapping) tile
    # will be slower and cost expensive.
    raw_data_cache_per_vds = {}
    for vds_name in vds_proto_map:
        # Global `raw_data_time_limits` filtering is already applied on pre-registered temp views.
        raw_data_df = spark.table(vds_name)
        raw_data_cache_per_vds[vds_name] = raw_data_df
        # Persists the DataFrame with the default storage level (MEMORY_AND_DISK).
        raw_data_cache_per_vds[vds_name].cache()

    tile_length = time_utils.proto_to_duration(feature_package_utils.get_tile_interval(feature_package))
    batch_schedule = time_utils.proto_to_duration(
        feature_package_utils.get_batch_materialization_schedule(feature_package)
    )
    tile_start_time = raw_data_time_limits.start
    tile_end_time = tile_start_time.add(seconds=tile_length.in_seconds())

    offline_store_df = None
    online_store_df = None
    for i in range(tile_count):
        # Register (overwrite) temp views based on tile's time range for each batch DS
        for vds_name in raw_data_cache_per_vds:
            raw_data_for_tile = data_source_helper.apply_partition_and_timestamp_filter(
                raw_data_cache_per_vds[vds_name],
                vds_proto_map[vds_name].batch_data_source,
                tile_end_time - tile_start_time,
                fwv3=False,
            )
            raw_data_for_tile.createOrReplaceTempView(vds_name)

        offline_store_tile_df, online_store_tile_df = _materialize_single_tile_for_TFP(
            spark,
            feature_package,
            tile_end_time - tile_start_time,
            vds_proto_map,
            transformation_id2proto,
            called_for_online_feature_store,
        )
        # Append newly materialized tile to the existing ones
        offline_store_df = (
            offline_store_df.union(offline_store_tile_df) if offline_store_df is not None else offline_store_tile_df  # type: ignore
        )
        online_store_df = (
            online_store_df.union(online_store_tile_df) if online_store_df is not None else online_store_tile_df  # type: ignore
        )

        # Move to next tile
        tile_start_time = tile_start_time.add(seconds=batch_schedule.in_seconds())
        tile_end_time = tile_end_time.add(seconds=batch_schedule.in_seconds())

    return offline_store_df, online_store_df


def _materialize_interval_for_temporal_feature_view(
    spark: SparkSession,
    fpov: FeaturePackageOrView,
    raw_data_time_limits: pendulum.Period,
    vds_proto_map: Dict[str, VirtualDataSource],
    new_transformations: List[NewTransformation],
    called_for_online_feature_store: bool,
    consume_streaming_data_sources: bool,
    called_for_schema_computation: bool,
    schedule_interval: Optional[pendulum.Duration] = None,
    DO_NOT_USE_vds_df_override_for_fv: Optional[DataFrame] = None,
) -> Tuple[DataFrame, DataFrame, DataFrame]:
    tile_df = pipeline_to_dataframe(
        spark,
        fpov.fv.pipeline,
        consume_streaming_data_sources,
        list(vds_proto_map.values()),
        new_transformations,
        feature_time_limits=raw_data_time_limits,
        schedule_interval=schedule_interval,
        DO_NOT_USE_vds_df_override=DO_NOT_USE_vds_df_override_for_fv,
        called_for_schema_computation=called_for_schema_computation,
    )

    timestamp_key = fpov.timestamp_key
    tile_df = _possibly_apply_feature_time_limits(tile_df, raw_data_time_limits, vds_proto_map, timestamp_key, True)
    cacheable_df = tile_df

    # We infer partition column (i.e. anchor time) by looking at the feature timestamp column and grouping
    # all the features within `[anchor_time,  anchor_time + batch_schedule)` together.
    version = fpov.get_feature_store_format_version
    anchor_time_val = convert_timestamp_to_epoch(functions.col(timestamp_key), version)
    batch_mat_schedule = convert_timedelta_for_version(fpov.batch_materialization_schedule, version)
    offline_store_tile_df = tile_df.withColumn(
        TEMPORAL_ANCHOR_COLUMN_NAME, anchor_time_val - anchor_time_val % batch_mat_schedule
    )

    if called_for_online_feature_store:
        # Add raw data end time as a column as it's used for status reporting while writing to Online Feature Store.
        # When materializing multiple tiles, include `raw_data_end_time` per tile so that we can distribute writing
        # to Kafka into multiple partitions.
        online_store_tile_df = offline_store_tile_df.withColumn(
            MATERIALIZED_RAW_DATA_END_TIME, functions.col(TEMPORAL_ANCHOR_COLUMN_NAME) + batch_mat_schedule
        ).drop(TEMPORAL_ANCHOR_COLUMN_NAME)
    else:
        online_store_tile_df = tile_df

    return offline_store_tile_df, online_store_tile_df, cacheable_df


def _materialize_single_tile_for_TFP(
    spark: SparkSession,
    feature_package: FeaturePackage,
    raw_data_time_limits: Optional[pendulum.Period],
    vds_proto_map: Dict[str, VirtualDataSource],
    transformation_id2proto: Dict[str, Transformation],
    called_for_online_feature_store: bool,
) -> Tuple[DataFrame, DataFrame]:
    context = MaterializationContext.default()
    if raw_data_time_limits:
        context = MaterializationContext.build(raw_data_time_limits, feature_package)

    feature_transformation = feature_package.feature_transformation
    if feature_transformation.HasField("final_transformation_id"):
        vds_id2proto = data_source_helper.get_vds_id2proto_map(vds_proto_map.values())
        tile_df = _transformation_dag_to_df(
            spark, context, feature_transformation, transformation_id2proto, vds_id2proto
        )
    else:
        # Deprecated! SQLTransformation should be used in view_sql.
        tile_df = spark.sql(feature_transformation.view_sql)

    feature_type = feature_package_utils.get_feature_type(feature_transformation)
    timestamp_key = feature_package_utils.get_timestamp_key(feature_type)
    tile_df = _possibly_apply_feature_time_limits(tile_df, raw_data_time_limits, vds_proto_map, timestamp_key, False)

    # Add an anchor time (feature data start time from the `context`) as a new column that will be used as a parittion
    # column in offline feature store. This behavior mimics TAFP materialization into offline feature store.
    version = feature_package_utils.get_feature_store_format_version(feature_package)
    anchor_time = convert_timestamp_to_epoch(context.feature_data_start_time, version)
    offline_store_tile_df = tile_df.withColumn(TEMPORAL_ANCHOR_COLUMN_NAME, functions.lit(anchor_time))

    if called_for_online_feature_store:
        # Add raw data end time as a column as it's used for status reporting while writing to Online Feature Store.
        # When materializing multiple tiles, include `raw_data_end_time` per tile so that we can distribute writing
        # to Kafka into multiple partitions.
        raw_data_end_time = convert_timestamp_to_epoch(context.raw_data_end_time, version)
        online_store_tile_df = tile_df.withColumn(MATERIALIZED_RAW_DATA_END_TIME, functions.lit(raw_data_end_time))
    else:
        online_store_tile_df = tile_df

    return offline_store_tile_df, online_store_tile_df


def _transformation_dag_to_df(
    spark: SparkSession,
    context: MaterializationContext,
    feature_transformation: FeatureTransformation,
    transformation_id2proto: Dict[str, Transformation],
    vds_id2proto: Dict[str, VirtualDataSource],
):
    """
    Returns a DataFrame using maps of IDs to Transformation/VirtualDataSource FCO protos and
    feature_transformation.final_transformation_id.
    """
    return (
        TransformationDataProtoDAG.create_from_maps(
            final_transformation_id_pb2=feature_transformation.final_transformation_id,
            transformation_pb2_map=transformation_id2proto,
            vds_pb2_map=vds_id2proto,
        )
        .final_transformation()
        ._dataframe_for_materialization(spark, context)
    )


def _possibly_apply_feature_time_limits(
    spark_df,
    raw_data_time_limits: Optional[pendulum.Period],
    vds_proto_map: Dict[str, VirtualDataSource],
    timestamp_key: Optional[str],
    is_feature_view: bool,
):
    # Apply time filter here if any of the VDS for this FP does not contain the time column field
    # The reason being that if all VDS contains time column fields then the time filter is already applied everywhere on
    # the raw data level.
    if raw_data_time_limits and is_feature_view:
        # note that raw_data_time_limits is actually feature data time limits for FV
        # TODO: rename this once fwv1 is destroyed
        def validate_time_limits(ts):
            if not raw_data_time_limits.start <= ts.replace(tzinfo=pendulum.timezone("UTC")) < raw_data_time_limits.end:
                raise TectonFeatureTimeError(timestamp_key, ts, raw_data_time_limits.start, raw_data_time_limits.end)
            else:
                return True

        udf_checker = udf(validate_time_limits, BooleanType())
        # force the output of the udf to be filtered on, so udf cannot be optimized away
        return spark_df.where(udf_checker(functions.col(timestamp_key)))
    elif raw_data_time_limits and (
        not all(
            [
                vds_proto.batch_data_source.HasField("timestamp_column_properties")
                for vds_proto in vds_proto_map.values()
            ]
        )
    ):
        timestamp_key = functions.col(timestamp_key)
        return spark_df.where(
            (raw_data_time_limits.start <= timestamp_key) & (timestamp_key <= raw_data_time_limits.end)
        )

    return spark_df


def get_stream_materialization_plan(
    spark: SparkSession,
    feature_transformation: FeatureTransformation,
    vds_proto_map: Dict[str, VirtualDataSource],
    transformation_id2proto: Dict[str, Transformation],
    feature_package_or_view: FeaturePackageOrView,
    new_transformations: List[NewTransformation],
) -> MaterializationPlan:

    new_transformations = new_transformations or []

    if feature_package_or_view and feature_package_or_view.is_feature_view:
        return get_feature_view_stream_materialization_plan(
            spark, feature_package_or_view, list(vds_proto_map.values()), new_transformations
        )
    else:
        if feature_transformation.HasField("final_transformation_id"):
            vds_id2proto = data_source_helper.get_vds_id2proto_map(vds_proto_map.values())
            spark_df = _transformation_dag_to_df(
                spark, MaterializationContext.default(), feature_transformation, transformation_id2proto, vds_id2proto
            )
        else:
            # Deprecated! SQLTransformation should be used in view_sql.
            spark_df = spark.sql(feature_transformation.view_sql)

        feature_type = feature_package_utils.get_feature_type(feature_transformation)
        if feature_type:
            if feature_package_utils.is_temporal_aggregate(feature_type):
                spark_df = construct_partial_time_aggregation_df(
                    spark_df,
                    list(feature_transformation.join_keys),
                    feature_transformation.feature_type.trailing_time_window_aggregation,
                    feature_package_or_view.get_feature_store_format_version,
                )
            else:
                # For temporal features the output DF is identical to the input DF
                pass
    return MaterializationPlan(None, spark_df, spark_df, 0)


def get_feature_view_stream_materialization_plan(
    spark: SparkSession,
    feature_package_or_view: FeaturePackageOrView,
    virtual_data_sources: List[VirtualDataSource],
    new_transformations: List[NewTransformation],
) -> MaterializationPlan:
    df = pipeline_to_dataframe(
        spark, feature_package_or_view.fv.pipeline, True, virtual_data_sources, new_transformations
    )
    if feature_package_or_view.is_temporal_aggregate:
        df = construct_partial_time_aggregation_df(
            df,
            list(feature_package_or_view.join_keys),
            feature_package_or_view.trailing_time_window_aggregation,
            feature_package_or_view.get_feature_store_format_version,
        )
    return MaterializationPlan(None, df, df, 0)


def get_materialization_schema(
    spark: SparkSession,
    feature_transformation: FeatureTransformation,
    virtual_data_sources: List[VirtualDataSource],
    transformations: List[Transformation],
) -> schema.Schema:
    # We don't need actual tiling information to get the schema
    wrapping_fp = FeaturePackage()
    wrapping_fp.feature_transformation.CopyFrom(feature_transformation)
    dummy_tile_interval = pendulum.duration(seconds=60)
    wrapping_fp.materialization_params.batch_materialization_schedule.FromTimedelta(dummy_tile_interval)

    online_plan = get_batch_materialization_plan(
        spark=spark,
        feature_package_or_view=FPBackedFeaturePackageOrView(wrapping_fp),
        raw_data_time_limits=None,
        coalesce=0,
        vds_proto_map=data_source_helper.get_vds_proto_map(virtual_data_sources),
        transformation_id2proto=transformation_helper.get_transformation_id2proto_map(transformations),
        called_for_schema_computation=True,
    ).online_store_data_frame
    assert online_plan is not None
    return schema.Schema.from_spark(online_plan.schema)


def get_materialization_schema_for_feature_view(
    spark: SparkSession,
    pipeline: Pipeline,
    virtual_data_sources: List[VirtualDataSource],
    transformations: List[NewTransformation],
    timestamp_key: str,
    join_keys: List[str],
    temporal_aggregate: Optional[NewTemporalAggregate] = None,
    batch_schedule: Optional[pendulum.Duration] = None,
) -> schema.Schema:

    wrapping_fv = FeatureView()
    wrapping_fv.pipeline.CopyFrom(pipeline)
    wrapping_fv.timestamp_key = timestamp_key
    wrapping_fv.join_keys.extend(join_keys)
    if temporal_aggregate:
        wrapping_fv.temporal_aggregate.CopyFrom(temporal_aggregate)
    else:
        wrapping_fv.temporal.serving_ttl.FromSeconds(3600)
    dummy_tile_interval = pendulum.duration(seconds=60)
    wrapping_fv.materialization_params.schedule_interval.FromTimedelta(dummy_tile_interval)
    dummy_raw_data_time_limit = pendulum.Period(pendulum.datetime(2021, 1, 1), pendulum.datetime(2021, 1, 31))

    online_plan = get_batch_materialization_plan(
        spark=spark,
        feature_package_or_view=FeaturePackageOrView.from_fv(wrapping_fv),
        raw_data_time_limits=dummy_raw_data_time_limit,
        coalesce=0,
        vds_proto_map=data_source_helper.get_vds_proto_map(virtual_data_sources),
        transformation_id2proto={},
        new_transformations=transformations,
        called_for_schema_computation=True,
        schedule_interval=batch_schedule,
    ).online_store_data_frame
    assert online_plan is not None
    return schema.Schema.from_spark(online_plan.schema)
