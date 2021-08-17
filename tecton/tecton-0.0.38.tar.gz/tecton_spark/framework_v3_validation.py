import random
import time

import pandas
import pendulum
from pandas.testing import assert_frame_equal
from pyspark import StorageLevel
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.functions import to_date
from pyspark.sql.functions import udf
from pyspark.sql.types import TimestampType

from tecton_proto.data.remote_spark_pb2 import ValidateDuplicateFeatureDefinitions
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource
from tecton_spark import data_source_helper
from tecton_spark import materialization_plan
from tecton_spark import transformation_helper
from tecton_spark.feature_package_view import FeaturePackageOrView
from tecton_spark.materialization_params import MaterializationParams

pandas.set_option("display.max_rows", None, "display.max_columns", None)

TILE_END_TIME = pendulum.datetime(2021, 7, 10, 0, 0, 0)
SAMPLE_DATA_TIME_RANGE = TILE_END_TIME.add(hours=6) - TILE_END_TIME
SAMPLE_DATA_SIZE = 100
S3_COALESCE = 10


def validate_duplicate_feature_definitions(spark: SparkSession, request: ValidateDuplicateFeatureDefinitions):
    """
    Constructs mock VDS views based on the sampled data and validates that materialization pipelines run
    on the mock data result into the identical feature valus for both FP and FV definitions.
    """
    sample_vds_df = _get_sample_data(spark, request.vds_for_fp, SAMPLE_DATA_TIME_RANGE, SAMPLE_DATA_SIZE)
    sample_vds_df.persist(StorageLevel.MEMORY_AND_DISK)

    fpov = FeaturePackageOrView.from_fp(feature_package_proto=request.feature_package)
    # `slide_interval` for TAFP and `data_lookback` for TFP
    tile_length = fpov.get_tile_interval
    # `slide_interval` for TAFP and `batch_schedule` for TFP
    tile_offset = fpov.min_scheduling_interval
    if tile_length.total_seconds() > 2 * tile_offset.total_seconds():
        # Only spread events out over several tiles to not have unpopulated offset periods at the end.
        raw_data_tile_length = pendulum.Duration(seconds=3 * tile_offset.total_seconds())
    else:
        raw_data_tile_length = tile_length

    _validate_materializing_single_tile(spark, request, sample_vds_df, tile_length, tile_offset, raw_data_tile_length)
    _validate_materializing_multiple_tiles(
        spark, request, sample_vds_df, tile_length, tile_offset, raw_data_tile_length
    )

    spark.catalog.clearCache()


def _get_sample_data(
    spark: SparkSession, vds: VirtualDataSource, time_range: pendulum.Duration, num_rows_limit: int
) -> DataFrame:
    """Returns a sampled view of the output of the VDS."""
    start = time.time()
    sample_vds_df = data_source_helper.get_vds_dataframe(
        spark=spark, vds=vds, consume_streaming_data_source=False, raw_data_time_limits=time_range, fwv3=True
    ).limit(num_rows_limit)
    print(f"[FV3] Sample data fetch time for '{vds.fco_metadata.name}': {time.time() - start}")

    return sample_vds_df


def _validate_materializing_single_tile(
    spark: SparkSession,
    request: ValidateDuplicateFeatureDefinitions,
    sample_vds_df: DataFrame,
    tile_length: pendulum.Duration,
    tile_offset: pendulum.Duration,
    raw_data_tile_length: pendulum.Duration,
):
    single_tile_df = _construct_tile_df(sample_vds_df, request.vds_for_fp, TILE_END_TIME, raw_data_tile_length)
    single_tile_df.persist(StorageLevel.MEMORY_AND_DISK)

    feature_data_time_range = pendulum.instance(TILE_END_TIME) - pendulum.instance(TILE_END_TIME - tile_offset)
    raw_data_time_range = pendulum.instance(TILE_END_TIME) - pendulum.instance(TILE_END_TIME - tile_length)
    _run_duplicate_fco_validation(spark, request, single_tile_df, feature_data_time_range, raw_data_time_range)


def _construct_tile_df(
    sample_vds_df: DataFrame, vds: VirtualDataSource, tile_end_time: pendulum.DateTime, tile_length: pendulum.Duration
) -> DataFrame:
    """Duplicates `sample_vds_df` and spreads its timestamps out across tile's time range."""
    # Duplicate rows so that each set of `join_keys` is repeated at least twice.
    df = sample_vds_df.union(sample_vds_df)

    ts_column = vds.batch_data_source.timestamp_column_properties.column_name
    assert ts_column, f"Timestamp column not found for VDS: {vds}"

    tile_time_range = pendulum.instance(tile_end_time) - pendulum.instance(tile_end_time - tile_length)
    adding_timestamps = udf(lambda _: _get_random_timestamp(tile_time_range), TimestampType())
    df = df.withColumn(ts_column, adding_timestamps(col(ts_column)))

    assert len(vds.batch_data_source.datetime_partition_columns) == 0, "datetime_partition_columns not supported"
    partition_column = vds.batch_data_source.date_partition_column
    if partition_column:
        df = df.withColumn(partition_column, to_date(ts_column))

    return df


def _get_random_timestamp(time_range: pendulum.Duration) -> pendulum.DateTime:
    offset_secs = random.randint(0, time_range.total_seconds() - 1)
    return time_range.start.add(seconds=offset_secs)


