from typing import List

from pyspark.sql import functions

from tecton_proto.data.feature_types_pb2 import TrailingTimeWindowAggregation
from tecton_spark.aggregation_plans import get_aggregation_plan
from tecton_spark.aggregation_utils import get_aggregation_column_prefixes
from tecton_spark.aggregation_utils import get_continuous_aggregation_value
from tecton_spark.time_utils import convert_timestamp_to_epoch

TEMPORAL_ANCHOR_COLUMN_NAME = "_anchor_time"
WINDOW_COLUMN_NAME = "window"


def _get_feature_partial_aggregations(aggregation_plan, feature_name: str):
    column_names = set()
    for column_name, aggregated_column in zip(
        aggregation_plan.materialized_column_names(feature_name),
        aggregation_plan.partial_aggregation_transform(feature_name),
    ):
        if column_name in column_names:
            continue
        column_names.add(column_name)

        yield column_name, aggregated_column.alias(column_name)


def _convert_window_to_anchor_time(output_df, is_continuous, time_key, version):
    # For continuous aggregations this will simply be the time key.
    if is_continuous:
        anchor_time_val = functions.col(time_key)
    else:
        # Grouping by Spark Window introduces the "window" struct with "start" and "end" columns.
        # We only need to keep the "start" column as an anchor time.
        anchor_time_val = functions.col(f"{WINDOW_COLUMN_NAME}.start")

    output_df = output_df.withColumn(TEMPORAL_ANCHOR_COLUMN_NAME, convert_timestamp_to_epoch(anchor_time_val, version))

    if is_continuous:
        return output_df
    else:
        return output_df.drop(WINDOW_COLUMN_NAME)


def construct_partial_time_aggregation_df(
    df, join_keys: List[str], time_aggregation: TrailingTimeWindowAggregation, version
):
    output_columns = set()
    if not time_aggregation.is_continuous:
        group_by_cols = [functions.col(join_key) for join_key in join_keys]
        slide_str = f"{time_aggregation.aggregation_slide_period.seconds} seconds"
        window_spec = functions.window(time_aggregation.time_key, slide_str, slide_str)
        group_by_cols = [window_spec] + group_by_cols
        aggregations = []
        for feature in time_aggregation.features:
            aggregation_plan = get_aggregation_plan(feature.function, feature.function_params)
            for name, aggregation in _get_feature_partial_aggregations(aggregation_plan, feature.input_feature_name):
                if name in output_columns:
                    continue
                output_columns.add(name)
                aggregations.append(aggregation)
        output_df = df.groupBy(*group_by_cols).agg(*aggregations)
    else:
        columns_to_drop = set()
        for feature in time_aggregation.features:
            column_prefixes = get_aggregation_column_prefixes(feature.function)
            for column_prefix in column_prefixes:
                full_name = f"{column_prefix}_{feature.input_feature_name}"
                if full_name in output_columns:
                    continue
                output_columns.add(full_name)
                df = df.withColumn(
                    full_name, get_continuous_aggregation_value(column_prefix, feature.input_feature_name)
                )
            columns_to_drop.add(feature.input_feature_name)
        # Drop the original feature columns.
        for column in columns_to_drop:
            df = df.drop(column)
        output_df = df

    output_df = _convert_window_to_anchor_time(
        output_df, time_aggregation.is_continuous, time_aggregation.time_key, version
    )
    return output_df
