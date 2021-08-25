from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import attr
import pendulum
import pytimeparse
from google.protobuf.duration_pb2 import Duration
from pyspark.sql.types import StructType

from tecton._internals import errors
from tecton.aggregation_functions import AggregationFunction
from tecton.data_sources.data_source_config import DataSourceConfig
from tecton_proto.args import feature_package_pb2
from tecton_proto.args import feature_view_pb2
from tecton_proto.args.basic_info_pb2 import BasicInfo
from tecton_proto.common.id_pb2 import Id
from tecton_spark.id_helper import IdHelper
from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper

CONTINUOUS_MODE = "continuous"
AVAILABILITY_SPOT = "spot"
AVAILABILITY_ON_DEMAND = "on_demand"
SUPPORTED_AVAILABILITY = [AVAILABILITY_SPOT, AVAILABILITY_ON_DEMAND]
BACKFILL_CONFIG_MODE_PROTO_PREFIX = "BACKFILL_CONFIG_MODE_"
BACKFILL_CONFIG_MODE_MULTIPLE = "multiple_batch_schedule_intervals_per_job"
BACKFILL_CONFIG_MODE_SINGLE = "single_batch_schedule_interval_per_job"


@attr.s(auto_attribs=True)
class FeatureAggregation(object):
    """
    This class describes a single aggregation that is applied in a batch or stream window aggregate feature view.

    :param column: Column name of the feature we are aggregating.
    :type column: str
    :param function: One of the built-in aggregation functions.
    :type function: Union[str, AggregationFunction]
    :param time_windows: Duration to aggregate over in pytimeparse_ format. Examples: ``"30days"``, ``["8hours", "30days", "365days"]``.
    :type time_windows: Union[str, List[str]]

    `function` can be one of predefined numeric aggregation functions, namely ``"count"``, ``"sum"``, ``"mean"``, ``"min"``, ``"max"``. For
    these numeric aggregations, you can pass the name of it as a string.

    In addition to numeric aggregations, :class:`FeatureAggregation` supports "last-n" aggregations that
    will compute the last N distinct values for the column by timestamp. Right now only string column types are supported as inputs
    to this aggregation, i.e., the resulting feature value will be a list of strings.

    You can use it via the ``last_distinct()`` helper function like this:

    .. code-block:: python

        from tecton.aggregation_functions import last_distinct
        my_fv = BatchWindowAggregateFeatureView(
        ...
        aggregations=[FeatureAggregation(
            column='my_column',
            function=last_distinct(15),
            time_windows=['7days'])],
        ...
        )

    .. _pytimeparse: https://pypi.org/project/pytimeparse/
    """

    column: str
    """"""
    function: Union[str, AggregationFunction]
    """One of the built-in aggregation functions (`'count'`, `'sum'`, `'mean'`, `'min'`, `'max'`)."""
    time_windows: Union[str, List[str]]
    """
       Examples: `"30days"`, `["8hours", "30days", "365days"]`.

       .. _pytimeparse: https://pypi.org/project/pytimeparse/
       """

    def _to_proto(self):
        proto = feature_package_pb2.FeatureAggregation()
        proto.column = self.column

        if isinstance(self.function, str):
            proto.function = self.function
        elif isinstance(self.function, AggregationFunction):
            proto.function = self.function.name
            for k, v in self.function.params.items():
                assert isinstance(v, int)
                proto.function_params[k].CopyFrom(feature_package_pb2.ParamValue(int64_value=v))
        else:
            raise TypeError(f"Invalid function type: {type(self.function)}")

        windows = self.time_windows if isinstance(self.time_windows, list) else [self.time_windows]
        for w in windows:
            duration = Duration()
            duration.FromTimedelta(pendulum.duration(seconds=pytimeparse.parse(w)))
            proto.time_window_durations.append(duration)
            proto.time_windows.append(w)
        return proto


@attr.s(auto_attribs=True)
class ExistingClusterConfig:
    """Use an existing Databricks or EMR cluster.

    :param existing_cluster_id: ID of the existing cluster.
    """

    existing_cluster_id: str

    def _to_proto(self) -> feature_package_pb2.ExistingClusterConfig:
        proto = feature_package_pb2.ExistingClusterConfig()
        proto.existing_cluster_id = self.existing_cluster_id

        return proto


