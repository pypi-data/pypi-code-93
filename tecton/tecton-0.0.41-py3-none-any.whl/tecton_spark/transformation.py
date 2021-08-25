from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import pandas as pd
import pendulum
from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql.types import AtomicType
from pyspark.sql.types import BooleanType
from pyspark.sql.types import DoubleType
from pyspark.sql.types import LongType
from pyspark.sql.types import StringType
from pyspark.sql.types import StructType

from tecton_proto.args.data_source_config_pb2 import DataSourceConfig
from tecton_proto.args.data_source_config_pb2 import DataSourceConfig as DataSourceConfigProto
from tecton_proto.args.transformation_pb2 import RequestContext as RequestContextProto
from tecton_proto.args.transformation_pb2 import TransformationType
from tecton_proto.common.id_pb2 import Id
from tecton_proto.data.transformation_pb2 import Transformation as TransformationDataProto
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource as VirtualDataSourceProto
from tecton_spark import data_source_helper
from tecton_spark import errors
from tecton_spark import function_serialization as func_ser
from tecton_spark.id_helper import IdHelper
from tecton_spark.materialization_common import MaterializationContext
from tecton_spark.schema import Schema
from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper

InputType = Union["VirtualDataSourceProto", "TransformationDataProto"]
TRANSFORMATION_TEMP_VIEW_PREFIX = "_tecton_transformation_"

VALID_FEATURE_SERVER_TYPES = [LongType(), DoubleType(), StringType(), BooleanType()]
VALID_FEATURE_SERVER_TYPES_ERROR_STR = ", ".join([str(t) for t in VALID_FEATURE_SERVER_TYPES])


class RequestContext:
    """
    RequestContext defines an input context for OnlineTransformations.
    """

    def __init__(self, schema: Dict[str, AtomicType]):
        """
        Creates a RequestContext.

        :param schema: Dictionary mapping string -> data types. Supported types are LongType, DoubleType, StringType, BooleanType.
        """
        for field, typ in schema.items():
            if typ not in VALID_FEATURE_SERVER_TYPES:
                raise errors.TectonValidationError(
                    f"RequestContext schema type {typ} for field '{field}' not supported. Expected one of {VALID_FEATURE_SERVER_TYPES_ERROR_STR}"
                )

        self.arg_to_schema = schema

    def _to_proto(self) -> RequestContextProto:
        s = StructType()
        for field, typ in self.arg_to_schema.items():
            s.add(field, typ)
        wrapper = SparkSchemaWrapper(s)
        return RequestContextProto(schema=wrapper.to_proto())

    def _set_schema_field_order(self, schema_field_order: List[str]):
        """
        Forces an ordering for schemas with multiple fields.

        :param schema_field_order: Ordered list of schema fields.
        """
        assert set(schema_field_order) == set(self.arg_to_schema.keys()) and len(schema_field_order) == len(
            self.arg_to_schema.keys()
        ), f"Schema ordering fields {schema_field_order} must contain the same elements as schema dictionary keys {list(self.arg_to_schema.keys())}."
        new_schema = {}
        for field in schema_field_order:
            new_schema[field] = self.arg_to_schema[field]
        self.arg_to_schema = new_schema

    @classmethod
    def _from_proto(cls, proto: RequestContextProto):
        wrapper = SparkSchemaWrapper.from_proto(proto.schema)
        schema_dict = {field: typ for field, typ in wrapper.column_name_types()}
        return RequestContext(schema=schema_dict)

    def _merge(self, other):
        for field in other.arg_to_schema:
            if field in self.arg_to_schema:
                # should not happen
                assert (
                    self.arg_to_schema[field] == other.arg_to_schema[field]
                ), f"Mismatched request context field types for {field}"
            else:
                self.arg_to_schema[field] = other.arg_to_schema[field]


