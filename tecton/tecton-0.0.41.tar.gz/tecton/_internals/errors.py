from typing import List
from typing import Set

from tecton.fco import Fco
from tecton.tecton_errors import TectonInternalError
from tecton.tecton_errors import TectonValidationError

# Generic
INTERNAL_ERROR = lambda message: TectonInternalError(
    f"We seem to have encountered an error. Please contact support for assistance. Error details: {message}"
)
MDS_INACCESSIBLE = lambda host_port: TectonInternalError(
    f"Failed to connect to Tecton cluster at {host_port}, please check your connectivity or contact support"
)
VALIDATION_ERROR_FROM_MDS = lambda message, trace_id: TectonValidationError(f"{message}, trace ID: {trace_id}")
INTERNAL_ERROR_FROM_MDS = lambda message, trace_id: TectonInternalError(
    f"Internal Tecton server error, please contact support with error details: {message}, trace ID: {trace_id}"
)
REQUIRED_ARGUMENT = lambda arg_name: TectonValidationError(f"Missing required argument: {arg_name}")
INVALID_ARGUMENT_TYPE = lambda arg_name, expected_type: TectonValidationError(
    (f"Invalid type for argument: {arg_name}. Expected: {expected_type}")
)
TIME_KEY_TYPE_ERROR = lambda timestamp_key, found_type: TectonValidationError(
    f"Column '{timestamp_key}' must be Spark type 'TimestampType'. Found '{str(found_type)}'"
)
# Add a link to reference explaining time/duration formats
TIME_PARSING_ERROR = lambda param_name, time_str: TectonValidationError(
    f"Error parsing time '{time_str}' in '{param_name}'"
)
ERROR_RESOLVING_COLUMN = lambda column_name: TectonValidationError(f"Error resolving column '{column_name}'")
FLOATING_POINT_JOIN_KEY = lambda column_name: TectonValidationError(
    f"Floating point types are not allowed for join_key '{column_name}'"
)
INVALID_SPINE_TYPE = lambda t: TectonValidationError(
    f"Invalid type of spine '{t}'. Spine must be an instance of [pyspark.sql.dataframe.DataFrame, " "pandas.DataFrame]."
)
UNSUPPORTED_OPERATION = lambda op, reason: TectonValidationError(f"Operation '{op}' is not supported: {reason}")
INVALID_SPINE_TIME_KEY_TYPE = lambda t: TectonValidationError(
    f"Invalid type of timestamp_key column in the given spine. Expected TimestampType, got {t}"
)
INVALID_FEATURE_PACKAGE_TYPE = lambda invalid_type, expected_type: TectonValidationError(
    f"Feature package exists, but the type is not {invalid_type}. Use either {expected_type}.get() or tecton.get_feature_package(..) to retrieve it."
)
MISSING_SPINE_COLUMN = lambda param, col, existing_cols: TectonValidationError(
    f"TectonValidationError: {param} column is missing from the spine. Expected to find '{col}' among available spine columns: '{', '.join(existing_cols)}'."
)
INVALID_DATETIME_PARTITION_COLUMNS = lambda datepart: TectonValidationError(
    f'TectonValidationError: Invalid set of DatetimePartitionColumns: missing "{datepart}"'
)
DURATION_NEGATIVE_OR_AMBIGUOUS = lambda param_name, param_value: TectonValidationError(
    f"{param_name} must be a positive value and must not contain ambiguous durations such as months and years. Instead got {param_value}"
)
NONEXISTENT_WORKSPACE = lambda name, workspaces: TectonValidationError(
    f'Workspace "{name}" not found. Possible values: {workspaces}'
)
INCORRECT_MATERIALIZATION_ENABLED_FLAG = lambda user_set_bool, server_side_bool: TectonValidationError(
    f"'automatic_materialization_enabled={user_set_bool}' argument does not match the value on the server: {server_side_bool}"
)
UNSUPPORTED_OPERATION_IN_NON_PROD_WORKSPACE = lambda op: TectonValidationError(
    f"Operation '{op}' is not supported in a workspace with automatic materialization disabled"
)
INVALID_JOIN_KEYS_TYPE = lambda t: TectonValidationError(
    f"Invalid type for join_keys. Expected Dict[str, Union[int, str, bytes]], got {t}"
)
INVALID_REQUEST_CONTEXT_TYPE = lambda t: TectonValidationError(
    f"Invalid type for requests_context_map. Expected Dict[str, Union[int, str, bytes, float]], got {t}"
)
INVALID_CONTEXT_TYPE = lambda t: TectonValidationError(
    f"Invalid type for context. Expected `MaterializationContext` but got `{t}`."
)
CONTEXT_REQUIRED = lambda: TectonValidationError("Expected `context` to be a `MaterializationContext` but got `None`.")


