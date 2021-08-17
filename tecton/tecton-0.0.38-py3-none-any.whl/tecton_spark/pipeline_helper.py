import random
import string
from typing import *

import pandas as pd
import pendulum
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql.types import BooleanType
from pyspark.sql.types import DoubleType
from pyspark.sql.types import LongType
from pyspark.sql.types import StringType
from pyspark.sql.types import StructType

from tecton_proto.args.new_transformation_pb2 import NewTransformationArgs
from tecton_proto.args.new_transformation_pb2 import TransformationMode
from tecton_proto.args.pipeline_pb2 import ConstantNode
from tecton_proto.args.pipeline_pb2 import DataSourceNode
from tecton_proto.args.pipeline_pb2 import Input as InputProto
from tecton_proto.args.pipeline_pb2 import Pipeline
from tecton_proto.args.pipeline_pb2 import PipelineNode
from tecton_proto.args.pipeline_pb2 import TransformationNode
from tecton_proto.data.new_transformation_pb2 import NewTransformation
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource
from tecton_spark import data_source_helper
from tecton_spark import function_serialization
from tecton_spark import time_utils
from tecton_spark.id_helper import IdHelper
from tecton_spark.materialization_context import BaseMaterializationContext
from tecton_spark.materialization_context import BoundMaterializationContext
from tecton_spark.transformation import RequestContext

MODE_TO_TYPE_LOOKUP = {"pandas": pd.DataFrame, "pyspark": DataFrame, "pipeline": PipelineNode, "spark_sql": str}


class RequestDataSource:
    def __init__(
        self,
        request_schema: StructType,
    ):
        self.request_schema = request_schema
        self.id = IdHelper.from_string(IdHelper.generate_string_id())


# Pandas Pipeline (ODFV)
# input_df (spark df) is the spine passed in by the user (including request context),
# and it has been augmented with dependent fv fields in of the form "_udf_internal_{input_name}.{feature_field_name}".
# The spark dataframe we return will be everything from the spine, with the on-demand features added, and with the _udf_internal fields removed.
def dataframe_with_input(
    spark: SparkSession,
    pipeline: Pipeline,
    # This should have data from all inputs
    input_df: DataFrame,
    output_schema: StructType,
    transformations,
    name,
    namespace: Optional[str],
) -> DataFrame:
    udf_args = [f"{c.name}" for c in input_df.schema]
    udf_arg_idx_map = {}
    for idx in range(len(udf_args)):
        udf_arg_idx_map[udf_args[idx]] = idx
    builder = _PandasPipelineBuilder(
        name=name,
        pipeline=pipeline,
        transformations=transformations,
        udf_arg_idx_map=udf_arg_idx_map,
        output_schema=output_schema,
    )

    from pyspark.sql.functions import col, pandas_udf, from_json

    input_columns = [f"`{c.name}`" for c in input_df.schema]
    _online_udf = pandas_udf(builder._udf_wrapper, StringType())
    if namespace is None:
        namespace = name
    output_columns = [col(f"_json.{c.name}").alias(f"{namespace}.{c.name}") for c in output_schema]
    reduced_input_columns = [col for col in input_columns if "_udf_internal_" not in col]
    return input_df.select(*input_columns, from_json(_online_udf(*input_columns), output_schema).alias("_json")).select(
        *reduced_input_columns, *output_columns
    )


def transformation_type_checker(object_name, result, mode, supported_modes):
    possible_mode = None
    for candidate_mode, candidate_type in MODE_TO_TYPE_LOOKUP.items():
        if isinstance(result, candidate_type):
            possible_mode = candidate_mode
            break
    expected_type = MODE_TO_TYPE_LOOKUP[mode]
    actual_type = type(result)

    if isinstance(result, expected_type):
        return
    elif possible_mode is not None and possible_mode in supported_modes:
        raise TypeError(
            f"Transformation function {object_name} with mode '{mode}' is expected to return result with type {expected_type}, but returns result with type {actual_type} instead. Did you mean to set mode='{possible_mode}'?"
        )
    else:
        raise TypeError(
            f"Transformation function {object_name} with mode {mode} is expected to return result with type {expected_type}, but returns result with type {actual_type} instead."
        )