class Transformation:
    """
    Defines DataFrame-based transformations.
    """

    def __init__(
        self,
        *,
        name: str,
        description: str,
        inputs: List[InputType],
        transformer: Callable[..., Union[DataFrame, str, pd.Series, pd.DataFrame]],
        transformation_type: TransformationType,
        has_context: bool,
        transformation_pb2_map: Dict[str, TransformationDataProto],
        transformation_id_pb2: Id,
        vds_pb2_map: Optional[Dict[str, VirtualDataSourceProto]] = None,
        request_context: Optional[RequestContext] = None,
        output_schema: Optional[StructType] = None,
    ):
        """
        :param name: Unique, human friendly name that identifies the Transformation
        :param description: Short description of the Transformation
        :param inputs: List of inputs for the Transformation. Each input can be
                       either a VirtualDataSourceProto or TransformationProto.
        :param transformer: A function that takes input DataFrames or temp views and outputs the transformed DataFrame
                            or SQL, depending on the type of the transformation.
                            The function parameters will preserve the order of the inputs provided by the "input" argument.
                            If has_context=True the context is passed as the first parameter to transformer.
        :param transformation_type: SQL, PYSPARK, or ONLINE
        :param has_context: Whether or not the transformer function uses context.
        :param transformation_pb2_map: Map from string(ID) to Transformation protos containing this Transformation and its upstream dependencies.
        :param transformation_id_pb2: ID of the Transformation data proto. This ID should be contained in transformation_pb2_map.
        :param vds_pb2_map: Map from string(ID) to VirtualDataSource protos containing any inputs to this Transformation or its upstream dependencies.
        :param request_context: (OnlineTransformation only) RequestContext object used to define inputs.
        :param output_schema: (OnlineTransformation only) StructType describing the schema of an output.
        """
        self.transformation_id_pb2 = transformation_id_pb2
        self.transformation_pb2_map = transformation_pb2_map
        self.vds_pb2_map = vds_pb2_map

        if "." in name:
            raise errors.TectonValidationError(
                f"Transformation name '{name}' cannot contain a dot. Please, remove it and try again."
            )

        if transformation_type == TransformationType.ONLINE:
            assert len(inputs) == 0
            assert not has_context
            assert request_context is not None
        else:
            assert request_context is None

        self.name = name
        self.description = description
        self.inputs = inputs
        self.transformer = transformer
        self.transformation_type = transformation_type
        self.has_context = has_context
        self.request_context = request_context
        self.output_schema = output_schema

    @classmethod
    def _from_data_proto(
        cls,
        transformation_id_pb2: Id,
        transformation_pb2_map: Dict[str, TransformationDataProto],
        vds_pb2_map: Dict[str, VirtualDataSourceProto],
    ):
        transformation_pb2 = transformation_pb2_map[IdHelper.to_string(transformation_id_pb2)]
        transformer = func_ser.from_proto(transformation_pb2.transformer, scope={})
        inputs = []
        for input_pb2 in transformation_pb2.inputs:
            if input_pb2.HasField("transformation_id"):
                inputs.append(transformation_pb2_map[IdHelper.to_string(input_pb2.transformation_id)])
            elif input_pb2.HasField("virtual_data_source_id"):
                inputs.append(vds_pb2_map[IdHelper.to_string(input_pb2.virtual_data_source_id)])
            else:
                raise Exception("Invalid state! Neither of transformation_id or virtual_data_source_id is set.")

        if transformation_pb2.transformation_type == TransformationType.SQL:
            return SQLTransformation(
                name=transformation_pb2.fco_metadata.name,
                description=transformation_pb2.fco_metadata.description,
                inputs=inputs,
                transformer=transformer,
                has_context=transformation_pb2.has_context,
                transformation_pb2_map=transformation_pb2_map,
                vds_pb2_map=vds_pb2_map,
                transformation_id_pb2=transformation_pb2.transformation_id,
            )
        elif transformation_pb2.transformation_type == TransformationType.PYSPARK:
            return PySparkTransformation(
                name=transformation_pb2.fco_metadata.name,
                description=transformation_pb2.fco_metadata.description,
                inputs=inputs,
                transformer=transformer,
                has_context=transformation_pb2.has_context,
                transformation_pb2_map=transformation_pb2_map,
                vds_pb2_map=vds_pb2_map,
                transformation_id_pb2=transformation_pb2.transformation_id,
            )
        elif transformation_pb2.transformation_type == TransformationType.ONLINE:
            return OnlineTransformation(
                name=transformation_pb2.fco_metadata.name,
                description=transformation_pb2.fco_metadata.description,
                transformer=transformer,
                request_context=RequestContext._from_proto(transformation_pb2.request_context),
                output_schema=SparkSchemaWrapper.from_proto(transformation_pb2.output_schema)._schema,
                transformation_pb2_map=transformation_pb2_map,
                transformation_id_pb2=transformation_pb2.transformation_id,
            )
        else:
            raise errors.TectonValidationError(
                f"Unsupported Transformation type {transformation_pb2.transformation_type}"
            )

    def _get_data_source_configs(self, config_map: Dict[str, Tuple[DataSourceConfigProto, VirtualDataSourceProto]]):
        """
        Get virtual data sources and corresponding data source configs that this
        transformation DAG depends on.
        """
        if self.vds_pb2_map is not None:
            for vds_pb2 in self.vds_pb2_map.values():
                if vds_pb2.fco_metadata.name not in config_map:
                    dsc = DataSourceConfig()
                    dsc.virtual_data_source_id.CopyFrom(vds_pb2.virtual_data_source_id)
                    config_map[vds_pb2.fco_metadata.name] = (dsc, vds_pb2)

    @classmethod
    def _get_feature_package_view_schema(
        cls,
        spark: SparkSession,
        view_sql: Optional[str],
        transformation: "Transformation",
        dscs,
        id_to_vds_map,
    ) -> Schema:
        """
        Deprecated. Use _get_transformation_spark_schema whenever possible (https://tecton.atlassian.net/browse/TEC-2570)
        Returns a schema in the Schema proto format. This is used for schemas computed and stored
        as part of FeaturePackage protos.
        """
        if transformation is not None:
            schema = Transformation._get_df_schema(spark, transformation)
        else:
            for dsc in dscs:
                vds = id_to_vds_map[IdHelper.to_string(dsc.virtual_data_source_id)]
                data_source_helper.register_temp_view_for_data_source(
                    spark,
                    vds,
                    register_stream=False,
                    called_for_schema_computation=True,
                    data_source_config=dsc,
                    fwv3=False,
                )
            schema = spark.sql(view_sql).schema

        return Schema.from_spark(schema)

    @classmethod
    def _get_df_schema(cls, spark, transformation: "Transformation") -> StructType:
        return transformation.dataframe(spark, called_for_schema_computation=True).schema

    @classmethod
    def _get_transformation_spark_schema(cls, spark, transformation: "Transformation") -> SparkSchemaWrapper:
        """
        Returns a schema in the SparkSchema proto format. Use this schema format whenever possible instead of
        the format returned by _get_feature_package_view_schema().
        """
        return SparkSchemaWrapper(Transformation._get_df_schema(spark, transformation))

    def dataframe(
        self,
        spark: SparkSession,
        time_range: Optional[pendulum.Period] = None,
        context: Optional[MaterializationContext] = None,
        called_for_schema_computation: bool = False,
    ):
        """
        Returns a dataframe based on the output of this transformation.

        :param spark: Spark session.
        :param time_range: (Optional) time limits to apply to all of the upstream VirtualDataSources.
        :param context: (Optional) materialization context for parameterizing transformations.

        :return: Spark DataFrame.
        """
        config_map: Dict[str, Tuple[DataSourceConfigProto, VirtualDataSourceProto]] = {}
        self._get_data_source_configs(config_map)
        for dsc, vds in config_map.values():
            name = vds.fco_metadata.name
            data_source_helper.register_temp_view_for_data_source(
                spark,
                vds,
                register_stream=False,
                raw_data_time_limits=time_range,
                called_for_schema_computation=called_for_schema_computation,
                data_source_config=dsc,
                fwv3=False,
            )
        if context is None:
            context = MaterializationContext.default()
        return self._dataframe(spark=spark, context=context)

    def _dataframe_for_materialization(self, spark: SparkSession, context: MaterializationContext):
        assert (
            self.transformation_type != TransformationType.ONLINE
        ), "OnlineTransformations cannot be used for materialized FeaturePackages."
        return self._dataframe(spark=spark, context=context)

    def _get_output_of_dependency(
        self, *, spark: SparkSession, input: InputType, context: MaterializationContext
    ) -> Union[str, DataFrame]:
        """Return the output dataframe or temp view of the given the transformation input."""
        if isinstance(input, VirtualDataSourceProto):
            return f"`{input.fco_metadata.name}`"
        elif isinstance(input, TransformationDataProto):
            return Transformation._from_data_proto(
                transformation_id_pb2=input.transformation_id,
                transformation_pb2_map=self.transformation_pb2_map,
                vds_pb2_map=self.vds_pb2_map or {},
            )._dataframe(spark=spark, context=context)
        else:
            raise Exception(
                f"Invalid input type {type(input)} to Transformation '{self.name}'. Expected either VirtualDataSource proto or Transformation proto"
            )

    def _dataframe(self, *, spark: SparkSession, context: MaterializationContext):
        raise NotImplementedError(
            "You can't use Transformation directly. Use one of its subclasses: SQLTransformation or PySparkTransformation."
        )

    def __str__(self):
        return f"{self.__class__.__name__}(name='{self.name}', description='{self.description}', transformer=...)"

    def __repr__(self):
        return str(self)