def EMPTY_ARGUMENT(argument: str):
    return TectonValidationError(f"Argument '{argument}' can not be empty.")


def EMPTY_ELEMENT_IN_ARGUMENT(argument: str):
    return TectonValidationError(f"Argument '{argument}' can not have an empty element.")


def WRONG_ARGUMENT_TYPE(argument, expected_type):
    return TectonValidationError(f"Argument '{argument}' must be of type '{expected_type}'")


def DUPLICATED_ELEMENTS_IN_ARGUMENT(argument: str):
    return TectonValidationError(f"Argument '{argument}' can not have duplicated elements.")


def FCO_NOT_FOUND(fco: Fco, fco_reference: str):
    raise TectonValidationError(
        f"{fco._fco_type_name_singular_capitalized()} '{fco_reference}' not found. "
        f"Try running tecton.list_{fco._fco_type_name_plural_snake_case()}() to view all registered "
        f"{fco._fco_type_name_plural_capitalized()}"
    )


def FCO_NOT_FOUND_WRONG_TYPE(fco: Fco, fco_reference: str, expected_method):
    raise TectonValidationError(
        f"{fco._fco_type_name_singular_capitalized()} '{fco_reference}' not found. "
        f"Did you mean tecton.{expected_method}?"
    )


def UNKNOWN_REQUEST_CONTEXT_KEY(keys, key):
    return TectonValidationError(f"Unknown request context key '{key}', expected one of: {keys}")


# FeaturePackage
FP_TIMEZONE_MISSING = lambda param_name: TectonValidationError(f"{param_name} must contain timezone")
FP_ONEOF_SQL_TRANSFORMATION_NEEDED = TectonValidationError(
    "Exactly one of sql or transformation fields should be set when creating a FeaturePackage."
)
FP_TIME_KEY_MISSING = lambda fp_name: TectonValidationError(f"timestamp_key is required for Feature Package {fp_name}")
FP_NEEDS_TO_BE_MATERIALIZED = lambda fp_name: TectonValidationError(
    f"Feature Package {fp_name} has not been configured for materialization. "
    + f"Set offline_materialization_enabled=True in the feature package definition to enable this feature"
)
FP_MATERIALIZATION_TIMEOUT = lambda fp_name: TectonValidationError(
    f"Materialization of Feature Package {fp_name} has not completed in the allotted time, please check for potential errors using the .materialization_status() method, or try again"
)
FP_MATERIALIZATION_IN_PROGRESS = lambda fp_name: TectonValidationError(
    f"Materialization of Feature Package {fp_name} is in progress, please use .wait_until_materialization_up_to_date()"
)
FP_FEATURE_STORE_START_TIME_INVALID = lambda actual_start_time, latest_allowed_start_time: TectonValidationError(
    f"Feature store start time {actual_start_time} is invalid. It must not be greater than the current time {latest_allowed_start_time}"
)

FP_MISSING_DSC = lambda table_name: TectonValidationError(
    f"Missing data source configuration for '{table_name}' in data_source_configs"
)
FP_DSC_DUPLICATE_NAMES = lambda dsc_name, fp_name: TectonValidationError(
    f"Multiple data sources with the same name {dsc_name} in FeaturePackage {fp_name}"
)

