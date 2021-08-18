import functools
from dataclasses import dataclass
from dataclasses import field
from inspect import signature
from typing import Callable
from typing import Dict
from typing import Optional
from typing import Union

from google.protobuf.empty_pb2 import Empty
from pandas import DataFrame as PandasDataFrame
from pyspark.sql import DataFrame
from typeguard import typechecked

from tecton import materialization_context
from tecton._internals import errors
from tecton.basic_info import prepare_basic_info
from tecton.cli.common import get_fco_source_info
from tecton.transformations.const import Constant
from tecton_proto.args.new_transformation_pb2 import NewTransformationArgs
from tecton_proto.args.new_transformation_pb2 import TransformationMode
from tecton_proto.args.pipeline_pb2 import Input
from tecton_proto.args.pipeline_pb2 import MaterializationContextNode
from tecton_proto.args.pipeline_pb2 import PipelineNode
from tecton_proto.args.repo_metadata_pb2 import SourceInfo
from tecton_proto.common.id_pb2 import Id
from tecton_spark import function_serialization as func_ser
from tecton_spark.id_helper import IdHelper
from tecton_spark.materialization_common import MaterializationContext
from tecton_spark.materialization_context import UnboundMaterializationContext

SPARK_SQL_MODE = "spark_sql"
PYSPARK_MODE = "pyspark"
PANDAS_MODE = "pandas"

_GLOBAL_TRANSFORMATIONS_LIST = []


@dataclass
class Transformation:
    name: str
    mode: str
    user_function: Callable[..., Union[str, DataFrame]]
    description: str
    owner: str
    family: str
    tags: Dict[str, str]
    _source_info: SourceInfo = field(init=False, repr=False)
    _args: NewTransformationArgs = field(init=False, repr=False)
    _ARGUMENT_TYPE = Union[PipelineNode, Constant, UnboundMaterializationContext]

    def _docstring(self):
        return None

    @property
    def transformer(self):
        return func_ser.from_proto(self._args.user_function)

    def _is_builtin(self):
        return False

    def __post_init__(self):
        self._source_info = get_fco_source_info()

        self._args = NewTransformationArgs()
        self._args.transformation_id.CopyFrom(IdHelper.from_string(IdHelper.generate_string_id()))
        self._args.info.CopyFrom(
            prepare_basic_info(
                name=self.name, description=self.description, owner=self.owner, family=self.family, tags=self.tags
            )
        )
        if self.mode == SPARK_SQL_MODE:
            transform_mode = TransformationMode.TRANSFORMATION_MODE_SPARK_SQL
            return_type = str
        elif self.mode == PYSPARK_MODE:
            transform_mode = TransformationMode.TRANSFORMATION_MODE_PYSPARK
            return_type = DataFrame
        elif self.mode == PANDAS_MODE:
            transform_mode = TransformationMode.TRANSFORMATION_MODE_PANDAS
            return_type = PandasDataFrame
        else:
            raise errors.InvalidTransformationMode(self.name, self.mode, [SPARK_SQL_MODE, PYSPARK_MODE])
        if self._docstring() is not None:
            self._args.docstring = self._docstring()
        self._args.transformation_mode = transform_mode
        self._args.user_function.CopyFrom(func_ser.to_proto(func_ser.inlined(self.user_function), return_type))
        self._args.is_builtin = self._is_builtin()
        _GLOBAL_TRANSFORMATIONS_LIST.append(self)

    def _args_proto(self) -> NewTransformationArgs:
        return self._args

    def __call__(self, *args, **kwargs) -> PipelineNode:
        wrapper = PipelineNode()
        node = wrapper.transformation_node
        node.transformation_id.CopyFrom(self._args.transformation_id)

        try:
            bound_user_function = signature(self.user_function).bind(*args, **kwargs)
        except TypeError as e:
            raise TypeError(f"while binding inputs to function {self.name}, TypeError: {e}")

        materialization_context_count = 0

        for i, arg in enumerate(args):
            input_ = Input()
            input_.arg_index = i
            input_.node.CopyFrom(self._value_to_node(arg))
            node.inputs.append(input_)
            if isinstance(arg, UnboundMaterializationContext):
                materialization_context_count += 1
        for name, arg in kwargs.items():
            input_ = Input()
            input_.arg_name = name
            input_.node.CopyFrom(self._value_to_node(arg))
            node.inputs.append(input_)
            if isinstance(arg, UnboundMaterializationContext):
                materialization_context_count += 1

        for param in signature(self.user_function).parameters.values():
            if isinstance(param.default, UnboundMaterializationContext):
                if param.name in bound_user_function.arguments:
                    # the user passed in context explicitly, so no need to double register
                    continue
                input_ = Input()
                input_.arg_name = param.name
                input_.node.CopyFrom(self._value_to_node(param.default))
                node.inputs.append(input_)
                if isinstance(param.default, UnboundMaterializationContext):
                    materialization_context_count += 1
            elif isinstance(param.default, MaterializationContext):
                raise Exception(
                    "tecton.MaterializationContext() is not a valid value here. Did you mean "
                    "tecton.materialization_context()?"
                )
            elif param.default is materialization_context:
                raise Exception(
                    "It seems you passed in tecton.materialization_context. Did you mean tecton.materialization_context()?"
                )

        if materialization_context_count > 1:
            raise Exception(f"Only 1 materialization_context can be passed into transformation {self.name}")

        return wrapper

    def _value_to_node(self, arg: _ARGUMENT_TYPE) -> PipelineNode:
        if isinstance(arg, PipelineNode):
            return arg
        elif isinstance(arg, Constant):
            wrapper = PipelineNode()
            node = wrapper.constant_node
            if arg.value is None:
                node.null_const.CopyFrom(Empty())
            elif arg.value_type == str:
                node.string_const = arg.value
            elif arg.value_type == int:
                node.int_const = repr(arg.value)
            elif arg.value_type == float:
                node.float_const = repr(arg.value)
            elif arg.value_type == bool:
                node.bool_const = arg.value
            return wrapper
        elif isinstance(arg, UnboundMaterializationContext):
            wrapper = PipelineNode()
            wrapper.materialization_context_node.CopyFrom(MaterializationContextNode())
            assert wrapper.HasField("materialization_context_node")
            return wrapper
        else:
            raise errors.InvalidTransformInvocation(self.name, arg)

    def _id(self) -> Id:
        return self._args.transformation_id

    def __hash__(self):
        return hash(self.name)


@typechecked
def transformation(
    mode: str,
    name_override: Optional[str] = None,
    description: str = "",
    owner: str = "",
    family: str = "",
    tags: Dict[str, str] = None,
):
    """
    Declares a Transformation that wraps a user function. Transformations are assembled in a pipeline function of a Feature View.

    :param mode: The mode for this transformation; should be one of SPARK_SQL_MODE, PYSPARK_MODE or PANDAS_MODE
    :param name_override: (Optional) Unique, human friendly name override that identifies the Transformation.
    :param description: (Optional) description.
    :param owner: Owner name (typically the email of the primary maintainer).
    :param family: (Optional) Family of this transformation, used to group Tecton Primitives.
    :param tags: (Optional) Tags associated with this Tecton Primitive (key-value pairs of arbitrary metadata).
    :return: A wrapped transformation
    """

    def decorator(user_function):
        transform_name = name_override or user_function.__name__
        transform = Transformation(transform_name, mode, user_function, description, owner, family, tags)
        functools.update_wrapper(wrapper=transform, wrapped=user_function)

        return transform

    return decorator