class PySparkTransformation(Transformation):
    """
    (Tecton Primitive) PysparkTransformation class.

    The PysparkTransformation class defines a Pyspark-based transformation.

    Pyspark Transformations are Transformations defined by a Pyspark function that is applied to one or many input
    DataFrames or raw data sources.
    """

    def __init__(
        self,
        *,
        name: str,
        inputs: Union[InputType, List[InputType]],
        transformer: Callable[..., DataFrame],
        has_context: bool = False,
        description: str = "",
        transformation_pb2_map: Dict[str, TransformationDataProto],
        vds_pb2_map: Dict[str, VirtualDataSourceProto],
        transformation_id_pb2: Id,
    ):
        """
        Instantiates a PysparkTransformation.

        :param name: Unique, human friendly name that identifies the Transformation
        :param description: Short description of the Transformation
        :param inputs: One or more inputs for the Transformation. Each input can be
                       either a VirtualDataSource, or another Transformation
        :param transformer: A function that takes input DataFrames or temp views and outputs the transformed DataFrame.
                            The function parameters will preserve the order of the inputs provided by the "input" argument.
        """
        super().__init__(
            name=name,
            description=description,
            inputs=inputs,
            transformer=transformer,
            transformation_type=TransformationType.PYSPARK,
            has_context=has_context,
            transformation_pb2_map=transformation_pb2_map,
            transformation_id_pb2=transformation_id_pb2,
            vds_pb2_map=vds_pb2_map,
        )

    def _dataframe(self, *, spark: SparkSession, context: MaterializationContext):
        dataframes = []
        for input in self.inputs:
            output = self._get_output_of_dependency(spark=spark, input=input, context=context)
            if isinstance(output, str):
                dataframe = spark.table(output)
            else:
                dataframe = output
            dataframes.append(dataframe)
        if self.has_context:
            return self.transformer(context, *dataframes)
        else:
            return self.transformer(*dataframes)


