from typing import Optional
from typing import Union

from tecton._internals import errors
from tecton.data_sources.virtual_data_source import VirtualDataSource
from tecton.interactive.virtual_data_source import VirtualDataSource as VirtualDataSourceInteractive
from tecton_proto.args.data_source_config_pb2 import DataSourceConfig as DataSourceConfigProto
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource as VirtualDataSourceProto
from tecton_spark.data_source_helper import INITIAL_STREAM_POSITION_STR_TO_ENUM
from tecton_spark.time_utils import strict_pytimeparse


class DataSourceConfig:
    """
    (Helper Class) DataSourceConfig class.

    The DataSourceConfig configures a VirtualDataSource for use in FeatureViews.
    """

    def __init__(
        self,
        virtual_data_source: Union[VirtualDataSource, VirtualDataSourceInteractive],
        initial_stream_position: Optional[str] = None,
        watermark_delay_threshold: Optional[str] = None,
    ):
        """
        :param virtual_data_source: VirtualDataSource object.
        :param initial_stream_position: (Optional, Advanced) Override for the initial position in stream ("latest" or "trim_horizon"),
            defaults to the setting in the VirtualDataSource if unspecified, ignored for batch-only sources.
        :param watermark_delay_threshold: (Optional, Advanced) Override for the Watermark time interval in stream (e.g., "30 minutes"),
            defaults to the setting in the VirtualDataSource if unspecified, ignored for batch-only sources.
        """

        dsc_proto = DataSourceConfig._create(virtual_data_source, initial_stream_position, watermark_delay_threshold)
        self.proto = dsc_proto
        self.virtual_data_source = virtual_data_source

    @classmethod
    def _from_proto(cls, proto: DataSourceConfigProto, vds_proto: VirtualDataSourceProto) -> "DataSourceConfig":
        obj = cls.__new__(cls)
        obj.proto = proto
        obj.virtual_data_source = VirtualDataSourceInteractive._create_from_proto(vds_proto)
        return obj

    @classmethod
    def _create(
        cls,
        virtual_data_source: Union[VirtualDataSource, VirtualDataSourceInteractive],
        initial_stream_position: Optional[str] = None,
        watermark_delay_threshold: Optional[str] = None,
    ) -> DataSourceConfigProto:
        if initial_stream_position is not None and initial_stream_position not in INITIAL_STREAM_POSITION_STR_TO_ENUM:
            raise errors.FP_DSC_STREAM_POSITION(INITIAL_STREAM_POSITION_STR_TO_ENUM.keys())

        vds = virtual_data_source

        dsc_proto = DataSourceConfigProto()
        dsc_proto.virtual_data_source_id.CopyFrom(
            vds._id_proto() if isinstance(vds, VirtualDataSourceInteractive) else vds._id()
        )

        if initial_stream_position is not None:
            dsc_proto.stream_config.initial_stream_position = INITIAL_STREAM_POSITION_STR_TO_ENUM[
                initial_stream_position
            ]

        if watermark_delay_threshold is not None:
            dsc_proto.stream_config.watermark_delay_threshold.FromSeconds(strict_pytimeparse(watermark_delay_threshold))

        return dsc_proto
