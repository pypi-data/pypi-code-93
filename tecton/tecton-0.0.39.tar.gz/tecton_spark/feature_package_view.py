from abc import ABC
from abc import abstractmethod
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pendulum

from tecton_proto.args.feature_package_pb2 import OfflineFeatureStoreConfig
from tecton_proto.args.pipeline_pb2 import Pipeline
from tecton_proto.args.pipeline_pb2 import PipelineNode
from tecton_proto.data.feature_package_pb2 import FeaturePackage
from tecton_proto.data.feature_package_pb2 import FeatureTransformation
from tecton_proto.data.feature_types_pb2 import FeatureType
from tecton_proto.data.feature_types_pb2 import TrailingTimeWindowAggregation
from tecton_proto.data.feature_view_pb2 import FeatureView
from tecton_proto.data.fp_materialization_pb2 import FpMaterialization
from tecton_proto.data.new_transformation_pb2 import NewTransformation
from tecton_proto.data.transformation_pb2 import Transformation
from tecton_proto.data.virtual_data_source_pb2 import VirtualDataSource
from tecton_spark import feature_package_utils
from tecton_spark import time_utils
from tecton_spark import transformation_helper
from tecton_spark.feature_package_utils import CONTINUOUS_MODE_BATCH_INTERVAL
from tecton_spark.feature_package_utils import get_temporal
from tecton_spark.feature_package_utils import get_temporal_aggregation
from tecton_spark.feature_package_utils import validate_version
from tecton_spark.id_helper import IdHelper
from tecton_spark.logger import get_logger
from tecton_spark.online_serving_index import OnlineServingIndex
from tecton_spark.schema import Schema

logger = get_logger("FeaturePackageOrView")


