from pyspark.sql import functions

from tecton_proto.common import aggregation_function_pb2 as afpb


def get_aggregation_function_name(aggregation_function_enum):
    return afpb.AggregationFunction.Name(aggregation_function_enum).replace("AGGREGATION_FUNCTION_", "").lower()


def get_continuous_aggregation_value(column_prefix, feature_input_name):
    if column_prefix == get_aggregation_function_name(afpb.AGGREGATION_FUNCTION_COUNT):
        return functions.lit(1).cast("long")
    elif column_prefix == get_aggregation_function_name(afpb.AGGREGATION_FUNCTION_LASTN):
        return functions.array(functions.col(feature_input_name))
    elif column_prefix == get_aggregation_function_name(afpb.AGGREGATION_FUNCTION_MEAN):
        return functions.col(feature_input_name).cast("double")
    else:
        return functions.col(feature_input_name)


def get_aggregation_column_prefixes(aggregation_function):
    col_names = CONTINUOUS_AGGREGATION_COLUMN_PREFIX_MAP.get(aggregation_function, None)
    if col_names is None:
        raise ValueError(f"Unsupported aggregation function {aggregation_function}")
    return col_names


CONTINUOUS_AGGREGATION_COLUMN_PREFIX_MAP = {
    afpb.AGGREGATION_FUNCTION_SUM: [get_aggregation_function_name(afpb.AGGREGATION_FUNCTION_SUM)],
    afpb.AGGREGATION_FUNCTION_MIN: [get_aggregation_function_name(afpb.AGGREGATION_FUNCTION_MIN)],
    afpb.AGGREGATION_FUNCTION_MAX: [get_aggregation_function_name(afpb.AGGREGATION_FUNCTION_MAX)],
    afpb.AGGREGATION_FUNCTION_COUNT: [get_aggregation_function_name(afpb.AGGREGATION_FUNCTION_COUNT)],
    afpb.AGGREGATION_FUNCTION_LAST: [get_aggregation_function_name(afpb.AGGREGATION_FUNCTION_LAST)],
    afpb.AGGREGATION_FUNCTION_LASTN: [get_aggregation_function_name(afpb.AGGREGATION_FUNCTION_LASTN)],
    afpb.AGGREGATION_FUNCTION_MEAN: [
        get_aggregation_function_name(afpb.AGGREGATION_FUNCTION_MEAN),
        get_aggregation_function_name(afpb.AGGREGATION_FUNCTION_COUNT),
    ],
}