class SQLTransformation(Transformation):
    """
    (Tecton Primitive) SQLTransformation Class.

    The SQLTransformation class defines a SQL-based transformation.

    SQLTransformations are Transformations defined by a SQL string that is applied to one or many input DataFrames or
    raw data sources.
    """

    def __init__(
        self,
        *,
        name: str,
        inputs: Union[InputType, List[InputType]],
        transformer: Callable[..., DataFrame],
        has_context: bool = False,
        description: str = "",
        transformation_pb2_map: Dict[str, TransformationDataProto],
        vds_pb2_map: Dict[str, VirtualDataSourceProto],
        transformation_id_pb2: Id,
    ):
        """
        :param name: Unique, human friendly name that identifies the Transformation
        :param description: Short description of the Transformation
        :param inputs: One or more inputs for the Transformation. Each input can be
                       either a VirtualDataSource, or another Transformation
        :param transformer: A function that takes input DataFrames or temp views and outputs the transformed DataFrame.
                            The function parameters will preserve the order of the inputs provided by the "input" argument.
        """
        super().__init__(
            name=name,
            description=description,
            inputs=inputs,
            transformer=transformer,
            transformation_type=TransformationType.SQL,
            has_context=has_context,
            transformation_pb2_map=transformation_pb2_map,
            transformation_id_pb2=transformation_id_pb2,
            vds_pb2_map=vds_pb2_map,
        )

    def _dataframe(self, *, spark: SparkSession, context: MaterializationContext):
        temp_views = []
        for input in self.inputs:
            output = self._get_output_of_dependency(spark=spark, input=input, context=context)
            if isinstance(output, DataFrame):
                input_name = input.fco_metadata.name if isinstance(input, TransformationDataProto) else input.name
                temp_view = TRANSFORMATION_TEMP_VIEW_PREFIX + input_name
                output.createOrReplaceTempView(temp_view)
            else:
                temp_view = output
            temp_views.append(temp_view)
        if self.has_context:
            return spark.sql(self.transformer(context, *temp_views))
        else:
            return spark.sql(self.transformer(*temp_views))


