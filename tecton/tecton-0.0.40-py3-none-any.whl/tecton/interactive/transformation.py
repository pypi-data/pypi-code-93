from typing import Iterable
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
from tecton.interactive.new_transformation import NewTransformation
from tecton.tecton_context import TectonContext
from tecton_proto.args.transformation_pb2 import RequestContext
from tecton_proto.args.transformation_pb2 import TransformationType
from tecton_proto.common.id_pb2 import Id
from tecton_proto.data.transformation_pb2 import Transformation as TransformationProto
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource as VirtualDataSourceProto
from tecton_proto.metadataservice.metadata_service_pb2 import GetTransformationRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetTransformationSummaryRequest
from tecton_spark import data_source_helper
from tecton_spark import function_serialization as func_ser
from tecton_spark import transformation_helper
from tecton_spark.id_helper import IdHelper
from tecton_spark.logger import get_logger
from tecton_spark.materialization_common import MaterializationContext
from tecton_spark.transformation import Transformation as InternalTransformation


logger = get_logger("Transformation")
TRANSFORMATION_TEMP_VIEW_PREFIX = "_tecton_transformation_run_"


class Transformation(Fco):
    """
    Transformation Class.

    A Transformation is a Tecton primitive that contains logic for creating a feature.
    """

    _transformation_proto: TransformationProto
    _transformation: InternalTransformation

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
        return func_ser.from_proto(self._transformation_proto.transformer, scope={})

    @classmethod
    def _from_proto_with_enrichments(cls, proto: TransformationProto) -> "Transformation":
        return Transformation._from_proto_and_deps(
            proto.transformation_id,
            list(proto.enrichments.transformations) + [proto],
            proto.enrichments.virtual_data_sources,
        )

    @classmethod
    def _from_proto_and_deps(
        cls,
        transformation_id_pb2: Id,
        transformations: Iterable[TransformationProto],
        virtual_data_sources: Iterable[VirtualDataSourceProto],
    ):
        """
        Returns a Transformation instance.

        :param transformation_id_pb2: Id of the Transformation proto object.
        :param transformations: List of Transformation data protos in this Transformation's transitive deps,
                                including the Transformation itself (referenced by transformation_id_pb2).
        :param virtual_data_sources: List of VirtualDataSource data protos in this Transformation's transitive deps.

        """
        transform_map = transformation_helper.get_transformation_id2proto_map(transformations)

        obj = Transformation.__new__(cls)
        obj._transformation_proto = transform_map[IdHelper.to_string(transformation_id_pb2)]
        obj._transformation = InternalTransformation._from_data_proto(
            transformation_id_pb2=transformation_id_pb2,
            transformation_pb2_map=transform_map,
            vds_pb2_map=data_source_helper.get_vds_id2proto_map(virtual_data_sources),
        )
        return obj

    @classmethod
    def _request_context_from_proto_and_deps(
        cls,
        transformation_id_pb2: Id,
        transformations: List[TransformationProto],
    ) -> RequestContext:
        transform_map = transformation_helper.get_transformation_id2proto_map(transformations)
        return transform_map[IdHelper.to_string(transformation_id_pb2)].request_context

    def _validate_context(self, context):
        if self._transformation_proto.has_context and context is None:
            raise errors.CONTEXT_REQUIRED()
        if context is not None and not isinstance(context, MaterializationContext):
            raise errors.INVALID_CONTEXT_TYPE(type(context))

    @sdk_public_method
    def run(
        self,
        *inputs: Union["pd.DataFrame", "pd.Series", "DataFrame", str],
        context: Optional[MaterializationContext] = None,
    ):
        """Run the transformation against inputs.

        :param inputs: positional arguments to the transformation function. For PySpark and SQL transformations,
                       these are either ``pandas.DataFrame`` or ``pyspark.sql.DataFrame`` objects.
                       For Online transformations, these are ``pandas.Series`` objects.
        :param context: (Optional) A MaterializationContext object; this is required if ``has_context=True``
                        in the transformation's definition.
        """

        if self._transformation_proto.transformation_type == TransformationType.SQL:
            self._validate_context(context)
            return self._sql_run(*inputs, context=context)
        elif self._transformation_proto.transformation_type == TransformationType.PYSPARK:
            self._validate_context(context)
            return self._pyspark_run(*inputs, context=context)
        elif self._transformation_proto.transformation_type == TransformationType.ONLINE:
            return self._online_run(*inputs)
        raise RuntimeError(f"{self._transformation_proto.transformation_type} does not support `run(...)`")

    def _pyspark_run(self, *inputs, context=None):
        temp_views = [tecton.interactive.data_frame.DataFrame._create(df).to_spark() for df in inputs]
        args = [context] + temp_views if self._transformation_proto.has_context else temp_views
        return tecton.interactive.data_frame.DataFrame._create(self.transformer(*args))

    def _sql_run(self, *inputs, context=None):
        def create_temp_view(df, dataframe_index):
            df = tecton.interactive.data_frame.DataFrame._create(df).to_spark()
            temp_view = f"{TRANSFORMATION_TEMP_VIEW_PREFIX}{self._fco_metadata.name}_input_{dataframe_index}"
            df.createOrReplaceTempView(temp_view)
            return temp_view

        temp_views = [create_temp_view(df, i) for i, df in enumerate(inputs)]
        args = [context] + temp_views if self._transformation_proto.has_context else temp_views

        spark = TectonContext.get_instance()._get_spark()
        return tecton.interactive.data_frame.DataFrame._create(spark.sql(self.transformer(*args)))

    def _online_run(self, *inputs):
        for series in inputs:
            if not isinstance(series, pd.Series):
                raise TypeError(f"Input must be of type pandas.Series, but was {type(series)}.")

        return tecton.interactive.data_frame.DataFrame._create(self.transformer(*inputs))

    def _dataframe(self, time_range: Optional[pendulum.Period] = None) -> DataFrame:
        tc = TectonContext.get_instance()
        return self._transformation.dataframe(tc._spark, time_range=time_range)

    def get_output_dataframe(self, time_range: Optional[pendulum.Period] = None) -> DataFrame:
        """
        Returns Spark DataFrame of this Transformation's output.
        Can be used with SQLTransformation and PySparkTransformation.

        :param time_range: (Optional) Time range to collect features from. Will default to recent data (past 2 days).

        :return: Pandas DataFrame.
        """
        if self._transformation_proto.transformation_type == TransformationType.ONLINE:
            raise errors.TRANSFORMATION_DATAFRAME_NOT_ONLINE
        return self._dataframe(time_range)

    def preview(self, limit=10, time_range: Optional[pendulum.Period] = None) -> pd.DataFrame:
        """
        Returns Pandas DataFrame preview of this Transformation's output.

        :param limit: (Optional, default=10) The number of rows to preview
        :param time_range: (Optional) Time range to collect features from. Will default to recent data (past 2 days).

        :return: Pandas DataFrame.
        """
        if self._transformation_proto.transformation_type == TransformationType.ONLINE:
            raise errors.TRANSFORMATION_DATAFRAME_NOT_ONLINE
        return self._dataframe(time_range).limit(limit).toPandas()

    def summary(self):
        """
        Displays a human readable summary of this Transformation.
        """
        request = GetTransformationSummaryRequest()
        request.fco_locator.id.CopyFrom(self._transformation_proto.transformation_id)
        request.fco_locator.workspace = self.workspace

        response = metadata_service.instance().GetTransformationSummary(request)
        return Displayable.from_fco_summary(response.fco_summary)

    def online_transform_dataframe(self, input_df: DataFrame, join_keys: List[str] = []) -> DataFrame:
        """
        Returns a DataFrame containing the transformed result of an input DataFrame.
        Can only be used with OnlineTransformation.

        :param input_df: DataFrame to be transformed.
        :param join_keys: List of join keys columns.
                          Only required if OnlineFeaturePackage has a specified Entity.
        :return: Spark DataFrame
        """
        if not self._transformation_proto.transformation_type == TransformationType.ONLINE:
            raise errors.TRANSFORMATION_DATAFRAME_ONLINE_ONLY
        return self._transformation.dataframe_with_input(
            spark=TectonContext.get_instance()._spark, input_df=input_df, join_keys=join_keys
        )


@sdk_public_method
def get_transformation(name: str, workspace_name: Optional[str] = None) -> Union[Transformation, NewTransformation]:
    """
    Fetch an existing :class:`Transformation` by name.

    :param name: An unique name of the registered Transformation.

    :return: A :class:`Transformation` class instance.

    :raises TectonValidationError: if a Transformation with the passed name is not found.
    """
    from tecton.interactive.new_transformation import get_transformation as get_new_transformation

    request = GetTransformationRequest()
    request.name = name
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")

    response = metadata_service.instance().GetTransformation(request)
    if not response.HasField("transformation"):
        return get_new_transformation(name, workspace_name=workspace_name)
    return Transformation._from_proto_with_enrichments(response.transformation)
