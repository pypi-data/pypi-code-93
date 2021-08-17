from typing import Dict
from typing import List
from typing import Optional

from pyspark.sql.types import StructType

from tecton._internals import errors
from tecton.basic_info import prepare_basic_info
from tecton.data_sources.data_source_config import DataSourceConfig
from tecton.feature_packages.feature_package_args import FeatureAggregation
from tecton.feature_packages.feature_package_args import MaterializationConfig
from tecton.feature_packages.feature_package_args import MonitoringConfig
from tecton.feature_packages.feature_package_args import prepare_fp_args
from tecton.feature_packages.feature_package_args import set_online_args
from tecton.feature_packages.feature_package_args import set_push_args
from tecton.feature_packages.feature_package_args import set_temporal_aggregate_args
from tecton.feature_packages.feature_package_args import set_temporal_args
from tecton.transformations.transformation import OnlineTransformation
from tecton.transformations.transformation import Transformation
from tecton_proto.args.feature_package_pb2 import FeaturePackageArgs
from tecton_proto.args.repo_metadata_pb2 import SourceInfo
from tecton_proto.common.id_pb2 import Id
from tecton_spark.logger import get_logger

logger = get_logger("FeaturePackage")


class FeaturePackage:
    """
    Represents a Tecton FeaturePackage declaration.

    To get a declared FeaturePackage instance, call :py:meth:`tecton.get_feature_package`.
    """

    _args: FeaturePackageArgs
    _source_info: SourceInfo

    def _id(self) -> Id:
        return self._args.feature_package_id

    @property
    def name(self) -> str:
        return self._args.info.name

    def __getitem__(self, features):
        from tecton.feature_services.feature_service_args import FeaturesConfig

        return FeaturesConfig(feature_package=self, namespace=self.name, features=features)


class TemporalAggregateFeaturePackage(FeaturePackage):
    """
    Declare a TemporalAggregateFeaturePackage.

    In Tecton, the abstraction for creating and managing features is the Feature Package, implemented as the `FeaturePackage` class.
    A Feature Package contains all information required to manage one or more related features, including:

    - Metadata about the features, which Tecton uses for organization. Examples are name, feature owner, and tags ("developmental", "released", for example.)
    - References to Transformations and Entities, which describe the logic used to generate feature values from raw data.
    - Materialization settings, which describe how and when Tecton should compute feature values.

    The TemporalAggregateFeaturePackage class is used in Tecton to represent one or many
    aggregation-based features. The TemporalAggregateFeaturePackage implements aggregation
    logic that efficient for stream computations, or on many long-running windows.
    """

    def __init__(
        self,
        *,  # All arguments must be specified with keywords
        name: str,
        description: str = "",
        family: str = "",
        tags: Dict[str, str] = None,
        entities: List,
        timestamp_key: Optional[str] = None,
        aggregation_slide_period: str,
        aggregations: List[FeatureAggregation],
        sql: str = None,
        transformation: Transformation = None,
        data_source_configs: Optional[List[DataSourceConfig]] = None,
        online_serving_index: Optional[List[str]] = None,
        owner: str = "",
        materialization: Optional[MaterializationConfig] = None,
        monitoring: Optional[MonitoringConfig] = None,
    ):
        """
        Instantiates a new TemporalAggregateFeaturePackage.

        :param name: Unique, human friendly name that identifies the FeaturePackage.
        :param entities: A list of Entity objects.
        :param aggregation_slide_period: Frequency of Tecton updating the aggregations with new data.
            Tecton batches incoming data and updates the aggregations at the end of every period.
            Formatted as in pytimeparse_.
            Example: `"2hours"`.
        :param aggregations: A list of :class:`FeatureAggregation` structs
        :param transformation: Transformation used to fetch the feature's values. Exactly one of sql & transformation must be set.
        :param materialization: Configuration for how Tecton will materialize data to the feature store.
        :param description: (Optional) Description.
        :param family: (Optional) Family.
        :param owner: (Optional) Owner name, used to organize features.
        :param tags: (Optional) Arbitrary key-value pairs of tagging metadata.
        :param monitoring (Optional): `MonitoringConfig` used to specify the freshness requirements for this feature.
        :param timestamp_key: (Optional) Name of the column that identifies the time of feature values. The column must be of type Spark timestamp.
        :param data_source_configs: (Optional, advanced) List of :class:`DataSourceConfig` that link this FeaturePackage to its VirtualDataSource inputs. Only needed when using sql parameter.
        :param online_serving_index: (Optional, advanced) Defines the set of join keys that will be indexed and queryable during online serving.
            Defaults to the complete set of join keys. Up to one join key may be omitted. If one key is omitted, online requests to a Feature Service will
            return all feature vectors that match the specified join keys. See how to use this in the `Example`_.

        .. _pytimeparse: https://pypi.org/project/pytimeparse/
        .. _Example: https://docs.tecton.ai/v2/examples/fetch-real-time-features.html#fetching-multiple-feature-vectors-with-a-wildcard-index
        """
        from tecton.cli.common import get_fco_source_info

        if data_source_configs is None and sql is not None:
            raise errors.REQUIRED_ARGUMENT("data_source_configs")

        self._source_info = get_fco_source_info()

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=family, tags=tags)
        args = prepare_fp_args(
            basic_info=basic_info,
            entities=entities,
            timestamp_key=timestamp_key,
            sql=sql,
            final_transformation_id=transformation._id() if transformation else None,
            data_source_configs=data_source_configs,
            online_serving_index=online_serving_index,
            materialization=materialization,
            monitoring=monitoring,
        )
        set_temporal_aggregate_args(args, aggregation_slide_period=aggregation_slide_period, aggregations=aggregations)

        self._args = args