FP_DSC_STREAM_POSITION = lambda valid_positions: TectonValidationError(
    f"Invalid initial_stream_position. Must be one of {valid_positions}"
)
FP_STREAMING_JOINS_NOT_SUPPORTED = lambda vds_name: TectonValidationError(
    f"JOINs for streaming data sources are not supported ({vds_name} is a streaming data source)"
)
FP_STREAMING_AGGREGATE_QUERIES_NOT_SUPPORTED = lambda vds_name: TectonValidationError(
    f"Aggregate queries on streaming data sources are not supported ({vds_name} is a streaming data source)"
)
FP_NO_MATERIALIZED_DATA = lambda fp_name: TectonValidationError(
    f"FeaturePackage {fp_name} doesn't have any materialized data. "
    "Materialization jobs may not have updated the offline feature store yet. "
    "Please monitor using materialization_status() or use from_source=True to compute from source data."
)
FP_DUPLICATED_COLUMNS = lambda schema_type, fp_name, columns: TectonValidationError(
    f"The {schema_type} schema for FeaturePackage {fp_name} contains the following duplicate columns: {columns}"
)

FP_NOT_SUPPORTED_GET_FEATURE_DF = TectonValidationError(
    "This method cannot be used with this type of Feature Definition. Please use get_feature_dataframe(spine)."
)
FD_PREVIEW_NO_MATERIALIZED_OFFLINE_DATA = TectonValidationError(
    f"No materialized offline data found. If this Feature Definition was recently created,"
    + " its materialization backfill may still be in progress. This can be monitored using materialization_status()."
    + " In the meantime, you can set use_materialized_data=False on preview() to compute features directly from data sources."
)
FP_GET_FEATURE_DF_NO_SPINE = TectonValidationError("get_feature_dataframe() requires a 'spine' argument.")

FP_PUSH_ONLY_METHOD = TectonValidationError("This method is only supported for Push FeaturePackages")

FP_PUSH_DF_TOO_LARGE = TectonValidationError(
    "Dataframe too large for a single ingestion, consider splitting into smaller ones"
)
FP_GET_FEATURES_MATERIALIZATION_DISABLED = TectonValidationError(
    "Error: This FeaturePackage does not have offline materialization turned on. "
    "Try calling this function with 'from_source=True' to compute features on-demand, "
    "or alternatively configure offline materialization for this FeaturePackage in a workspace with automatic materialization enabled."
)
PFP_UNABLE_TO_ACCESS_SOURCE_DATA = lambda fp_name: TectonValidationError(
    f"The source data for PushFeaturePackage {fp_name} does not exist. "
    "Please use from_source=False when calling this function."
)

FD_GET_FEATURES_FROM_DISABLED_MATERIALIZATION = lambda fd_name, workspace: TectonValidationError(
    f"Feature Definition {fd_name} in workspace {workspace} has materialization disabled. "
    "Please use from_source=True when getting features."
)

FD_GET_MATERIALIZED_FEATURES_FROM_NONMATERIALIZABLE_WORKSPACE = lambda fd_name, workspace: TectonValidationError(
    f"Feature Definition {fd_name} is in workspace {workspace}, which does not have materialization enabled. "
    "Please use from_source=True when getting features."
)


def PUSH_UPLOAD_FAILED(reason):
    return TectonValidationError(f"Failed to upload dataframe: {reason}")


# DataSources
def VDS_STREAM_BATCH_SCHEMA_MISMATCH(columns):
    return TectonValidationError(
        f"Streaming data source schema has column(s) that are not present in the batch data source schema: {columns}"
    )


def VDS_INVALID_TABLE_COLUMN(column_name, existing_columns):
    return TectonValidationError(f"Column '{column_name}' is not among table columns {existing_columns}")


def VDS_INVALID_TABLE_PARTITION(partition_name, existing_partitions):
    return TectonValidationError(f"Column '{partition_name}' is not among table partitions {existing_partitions}")


def VDS_NAME_EQUALS_HIVE_TABLE_NAME(name):
    return TectonValidationError(
        f"VirtualDataSource name '{name}' is not allowed because a Glue (or Hive) table with the same name exists. "
        f"This is a current system limitation. Please rename your VirtualDataSource to, for instance, '{name}_vds'"
    )


def VDS_NAME_CANNOT_CONTAIN_DOT(name):
    return TectonValidationError(
        f"VirtualDataSource name '{name}' cannot contain a dot. Please, remove it and try again."
    )


def VDS_TIMESTAMP_COLUMN_MISSING_FOR_LOOKBACK(name):
    return TectonValidationError(
        "Setting data_lookback requires your upstream data source to specify a timestamp column to enable Tecton to "
        "filter your raw data according to the time range specified by data_lookback. Please specify 'timestamp_column'"
        f" on the batch_ds_config of your VirtualDataSource {name} or unset data_lookback to disable Tecton's "
        "raw data filtering."
    )