def _validate_materializing_multiple_tiles(
    spark: SparkSession,
    request: ValidateDuplicateFeatureDefinitions,
    sample_vds_df: DataFrame,
    tile_length: pendulum.Duration,
    tile_offset: pendulum.Duration,
    raw_data_tile_length: pendulum.Duration,
):
    multi_tile_df = _construct_multiple_tile_df(
        sample_vds_df, request.vds_for_fp, TILE_END_TIME, raw_data_tile_length, tile_offset
    )
    multi_tile_df.persist(StorageLevel.MEMORY_AND_DISK)

    feature_data_time_range = pendulum.instance(TILE_END_TIME) - pendulum.instance(
        TILE_END_TIME - tile_offset - tile_offset
    )
    raw_data_time_range = pendulum.instance(TILE_END_TIME) - pendulum.instance(
        TILE_END_TIME - tile_offset - tile_length
    )
    _run_duplicate_fco_validation(spark, request, multi_tile_df, feature_data_time_range, raw_data_time_range)


def _construct_multiple_tile_df(
    sample_vds_df: DataFrame,
    vds: VirtualDataSource,
    end_time: pendulum.DateTime,
    tile_length: pendulum.Duration,
    tile_offset: pendulum.Duration,
) -> DataFrame:
    first_tile = _construct_tile_df(sample_vds_df, vds, end_time - tile_offset, tile_length)
    # Have some events that will only be part of the last tile.
    second_tile = _construct_tile_df(sample_vds_df, vds, end_time, tile_offset)

    return first_tile.union(second_tile)


def _run_duplicate_fco_validation(
    spark: SparkSession,
    request: ValidateDuplicateFeatureDefinitions,
    mock_vds_view: DataFrame,
    feature_data_time_range: pendulum.Duration,
    raw_data_time_range: pendulum.Duration,
):
    # 1. Compute offline features for the FeaturePackage
    mock_vds_view.createOrReplaceTempView(request.vds_for_fp.fco_metadata.name)

    fpov = FeaturePackageOrView.from_fp(feature_package_proto=request.feature_package)
    batch_schedule = MaterializationParams.from_package_or_view(fpov).batch_schedule
    plan = materialization_plan.get_batch_materialization_plan(
        spark=spark,
        feature_package_or_view=fpov,
        # When FP is passed, this method expects raw data time range
        raw_data_time_limits=raw_data_time_range,
        coalesce=S3_COALESCE,
        vds_proto_map=data_source_helper.get_vds_proto_map([request.vds_for_fp]),
        transformation_id2proto=transformation_helper.get_transformation_id2proto_map(request.transformations),
        new_transformations=None,
        called_for_online_feature_store=False,
        schedule_interval=batch_schedule,
    )
    fp_offline_df = plan.offline_store_data_frame

    # 2. Compute offline features for the FeatureView
    fpov = FeaturePackageOrView.from_fv(feature_view_proto=request.feature_view)
    batch_schedule = MaterializationParams.from_package_or_view(fpov).batch_schedule
    plan = materialization_plan.get_batch_materialization_plan(
        spark=spark,
        feature_package_or_view=fpov,
        # When FV is passed, this method expects feature data time range
        raw_data_time_limits=feature_data_time_range,
        coalesce=S3_COALESCE,
        vds_proto_map=data_source_helper.get_vds_proto_map([request.vds_for_fv]),
        transformation_id2proto=None,
        new_transformations=request.new_transformations,
        called_for_online_feature_store=False,
        schedule_interval=batch_schedule,
        DO_NOT_USE_vds_df_override_for_fv=mock_vds_view,
    )
    fv_offline_df = plan.offline_store_data_frame

    # 3. Validate that produced dataframes are identical (besides timestamp 1ms difference)
    ts_column = request.feature_view.timestamp_key
    _compare_feature_dataframes(fp_offline_df, fv_offline_df, fpov.name, ts_column)


def _compare_feature_dataframes(fp_df: DataFrame, fv_df: DataFrame, fp_name: str, ts_column: str):
    fp_df = fp_df.toPandas()
    fp_df = fp_df.sort_values(by=list(fp_df.columns)).reset_index(drop=True)
    fv_df = fv_df.toPandas()
    fv_df = fv_df.sort_values(by=list(fv_df.columns)).reset_index(drop=True)

    if ts_column in fp_df:
        # We check that if timestamps were adjusted by 1 seconds for all the rows, we add 1 second
        # back before we compare the dataframes.
        # Parameter `batch_schedule` is always multiple of 1 hour, so we check for `xx:59:59.999`
        all_timestamps_adjusted = len(fv_df) == len(
            fv_df.loc[
                (fv_df[ts_column].dt.minute == 59)
                & (fv_df[ts_column].dt.second == 59)
                & (fv_df[ts_column].dt.microsecond == 999999)
            ]
        )
        if all_timestamps_adjusted:
            fv_df.loc[
                (fv_df[ts_column].dt.minute == 59)
                & (fv_df[ts_column].dt.second == 59)
                & (fv_df[ts_column].dt.microsecond == 999999),
                ts_column,
            ] += pandas.to_timedelta("1microsecond")

    print(f"[FV3] Resulted offline feature dataframes for '{fp_name}':")
    print(fp_df)
    print(fv_df)

    assert_frame_equal(fp_df, fv_df)