class TemporalFeaturePackage(FeaturePackage):
    """
    Declare a TemporalFeaturePackage.

    In Tecton, the abstraction for creating and managing features is the Feature Package, implemented as the `FeaturePackage` class.
    A Feature Package contains all information required to manage one or more related features, including:

    - Metadata about the features, which Tecton uses for organization. Examples are name, feature owner, and tags ("developmental", "released", for example.)
    - References to Transformations and Entities, which describe the logic used to generate feature values from raw data.
    - Materialization settings, which describe how and when Tecton should compute feature values.

    The TemporalFeaturePackage class is the default class used to define features that are computed by Tecton. To push features to
    Tecton from external pipelines, use :class:``PushFeaturePackage``. To define features that are computed at retrieval-time, use
    :class:``OnlineFeaturePackage``.
    """

    def __init__(
        self,
        *,  # All arguments must be specified with keywords
        name: str,
        description: str = "",
        family: str = "",
        tags: Dict[str, str] = None,
        entities: List,
        timestamp_key: Optional[str] = None,
        sql: str = None,
        transformation: Transformation = None,
        data_source_configs: Optional[List[DataSourceConfig]] = None,
        online_serving_index: Optional[List[str]] = None,
        owner: str = "",
        materialization: Optional[MaterializationConfig] = None,
        monitoring: Optional[MonitoringConfig] = None,
    ):
        """
        Instantiates a new TemporalFeaturePackage.

        :param name: Unique, human friendly name that identifies the FeaturePackage.
        :param entities: A list of Entity objects, used to organize features.
        :param transformation: Transformation used to fetch the feature's values. Exactly one of sql & transformation must be set.
        :param materialization: Configuration for how Tecton will materialize data to the feature store.
        :param description: (Optional) description.
        :param family: (Optional) family.
        :param owner: (Optional) Owner name, used to organize features.
        :param tags: (Optional) Arbitrary key-value pairs of tagging metadata.
        :param monitoring (Optional): `MonitoringConfig` used to specify the freshness requirements for this feature.
        :param timestamp_key: (Optional) Name of the column that identifies the time of feature values. The column must be of type Spark timestamp.
        :param data_source_configs: (Optional, advanced) List of :class:`DataSourceConfigs` that link this FeaturePackage to its VirtualDataSource inputs. Only needed when using sql parameter.
        :param online_serving_index: (Optional, advanced) Defines the set of join keys that will be indexed and queryable during online serving.
            Defaults to the complete set of join keys. Up to one join key may be omitted. If one key is omitted, online requests to a Feature Service will
            return all feature vectors that match the specified join keys. See how to use this in the `Example`_.

        .. _Example: https://docs.tecton.ai/v2/examples/fetch-real-time-features.html#fetching-multiple-feature-vectors-with-a-wildcard-index
        """
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=family, tags=tags)
        args = prepare_fp_args(
            basic_info=basic_info,
            entities=entities,
            timestamp_key=timestamp_key,
            sql=sql,
            final_transformation_id=transformation._id() if transformation else None,
            data_source_configs=data_source_configs or [],
            online_serving_index=online_serving_index,
            materialization=materialization,
            monitoring=monitoring,
        )
        set_temporal_args(args)

        self._args = args


