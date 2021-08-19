import inspect
from typing import Callable
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql.types import AtomicType
from pyspark.sql.types import StructType

from tecton import VirtualDataSource
from tecton.basic_info import prepare_basic_info
from tecton.fco import Fco
from tecton_proto.args import basic_info_pb2 as BasicInfo
from tecton_proto.args.repo_metadata_pb2 import SourceInfo
from tecton_proto.args.transformation_pb2 import TransformationArgs
from tecton_proto.args.transformation_pb2 import TransformationInput
from tecton_proto.args.transformation_pb2 import TransformationType
from tecton_proto.common.id_pb2 import Id
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource as VirtualDataSourceProto
from tecton_spark import errors
from tecton_spark import function_serialization as func_ser
from tecton_spark.id_helper import IdHelper
from tecton_spark.logger import get_logger
from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper
from tecton_spark.transformation import RequestContext

logger = get_logger("Transformation")
InputType = Union[VirtualDataSource, "Transformation"]


class Transformation(Fco):
    """
    (Tecton Primitive) Transformation class.
    """

    _args: TransformationArgs
    _source_info: SourceInfo

    def __init__(
        self,
        *,
        name: str,
        description: str = "",
        owner: str = "",
        family: str = "",
        tags: Dict[str, str] = None,
        inputs: Union[InputType, List[InputType]],
        transformer: Callable[..., Union[DataFrame, str, pd.Series, pd.DataFrame]],
        transformation_type: TransformationType,
        has_context: bool = False,
        request_context: Optional[RequestContext] = None,
        output_schema: Optional[StructType] = None,
    ):
        """
        Instantiates a new Transformation object.

        :param name: Unique, human friendly name that identifies the Transformation
        :param description: Short description of the Transformation
        :param owner: Owner name
        :param family: Family name
        :param inputs: One or more inputs for the Transformation. Each input can be
                       either a VirtualDataSource, or another Transformation
        :param transformer: A function that takes input DataFrames or temp views and outputs the transformed DataFrame
                            or SQL, depending on the type of the transformation.
                            The function parameters will preserve the order of the inputs provided by the "input" argument.
                            If has_context=True the context is passed as the first parameter to transformer.
        :param transformation_type: SQL, PYSPARK, or ONLINE
        :param has_context: Whether or not the transformer function uses context.
        :param request_context: RequestContext object used to define OnlineTransformation inputs.
        :param output_schema: StructType describing the schema of an OnlineTransformation output.

        :raises TectonValidationError: if the input parameters are invalid.
        """
        if type(self) == Transformation:
            raise errors.TectonValidationError(f"Transformation base class is not instantiable")

        if transformation_type == TransformationType.ONLINE:
            if request_context is None:
                raise errors.REQUIRED_ARGUMENT("request_context")

            rc_schema_fields = list(request_context.arg_to_schema.keys())
            transformer_args = self._transformer_args(transformer)
            if set(rc_schema_fields) != set(transformer_args) or len(rc_schema_fields) != len(transformer_args):
                raise errors.TectonValidationError(
                    f"RequestContext schema fields {rc_schema_fields} do not match transformation function arguments {transformer_args}."
                )
            # Ensure RequestContext has a schema order set to the order of transformer function arguments.
            # This is necessary to ensure transformer function ordering doesn't depend on the dictionary order of the
            # schema dictionary passed to RequestContext.
            request_context._set_schema_field_order(schema_field_order=transformer_args)

        inputs = self._prepare_inputs(inputs)

        self._validate_transformer(name, transformer, transformation_type, inputs, has_context, request_context)

        # In-line due to circular dep
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()

        self._args = Transformation._prepare_args(
            basic_info=prepare_basic_info(name=name, description=description, owner=owner, family=family, tags=tags),
            inputs=inputs,
            transformer=transformer,
            transformation_type=transformation_type,
            has_context=has_context,
            request_context=request_context,
            output_schema=output_schema,
        )

    @property
    def transformer(self):
        """Returns the Python transformer function associated with this Transformation. Commonly used for testing."""
        return func_ser.from_proto(self._args.transformer, scope={})

    def _validate_transformer(
        self,
        name: str,
        transformer: Callable[..., Union[DataFrame, str, pd.Series, pd.DataFrame]],
        transformation_type: TransformationType,
        inputs: List[TransformationInput],
        has_context: bool,
        request_context: Optional[RequestContext] = None,
    ):
        """Validate that the transformer function has a correct parameter count.

        While we generally prefer to validate on the backend rather than the
        SDK, because this validation inspects the signature of the UDF we keep
        this logic in the SDK.
        """
        expected_arg_count = None
        actual_arg_count = len(inspect.signature(transformer).parameters)
        if transformation_type in [TransformationType.PYSPARK, TransformationType.SQL]:
            expected_arg_count = len(inputs) + int(has_context)
        elif transformation_type == TransformationType.ONLINE and request_context is not None:
            expected_arg_count = len(request_context.arg_to_schema.keys())

        if expected_arg_count != actual_arg_count:
            raise errors.TectonValidationError(
                f"Transformation '{name}' expected to take {expected_arg_count} argument(s), but {actual_arg_count} found."
            )

    @classmethod
    def _transformer_args(cls, transformer: Callable[..., Union[DataFrame, str, pd.Series, pd.DataFrame]]) -> List[str]:
        return list(inspect.signature(transformer).parameters.keys())

    @classmethod
    def _prepare_inputs(cls, inputs: Union[InputType, List[InputType]]) -> List[TransformationInput]:
        transformation_inputs = []
        inputs = inputs if type(inputs) in (list, tuple) else [inputs]
        for index, input in enumerate(inputs):
            input_pb2 = TransformationInput()
            if isinstance(input, Transformation):
                input_pb2.transformation_id.CopyFrom(input._id())
            elif isinstance(input, VirtualDataSourceProto):
                input_pb2.virtual_data_source_id.CopyFrom(input.virtual_data_source_id)
            elif isinstance(input, VirtualDataSource):
                input_pb2.virtual_data_source_id.CopyFrom(input._id())
            else:
                raise Exception(
                    f"Invalid input type {type(input)}. Expected either VirtualDataSource or Transformation"
                )
            transformation_inputs.append(input_pb2)
        return transformation_inputs

    @classmethod
    def _prepare_args(
        cls,
        basic_info: BasicInfo,
        inputs: List[TransformationInput],
        transformer: Callable[..., Union[DataFrame, str, pd.Series, pd.DataFrame]],
        transformation_type: TransformationType,
        has_context: bool,
        request_context: Optional[RequestContext],
        output_schema: Optional[StructType],
    ) -> TransformationArgs:
        """Returns a TransformationArgs Proto object created from arguments. Doesn't follow up the dependencies."""
        args_pb2 = TransformationArgs()
        args_pb2.transformation_id.CopyFrom(IdHelper.from_string(IdHelper.generate_string_id()))
        args_pb2.info.CopyFrom(basic_info)
        args_pb2.inputs.extend(inputs)
        args_pb2.transformer.CopyFrom(func_ser.to_proto(func_ser.inlined(transformer), DataFrame))
        args_pb2.transformation_type = transformation_type
        args_pb2.has_context = has_context
        if request_context is not None:
            args_pb2.request_context.CopyFrom(request_context._to_proto())
        if output_schema is not None:
            args_pb2.output_schema.CopyFrom(SparkSchemaWrapper(output_schema).to_proto())

        return args_pb2

    def _id(self) -> Id:
        return self._args.transformation_id

    @property
    def _args_name(self) -> str:
        return self._args.info.name


