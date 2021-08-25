from typing import List
from typing import Optional
from typing import Union

import pandas as pd
from pyspark.sql import DataFrame
from pyspark.sql.streaming import StreamingQuery

from tecton import conf
from tecton._internals import errors
from tecton._internals import metadata_service
from tecton._internals.display import Displayable
from tecton._internals.sdk_decorators import sdk_public_method
from tecton.fco import Fco
from tecton_proto.common.id_pb2 import Id
from tecton_proto.data.batch_data_source_pb2 import BatchDataSource as BatchDataSourceProto
from tecton_proto.data.stream_data_source_pb2 import StreamDataSource as StreamDataSourceProto
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource as VirtualDataSourceProto
from tecton_proto.metadataservice.metadata_service_pb2 import GetVirtualDataSourceRequest
from tecton_proto.metadataservice.metadata_service_pb2 import GetVirtualDataSourceSummaryRequest
from tecton_spark import data_source_helper
from tecton_spark.id_helper import IdHelper
from tecton_spark.logger import get_logger
from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper

logger = get_logger("DataSource")


class VirtualDataSource(Fco):
    """
    VirtualDataSource is Tecton's main data abstraction.
    """

    virtual_ds: Optional[VirtualDataSourceProto]
    batch_ds: BatchDataSourceProto
    stream_ds: Optional[StreamDataSourceProto]

    @classmethod
    def _from_proto_and_data_sources(
        cls,
        virtual_ds: VirtualDataSourceProto,
        batch_ds: Optional[BatchDataSourceProto],
        stream_ds: Optional[StreamDataSourceProto],
    ) -> "VirtualDataSource":
        """
        Create a new VDS instance.
        :param virtual_ds: VirtualDataSource proto to be unpacked into a class instance.
        :param batch_ds: BatchDataSource instance representing batch DS to be included
                         into this virtual DS.
        :param stream_ds: Optional StreamDataSource instance representing streaming DS to be
                          included into this virtual DS. If present, this VDS class
                          represents a stream DS backed up with the batch DS.
        """
        obj = cls.__new__(cls)
        obj.virtual_ds = virtual_ds
        obj.batch_ds = batch_ds
        obj.stream_ds = stream_ds
        return obj

    @classmethod
    def _create_from_proto(cls, virtual_proto) -> "VirtualDataSource":
        """
        Creates a new :class:`VirtualDataSource` class from persisted Virtual DS proto.

        :param virtual_proto: VirtualDataSource proto struct.

        :return: :class:`VirtualDataSource` class instance.
        """
        batch_ds = virtual_proto.batch_data_source
        stream_ds = None
        if virtual_proto.HasField("stream_data_source"):
            stream_ds = virtual_proto.stream_data_source

        return cls._from_proto_and_data_sources(virtual_proto, batch_ds, stream_ds)

    @property  # type: ignore
    @sdk_public_method
    def is_streaming(self) -> bool:
        """
        Whether or not the VirtualDataSource contains a stream source.
        """
        return self.stream_ds is not None

    @property  # type: ignore
    @sdk_public_method
    def columns(self) -> List[str]:
        """
        Returns streaming DS columns if it's present. Otherwise, returns batch DS columns.
        """
        if self.is_streaming:
            assert self.stream_ds is not None
            schema = self.stream_ds.spark_schema
        else:
            assert self.virtual_ds is not None
            schema = self.virtual_ds.batch_data_source.spark_schema
        return SparkSchemaWrapper.from_proto(schema).column_names()

    @property
    def _proto(self):
        """
        Returns virtual DS proto.
        """
        return self.virtual_ds

    @classmethod
    def _fco_type_name_singular_snake_case(cls) -> str:
        return "data_source"

    @classmethod
    def _fco_type_name_plural_snake_case(cls) -> str:
        return "data_sources"

    @property
    def _fco_metadata(self):
        return self._proto.fco_metadata

    def _id_proto(self) -> Id:
        return self._proto.virtual_data_source_id

    @property  # type: ignore
    @sdk_public_method
    def id(self) -> str:
        """
        Returns an unique ID for the virtual data source.
        """
        return IdHelper.to_string(self._id_proto())

    @sdk_public_method
    def start_stream_preview(self, table_name: str) -> StreamingQuery:
        """
        Starts a streaming job to write incoming records from this VDS's stream to a temporary table with a given name.

        After records have been written to the table, they can be queried using ``spark.sql()``. If ran in a Databricks
        notebook, Databricks will also automatically visualize the number of incoming records.

        This is a testing method, most commonly used to verify a VirtualDataSource is correctly receiving streaming events.
        Note that the table will grow infinitely large, so this is only really useful for debugging in notebooks.

        :param table_name: The name of the temporary table that this method will write to.
        """
        if not self.is_streaming:
            raise errors.VDS_STREAM_PREVIEW_ON_NON_STREAM

        import tecton

        spark = tecton.tecton_context.TectonContext.get_instance()._spark
        dsc = tecton.DataSourceConfig(self)
        df = data_source_helper.get_stream_dataframe_with_options(spark, self.stream_ds, dsc.proto)
        return df.writeStream.format("memory").queryName(table_name).outputMode("append").start()

    @sdk_public_method
    def preview(self, limit: int = 10) -> pd.DataFrame:
        """
        Shows a preview of the VirtualDataSource's data from its batch data source.

        :param limit: (default=10) The number of rows to preview.
        :return: A pandas DataFrame containing a preview of data.
        """
        import tecton

        spark_df = self.dataframe().limit(limit)
        return tecton.DataFrame._create(spark_df).to_pandas()

    @sdk_public_method
    def dataframe(self) -> DataFrame:
        """
        Returns this VirtualDataSource's source data as a Spark DataFrame.

        :return: A Spark DataFrame containing the VirtualDataSource's source data.
        """
        from tecton.tecton_context import TectonContext

        spark = TectonContext.get_instance()._spark

        df = data_source_helper.get_table_dataframe(spark, self.batch_ds)
        if self.is_streaming:
            df = df.select(*self.columns)

        return df

    @sdk_public_method
    def summary(self) -> Displayable:
        """
        Displays a human readable summary of this VirtualDataSource.
        """
        assert self.virtual_ds is not None
        request = GetVirtualDataSourceSummaryRequest()
        request.fco_locator.id.CopyFrom(self.virtual_ds.virtual_data_source_id)
        request.fco_locator.workspace = self.workspace

        response = metadata_service.instance().GetVirtualDataSourceSummary(request)
        return Displayable.from_fco_summary(response.fco_summary)