@attr.s(auto_attribs=True)
class EMRClusterConfig:
    """Configuration used to specify materialization cluster options.

    This class describes the attributes of the new clusters which are created in EMR during
    materialization jobs. You can configure options of these clusters, like cluster size and extra pip dependencies.

    :param instance_type: Instance type for the cluster. Must be a valid type as listed in https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-supported-instance-types.html.
        If not specified, a value determined by the Tecton backend is used.
    :param instance_availability: Instance availability for the cluster : "spot" or "on_demand".
        If not specified, default is spot.
    :param number_of_workers: Number of instances for the materialization job. If not specified, a value determined by the Tecton backend is used
    :param root_volume_size_in_gb: Size of the root volume in GB per instance for the materialization job.
        If not specified, a value determined by the Tecton backend is used.
    :param extra_pip_dependencies: Extra pip dependencies to be installed on the cluster.
    :param spark_config: Map of Spark configuration options and their respective values that will be passed to the
        FeatureView materialization Spark cluster. Currently, we support only the following options: ``spark.driver.memory``, ``spark.driver.memoryOverhead``, ``spark.executor.memory``, ``spark.executor.memoryOverhead``


    Note on ``extra_pip_dependencies``: This is a list of PyPI package names that will be installed during
    materialization. These libraries will only be available to use inside Spark UDFs. For example, if you set
    ``extra_pip_dependencies=["tensorflow"]``, you can use it in your transformation like this:

    .. code-block:: python

        @transformation(mode='pyspark')
        def test_transformation(transformation_input):
            from pyspark.sql import functions as F
            from pyspark.sql.types import IntegerType

            def my_tensorflow(x):
                import tensorflow as tf
                return int(tf.math.log1p(float(x)).numpy())

            my_tensorflow_udf = F.udf(my_tensorflow, IntegerType())

    The import has to be within the UDF body. Putting it at the top of the file or inside transformation
    function won't work.
    """

    instance_type: Optional[str] = None
    instance_availability: Optional[str] = None
    number_of_workers: Optional[int] = None
    root_volume_size_in_gb: Optional[int] = None
    extra_pip_dependencies: Optional[List[str]] = None
    spark_config: Optional[Dict[str, str]] = None

    def _to_proto(self) -> feature_package_pb2.NewEMRClusterConfig:
        proto = feature_package_pb2.NewEMRClusterConfig()
        if self.instance_type:
            proto.instance_type = self.instance_type
        if self.instance_availability:
            if self.instance_availability not in SUPPORTED_AVAILABILITY:
                raise ValueError(
                    f"Instance availability {self.instance_availability} is not supported. Choose {AVAILABILITY_SPOT} or {AVAILABILITY_ON_DEMAND}"
                )
            proto.instance_availability = self.instance_availability
        if self.number_of_workers:
            proto.number_of_workers = self.number_of_workers
        if self.root_volume_size_in_gb:
            proto.root_volume_size_in_gb = self.root_volume_size_in_gb
        if self.extra_pip_dependencies:
            proto.extra_pip_dependencies.extend(self.extra_pip_dependencies)
        if self.spark_config:
            spark_config = SparkConfigWrapper(self.spark_config)._to_proto()
            proto.spark_config.CopyFrom(spark_config)

        return proto


# This is for historical reasons before we introduced EMRClusterConfig
NewEMRClusterConfig = EMRClusterConfig