class PySparkTransformation(Transformation):
    """
    (Tecton Primitive) PySparkTransformation class.

    The PySparkTransformation class defines a PySpark-based transformation.

    PySpark Transformations are Transformations defined by a PySpark function that is applied to one or many input
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
        owner: str = "",
        family: str = "",
        tags: Dict[str, str] = None,
    ):
        """
        Instantiates a PySparkTransformation.

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
            owner=owner,
            family=family,
            tags=tags,
            inputs=inputs,
            transformer=transformer,
            transformation_type=TransformationType.PYSPARK,
            has_context=has_context,
            request_context=None,
        )


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
        owner: str = "",
        family: str = "",
        tags: Dict[str, str] = None,
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
            owner=owner,
            family=family,
            tags=tags,
            inputs=inputs,
            transformer=transformer,
            transformation_type=TransformationType.SQL,
            has_context=has_context,
            request_context=None,
        )


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
        owner: str = "",
        family: str = "",
        tags: Dict[str, str] = None,
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
            owner=owner,
            family=family,
            tags=tags,
            inputs=[],
            transformer=transformer,
            transformation_type=TransformationType.ONLINE,
            has_context=False,
            request_context=request_context,
            output_schema=output_schema,
        )


def pyspark_transformation(
    *,
    inputs: Union[InputType, List[InputType]],
    has_context: bool = False,
    description: str = "",
    owner: str = "",
    family: str = "",
    tags: Dict[str, str] = None,
):
    """
    Decorator used to create a PySparkTransformation.

    A PySparkTransformation is a Tecton Primitive which transforms input data to processed data
    by applying PySpark operations an input DataFrame. It is used as a part
    of a feature pipeline to produce feature values from raw data.

    To create a SQL Transformation, apply this decorator to a function.

    - The decorated function should take a list of PySpark DataFrames as an input (currently,
      only one DataFrame supported.)
    - The decorated function should return a processed PySpark DataFrame.
    - The name of the decorated function will be registered as the name of the Transformation in Tecton.

    Example usage:

    .. highlight:: python
    .. code-block:: python

       @pyspark_transformation(
           inputs=[my_virtual_data_source],
           description="example no-op PySpark Transformation named 'my_transformation'"
        )
       def limit_1000_transformation(input_df):
           return input_df.limit(1000)

    :param inputs: list, The inputs to this pyspark_transformation. Should be of class
        `tecton.VirtualDataSource` or `tecton.Transformation`
    :param has_context: bool, Whether or not the decorated function should take a `context`
        argument of type `tecton.MaterializationContext` as its first argument.
    :param description: (Optional) description.
    :param owner: (Optional) Owner name.
    :param family: The family that this feature belongs to.
    :param tags: (Optional) Arbitrary key-value pairs of tagging metadata.
    """

    def decorated(fn):
        return PySparkTransformation(
            name=fn.__name__,
            inputs=inputs,
            transformer=fn,
            has_context=has_context,
            description=description,
            owner=owner,
            family=family,
            tags=tags,
        )

    return decorated


