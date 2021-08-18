from typing import Any
from typing import List
from typing import Optional
from typing import Union

import pandas as pd
import pendulum
from pyspark.sql import DataFrame

import tecton.interactive.data_frame
from tecton import conf
from tecton._internals import errors
from tecton._internals import metadata_service
from tecton._internals.display import Displayable
from tecton._internals.sdk_decorators import sdk_public_method
from tecton.fco import Fco
from tecton.tecton_context import TectonContext
from tecton_proto.args.new_transformation_pb2 import TransformationMode
from tecton_proto.args.transformation_pb2 import RequestContext
from tecton_proto.common.id_pb2 import Id
from tecton_proto.data.new_transformation_pb2 import NewTransformation as NewTransformationProto
from tecton_proto.metadataservice.metadata_service_pb2 import GetTransformationRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetTransformationSummaryRequest
from tecton_spark import function_serialization as func_ser
from tecton_spark import transformation_helper
from tecton_spark.id_helper import IdHelper
from tecton_spark.logger import get_logger
from tecton_spark.materialization_common import MaterializationContext

logger = get_logger("Transformation")
TRANSFORMATION_TEMP_VIEW_PREFIX = "_tecton_transformation_run_"


class NewTransformation(Fco):
    """
    Transformation Class.

    A Transformation is a Tecton primitive that contains logic for creating a feature.

    To get a Transformation instance, call :py:func:`tecton.get_transformation`.

    WARNING: This class will be renamed to `Transformation` once the migration to FeatureView is complete.
    """

    _transformation_proto: NewTransformationProto

    def __init__(self):
        """ Do not call this directly. Use :py:func:`tecton.get_transformation` """

    @classmethod
    def _fco_type_name_singular_snake_case(cls) -> str:
        return "transformation"

    @classmethod
    def _fco_type_name_plural_snake_case(cls) -> str:
        return "transformations"

    @property
    def _fco_metadata(self):
        return self._transformation_proto.fco_metadata

    @property
    def transformer(self):
        """
        Returns the raw transformation function encapsulated by this Transformation.
        """
        return func_ser.from_proto(self._transformation_proto.user_function, scope={})

    @classmethod
    def _from_proto(
        cls,
        transformation: NewTransformationProto,
    ):
        """
        Returns a Transformation instance.

        :param transformation_id_pb2: Id of the Transformation proto object.
        :param transformations: List of Transformation data protos in this Transformation's transitive deps,
                                including the Transformation itself (referenced by transformation_id_pb2).
        """

        obj = NewTransformation.__new__(cls)
        obj._transformation_proto = transformation
        return obj

    @classmethod
    def _request_context_from_proto_and_deps(
        cls,
        transformation_id_pb2: Id,
        transformations: List[NewTransformationProto],
    ) -> RequestContext:
        transform_map = transformation_helper.get_transformation_id2proto_map(transformations)
        return transform_map[IdHelper.to_string(transformation_id_pb2)].request_context

    def _validate_context(self, context):
        if self._transformation_proto.has_context and context is None:
            raise errors.CONTEXT_REQUIRED()
        if context is not None and not isinstance(context, MaterializationContext):
            raise errors.INVALID_CONTEXT_TYPE(type(context))

    @sdk_public_method
    def run(self, *inputs: Any) -> Union[DataFrame, str]:
        """Run the transformation against inputs.

        :param inputs: positional arguments to the transformation function. For PySpark and SQL transformations,
                       these are either ``pandas.DataFrame`` or ``pyspark.sql.DataFrame`` objects.
                       For Online transformations, these are ``pandas.Series`` objects.
        """

        if self._transformation_proto.transformation_mode == TransformationMode.TRANSFORMATION_MODE_SPARK_SQL:
            return self._sql_run(*inputs)
        elif self._transformation_proto.transformation_mode == TransformationMode.TRANSFORMATION_MODE_PYSPARK:
            return self._pyspark_run(*inputs)
        elif self._transformation_proto.transformation_mode == TransformationMode.TRANSFORMATION_MODE_PANDAS:
            return self._online_run(*inputs)
        raise RuntimeError(f"{self._transformation_proto.transformation_mode} does not support `run(...)`")

    def _pyspark_run(self, *inputs, context=None) -> DataFrame:
        temp_views = [tecton.interactive.data_frame.DataFrame._create(df).to_spark() for df in inputs]
        args = [context] + temp_views if self._transformation_proto.has_context else temp_views
        return tecton.interactive.data_frame.DataFrame._create(self.transformer(*args))

    def _sql_run(self, *inputs, context=None) -> Union[DataFrame, str]:
        def create_temp_view(df, dataframe_index):
            df = tecton.interactive.data_frame.DataFrame._create(df).to_spark()
            temp_view = f"{TRANSFORMATION_TEMP_VIEW_PREFIX}{self._fco_metadata.name}_input_{dataframe_index}"
            df.createOrReplaceTempView(temp_view)
            return temp_view

        temp_views = [create_temp_view(df, i) for i, df in enumerate(inputs)]
        args = [context] + temp_views if self._transformation_proto.has_context else temp_views

        spark = TectonContext.get_instance()._get_spark()
        return tecton.interactive.data_frame.DataFrame._create(spark.sql(self.transformer(*args)))

    def _online_run(self, *inputs) -> DataFrame:
        for series in inputs:
            if not isinstance(series, pd.Series):
                raise TypeError(f"Input must be of type pandas.Series, but was {type(series)}.")

        return tecton.interactive.data_frame.DataFrame._create(self.transformer(*inputs))

    def _dataframe(self, time_range: Optional[pendulum.Period] = None) -> DataFrame:
        tc = TectonContext.get_instance()
        return self._transformation.dataframe(tc._spark, time_range=time_range)

    def summary(self):
        """
        Displays a human readable summary of this Transformation.
        """
        request = GetTransformationSummaryRequest()
        request.fco_locator.id.CopyFrom(self._transformation_proto.transformation_id)
        request.fco_locator.workspace = self.workspace

        response = metadata_service.instance().GetTransformationSummary(request)
        return Displayable.from_fco_summary(response.fco_summary)

    def online_transform_dataframe(self, input_df: DataFrame, join_keys: List[str] = None) -> DataFrame:
        """
        Returns a DataFrame containing the transformed result of an input DataFrame.
        Can only be used with OnlineTransformation.

        :param input_df: Spark DataFrame to be transformed.
        :param join_keys: List of join keys columns.
                          Only required if OnDemandFeatureView has a specified Entity.
        :return: Spark DataFrame
        """
        if not self._transformation_proto.transformation_type == TransformationMode.TRANSFORMATION_MODE_PANDAS:
            raise errors.TRANSFORMATION_DATAFRAME_ONLINE_ONLY
        return self._transformation.dataframe_with_input(
            spark=TectonContext.get_instance()._spark, input_df=input_df, join_keys=join_keys or []
        )


@sdk_public_method
def get_transformation(name, workspace_name: Optional[str] = None) -> NewTransformation:
    """
    Fetch an existing :class:`NewTransformation` by name.

    :param name: An unique name of the registered Transformation.

    :return: A :class:`NewTransformation` class instance.

    :raises TectonValidationError: if a Transformation with the passed name is not found.
    """
    request = GetTransformationRequest()
    request.name = name
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")

    response = metadata_service.instance().GetTransformation(request)
    if not response.HasField("new_transformation"):
        raise errors.FCO_NOT_FOUND(NewTransformation, name)
    return NewTransformation._from_proto(response.new_transformation)