def run_mock_pandas_pipeline(pipeline: Pipeline, transformations, name, mock_inputs):
    builder = _PandasPipelineBuilder(
        name=name,
        pipeline=pipeline,
        transformations=transformations,
        udf_arg_idx_map={},
        output_schema=None,
        mock_inputs=mock_inputs,
    )
    return builder._udf_node_to_value(pipeline.root)


def pipeline_to_dataframe(
    spark: SparkSession,
    pipeline: Pipeline,
    consume_streaming_data_sources: bool,
    virtual_data_sources: List[VirtualDataSource],
    transformations: List[NewTransformation],
    feature_time_limits: Optional[pendulum.Period] = None,
    schedule_interval: Optional[pendulum.Duration] = None,
    mock_inputs: Optional[Dict[str, DataFrame]] = None,
    # TODO(FV3-cleanup): Remove after the migration
    DO_NOT_USE_vds_df_override: Optional[DataFrame] = None,
    called_for_schema_computation: Optional[bool] = False,
) -> DataFrame:
    return _PipelineBuilder(
        spark,
        pipeline,
        consume_streaming_data_sources,
        virtual_data_sources,
        transformations,
        feature_time_limits,
        schedule_interval=schedule_interval,
        mock_inputs=mock_inputs,
        DO_NOT_USE_vds_df_override=DO_NOT_USE_vds_df_override,
        called_for_schema_computation=called_for_schema_computation,
    ).get_dataframe()


# (validly) assumes we have at most a single request data source in the pipeline
def find_request_context(node: PipelineNode) -> Optional[RequestContext]:
    if node.HasField("request_data_source_node"):
        return node.request_data_source_node.request_context
    elif node.HasField("transformation_node"):
        for child in node.transformation_node.inputs:
            rc = find_request_context(child.node)
            if rc is not None:
                return rc
    return None


def get_all_input_keys(node: PipelineNode) -> Set[str]:
    names_set = set()
    _get_all_input_keys_helper(node, names_set)
    return names_set


def _get_all_input_keys_helper(node: PipelineNode, names_set: Set[str]):
    if node.HasField("request_data_source_node"):
        names_set.add(node.request_data_source_node.input_name)
    elif node.HasField("data_source_node"):
        names_set.add(node.data_source_node.input_name)
    elif node.HasField("feature_view_node"):
        names_set.add(node.feature_view_node.input_name)
    elif node.HasField("transformation_node"):
        for child in node.transformation_node.inputs:
            _get_all_input_keys_helper(child.node, names_set)
    return names_set