class OnlineTransformation(Transformation):
    """
    (Tecton Primitive) OnlineTransformation class.

    The OnlineTransformation class defines an online transformation.

    OnlineTransformations are Pandas UDF-based Transformations that are applied at retrieval time.
    OnlineTransformations operate on a RequestContext which is supplied at retrieval time.
    """

    def __init__(
        self,
        *,
        name: str,
        request_context: RequestContext,
        transformer: Callable[..., pd.Series],
        output_schema: StructType,
        description: str = "",
        transformation_pb2_map: Dict[str, TransformationDataProto],
        transformation_id_pb2: Id,
    ):
        """
        Constructs an OnlineTransformation.

        :param name: Unique, human friendly name that identifies the Transformation
        :param description: Short description of the Transformation
        :param request_context: RequestContext object that specifies input schema.
        :param transformer: Pandas UDF function that accepts one or more pandas.Series inputs
                            (one for each field specified in RequestContext's schema) and returns
                            a pandas.DataFrame.
        :param output_schema: StructType describing the schema of an OnlineTransformation output.
        """
        super().__init__(
            name=name,
            description=description,
            inputs=[],
            transformer=transformer,
            transformation_type=TransformationType.ONLINE,
            has_context=False,
            request_context=request_context,
            output_schema=output_schema,
            transformation_pb2_map=transformation_pb2_map,
            transformation_id_pb2=transformation_id_pb2,
        )

    def dataframe_with_input(self, *, spark: SparkSession, input_df: DataFrame, join_keys: List[str] = []) -> DataFrame:
        """
        Returns a DataFrame containing the transformed result of an input DataFrame. For internal use only.

        :param spark: A SparkSession
        :param input_df: DataFrame to be transformed.
        :param join_keys: List of join keys columns. These are used for type validation and to ensure
                          there is no overlap with RequestContext schema columns.
        :return: DataFrame
        """
        from pyspark.sql.functions import from_json, pandas_udf

        assert self.request_context is not None
        assert self.transformation_type == TransformationType.ONLINE

        # A class that encapsulates the minimal dependency closure of UDFs containing
        # both the user specified UDF and our own wrapper.
        # This is necessary as long as we maintain the _udf shim.
        class _UDFWrapper:

            SPARK_TO_PANDAS_TYPES = {
                LongType(): "int64",
                DoubleType(): "float64",
                StringType(): "object",
                BooleanType(): "bool",
            }

            def __init__(self, name, tf, output_schema):
                self._name = name
                self._transformer = tf
                self._output_schema = output_schema

            # A wrapper around the user-specified UDF that serializes StructTypes to JSON and returns a pandas Series of StringTypes.
            # This is necessary since Spark <3.0.0 does not support scalar UDFs with StructType outputs. Once we start using
            # Spark 3.0.0 the _udf_wrapper shim can be removed and the customer-specified UDF can be invoked directly.
            def _udf(self, *args):
                import pandas as pd
                import json

                output_df = self._transformer(*args)

                assert (
                    type(output_df) == pd.DataFrame
                ), f"transformer returns {str(output_df)}, but must return a pandas.DataFrame instead."

                for field in self._output_schema:
                    assert field.name in output_df.columns, (
                        f"Expected output schema field '{field.name}' not found in columns of DataFrame returned by "
                        f"'{self._name}': [" + ", ".join(output_df.columns) + "]"
                    )
                    assert self.SPARK_TO_PANDAS_TYPES[field.dataType] == output_df[field.name].dtype.name, (
                        f"DataFrame field '{field.name}' returned from '{self._name}' has type '{output_df[field.name].dtype.name}', "
                        f"but is expected to have Pandas dtype '{self.SPARK_TO_PANDAS_TYPES[field.dataType]}' (corresponding to Spark type {field.dataType.__class__.__name__}). "
                        "See https://pandas.pydata.org/pandas-docs/stable/getting_started/basics.html#dtypes for more info on Pandas dtypes."
                    )

                output_strs = []

                # itertuples() is used instead of iterrows() to preserve type safety.
                # See notes in https://pandas.pydata.org/pandas-docs/version/0.17.1/generated/pandas.DataFrame.iterrows.html.
                for row in output_df.itertuples(index=False):
                    output_strs.append(json.dumps(row._asdict()))

                return pd.Series(output_strs)

        # Register UDF
        _wrapped_udf = _UDFWrapper(self.name, self.transformer, self.output_schema)._udf
        _online_udf = pandas_udf(_wrapped_udf, StringType())

        for col_name in join_keys:
            if col_name in list(self.request_context.arg_to_schema.keys()):
                raise errors.TectonValidationError(
                    f"Join key column '{col_name}' must not overlap with RequestContext schema columns: ["
                    + ", ".join(self.request_context.arg_to_schema.keys())
                    + "]"
                )

            if input_df.schema[col_name].dataType not in VALID_FEATURE_SERVER_TYPES:
                raise errors.TectonValidationError(
                    f"Join key column type {col_name} not supported. Found {input_df.schema[col_name].dataType.typeName()}, but expected one of {VALID_FEATURE_SERVER_TYPES_ERROR_STR}"
                )

        udf_args = []
        for input_field in self.request_context.arg_to_schema.keys():
            if input_field not in input_df.columns:
                raise errors.TectonValidationError(
                    f"RequestContext schema field {input_field} not found in spine columns "
                    + ", ".join(input_df.columns)
                )
            if input_df.schema[input_field].dataType != self.request_context.arg_to_schema[input_field]:
                raise errors.TectonValidationError(
                    "Found type {} for input {}, but expected {}".format(
                        str(input_df.schema[input_field].dataType),
                        input_field,
                        str(self.request_context.arg_to_schema[input_field]),
                    )
                )
            udf_args.extend([input_field])

        input_columns = [f"`{c.name}`" for c in input_df.schema]

        # Unpack the serialized JSON strings with the user-specified output_schema and explode the Struct into top level columns.
        return input_df.select(
            *input_columns, from_json(_online_udf(*udf_args), self.output_schema).alias("_json")
        ).select(*input_columns, "_json.*")

    def dataframe(
        self,
        spark: SparkSession,
        time_range: Optional[pendulum.Period] = None,
        context: Optional[MaterializationContext] = None,
        called_for_schema_computation: bool = False,
    ):
        """
        Returns an empty DataFrame with the OnlineTransformation's output schema. Internal use only.
        """
        return spark.createDataFrame([], self.output_schema)