def sql_transformation(
    *,
    inputs: Union[InputType, List[InputType]],
    has_context: bool = False,
    description: str = "",
    owner: str = "",
    family: str = "",
    tags: Dict[str, str] = None,
):
    """
    Decorator used to create a SQLTransformation.

    A SQLTransformation is a Tecton Primitive which transforms input data to processed data
    by applying a SQL statement to an input view. It is used as a part of a feature pipeline
    to produce feature values from raw data.

    To create a SQL Transformation, apply this decorator to a function.

    - The decorated function should take a list of views as an input (currently, only one view supported.)
    - The decorated function should return a SQL string, which Tecton will execute when this Transformation
      is run. FROM clauses in this SQL string should only reference views passed as inputs
      to the function, or CTEs defined in the SQL string.
    - The name of the decorated function will be registered as the name of the Transformation in Tecton.

    Example usage:

    .. highlight:: python
    .. code-block:: python

       @sql_transformation(
           inputs=[my_virtual_data_source],
           description="example no-op Transformation named 'my_transformation'"
        )
       def limit_1000_transformation(input_df):
           return f"SELECT * FROM {input_df} LIMIT 1000"

    :param inputs: list, The inputs to this sql_transformation. Should be of class
        `tecton.VirtualDataSource` or `tecton.Transformation`
    :param has_context: bool, Whether or not the decorated function should take a `context`
        argument of type `tecton.MaterializationContext` as its first argument.
    :param description: (Optional) description.
    :param owner: (Optional) Owner name.
    :param family: The family that this feature belongs to.
    :param tags: (Optional) Arbitrary key-value pairs of tagging metadata.
    """

    def decorated(fn):
        return SQLTransformation(
            name=fn.__name__,
            inputs=inputs,
            transformer=fn,
            has_context=has_context,
            description=description,
            owner=owner,
            family=family,
            tags=tags,
        )

    return decorated


def online_transformation(
    *,
    request_context: RequestContext,
    description: str = "",
    output_schema=Union[AtomicType, StructType],
    owner: str = "",
    family: str = "",
    tags: Dict[str, str] = None,
):
    """
    Decorator used to create an OnlineTransformation.

    An OnlineTransformation is a Tecton Primitive which transforms input data to processed data
    by applying Pandas code to input data that is passed to the transformation at request-time.

    To create a Online Transformation, apply this decorator to a function.

    - The decorated function should take one or more `pandas.Series` as inputs.
    - The decorated function should return a processed `pandas.DataFrame`. Rows should be
      returned in the same order as the input `pd.Series`.
    - The name of the decorated function will be registered as the name of the Transformation in Tecton.

    Example usage:

    .. highlight:: python
    .. code-block:: python

       from tecton import RequestContext, online_transformation
       from pyspark.sql.types import LongType, StructType, StructField

       request_context = RequestContext(schema={
           "my_input": LongType()
       })

       output_schema = StructType()
       output_schema.add(StructField("my_feature", LongType()))

       @online_transformation(
           request_context=request_context,
           output_schema=output_schema,
           description="Example Online Transformation"
       )
       def my_online_transformation(my_inputs: pandas.Series):

           series = []
           for my_input in my_inputs:
               series.append({
                   "my_feature": 1 if my_input > 0 else 0,
               })

           return pd.DataFrame(series)

    :param request_context: A `tecton.RequestContext` instance that specifies the inputs to this
        OnlineTransformation.
    :param output_schema: A PySpark StructType object the defines the schema of the pandas
        DataFrame returned by this OnlineTransformation.
    :param description: (Optional) description.
    :param owner: (Optional) Owner name.
    :param family: The family that this feature belongs to.
    :param tags: (Optional) Arbitrary key-value pairs of tagging metadata.
    """

    def decorated(fn):
        return OnlineTransformation(
            name=fn.__name__,
            request_context=request_context,
            transformer=fn,
            description=description,
            output_schema=output_schema,
            owner=owner,
            family=family,
            tags=tags,
        )

    return decorated