DS_TIME_KEY_MISSING_ERROR = lambda timestamp_key, all_cols: TectonValidationError(
    f"Timestamp column '{timestamp_key}' missing from Schema. Found columns {all_cols}"
)

VDS_STREAM_PREVIEW_ON_NON_STREAM = TectonValidationError("start_stream_preview called on non-streaming data source")


def DS_DEDUPLICATION_COLUMN_MISSING(column, schema_columns):
    return TectonValidationError(
        f"Deduplication column '{column}' not present in the translated stream schema {schema_columns}"
    )


# FeatureSetConfig and FeatureService
def FS_FAILED_TO_LOAD_FP(name):
    return TectonValidationError(f"Failed to load FeaturePackage {name}")


def FS_FP_JOIN_KEY_OVERRIDE_INVALID(spine_key, fp_key, possible_keys):
    return TectonValidationError(
        f"FeaturePackage join key override '{fp_key}' (mapped to spine join key '{spine_key}') not found in FeaturePackage join keys {possible_keys}"
    )


def FS_SPINE_JOIN_KEY_OVERRIDE_INVALID(spine_key, fp_key, possible_columns):
    return TectonValidationError(
        f"Spine join key '{spine_key}' (mapped from FeaturePackage join key '{fp_key}') not found in spine schema {possible_columns}"
    )


def FS_SPINE_TIMESTAMP_KEY_INVALID(timestamp_key, possible_columns):
    return TectonValidationError(f"Spine timestamp key '{timestamp_key}' not found in spine schema {possible_columns}")


def FS_BACKEND_ERROR(message):
    return TectonInternalError(f"Error calling Feature Service backend: {message}")


def FS_MISSING_FPS(param_name):
    return TectonValidationError(f"At least one FeaturePackage is required in '{param_name}'")


def FS_AMBIGUOUS_TIMESTAMP_KEY(keys):
    return TectonValidationError(f"Multiple default timestamp keys found: {keys}. Parameter timestamp_key must be set.")


FS_GET_FEATURE_VECTOR_REQUIRED_ARGS = TectonValidationError(
    "get_feature_vector requires at least one of join_keys or request_context_map"
)

FS_TIMESTAMP_KEY_REQUIRED = TectonValidationError("timestamp_key is required.")

FS_API_KEY_MISSING = TectonValidationError(
    "API key is required for online feature requests, but was not found in the environment. Please generate a key and set TECTON_API_KEY "
    + "using https://docs.tecton.ai/v2/examples/fetch-real-time-features.html#generating-an-api-key"
)

# TrailingTimeWindowAggregation
TTWA_EMPTY_FEATURES = TectonValidationError(f"TrailingTimeWindowAggregation without any features, use .add() method")
TTWA_UNSUPPORTED_AGGREGATION = lambda param_name, aggregation_function: TectonValidationError(
    f"Unsupported '{aggregation_function}' in '{param_name}'"
)
TTWA_WINDOW_LENGTH_ERROR = lambda feature_name, slide_period: TectonValidationError(
    f"Aggregation window for '{feature_name}' should be an integer multiple of the aggregation slide period '{slide_period}'"
)
TTWA_UNREFERENCED_COLUMNS = lambda feature_names: TectonValidationError(
    f"All columns must be referenced in aggregations, extra columns: '{feature_names}'"
)
TTWA_INVALID_NUMERIC_AGGREGATION = lambda function, feature_name, feature_type: TectonValidationError(
    f"Invalid aggregation function '{function}' for non-numeric column '{feature_name}':{feature_type}"
)
TTWA_SLIDE_PERIOD_TOO_SMALL = lambda value_seconds, min_value_seconds: TectonValidationError(
    f"Slide period of {value_seconds} seconds is too short, the shortest supported period is {min_value_seconds} seconds. "
)
TTWA_AGG_WINDOW_TOO_SMALL = lambda agg, min_value_seconds: TectonValidationError(
    f"Aggregation window of {agg.window.ToSeconds()} seconds for column {agg.input_feature_name} is too short. "
    f"Aggregation window has to be at least {min_value_seconds} seconds. "
)
TTWA_AGG_WINDOW_TOO_LARGE = lambda agg, max_value_seconds: TectonValidationError(
    f"Aggregation window of {agg.window.ToSeconds()} seconds for column {agg.input_feature_name} is too large. "
    f"Aggregation window has to be no more than {max_value_seconds} seconds when using a streaming data source. "
)