class TransformationDataProtoDAG:
    transformations: List[Transformation] = []

    def __init__(
        self,
        *,
        transformations: List[Transformation],
    ):
        """
        Takes a list of Transformation python objects in topologically sorted order.
        This assumes the final element in the list is the terminal node of the Transformation DAG.
        """
        # Ensure the final node is the terminal node of the Transformation DAG.
        final_transformation = transformations[-1]
        for t in transformations[0:-1]:
            for input in t.inputs:
                if isinstance(input, TransformationDataProto):
                    assert (
                        input.transformation_id != final_transformation.transformation_id_pb2
                    ), "Final transformation is an input to another Transformation"
        self.transformations = transformations

    def final_transformation(self) -> Transformation:
        """
        Returns the terminal node of the Transformation DAG.
        """
        return self.transformations[-1]

    @classmethod
    def _filter_dependency_maps(
        cls,
        transformation_pb2: TransformationDataProto,
        transformation_pb2_map: Dict[str, TransformationDataProto],
        vds_pb2_map: Dict[str, VirtualDataSourceProto],
    ) -> Tuple[Dict[str, TransformationDataProto], Dict[str, VirtualDataSourceProto]]:
        """
        Given a terminal node (transformation_pb2), return filtered versions of transformation_pb2_map and vds_pb2_map
        that only contain upstream dependencies to the terminal node.

        For example, given the DAG:

            VDS->T1->T2->T3

        T3's filtered maps will contain T3, T2, T1 and VDS
        T2's filtered maps will contain T2, T1 and VDS
        T1's filtered maps will contain T1 and VDS

        """
        tf_map: Dict[str, TransformationDataProto] = {}
        vds_map: Dict[str, VirtualDataSourceProto] = {}
        upstream_deps = [transformation_pb2]
        while len(upstream_deps) > 0:
            dep = upstream_deps.pop(0)
            if isinstance(dep, TransformationDataProto):
                id_str = IdHelper.to_string(dep.transformation_id)
                if id_str in tf_map.keys():
                    continue
                tf_map[id_str] = dep

                for input_pb2 in dep.inputs:
                    if input_pb2.HasField("transformation_id"):
                        upstream_deps.append(transformation_pb2_map[IdHelper.to_string(input_pb2.transformation_id)])
                    elif input_pb2.HasField("virtual_data_source_id"):
                        upstream_deps.append(vds_pb2_map[IdHelper.to_string(input_pb2.virtual_data_source_id)])
                    else:
                        raise Exception("Invalid state! Neither of transformation_id or virtual_data_source_id is set.")
            elif isinstance(dep, VirtualDataSourceProto):
                id_str = IdHelper.to_string(dep.virtual_data_source_id)
                if id_str in vds_map.keys():
                    continue
                vds_map[id_str] = dep

        return tf_map, vds_map or {}

    @classmethod
    def create_from_maps(
        cls,
        *,
        final_transformation_id_pb2: Id,
        transformation_pb2_map: Dict[str, TransformationDataProto],
        vds_pb2_map: Dict[str, VirtualDataSourceProto],
    ) -> "TransformationDataProtoDAG":
        """
        Creates a TransformationDataProtoDAG from multiple parameters.
        :param final_transformation_pb2: Id of the terminal node of the Transformation DAG.
        :param transformation_pb2_map: Transformation ID -> data.Transformation proto map containing all Transformations in the DAG.
        :param vds_pb2_map: Virtual Data Source ID -> data.VirtualDataSource proto map containing all inputs to the DAG.
        :return: A TransformationDataProtoDAG object.
        """
        final_transformation_id_str = IdHelper.to_string(final_transformation_id_pb2)
        # Make sure final_transformation_id_str is the final transformation ID in the transformations_ids list.
        # Ordering doesn't really matter as long as the final transformation ID is the last list element
        # since TransformationDataProtoDAG assumes the final transformation is the last element in the final_transformation() method.
        transformations_ids = [id for id in transformation_pb2_map.keys() if id != final_transformation_id_str]
        transformations_ids.append(final_transformation_id_str)
        transformations = []
        for transformation_id in transformations_ids:
            # Filter upstream dependencies so that each Transformation contains only its upstream dependencies,
            # instead of the entire DAG's dependencies.
            filtered_tf_pb2_map, filtered_vds_pb2_map = TransformationDataProtoDAG._filter_dependency_maps(
                transformation_pb2_map[transformation_id], transformation_pb2_map, vds_pb2_map
            )
            transformations.append(
                Transformation._from_data_proto(
                    transformation_pb2_map[transformation_id].transformation_id,
                    filtered_tf_pb2_map,
                    filtered_vds_pb2_map,
                )
            )

        return TransformationDataProtoDAG(transformations=transformations)