@attr.s(auto_attribs=True)
class DatabricksClusterConfig:
    """Configuration used to specify materialization cluster options.

    This class describes the attributes of the new clusters which are created in Databricks during
    materialization jobs. You can configure options of these clusters, like cluster size and extra pip dependencies.

    :param instance_type: Instance type for the cluster. Must be a valid type as listed in https://databricks.com/product/aws-pricing/instance-types.
        If not specified, a value determined by the Tecton backend is used.
    :param instance_availability: Instance availability for the cluster : "spot" or "on_demand".
        If not specified, default is spot.
    :param number_of_workers: Number of instances for the materialization job. If not specified, a value determined by the Tecton backend is used
    :param root_volume_size_in_gb: Size of the root volume in GB per instance for the materialization job.
        If not specified, a value determined by the Tecton backend is used.
    :param extra_pip_dependencies: Extra pip dependencies to be installed on the cluster. Can be PyPI packages or S3 wheels/eggs.
    :param spark_config: Map of Spark configuration options and their respective values that will be passed to the
        FeatureView materialization Spark cluster. Currently, we support only the following options: ``spark.driver.memory``, ``spark.driver.memoryOverhead``, ``spark.executor.memory``, ``spark.executor.memoryOverhead``


    Note on ``extra_pip_dependencies``: This is a list of pip package names that will be installed during
    materialization. These libraries will only be available to use inside Spark UDFs. For example, if you set
    ``extra_pip_dependencies=["tensorflow"]``, you can use it in your transformation like this:

    .. code-block:: python

        @transformation(mode='pyspark')
        def test_transformation(transformation_input):
            from pyspark.sql import functions as F
            from pyspark.sql.types import IntegerType

            def my_tensorflow(x):
                import tensorflow as tf
                return int(tf.math.log1p(float(x)).numpy())

            my_tensorflow_udf = F.udf(my_tensorflow, IntegerType())

    The import has to be within the UDF body. Putting it at the top of the file or inside transformation
    function won't work.
    """

    instance_type: Optional[str] = None
    instance_availability: Optional[str] = None
    number_of_workers: Optional[int] = None
    root_volume_size_in_gb: Optional[int] = None
    extra_pip_dependencies: Optional[List[str]] = None
    spark_config: Optional[Dict[str, str]] = None

    def _to_proto(self) -> feature_package_pb2.NewDatabricksClusterConfig:
        proto = feature_package_pb2.NewDatabricksClusterConfig()
        if self.instance_type:
            proto.instance_type = self.instance_type
        if self.instance_availability:
            if self.instance_availability not in SUPPORTED_AVAILABILITY:
                raise ValueError(
                    f"Instance availability {self.instance_availability} is not supported. Choose {AVAILABILITY_SPOT} or {AVAILABILITY_ON_DEMAND}"
                )
            proto.instance_availability = self.instance_availability
        if self.number_of_workers:
            proto.number_of_workers = self.number_of_workers
        if self.root_volume_size_in_gb:
            proto.root_volume_size_in_gb = self.root_volume_size_in_gb
        if self.extra_pip_dependencies:
            # Pretty easy to do e.g. extra_pip_dependencies="tensorflow" by mistake and end up with
            # [t, e, n, s, o, r, f, l, o, w] as a list of dependencies passed to the Spark job.
            #
            # Since this is annoying to debug, we check for that here.
            if isinstance(self.extra_pip_dependencies, str):
                raise ValueError("extra_pip_dependencies must be a list")
            proto.extra_pip_dependencies.extend(self.extra_pip_dependencies)
        if self.spark_config:
            spark_config = SparkConfigWrapper(self.spark_config)._to_proto()
            proto.spark_config.CopyFrom(spark_config)

        return proto


# This is for historical reasons before we introduced DatabricksClusterConfig
NewDatabricksClusterConfig = DatabricksClusterConfig


@attr.s(auto_attribs=True)
class SparkConfigWrapper:
    spark_config_map: Dict[str, str]

    SUPPORTED_OPTS = {
        "spark.driver.memory": "spark_driver_memory",
        "spark.executor.memory": "spark_executor_memory",
        "spark.driver.memoryOverhead": "spark_driver_memory_overhead",
        "spark.executor.memoryOverhead": "spark_executor_memory_overhead",
    }

    def _to_proto(self):
        proto = feature_package_pb2.SparkConfig()
        for opt, val in self.spark_config_map.items():
            if opt not in self.SUPPORTED_OPTS:
                raise ValueError(f"Spark config option {opt} is not supported.")
            setattr(proto, self.SUPPORTED_OPTS[opt], val)

        return proto


@attr.s(auto_attribs=True)
class ParquetConfig:
    """(Config Class) ParquetConfig Class.

    This class describes the attributes of Parquet-based offline feature store storage for a package.
    """

    def _to_proto(self):
        store_config = feature_package_pb2.OfflineFeatureStoreConfig()
        store_config.parquet.SetInParent()
        return store_config


@attr.s(auto_attribs=True)
class DeltaConfig:
    """(Config Class) DeltaConfig Class.

    This class describes the attributes of DeltaLake-based offline feature store storage for a package.
    """

    time_partition_size: Optional[str] = "24h"
    """The size of a time partition in the DeltaLake table, specified as a time string. Defaults to "24h"."""

    def _to_proto(self):
        store_config = feature_package_pb2.OfflineFeatureStoreConfig()
        store_config.delta.time_partition_size.FromTimedelta(
            pendulum.duration(seconds=pytimeparse.parse(self.time_partition_size))
        )
        return store_config


