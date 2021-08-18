from typing import List
from typing import Optional

from google.protobuf import duration_pb2
from pyspark.sql import DataFrame

from tecton_proto.common.schema_pb2 import Schema as SchemaProto
from tecton_proto.data.feature_package_pb2 import FeaturePackage
from tecton_proto.data.feature_package_pb2 import FeatureTransformation
from tecton_proto.data.feature_store_pb2 import FeatureStoreFormatVersion
from tecton_proto.data.feature_types_pb2 import FeatureType
from tecton_proto.data.feature_types_pb2 import Online
from tecton_proto.data.feature_types_pb2 import Push
from tecton_proto.data.feature_types_pb2 import Temporal
from tecton_proto.data.feature_types_pb2 import TrailingTimeWindowAggregation
from tecton_spark import errors
from tecton_spark.schema import Schema

CONTINUOUS_MODE_BATCH_INTERVAL = duration_pb2.Duration(seconds=86400)


def is_temporal_aggregate(feature_type: FeatureType):
    return get_temporal_aggregation(feature_type) is not None


def is_continuous_temporal_aggregate(feature_type: FeatureType):
    return get_temporal_aggregation(feature_type).is_continuous


def is_temporal(feature_type: FeatureType):
    return get_temporal(feature_type) is not None


def is_online(feature_type: FeatureType):
    return get_online(feature_type) is not None


def is_push(feature_type: FeatureType):
    return get_push(feature_type) is not None


def get_feature_type(feature_transformation: FeatureTransformation) -> Optional[FeatureType]:
    return feature_transformation.feature_type if feature_transformation.HasField("feature_type") else None


def get_temporal(feature_type: FeatureType) -> Temporal:
    return feature_type.temporal if feature_type.HasField("temporal") else None


def get_online(feature_type: FeatureType) -> Online:
    return feature_type.online if feature_type.HasField("online") else None


def get_push(feature_type: FeatureType) -> Push:
    return feature_type.push if feature_type.HasField("push") else None


def get_temporal_aggregation(feature_type: FeatureType) -> TrailingTimeWindowAggregation:
    return (
        feature_type.trailing_time_window_aggregation
        if feature_type.HasField("trailing_time_window_aggregation")
        else None
    )


def get_timestamp_key(feature_type: FeatureType) -> Optional[str]:
    if is_temporal_aggregate(feature_type):
        return get_temporal_aggregation(feature_type).time_key
    elif is_temporal(feature_type):
        return get_temporal(feature_type).time_key
    elif is_push(feature_type):
        return get_push(feature_type).time_key
    else:
        return None


def get_serving_ttl(feature_type: FeatureType) -> Optional[str]:
    if is_temporal(feature_type):
        return get_temporal(feature_type).serving_ttl
    elif is_push(feature_type):
        return get_push(feature_type).serving_ttl
    else:
        return None


# Keep in sync with FeaturePackageUtils.java
def get_data_lookback(feature_package: FeaturePackage):
    feature_type = get_feature_type(feature_package.feature_transformation)
    assert feature_type is None or not is_temporal_aggregate(feature_type)

    if feature_type and get_temporal(feature_type).HasField("data_lookback"):
        return get_temporal(feature_type).data_lookback

    return feature_package.materialization_params.batch_materialization_schedule


def get_tile_interval(feature_package: FeaturePackage):
    feature_type = get_feature_type(feature_package.feature_transformation)

    if is_temporal_aggregate(feature_type):
        return get_temporal_aggregation(feature_type).aggregation_slide_period
    elif is_temporal(feature_type):
        return get_data_lookback(feature_package)

    raise ValueError(f"Invalid invocation on unsupported FeaturePackage type")


def get_batch_materialization_schedule(feature_package: FeaturePackage):
    feature_type = get_feature_type(feature_package.feature_transformation)

    if feature_type and is_temporal_aggregate(feature_type):
        if not feature_package.materialization_params.HasField("batch_materialization_schedule"):
            if is_continuous_temporal_aggregate(feature_type):
                return CONTINUOUS_MODE_BATCH_INTERVAL
            else:
                return get_temporal_aggregation(feature_type).aggregation_slide_period
    elif feature_type and is_temporal(feature_type):
        return feature_type.temporal.schedule_interval

    return feature_package.materialization_params.batch_materialization_schedule


def get_min_scheduling_interval(feature_package: FeaturePackage):
    feature_type = get_feature_type(feature_package.feature_transformation)

    if feature_type and is_temporal_aggregate(feature_type):
        return get_temporal_aggregation(feature_type).aggregation_slide_period
    elif feature_type and is_temporal(feature_type):
        return feature_type.temporal.schedule_interval

    return feature_package.materialization_params.batch_materialization_schedule


def get_feature_store_format_version(feature_package: FeaturePackage):
    version = feature_package.feature_store_format_version
    validate_version(version)
    return version


def get_input_feature_columns(view_schema: SchemaProto, join_keys: List[str], timestamp_key: str) -> List[str]:
    column_names = (c.name for c in view_schema.columns)
    return [c for c in column_names if c not in join_keys and c != timestamp_key]


def get_max_aggregation_window(feature_transformation: FeatureTransformation):
    """Returns maximum aggregation window for temporal aggregate features."""
    feature_type = get_feature_type(feature_transformation)

    if is_temporal_aggregate(feature_type):
        return max(
            [feature.window for feature in get_temporal_aggregation(feature_type).features],
            key=lambda window: window.ToSeconds(),
        )

    return None


def validate_df_schema(df: DataFrame, view_schema: Schema):
    df_columns = Schema.from_spark(df.schema).column_name_types()
    df_column_names = frozenset([x[0] for x in df_columns])
    fp_columns = view_schema.column_name_types()
    fp_column_names = frozenset([x[0] for x in fp_columns])

    if fp_column_names.difference(df_column_names):
        raise errors.INGEST_DF_MISSING_COLUMNS(list(fp_column_names.difference(df_column_names)))
    for fp_column in fp_columns:
        if fp_column not in df_columns:
            raise errors.INGEST_COLUMN_TYPE_MISMATCH(
                fp_column[0], fp_column[1], [x for x in df_columns if x[0] == fp_column[0]][0][1]
            )


def validate_version(version):
    assert (
        version >= FeatureStoreFormatVersion.FEATURE_STORE_FORMAT_VERSION_DEFAULT
        or version <= FeatureStoreFormatVersion.FEATURE_STORE_FORMAT_VERSION_MAX
    )