class OnlineFeaturePackage(FeaturePackage):
    """
    Declare an OnlineFeaturePackage.

    In Tecton, the abstraction for creating and managing features is the Feature Package, implemented as the `FeaturePackage` class.
    A Feature Package contains all information required to manage one or more related features, including:

    - Metadata about the features, which Tecton uses for organization. Examples are name, feature owner, and tags ("developmental", "released", for example.)
    - References to Transformations and Entities, which describe the logic used to generate feature values from raw data.
    - Materialization settings, which describe how and when Tecton should compute feature values.

    The OnlineFeaturePackage class is used in Tecton to represent one or many features that are computed at retrieval time. To push features to
    Tecton from external pipelines, use :class:``PushFeaturePackage``. To define features that are pre-computed before retrieval,
    use :class:``TemporalFeaturePackage``.
    """

    def __init__(
        self,
        *,  # All arguments must be specified with keywords
        name: str,
        description: str = "",
        family: str = "",
        tags: Dict[str, str] = None,
        entities: Optional[List] = None,
        transformation: OnlineTransformation,
        owner: str = "",
    ):
        """
        Instantiates a new OnlineFeaturePackage.

        :param name: Unique, human friendly name that identifies the FeaturePackage.
        :param entities: A list of Entity objects, used to organize features.
        :param transformation: Transformation used to fetch the feature's values. Exactly one of sql & transformation must be set.
        :param description: (Optional) description.
        :param family: (Optional) family.
        :param owner: (Optional) Owner name, used to organize features.
        :param tags: (Optional) Arbitrary key-value pairs of tagging metadata.
        """
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()
        entities = entities or []
        assert isinstance(transformation, OnlineTransformation)

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=family, tags=tags)
        args = prepare_fp_args(
            basic_info=basic_info,
            entities=entities,
            timestamp_key=None,
            sql=None,
            final_transformation_id=transformation._id() if transformation else None,
            data_source_configs=[],
            online_serving_index=None,
            materialization=None,
            monitoring=None,
        )

        set_online_args(args)

        self._args = args


class PushFeaturePackage(FeaturePackage):
    """
    Declare a PushFeaturePackage.

    In Tecton, the abstraction for creating and managing features is the Feature Package, implemented as the `FeaturePackage` class.
    A Feature Package contains all information required to manage one or more related features, including:

    - Metadata about the features, which Tecton uses for organization. Examples are name, feature owner, and tags ("developmental", "released", for example.)
    - References to Transformations and Entities, which describe the logic used to generate feature values from raw data.
    - Materialization settings, which describe how and when Tecton should compute feature values.

    The PushFeaturePackage class is used in Tecton to represent one or many features that are pushed to Tecton from external feature computation systems.
    To define features that are pre-computed before retrieval, use :class:``TemporalFeaturePackage``. To define features that are computed at retrieval-time, use
    :class:``OnlineFeaturePackage``.
    """

    def __init__(
        self,
        *,  # All arguments must be specified with keywords
        name: str,
        entities: List,
        schema: StructType,
        timestamp_key: Optional[str] = None,
        description: str = "",
        family: str = "",
        tags: Dict[str, str] = None,
        owner: str = "",
        online_serving_index: Optional[List[str]] = None,
        materialization: Optional[MaterializationConfig] = None,
    ):
        """
        Instantiates a new PushFeaturePackage.

        :param name: Unique, human friendly name that identifies the FeaturePackage.
        :param entities: A list of Entity objects, used to organize features.
        :param timestamp_key: (Optional) Name of the column that identifies the time of feature values. The column must be of type Spark timestamp.
        :param schema: A Spark schema definition (StructType) for this FeaturePackage.
            Supported types are - LongType, DoubleType, StringType, BooleanType, TimestampType (for timestamp columns only).
        :param description: (Optional) description.
        :param family: (Optional) family.
        :param owner: (Optional) Owner name, used to organize features.
        :param online_serving_index: (Optional, advanced) Defines the set of join keys that will be indexed and queryable during online serving.
            Defaults to the complete set of join keys. Up to one join key may be omitted. If one key is omitted, online requests to a Feature Service will
            return all feature vectors that match the specified join keys.
        :param materialization: (Optional) configuration for materializing data in offline and online storage.
        """
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()
        entities = entities or []

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=family, tags=tags)
        args = prepare_fp_args(
            basic_info=basic_info,
            entities=entities,
            timestamp_key=timestamp_key,
            sql=None,
            final_transformation_id=None,
            data_source_configs=[],
            online_serving_index=online_serving_index,
            materialization=materialization,
            monitoring=None,
        )

        set_push_args(args, schema)

        self._args = args