@attr.s(auto_attribs=True)
class MaterializationConfig:
    """
    Configuration used to specify materialization options.

    This class is used as an argument to :class:`FeaturePackage`. It is used to group together
    materialization-related parameters.

    :param offline_enabled: Enable writing to offline feature store
    :param online_enabled: Enable writing to online feature store
    :param feature_start_time: Start time for materialization data. We won't compute feature values for timestamps earlier than this. Required if offline_enabled=True.
    :param schedule_interval: The aggregation granularity for aggregate feature transformations.
    :param serving_ttl: Time-to-live beyond which feature values become ineligible for serving in production.
    :param data_lookback_period: The amount of data processed by each batch transformation job.
    :param max_batch_aggregation_interval:  (Advanced) makes batch job scheduler group jobs together for efficiency.
    :param schedule_offset: The amount of time batch job scheduler will wait for late data.
    :param batch_materialization: Batch materialization cluster configuration. Should be one of:
        [``NewEMRClusterConfig``, ``NewDatabricksClusterConfig``, ``ExistingClusterConfig``]
    :param streaming_materialization: Streaming materialization cluster configuration. Should be one of:
        [``NewEMRClusterConfig``, ``NewDatabricksClusterConfig``, ``ExistingClusterConfig``]
    """

    offline_enabled: bool = False
    online_enabled: bool = False
    offline_config: Optional[Union[ParquetConfig, DeltaConfig]] = ParquetConfig()
    feature_start_time: Optional[pendulum.DateTime] = None
    schedule_interval: Optional[str] = None
    serving_ttl: Optional[str] = None
    data_lookback_period: Optional[str] = None
    max_batch_aggregation_interval: Optional[str] = None
    schedule_offset: Optional[str] = None
    batch_materialization: Optional[
        Union[ExistingClusterConfig, NewDatabricksClusterConfig, NewEMRClusterConfig]
    ] = None
    streaming_materialization: Optional[
        Union[ExistingClusterConfig, NewDatabricksClusterConfig, NewEMRClusterConfig]
    ] = None

    def _to_proto(self) -> feature_package_pb2.MaterializationConfig:
        proto = feature_package_pb2.MaterializationConfig()

        if self.schedule_interval:
            proto.schedule_interval.FromTimedelta(pendulum.duration(seconds=pytimeparse.parse(self.schedule_interval)))

        if self.serving_ttl:
            proto.serving_ttl.FromTimedelta(pendulum.duration(seconds=pytimeparse.parse(self.serving_ttl)))

        if self.feature_start_time:
            proto.feature_start_time.FromDatetime(self.feature_start_time)

        proto.online_enabled = self.online_enabled
        if self.offline_config:
            proto.offline_config.CopyFrom(self.offline_config._to_proto())

        proto.offline_enabled = self.offline_enabled

        if self.data_lookback_period:
            proto.data_lookback_period.FromTimedelta(
                pendulum.duration(seconds=pytimeparse.parse(self.data_lookback_period))
            )

        if self.max_batch_aggregation_interval:
            proto.max_batch_aggregation_interval.FromTimedelta(
                pendulum.duration(seconds=pytimeparse.parse(self.max_batch_aggregation_interval))
            )

        if self.schedule_offset:
            proto.schedule_offset.FromTimedelta(pendulum.duration(seconds=pytimeparse.parse(self.schedule_offset)))

        if self.batch_materialization:
            cluster_config = self.cluster_config_to_proto(self.batch_materialization)
            proto.batch_materialization.CopyFrom(cluster_config)
        if self.streaming_materialization:
            cluster_config = self.cluster_config_to_proto(self.streaming_materialization)
            proto.streaming_materialization.CopyFrom(cluster_config)
        return proto

    @staticmethod
    def cluster_config_to_proto(
        config: Union[ExistingClusterConfig, NewDatabricksClusterConfig, NewEMRClusterConfig]
    ) -> feature_package_pb2.ClusterConfig:
        if isinstance(config, ExistingClusterConfig):
            cluster_config = feature_package_pb2.ClusterConfig(existing_cluster=config._to_proto())
        elif isinstance(config, NewDatabricksClusterConfig):
            cluster_config = feature_package_pb2.ClusterConfig(new_databricks=config._to_proto())
        elif isinstance(config, NewEMRClusterConfig):
            cluster_config = feature_package_pb2.ClusterConfig(new_emr=config._to_proto())
        else:
            raise TypeError(f"Invalid cluster config type: {type(config)}")
        return cluster_config