class FeaturePackageOrView(ABC):
    @classmethod
    def from_fp(cls, feature_package_proto: FeaturePackage):
        return FPBackedFeaturePackageOrView(feature_package_proto)

    @classmethod
    def from_fv(cls, feature_view_proto: FeatureView):
        return FVBackedFeaturePackageOrView(feature_view_proto)

    @classmethod
    def of(cls, fpov: Union[FeaturePackage, FeatureView]):
        if isinstance(fpov, FeatureView):
            return FVBackedFeaturePackageOrView(fpov)
        elif isinstance(fpov, FeaturePackage):
            return FPBackedFeaturePackageOrView(fpov)
        else:
            raise ValueError(f"Unexpected type for argument: {type(fpov)}")

    @abstractmethod
    def id(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_temporal_aggregate(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_continuous_temporal_aggregate(self) -> bool:
        pass

    @property
    @abstractmethod
    def get_feature_store_format_version(self) -> int:
        pass

    @property
    @abstractmethod
    def is_temporal(self) -> bool:
        pass

    @property
    @abstractmethod
    def time_key(self) -> bool:
        pass

    @property
    @abstractmethod
    def join_keys(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def online_serving_index(self) -> OnlineServingIndex:
        pass

    @abstractmethod
    def offline_store_config(self) -> OfflineFeatureStoreConfig:
        pass

    @abstractmethod
    def feature_transformation(self) -> FeatureTransformation:
        pass

    @abstractmethod
    def feature_type(self) -> Optional[FeatureType]:
        pass

    @property
    @abstractmethod
    def timestamp_key(self) -> Optional[str]:
        pass

    @abstractmethod
    def materialization_enabled(self) -> bool:
        pass

    @abstractmethod
    def writes_to_offline_store(self) -> bool:
        pass

    @abstractmethod
    def writes_to_online_store(self) -> bool:
        pass

    @abstractmethod
    def feature_package_proto(self) -> FeaturePackage:
        pass

    @property
    @abstractmethod
    def view_schema(self) -> Schema:
        pass

    @property
    @abstractmethod
    def min_scheduling_interval(self) -> Optional[pendulum.Duration]:
        pass

    @property
    @abstractmethod
    def batch_materialization_schedule(self) -> pendulum.Duration:
        pass

    @abstractmethod
    def allowed_upstream_lateness(self) -> pendulum.Duration:
        pass

    @abstractmethod
    def start_timestamp(self) -> pendulum.datetime:
        pass

    @property
    @abstractmethod
    def data_partitions_coalesce_override(self) -> int:
        pass

    @property
    @abstractmethod
    def virtual_data_source_ids(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def virtual_data_sources(self) -> List[VirtualDataSource]:
        pass

    @property
    @abstractmethod
    def is_feature_view(self) -> bool:
        pass

    @property
    @abstractmethod
    def get_tile_interval(self) -> pendulum.Duration:
        pass

    @property
    @abstractmethod
    def fp_materialization(self) -> FpMaterialization:
        pass

    @property
    @abstractmethod
    def max_aggregation_window(self) -> Optional[int]:
        pass

    @property
    def wildcard_join_key(self) -> Optional[str]:
        """
        Returns a wildcard join key column name for the feature package if it exists;
        Otherwise returns None.
        """
        online_serving_index = self.online_serving_index
        wildcard_keys = [join_key for join_key in self.join_keys if join_key not in online_serving_index.join_keys]
        return wildcard_keys[0] if wildcard_keys else None

    @property
    @abstractmethod
    def vds_proto_map(self) -> Dict[str, VirtualDataSource]:
        pass

    @property
    @abstractmethod
    def transformation_id_proto_map(self) -> Dict[str, Transformation]:
        pass

    @property
    @abstractmethod
    def new_transformations(self) -> List[NewTransformation]:
        pass

    @property
    @abstractmethod
    def trailing_time_window_aggregation(self) -> Optional[TrailingTimeWindowAggregation]:
        pass

    @property
    @abstractmethod
    def serving_ttl(self) -> Optional[pendulum.Duration]:
        pass

    @property
    @abstractmethod
    def features(self) -> List[str]:
        pass

    @property
    @abstractmethod
    def workspace(self) -> str:
        pass

    @property
    @abstractmethod
    def is_online(self):
        pass

    @property
    @abstractmethod
    def is_push(self):
        pass

    @property
    @abstractmethod
    def final_transformation_id_and_deps(self):
        pass

    def _validate_and_return_use_materialized_data(self, use_materialized_data):
        if self.is_online:
            return False

        if use_materialized_data and not (self.writes_to_offline_store and self.materialization_enabled):
            logger.warning(
                "Calculating features from raw data source(s) since materialization to offline feature store is not enabled. This may "
                "result in slow feature computations."
            )
            use_materialized_data = False

        return use_materialized_data


class FPBackedFeaturePackageOrView(FeaturePackageOrView):
    def __init__(self, feature_package_proto: FeaturePackage):
        self.fp = feature_package_proto
        super().__init__()

    @property
    def id(self) -> str:
        return IdHelper.to_string(self.fp.feature_package_id)

    @property
    def name(self) -> str:
        return self.fp.fco_metadata.name

    @property
    def is_temporal_aggregate(self) -> bool:
        return self.fp.feature_transformation.feature_type.HasField("trailing_time_window_aggregation")

    @property
    def is_continuous_temporal_aggregate(self) -> bool:
        return self.fp.feature_transformation.feature_type.trailing_time_window_aggregation.is_continuous

    @property
    def get_feature_store_format_version(self) -> int:
        version = self.fp.feature_store_format_version
        validate_version(version)
        return version

    @property
    def is_temporal(self) -> bool:
        return self.fp.feature_transformation.feature_type.HasField("temporal")

    @property
    def time_key(self) -> bool:
        return self.fp.feature_transformation.feature_type.temporal.time_key

    @property
    def join_keys(self) -> List[str]:
        return list(self.fp.feature_transformation.join_keys)

    @property
    def online_serving_index(self) -> OnlineServingIndex:
        return OnlineServingIndex.from_proto(self.fp.online_serving_index)

    @property
    def offline_store_config(self) -> OfflineFeatureStoreConfig:
        return self.fp.materialization_params.offline_store_config

    @property
    def feature_transformation(self) -> FeatureTransformation:
        return self.fp.feature_transformation

    @property
    def feature_type(self) -> Optional[FeatureType]:
        return feature_package_utils.get_feature_type(self.feature_transformation)

    @property
    def timestamp_key(self) -> Optional[str]:
        return feature_package_utils.get_timestamp_key(self.feature_type)

    @property
    def materialization_enabled(self) -> bool:
        return self.fp.materialization_enabled

    @property
    def writes_to_offline_store(self) -> bool:
        return self.fp.materialization_params.writes_to_offline_store

    @property
    def writes_to_online_store(self) -> bool:
        return self.fp.materialization_params.writes_to_online_store

    @property
    def feature_package_proto(self) -> FeaturePackage:
        return self.fp

    @property
    def view_schema(self) -> Schema:
        return Schema(self.fp.schemas.view_schema)

    @property
    def min_scheduling_interval(self) -> Optional[pendulum.Duration]:
        feature_type = self.feature_type

        duration = None

        if self.is_temporal_aggregate:
            duration = get_temporal_aggregation(feature_type).aggregation_slide_period
        elif self.is_temporal:
            duration = get_temporal(feature_type).schedule_interval

        if not duration:
            duration = self.fp.materialization_params.batch_materialization_schedule

        return time_utils.proto_to_duration(duration)

    @property
    def batch_materialization_schedule(self) -> pendulum.Duration:
        feature_type = self.feature_type

        duration = None

        if self.is_temporal_aggregate:
            if not self.fp.materialization_params.HasField("batch_materialization_schedule"):
                if self.is_continuous_temporal_aggregate:
                    duration = CONTINUOUS_MODE_BATCH_INTERVAL
                else:
                    duration = get_temporal_aggregation(feature_type).aggregation_slide_period
        elif self.is_temporal:
            duration = get_temporal(feature_type).schedule_interval

        if not duration:
            duration = self.fp.materialization_params.batch_materialization_schedule

        return time_utils.proto_to_duration(duration)

    @property
    def allowed_upstream_lateness(self) -> pendulum.Duration:
        return time_utils.proto_to_duration(self.fp.materialization_params.allowed_upstream_lateness)

    @property
    def start_timestamp(self) -> pendulum.datetime:
        return pendulum.instance(self.fp.materialization_params.start_timestamp.ToDatetime())

    @property
    def data_partitions_coalesce_override(self) -> int:
        return self.fp.materialization_params.data_partitions_coalesce_override

    @property
    def virtual_data_source_ids(self) -> List[str]:
        vds_ids = []
        for dsc in self.feature_transformation.data_source_configs:
            vds_ids.append(IdHelper.to_string(dsc.virtual_data_source_id))
        return vds_ids

    @property
    def virtual_data_sources(self) -> List[VirtualDataSource]:
        return self.fp.enrichments.virtual_data_sources

    @property
    def is_feature_view(self) -> bool:
        return False

    @property
    def get_tile_interval(self) -> pendulum.Duration:
        return time_utils.proto_to_duration(feature_package_utils.get_tile_interval(self.fp))

    @property
    def fp_materialization(self) -> FpMaterialization:
        return self.fp.enrichments.fp_materialization

    @property
    def max_aggregation_window(self) -> Optional[int]:
        return feature_package_utils.get_max_aggregation_window(self.feature_transformation)

    @property
    def vds_proto_map(self) -> Dict[str, VirtualDataSource]:
        from tecton_spark import data_source_helper

        return data_source_helper.get_vds_proto_map(self.fp.enrichments.virtual_data_sources)

    @property
    def transformation_id_proto_map(self) -> Dict[str, Transformation]:
        return transformation_helper.get_transformation_id2proto_map(self.fp.enrichments.transformations)

    @property
    def new_transformations(self) -> List[NewTransformation]:
        raise NotImplementedError

    @property
    def trailing_time_window_aggregation(self) -> Optional[TrailingTimeWindowAggregation]:
        if not self.is_temporal_aggregate or not self.feature_type:
            return None

        return self.feature_type.trailing_time_window_aggregation

    @property
    def serving_ttl(self) -> Optional[pendulum.Duration]:
        return time_utils.proto_to_duration(feature_package_utils.get_serving_ttl(self.feature_type))

    @property
    def features(self) -> List[str]:
        if self.is_temporal_aggregate and self.trailing_time_window_aggregation:
            return [
                f.output_feature_name
                for f in self.trailing_time_window_aggregation.features
                if f.output_feature_name != self.timestamp_key
            ]
        elif feature_package_utils.is_online(self.feature_type):
            return Schema(self.fp.schemas.view_schema).column_names()
        view_schema = Schema(self.fp.schemas.view_schema)
        return feature_package_utils.get_input_feature_columns(
            view_schema.to_proto(), self.join_keys, self.timestamp_key
        )

    @property
    def workspace(self) -> str:
        return self.fp.fco_metadata.workspace

    @property
    def is_online(self):
        return self.feature_type is not None and feature_package_utils.is_online(self.feature_type)

    @property
    def is_push(self):
        return self.feature_type is not None and feature_package_utils.is_push(self.feature_type)

    @property
    def final_transformation_id_and_deps(self):
        if not self.feature_transformation.HasField("final_transformation_id"):
            return None

        return (
            self.feature_transformation.final_transformation_id,
            self.fp.enrichments.transformations,
            self.fp.enrichments.virtual_data_sources,
        )


class FVBackedFeaturePackageOrView(FeaturePackageOrView):
    def __init__(self, feature_view_proto: FeatureView):
        self.fv = feature_view_proto
        super().__init__()

    @property
    def id(self) -> str:
        return IdHelper.to_string(self.fv.feature_view_id)

    @property
    def name(self) -> str:
        return self.fv.fco_metadata.name

    @property
    def is_temporal_aggregate(self) -> bool:
        return self.fv.HasField("temporal_aggregate")

    @property
    def is_continuous_temporal_aggregate(self) -> bool:
        return self.fv.temporal_aggregate.is_continuous

    @property
    def get_feature_store_format_version(self) -> int:
        version = self.fv.feature_store_format_version
        validate_version(version)
        return version

    @property
    def is_temporal(self) -> bool:
        return self.fv.HasField("temporal")

    @property
    def is_feature_table(self) -> bool:
        return self.fv.HasField("feature_table")

    @property
    def time_key(self) -> bool:
        return self.fv.timestamp_key

    @property
    def join_keys(self) -> List[str]:
        return list(self.fv.join_keys)

    @property
    def online_serving_index(self) -> OnlineServingIndex:
        return OnlineServingIndex.from_proto(self.fv.online_serving_index)

    @property
    def offline_store_config(self) -> OfflineFeatureStoreConfig:
        return self.fv.materialization_params.offline_store_config

    @property
    def feature_transformation(self) -> FeatureTransformation:
        raise NotImplementedError

    @property
    def feature_type(self) -> Optional[FeatureType]:
        raise NotImplementedError

    @property
    def timestamp_key(self) -> Optional[str]:
        return self.fv.timestamp_key

    @property
    def materialization_enabled(self) -> bool:
        return self.fv.materialization_enabled

    @property
    def writes_to_offline_store(self) -> bool:
        if self.is_temporal_aggregate or self.is_temporal:
            return self.fv.materialization_params.writes_to_offline_store
        elif self.is_feature_table:
            return self.fv.feature_table.offline_enabled
        else:
            raise ValueError(f"Invalid invocation on unsupported FeatureView type")

    @property
    def writes_to_online_store(self) -> bool:
        if self.is_temporal_aggregate or self.is_temporal:
            return self.fv.materialization_params.writes_to_online_store
        elif self.is_feature_table:
            return self.fv.feature_table.online_enabled
        else:
            raise ValueError(f"Invalid invocation on unsupported FeatureView type")

    @property
    def feature_package_proto(self) -> FeaturePackage:
        raise NotImplementedError

    @property
    def view_schema(self) -> Schema:
        return Schema(self.fv.schemas.view_schema)

    @property
    def min_scheduling_interval(self) -> Optional[pendulum.Duration]:
        if self.is_push:
            return None

        duration = None
        if self.is_temporal_aggregate:
            duration = self.fv.temporal_aggregate.slide_interval
        elif self.is_temporal:
            duration = self.fv.materialization_params.schedule_interval

        return time_utils.proto_to_duration(duration)

    @property
    def batch_materialization_schedule(self) -> pendulum.Duration:
        if self.is_temporal_aggregate and not self.fv.materialization_params.HasField("schedule_interval"):
            if self.is_continuous_temporal_aggregate:
                return time_utils.proto_to_duration(CONTINUOUS_MODE_BATCH_INTERVAL)
            else:
                return time_utils.proto_to_duration(self.fv.temporal_aggregate.slide_interval)
        else:
            return time_utils.proto_to_duration(self.fv.materialization_params.schedule_interval)

    @property
    def allowed_upstream_lateness(self) -> pendulum.Duration:
        return time_utils.proto_to_duration(self.fv.materialization_params.allowed_upstream_lateness)

    @property
    def start_timestamp(self) -> pendulum.datetime:
        return pendulum.instance(self.fv.materialization_params.start_timestamp.ToDatetime())

    @property
    def data_partitions_coalesce_override(self) -> int:
        return 10  # Value of DEFAULT_COALESCE_FOR_S3 as defined in materilization.py

    @property
    def virtual_data_source_ids(self) -> List[str]:
        return pipeline_to_vds_ids(self.fv.pipeline)

    @property
    def virtual_data_sources(self) -> List[VirtualDataSource]:
        return self.fv.enrichments.virtual_data_sources

    @property
    def is_feature_view(self) -> bool:
        return True

    @property
    def get_tile_interval(self) -> pendulum.Duration:
        if self.is_temporal_aggregate:
            return time_utils.proto_to_duration(self.fv.temporal_aggregate.slide_interval)
        elif self.is_temporal:
            return time_utils.proto_to_duration(self.fv.materialization_params.schedule_interval)

        raise ValueError(f"Invalid invocation on unsupported FeatureView type")

    @property
    def fp_materialization(self) -> FpMaterialization:
        return self.fv.enrichments.fp_materialization

    @property
    def max_aggregation_window(self) -> Optional[int]:
        if self.is_temporal_aggregate:
            return max(
                [feature.window for feature in self.fv.temporal_aggregate.features],
                key=lambda window: window.ToSeconds(),
            )
        return None

    @property
    def vds_proto_map(self) -> Dict[str, VirtualDataSource]:
        from tecton_spark import data_source_helper

        return data_source_helper.get_vds_proto_map(self.fv.enrichments.virtual_data_sources)

    @property
    def transformation_id_proto_map(self) -> Dict[str, Transformation]:
        raise NotImplementedError

    @property
    def new_transformations(self) -> List[NewTransformation]:
        return list(self.fv.enrichments.transformations)

    @property
    def trailing_time_window_aggregation(self) -> Optional[TrailingTimeWindowAggregation]:
        if not self.is_temporal_aggregate:
            return None

        aggregation = TrailingTimeWindowAggregation()
        aggregation.time_key = self.timestamp_key
        slide_period_seconds = self.fv.temporal_aggregate.slide_interval.ToSeconds()
        aggregation.is_continuous = slide_period_seconds == 0
        aggregation.aggregation_slide_period.FromSeconds(slide_period_seconds)

        aggregation.features.extend(self.fv.temporal_aggregate.features)
        return aggregation

    @property
    def serving_ttl(self) -> Optional[pendulum.Duration]:
        if self.is_temporal:
            return time_utils.proto_to_duration(self.fv.temporal.serving_ttl)
        elif self.is_feature_table:
            return time_utils.proto_to_duration(self.fv.feature_table.serving_ttl)
        return None

    @property
    def features(self) -> List[str]:
        if self.is_temporal_aggregate and self.trailing_time_window_aggregation:
            return [
                f.output_feature_name
                for f in self.trailing_time_window_aggregation.features
                if f.output_feature_name != self.timestamp_key
            ]
        elif self.is_online:
            return Schema(self.fv.schemas.view_schema).column_names()
        view_schema = Schema(self.fv.schemas.view_schema)
        return feature_package_utils.get_input_feature_columns(
            view_schema.to_proto(), self.join_keys, self.timestamp_key
        )

    @property
    def workspace(self) -> str:
        return self.fv.fco_metadata.workspace

    @property
    def is_online(self) -> bool:
        return self.fv.HasField("on_demand_feature_view")

    @property
    def is_push(self) -> bool:
        return self.fv.HasField("feature_table")

    @property
    def final_transformation_id_and_deps(self):
        raise NotImplementedError


def pipeline_to_vds_ids(pipeline: Pipeline) -> List[str]:
    vds_ids: List[str] = []

    def _recurse_pipeline_to_vds_ids(pipeline_node: PipelineNode, vds_ids_: List[str]):
        if pipeline_node.HasField("data_source_node"):
            _id = pipeline_node.data_source_node.virtual_data_source_id
            vds_id = IdHelper.to_string(_id)
            vds_ids_.append(vds_id)
        elif pipeline_node.HasField("transformation_node"):
            inputs = pipeline_node.transformation_node.inputs
            for input_ in inputs:
                _recurse_pipeline_to_vds_ids(input_.node, vds_ids_)

    _recurse_pipeline_to_vds_ids(pipeline.root, vds_ids)

    return vds_ids