# This class is for Spark pipelines
class _PipelineBuilder:
    _CONSTANT_TYPE = Optional[Union[str, int, float, bool]]
    # The value of internal nodes in the tree
    _VALUE_TYPE = Union[DataFrame, _CONSTANT_TYPE, BaseMaterializationContext]

    def __init__(
        self,
        spark: SparkSession,
        pipeline: Pipeline,
        consume_streaming_data_sources: bool,
        virtual_data_sources: List[VirtualDataSource],
        # we only use mode and name from these
        transformations: Union[List[NewTransformation], List[NewTransformationArgs]],
        feature_time_limits: Optional[pendulum.Period],
        schedule_interval: Optional[pendulum.Duration] = None,
        mock_inputs: Optional[Dict[str, DataFrame]] = None,
        DO_NOT_USE_vds_df_override: Optional[DataFrame] = None,
        called_for_schema_computation: Optional[bool] = False,
    ):
        self._spark = spark
        self._pipeline = pipeline
        self._consume_streaming_data_sources = consume_streaming_data_sources
        self._feature_time_limits = feature_time_limits
        self._id_to_vds = {IdHelper.to_string(vds.virtual_data_source_id): vds for vds in virtual_data_sources}
        self._id_to_transformation = {IdHelper.to_string(t.transformation_id): t for t in transformations}

        self._registered_temp_view_names: List[str] = []
        self._schedule_interval = schedule_interval
        self._DO_NOT_USE_vds_df_override = DO_NOT_USE_vds_df_override
        self._called_for_schema_computation = called_for_schema_computation

        self._mock_inputs = mock_inputs

    def get_dataframe(self) -> DataFrame:
        df = self._node_to_value(self._pipeline.root)
        # Cleanup any temporary tables created during the process
        if self._DO_NOT_USE_vds_df_override is None:
            # Not dropping temp views is needed during validation; temp views will get cleaned up when
            # the cluster restarts. Number of validation runs will be small.
            for temp_name in self._registered_temp_view_names:
                self._spark.sql(f"DROP TABLE {temp_name}")
        assert isinstance(df, DataFrame)
        return df

    def _node_to_value(self, pipeline_node: PipelineNode) -> _VALUE_TYPE:
        if pipeline_node.HasField("transformation_node"):
            return self._transformation_node_to_dataframe(pipeline_node.transformation_node)
        elif pipeline_node.HasField("data_source_node"):
            if self._mock_inputs is not None:
                return self._mock_inputs[pipeline_node.data_source_node.input_name]
            else:
                return self._data_source_node_to_dataframe(pipeline_node.data_source_node)
        elif pipeline_node.HasField("constant_node"):
            return self._constant_node_to_value(pipeline_node.constant_node)
        elif pipeline_node.HasField("materialization_context_node"):
            if self._feature_time_limits is not None:
                feature_start_time = self._feature_time_limits.start
                feature_end_time = self._feature_time_limits.end
                batch_schedule = self._schedule_interval
            else:
                feature_start_time = pendulum.from_timestamp(0, pendulum.tz.UTC)
                feature_end_time = pendulum.datetime(2100, 1, 1)
                batch_schedule = self._schedule_interval or pendulum.duration()
            return BoundMaterializationContext._create_internal(feature_start_time, feature_end_time, batch_schedule)
        elif pipeline_node.HasField("request_data_source_node"):
            raise ValueError("RequestDataSource is not supported in Spark pipelines")
        elif pipeline_node.HasField("feature_view_node"):
            raise ValueError("Dependent FeatureViews are not supported in Spark pipelines")
        else:
            raise KeyError(f"Unknown PipelineNode type: {pipeline_node}")

    def _transformation_node_to_dataframe(self, transformation_node: TransformationNode) -> DataFrame:
        """Recursively translates inputs to values and then passes them to the transformation."""
        args: List[Union[DataFrame, str, int, float, bool]] = []
        kwargs = {}
        for transformation_input in transformation_node.inputs:
            node_value = self._node_to_value(transformation_input.node)
            if transformation_input.HasField("arg_index"):
                assert len(args) == transformation_input.arg_index
                args.append(node_value)
            elif transformation_input.HasField("arg_name"):
                kwargs[transformation_input.arg_name] = node_value
            else:
                raise KeyError(f"Unknown argument type for Input node: {transformation_input}")

        return self._apply_transformation_function(transformation_node, args, kwargs)

    def _apply_transformation_function(self, transformation_node, args, kwargs) -> Union[DataFrame, pd.DataFrame]:
        """For the given transformation node, returns the corresponding DataFrame transformation.

        If needed, resulted function is wrapped with a function that translates mode-specific input/output types to DataFrames.
        """
        transformation = self._id_to_transformation[IdHelper.to_string(transformation_node.transformation_id)]
        user_function = function_serialization.from_proto(transformation.user_function)
        transformation_name = self._transformation_name(transformation)

        if transformation.transformation_mode == TransformationMode.TRANSFORMATION_MODE_PYSPARK:
            res = user_function(*args, **kwargs)
            transformation_type_checker(transformation_name, res, "pyspark", self._possible_modes())
            return res
        elif transformation.transformation_mode == TransformationMode.TRANSFORMATION_MODE_SPARK_SQL:
            # type checking happens inside this function
            return self._wrap_sql_function(transformation_node, user_function)(*args, **kwargs)
        elif transformation.transformation_mode == TransformationMode.TRANSFORMATION_MODE_PANDAS:
            res = user_function(*args, **kwargs)
            transformation_type_checker(transformation_name, res, "pandas", self._possible_modes())
            return res
        else:
            raise KeyError(f"Unknown transformation mode: {transformation.transformation_mode}")

    def _wrap_sql_function(
        self, transformation_node: TransformationNode, user_function: Callable[..., str]
    ) -> Callable[..., DataFrame]:
        def wrapped(*args, **kwargs):
            wrapped_args = []
            for arg, node_input in zip(args, self._positional_inputs(transformation_node)):
                wrapped_args.append(self._wrap_node_inputvalue(node_input, arg))
            keyword_inputs = self._keyword_inputs(transformation_node)
            wrapped_kwargs = {}
            for k, v in kwargs.items():
                node_input = keyword_inputs[k]
                wrapped_kwargs[k] = self._wrap_node_inputvalue(node_input, v)
            sql_string = user_function(*wrapped_args, **wrapped_kwargs)
            transformation_name = self._transformation_name(
                self._id_to_transformation[IdHelper.to_string(transformation_node.transformation_id)]
            )
            transformation_type_checker(transformation_name, sql_string, "spark_sql", self._possible_modes())
            return self._spark.sql(sql_string)

        return wrapped

    def _wrap_node_inputvalue(
        self, node_input, value: _VALUE_TYPE
    ) -> Optional[Union[InputProto, str, int, float, bool]]:
        if node_input.node.HasField("constant_node"):
            assert (
                isinstance(value, str)
                or isinstance(value, int)
                or isinstance(value, float)
                or isinstance(value, bool)
                or value is None
            )
            return value
        elif node_input.node.HasField("materialization_context_node"):
            assert isinstance(value, BoundMaterializationContext)
            return value
        else:
            assert isinstance(value, DataFrame)
            return self._register_temp_table(self._node_name(node_input.node), value)

    def _node_name(self, node) -> str:
        """Returns a human-readable name for the node."""
        if node.HasField("transformation_node"):
            name = self._transformation_name(
                self._id_to_transformation[IdHelper.to_string(node.transformation_node.transformation_id)]
            )
            return f"transformation_{name}_output"
        elif node.HasField("data_source_node"):
            if node.data_source_node.HasField("input_name"):
                return node.data_source_node.input_name
            # TODO(TEC-5076): remove this legacy code, since input_name will always be set
            name = self._id_to_vds[IdHelper.to_string(node.data_source_node.virtual_data_source_id)].fco_metadata.name
            return f"data_source_{name}_output"
        else:
            raise Exception(f"Expected transformation or data source node: {node}")

    def _register_temp_table(self, name: str, df: DataFrame) -> str:
        """Registers a Dataframe as a temp table and returns its name."""
        unique_name = name + self._random_suffix()
        self._registered_temp_view_names.append(unique_name)
        df.createOrReplaceTempView(unique_name)
        return unique_name

    def _random_suffix(self) -> str:
        return "".join(random.choice(string.ascii_letters) for i in range(6))

    def _positional_inputs(self, transformation_node) -> List[InputProto]:
        """Returns the positional inputs of transformation_node in order."""
        return [node_input for node_input in transformation_node.inputs if node_input.HasField("arg_index")]

    def _keyword_inputs(self, transformation_node) -> Dict[str, InputProto]:
        """Returns the keyword inputs of transformation_node in a dict."""
        return {
            node_input.arg_name: node_input
            for node_input in transformation_node.inputs
            if node_input.HasField("arg_name")
        }

    def _data_source_node_to_dataframe(self, data_source_node: DataSourceNode) -> DataFrame:
        """Creates a DataFrame from a VDS and time parameters."""
        if self._DO_NOT_USE_vds_df_override is not None:
            return self._DO_NOT_USE_vds_df_override

        vds = self._id_to_vds[IdHelper.to_string(data_source_node.virtual_data_source_id)]
        time_window = self._get_time_window_from_data_source_node(data_source_node)
        return data_source_helper.get_vds_dataframe(
            self._spark,
            vds,
            self._consume_streaming_data_sources,
            raw_data_time_limits=time_window,
            called_for_schema_computation=self._called_for_schema_computation,
            fwv3=True,
        )

    def _get_time_window_from_data_source_node(self, data_source_node: DataSourceNode) -> Optional[pendulum.Period]:
        raw_data_limits = self._feature_time_limits
        if data_source_node.HasField("window") and raw_data_limits:
            new_start = raw_data_limits.start - time_utils.proto_to_duration(data_source_node.window)
            if self._schedule_interval:
                new_start = new_start + self._schedule_interval
            raw_data_limits = pendulum.Period(new_start, raw_data_limits.end)
        elif data_source_node.window_unbounded_preceding and raw_data_limits:
            raw_data_limits = pendulum.Period(pendulum.datetime(1970, 1, 1), raw_data_limits.end)
        return raw_data_limits

    def _constant_node_to_value(self, constant_node: ConstantNode) -> _CONSTANT_TYPE:
        if constant_node.HasField("string_const"):
            return constant_node.string_const
        elif constant_node.HasField("int_const"):
            return int(constant_node.int_const)
        elif constant_node.HasField("float_const"):
            return float(constant_node.float_const)
        elif constant_node.HasField("bool_const"):
            return constant_node.bool_constant
        elif constant_node.HasField("null_const"):
            return None
        raise KeyError(f"Unknown ConstantNode type: {constant_node}")

    def _possible_modes(self):
        # note that pipeline is included since this is meant to be a user hint, and it's
        # theoretically possible a pipeline wound up deeper than expected
        return ["pyspark", "spark_sql", "pipeline"]

    @staticmethod
    def _transformation_name(transformation: Union[NewTransformation, NewTransformationArgs]) -> str:
        if isinstance(transformation, NewTransformation):
            return transformation.fco_metadata.name
        elif isinstance(transformation, NewTransformationArgs):
            return transformation.info.name
        else:
            # should ideally never be thrown
            raise Exception(
                f"Invalid type (expected NewTransformation or NewTransformationArgs): {type(transformation)}"
            )