class BatchDataSource(VirtualDataSource):
    """
    BatchDataSource abstracts batch data sources.

    BatchFeatureViews and BatchWindowAggregateFeatureViews ingest data from BatchDataSources.
    """

    @classmethod
    def _fco_type_name_singular_snake_case(cls) -> str:
        return "batch_data_source"

    @classmethod
    def _fco_type_name_plural_snake_case(cls) -> str:
        return "batch_data_sources"


class StreamDataSource(VirtualDataSource):
    """
    StreamDataSource is an abstraction data over streaming data sources.

    StreamFeatureViews and StreamWindowAggregateFeatureViews ingest data from StreamDataSources.

    A StreamDataSource contains a Stream DataSourceConfig, as well as a Batch DataSourceConfig for back fills.
    """

    @classmethod
    def _fco_type_name_singular_snake_case(cls) -> str:
        return "stream_data_source"

    @classmethod
    def _fco_type_name_plural_snake_case(cls) -> str:
        return "stream_data_sources"


@sdk_public_method
def get_virtual_data_source(name, workspace_name: Optional[str] = None) -> VirtualDataSource:
    """
    Fetch an existing :class:`VirtualDataSource` by name.

    :param name: An unique name of the registered Virtual DS.

    :return: A :class:`VirtualDataSource` class instance.

    :raises TectonValidationError: if VDS with the passed name is not found.
    """
    request = GetVirtualDataSourceRequest()
    request.name = name
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")

    response = metadata_service.instance().GetVirtualDataSource(request)
    if not response.HasField("virtual_data_source"):
        raise errors.FCO_NOT_FOUND(VirtualDataSource, name)
    return VirtualDataSource._create_from_proto(response.virtual_data_source)


@sdk_public_method
def get_data_source(name, workspace_name: Optional[str] = None) -> Union[BatchDataSource, StreamDataSource]:
    """
    Fetch an existing :class:`BatchDataSource` or :class:`StreamDataSource` by name.

    :param name: An unique name of the registered Data Source.

    :return: A :class:`BatchDataSource` or :class:`StreamDataSource` class instance.

    :raises TectonValidationError: if a data source with the passed name is not found.
    """
    request = GetVirtualDataSourceRequest()
    request.name = name
    request.workspace = workspace_name or conf.get_or_none("TECTON_WORKSPACE")

    response = metadata_service.instance().GetVirtualDataSource(request)
    if not response.HasField("virtual_data_source"):
        raise errors.FCO_NOT_FOUND(VirtualDataSource, name)
    vds = VirtualDataSource._create_from_proto(response.virtual_data_source)
    if vds.stream_ds is not None:
        return StreamDataSource._create_from_proto(response.virtual_data_source)
    else:
        return BatchDataSource._create_from_proto(response.virtual_data_source)
