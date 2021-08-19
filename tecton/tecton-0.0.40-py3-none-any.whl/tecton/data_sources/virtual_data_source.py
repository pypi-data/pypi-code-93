from typing import Dict
from typing import Optional

from typeguard import typechecked

from tecton.basic_info import prepare_basic_info
from tecton.data_sources.base_data_source import BaseBatchDataSource
from tecton.data_sources.base_data_source import BaseStreamDataSource
from tecton_proto.args import virtual_data_source_pb2
from tecton_proto.args.basic_info_pb2 import BasicInfo
from tecton_proto.args.repo_metadata_pb2 import SourceInfo
from tecton_proto.args.virtual_data_source_pb2 import DataSourceType
from tecton_proto.args.virtual_data_source_pb2 import VirtualDataSourceArgs
from tecton_proto.common.id_pb2 import Id
from tecton_spark.id_helper import IdHelper
from tecton_spark.logger import get_logger

logger = get_logger("VirtualDataSource")


class VirtualDataSource:
    """
    Declare a VirtualDataSource (VDS), used to read data into Tecton.

    VirtualDataSource (commonly referred to as a VDS) is Tecton's main data abstraction.
    FeatureViews ingest data from VDS's. A VDS can represent a batch data source,
    or a streaming data source which has been backed up by a historical log represented by a batch data source.
    """

    _args: VirtualDataSourceArgs
    _source_info: SourceInfo

    def __init__(
        self,
        *,
        name: str,
        description: str = "",
        family: str = "",
        tags: Dict[str, str] = None,
        owner: str = "",
        batch_ds_config: BaseBatchDataSource,
        stream_ds_config: Optional[BaseStreamDataSource] = None,
    ) -> None:
        """
        Creates a new Virtual Data Source.

        :param name: An unique name of the Virtual DS.
        :param description: (Optional) Description.
        :param family: (Optional) Family of this VDS, used to group Tecton Primitives.
        :param tags: (Optional) Tags associated with this Tecton Primitive (key-value pairs of arbitrary metadata).
        :param owner: Owner name (typically the email of the primary maintainer).
        :param batch_ds_config: BatchDataSourceConfig object containing the configuration of the batch data source that is to be included
            in this VirtualDataSource.
        :param stream_ds_config: (Optional) StreamDataSourceConfig object containing the configuration of the
            stream data source that is to be included included in this VirtualDataSource. If present, this VDS class
            represents a stream data source backed up by the batch data source.

        :return: A :class:`VirtualDataSource` class instance.
        """
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=family, tags=tags)
        args = prepare_vds_args(
            basic_info=basic_info, batch_ds_config=batch_ds_config, stream_ds_config=stream_ds_config, vds_type=None
        )

        self._args = args

    def _id(self) -> Id:
        return self._args.virtual_data_source_id

    @property
    def name(self) -> str:
        """
        The name of this VDS.
        """
        return self._args.info.name

    @property
    def timestamp_key(self) -> str:
        """
        The name of the timestamp column or key of this VDS.
        """
        if self._args.HasField("hive_ds_config"):
            return self._args.hive_ds_config.timestamp_column_name
        if self._args.HasField("redshift_ds_config"):
            return self._args.redshift_ds_config.timestamp_key
        if self._args.HasField("snowflake_ds_config"):
            return self._args.snowflake_ds_config.timestamp_key
        if self._args.HasField("file_ds_config"):
            return self._args.file_ds_config.timestamp_column_name
        else:
            raise Exception(f"Unknown Data Source Type: {self.name}")


class BatchDataSource(VirtualDataSource):
    """
    Declare a BatchDataSource, used to read batch data into Tecton.

    BatchFeatureViews and BatchWindowAggregateFeatureViews ingest data from BatchDataSources.
    """

    _args: VirtualDataSourceArgs
    _source_info: SourceInfo

    @typechecked
    def __init__(
        self,
        *,
        name: str,
        description: str = "",
        family: str = "",
        tags: Dict[str, str] = None,
        owner: str = "",
        batch_ds_config: BaseBatchDataSource,
    ) -> None:
        """
        Creates a new BatchDataSource

        :param name: An unique name of the DataSource.
        :param description: (Optional) Description.
        :param family: (Optional) Family of this DataSource, used to group Tecton Primitives.
        :param tags: (Optional) Tags associated with this Tecton Primitive (key-value pairs of arbitrary metadata).
        :param owner: Owner name (typically the email of the primary maintainer).
        :param batch_ds_config: BatchDataSourceConfig object containing the configuration of the batch data source that is to be included
            in this DataSource.

        :return: A :class:`BatchDataSource` class instance.
        """
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=family, tags=tags)
        args = prepare_vds_args(
            basic_info=basic_info, batch_ds_config=batch_ds_config, stream_ds_config=None, vds_type=DataSourceType.BATCH
        )

        self._args = args


class StreamDataSource(VirtualDataSource):
    """
    Declare a StreamDataSource, used to read streaming data into Tecton.

    StreamFeatureViews and StreamWindowAggregateFeatureViews ingest data from StreamDataSources. A StreamDataSource contains both a Batch and Stream DataSourceConfig.
    """

    _args: VirtualDataSourceArgs
    _source_info: SourceInfo

    @typechecked
    def __init__(
        self,
        *,
        name: str,
        description: str = "",
        family: str = "",
        tags: Dict[str, str] = None,
        owner: str = "",
        batch_ds_config: BaseBatchDataSource,
        stream_ds_config: BaseStreamDataSource,
    ) -> None:
        """
        Creates a new StreamDataSource.

        :param name: An unique name of the DataSource.
        :param description: (Optional) Description.
        :param family: (Optional) Family of this DataSource, used to group Tecton Primitives.
        :param tags: (Optional) Tags associated with this Tecton Primitive (key-value pairs of arbitrary metadata).
        :param owner: Owner name (typically the email of the primary maintainer).
        :param batch_ds_config: BatchDataSourceConfig object containing the configuration of the batch data source that is to be included
            in this DataSource.
        :param stream_ds_config: StreamDataSourceConfig object containing the configuration of the
            stream data source that is to be included in this DataSource.

        :return: A :class:`StreamDataSource` class instance.
        """
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=family, tags=tags)
        args = prepare_vds_args(
            basic_info=basic_info,
            batch_ds_config=batch_ds_config,
            stream_ds_config=stream_ds_config,
            vds_type=DataSourceType.STREAM_WITH_BATCH,
        )

        self._args = args


def prepare_vds_args(
    *,
    basic_info: BasicInfo,
    batch_ds_config: BaseBatchDataSource,
    stream_ds_config: Optional[BaseStreamDataSource],
    vds_type: Optional["DataSourceType"],
):
    args = virtual_data_source_pb2.VirtualDataSourceArgs()
    args.virtual_data_source_id.CopyFrom(IdHelper.from_string(IdHelper.generate_string_id()))
    args.info.CopyFrom(basic_info)
    batch_ds_config._merge_batch_args(args)
    if stream_ds_config is not None:
        stream_ds_config._merge_stream_args(args)
    if vds_type:
        args.type = vds_type
    return args