@attr.s(auto_attribs=True)
class MonitoringConfig:
    """Configuration used to specify monitoring options.

    This class describes the FeatureView materialization freshness and alerting configurations. Requires
    materialization to be enabled.

    :param monitor_freshness: Defines the enabled/disabled state of monitoring.
    :type monitor_freshness: bool
    :param expected_feature_freshness: Threshold used to determine if recently materialized feature data is stale.
        Data is stale if ``now - anchor_time(most_recent_feature_value) > expected_feature_freshness``.
        Value must be at least 2 times the feature tile length.
        If not specified, a value determined by the Tecton backend is used
    :type expected_feature_freshness: str, optional
    :param alert_email: Email that alerts for this FeatureView will be sent to.
    :type alert_email: str, optional
    """

    monitor_freshness: bool
    expected_feature_freshness: Optional[str] = None
    alert_email: Optional[str] = None

    def _to_proto(self) -> feature_package_pb2.MonitoringConfig:
        proto = feature_package_pb2.MonitoringConfig()

        if self.expected_feature_freshness:
            proto.expected_feature_freshness.FromTimedelta(
                pendulum.duration(seconds=pytimeparse.parse(self.expected_feature_freshness))
            )

        proto.alert_email = self.alert_email or ""
        proto.monitor_freshness = self.monitor_freshness
        return proto


@attr.s(auto_attribs=True)
class BackfillConfig:
    """Configuration used to specify backfill options.

    This class configures the backfill behavior of a Batch Feature View. Requires
    materialization to be enabled.

    :param mode: Determines whether Tecton batches backfill jobs:
        [``single_batch_schedule_interval_per_job``, ``multiple_batch_schedule_intervals_per_job``]
    """

    mode: str

    def _to_proto(self) -> feature_view_pb2.BackfillConfig:
        proto = feature_view_pb2.BackfillConfig()
        mode_enum = feature_view_pb2.BackfillConfigMode.Value(BACKFILL_CONFIG_MODE_PROTO_PREFIX + self.mode.upper())
        if not mode_enum:
            # TODO: add BACKFILL_CONFIG_MODE_SINGLE when supported
            raise errors.InvalidBackfillConfigMode(self.name, self.mode, [BACKFILL_CONFIG_MODE_MULTIPLE])
        proto.mode = mode_enum
        return proto


def prepare_fp_args(
    *,  # All arguments must be specified with keywords
    basic_info: BasicInfo,
    entities: List,
    timestamp_key: Optional[str],
    sql: Optional[str],
    final_transformation_id: Optional[Id],
    data_source_configs: Optional[List[DataSourceConfig]],
    online_serving_index: Optional[List[str]],
    materialization: Optional[MaterializationConfig],
    monitoring: Optional[MonitoringConfig],
) -> feature_package_pb2.FeaturePackageArgs:
    # Basics
    args = feature_package_pb2.FeaturePackageArgs()
    args.feature_package_id.CopyFrom(IdHelper.from_string(IdHelper.generate_string_id()))
    args.info.CopyFrom(basic_info)
    args.entities.extend(
        [
            feature_package_pb2.EntityKeyOverride(entity_id=entity._id(), join_keys=entity._args_join_keys())
            for entity in entities
        ]
    )

    if sql is not None:
        args.view_sql = sql

    if data_source_configs:
        args.data_source_configs.extend([dsc.proto for dsc in data_source_configs])
    else:
        if data_source_configs is None and sql is not None:
            raise TypeError("data_source_configs cannot be empty when using sql parameter")

    if materialization:
        args.materialization.CopyFrom(materialization._to_proto())

    if monitoring:
        args.monitoring.CopyFrom(monitoring._to_proto())

    if online_serving_index:
        args.online_serving_index.extend(online_serving_index)

    if timestamp_key:
        args.timestamp_key = timestamp_key

    if final_transformation_id:
        args.final_transformation_id.CopyFrom(final_transformation_id)

    return args


def set_temporal_aggregate_args(
    args: feature_package_pb2.FeaturePackageArgs,
    *,
    aggregation_slide_period: str,
    aggregations: List[FeatureAggregation],
):
    args.temporal_aggregate_args.aggregation_slide_period = aggregation_slide_period
    aggregation_slide_period_val = aggregation_slide_period
    # For continuous mode we use slide interval as 0s
    if aggregation_slide_period == CONTINUOUS_MODE:
        aggregation_slide_period_val = "0s"
    args.temporal_aggregate_args.aggregation_slide_period_duration.FromTimedelta(
        pendulum.duration(seconds=pytimeparse.parse(aggregation_slide_period_val))
    )
    args.temporal_aggregate_args.aggregations.extend([agg._to_proto() for agg in aggregations])


def set_temporal_args(args: feature_package_pb2.FeaturePackageArgs):
    args.temporal_args.no_op = True


def set_online_args(args: feature_package_pb2.FeaturePackageArgs):
    args.online_args.CopyFrom(feature_package_pb2.OnlinePackageArgs(no_op=True))


def set_push_args(args: feature_package_pb2.FeaturePackageArgs, schema: StructType):
    args.push_args.schema.CopyFrom(SparkSchemaWrapper(schema).to_proto())