# We need to take the call a udf constructed from the pipeline that will generate the on-demand features.
# A pandas udf takes as inputs (pd.Series...) and outputs pd.Series.
# However, the user-defined transforms take as input pd.DataFrame and output pd.DataFrame.
# We use _PandasPipelineBuilder to construct a udf wrapper function that translates the inputs and outputs and
# performs some type checking.
#
# The general idea is that each Node of the pipeline evaluates to a pandas.DataFrame.
# This is what we want since the user-defined transforms take pandas.DataFrame as inputs both from RequestDataSourceNode or FeatureViewNode.
# _udf_wrapper then typechecks and translates the final pandas.DataFrame into a jsonized pandas.Series to match what spark expects.
class _PandasPipelineBuilder(_PipelineBuilder):
    def __init__(
        self,
        name: str,
        pipeline: Pipeline,
        transformations: List[NewTransformation],
        # maps input + feature name to arg index that udf function wrapper will be called with.
        # this is needed because we need to know which pd.Series that are inputs to this function correspond to the desired request context fields or dependent fv features that the customer-defined udf uses.
        udf_arg_idx_map: Dict[str, int],
        output_schema: StructType,
        mock_inputs: Optional[Dict[str, DataFrame]] = None,
    ):
        self._pipeline = pipeline
        self._name = name
        self.udf_arg_idx_map = udf_arg_idx_map
        self._id_to_transformation = {IdHelper.to_string(t.transformation_id): t for t in transformations}
        self._output_schema = output_schema
        self._mock_inputs = mock_inputs

    def _udf_wrapper(self, *args):
        SPARK_TO_PANDAS_TYPES = {
            LongType(): "int64",
            DoubleType(): "float64",
            StringType(): "object",
            BooleanType(): "bool",
        }

        # self.udf_arg_idx_map tells us which of these pd.Series correspond to a given RequestContext or FeatureView input
        self._udf_args: List[pd.Series] = args

        import pandas as pd
        import json

        output_df = self._udf_node_to_value(self._pipeline.root)

        assert (
            type(output_df) == pd.DataFrame
        ), f"transformer returns {str(output_df)}, but must return a pandas.DataFrame instead."

        for field in self._output_schema:
            assert field.name in output_df.columns, (
                f"Expected output schema field '{field.name}' not found in columns of DataFrame returned by "
                f"'{self._name}': [" + ", ".join(output_df.columns) + "]"
            )
            assert SPARK_TO_PANDAS_TYPES[field.dataType] == output_df[field.name].dtype.name, (
                f"DataFrame field '{field.name}' returned from '{self._name}' has type '{output_df[field.name].dtype.name}', "
                f"but is expected to have Pandas dtype '{SPARK_TO_PANDAS_TYPES[field.dataType]}' (corresponding to Spark type {field.dataType.__class__.__name__}). "
                "See https://pandas.pydata.org/pandas-docs/stable/getting_started/basics.html#dtypes for more info on Pandas dtypes."
            )

        output_strs = []

        # itertuples() is used instead of iterrows() to preserve type safety.
        # See notes in https://pandas.pydata.org/pandas-docs/version/0.17.1/generated/pandas.DataFrame.iterrows.html.
        for row in output_df.itertuples(index=False):
            output_strs.append(json.dumps(row._asdict()))

        return pd.Series(output_strs)

    def _transformation_node_to_online_dataframe(self, transformation_node: TransformationNode) -> pd.DataFrame:
        """Recursively translates inputs to values and then passes them to the transformation."""
        args: List[Union[DataFrame, str, int, float, bool]] = []
        kwargs = {}
        for transformation_input in transformation_node.inputs:
            node_value = self._udf_node_to_value(transformation_input.node)
            if transformation_input.HasField("arg_index"):
                assert len(args) == transformation_input.arg_index
                args.append(node_value)
            elif transformation_input.HasField("arg_name"):
                kwargs[transformation_input.arg_name] = node_value
            else:
                raise KeyError(f"Unknown argument type for Input node: {transformation_input}")

        return self._apply_transformation_function(transformation_node, args, kwargs)

    # evaluate a node in the Pipeline
    def _udf_node_to_value(
        self, pipeline_node: PipelineNode
    ) -> Union[str, int, float, bool, None, pd.DataFrame, DataFrame, pd.Series]:
        if pipeline_node.HasField("constant_node"):
            return self._constant_node_to_value(pipeline_node.constant_node)
        elif pipeline_node.HasField("feature_view_node"):
            if self._mock_inputs is not None:
                return self._mock_inputs[pipeline_node.feature_view_node.input_name]
            else:
                all_series = []
                features = []
                # The input name of this FeatureViewNode tells us which of the udf_args correspond to the pandas.DataFrame we should generate that the parent TransformationNode expects as an input.
                # It also expects the DataFrame to have its columns named by the feature names.
                for feature in self.udf_arg_idx_map:
                    if not feature.startswith(f"_udf_internal_{pipeline_node.feature_view_node.input_name}"):
                        continue
                    idx = self.udf_arg_idx_map[feature]
                    all_series.append(self._udf_args[idx])
                    features.append(feature.split(".")[1])
                df = pd.concat(all_series, keys=features, axis=1)
                return df
        elif pipeline_node.HasField("request_data_source_node"):
            if self._mock_inputs is not None:
                return self._mock_inputs[pipeline_node.request_data_source_node.input_name]
            else:
                all_series = []
                request_context = pipeline_node.request_data_source_node.request_context
                field_names = [field.name for field in request_context.schema.fields]
                for input_col in field_names:
                    idx = self.udf_arg_idx_map[input_col]
                    all_series.append(self._udf_args[idx])
                df = pd.concat(all_series, keys=field_names, axis=1)
                return df
        elif pipeline_node.HasField("transformation_node"):
            return self._transformation_node_to_online_dataframe(pipeline_node.transformation_node)
        elif pipeline_node.HasField("materialization_context_node"):
            raise ValueError("MaterializationContext is unsupported for pandas pipelines")
        else:
            raise NotImplementedError("This is not yet implemented")

    def _possible_modes(self):
        # note that pipeline is included since this is meant to be a user hint, and it's
        # theoretically possible a pipeline wound up deeper than expected
        return ["pandas", "pipeline"]