# FileDSConfig
FDSC_UNSUPPORTED_FILE_FORMAT = lambda file_format: TectonValidationError(f"Unsupported file format '{file_format}'")

# Snowflake
SNOWFLAKE_TABLE_QUERY_SET_ERROR = TectonValidationError("Exactly one of table and query sources must be set")

# Entity
def ENTITY_INVALID_JOIN_KEYS_OVERRIDE(entity_name: str):
    return TectonValidationError(
        f"New join_keys must have the same amount of columns as existing join_keys for entity '{entity_name}'."
    )


def WRONG_ENTITY_TYPE():
    return TectonValidationError(
        f"Invalid type for an element of argument 'entities'. Expected an Entity object or string entity name."
    )


def DUPLICATE_ENTITIES_IN_FP(entity_name, join_keys):
    return TectonValidationError(
        f"FeaturePackage cannot have duplicate enitites with name='{entity_name}' and join_keys={join_keys}"
    )


def FP_JOIN_KEY_IN_REQUEST_CONTEXT(join_key, request_context_keys: List[str]):
    return TectonValidationError(
        f"RequestContext schema must not overlap with FeaturePackage join keys, but '{join_key}' was found in "
        f"RequestContext schema: " + ", ".join(request_context_keys)
    )


def FP_JOIN_KEY_IN_OUTPUT_SCHEMA(join_key, output_schema_fields: List[str]):
    return TectonValidationError(
        f"OnlineTransformation output schema must not overlap with FeaturePackage join keys, but '{join_key}' was "
        f"found in output schema: " + ", ".join(output_schema_fields)
    )


def FV_INVALID_MOCK_INPUTS(mock_inputs: Set[str], inputs: Set[str]):
    return TectonValidationError(f"Mock input names {mock_inputs} do not match FeatureView's inputs {inputs}")


class InvalidBackfillConfigMode(TectonValidationError):
    def __init__(self, name: str, got: str, allowed_modes: List[str]):
        super().__init__(f"BackfillConfig mode for '{name}' got '{got}', must be one of: {', '.join(allowed_modes)}")


# Transformation
TRANSFORMATION_DATAFRAME_ONLINE_ONLY = TectonValidationError(
    "Method can only be used with OnlineTransformation objects"
)

TRANSFORMATION_DATAFRAME_NOT_ONLINE = TectonValidationError("Method cannot be used with OnlineTransformation objects")


class InvalidTransformationMode(TectonValidationError):
    def __init__(self, name: str, got: str, allowed_modes: List[str]):
        super().__init__(f"Transformation mode for '{name}' got '{got}', must be one of: {', '.join(allowed_modes)}")


class InvalidConstantType(TectonValidationError):
    def __init__(self, value, allowed_types):
        allowed_types = [str(allowed_type) for allowed_type in allowed_types]
        super().__init__(
            f"Tecton const value '{value}' must have one of the following types: {', '.join(allowed_types)}"
        )


class InvalidTransformInvocation(TectonValidationError):
    def __init__(self, transformation_name: str, got: str):
        super().__init__(
            f"Allowed arguments for Transformation '{transformation_name}' are: "
            f"tecton.const, tecton.materialization_context, transformations, and DataSource inputs. Got: '{got}'"
        )


# Dataset
DATASET_SPINE_COLUMNS_NOT_SET = TectonValidationError(
    "Cannot retrieve spine DF when DataFrame was created without a " "spine."
)

# Feature Retrevial
def GET_HISTORICAL_FEATURES_WRONG_PARAMS(params: List[str], if_statement: str):
    return TectonValidationError("Cannot provide parameters " + ", ".join(params) + f" if {if_statement}")


FV_NOT_SUPPORTED_GET_HISTORICAL_FEATURES = TectonValidationError(
    "This method cannot be used with this type of Feature Definition. Please use get_historical_features(spine)."
)


GET_ONLINE_FEATURES_REQUIRED_ARGS = TectonValidationError(
    "get_online_features requires at least one of join_keys or request_context_map"
)
