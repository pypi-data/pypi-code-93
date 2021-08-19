from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import pendulum
from pyspark.sql.types import StructType
from typeguard import typechecked

from tecton._internals.feature_definition import FeatureDefinition
from tecton.basic_info import prepare_basic_info
from tecton.entities.entity import Entity
from tecton.entities.entity import OverriddenEntity
from tecton.feature_packages.feature_package_args import DeltaConfig
from tecton_proto.args.feature_package_pb2 import EntityKeyOverride
from tecton_proto.args.feature_view_pb2 import FeatureTableArgs
from tecton_proto.args.feature_view_pb2 import FeatureViewArgs
from tecton_proto.args.feature_view_pb2 import FeatureViewType
from tecton_spark.id_helper import IdHelper
from tecton_spark.spark_schema_wrapper import SparkSchemaWrapper
from tecton_spark.time_utils import strict_pytimeparse


class FeatureTable(FeatureDefinition):
    """
    Declare a FeatureTable.

    The FeatureTable class is used to represent one or many features that are pushed to Tecton from external feature computation systems.
    """

    @typechecked
    def __init__(
        self,
        *,  # All arguments must be specified with keywords
        name: str,
        entities: List[Union[Entity, OverriddenEntity]],
        schema: StructType,
        online: bool = False,
        offline: bool = False,
        ttl: Optional[str] = None,
        description: str = "",
        family: str = "",
        tags: Dict[str, str] = None,
        owner: str = "",
        online_serving_index: Optional[List[str]] = None,
        offline_config: DeltaConfig = DeltaConfig()
    ):
        """
        Instantiates a new FeatureTable.

        :param name: Unique, human friendly name that identifies the FeatureTable.
        :param entities: A list of Entity objects, used to organize features.
        :param schema: A Spark schema definition (StructType) for the FeatureTable.
            Supported types are: LongType, DoubleType, StringType, BooleanType and TimestampType (for inferred timestamp column only).
        :param online: Enable writing to online feature store.
        :param offline: Enable writing to offline feature store.
        :param ttl: Time-to-live beyond which feature values become ineligible for serving in production.
        :param description: (Optional) description.
        :param family: (Optional) Family of this Feature Table, used to group Tecton Primitives.
        :param tags: (Optional) Tags associated with this Tecton Primitive (key-value pairs of arbitrary metadata).
        :param owner: Owner name (typically the email of the primary maintainer).
        :param online_serving_index: (Optional, advanced) Defines the set of join keys that will be indexed and queryable during online serving.
            Defaults to the complete set of join keys. Up to one join key may be omitted. If one key is omitted, online requests to a Feature Service will
            return all feature vectors that match the specified join keys.
        :param offline_config: Configuration for how data is written to the offline feature store.
        :returns: A Feature Table
        """
        from tecton.cli.common import get_fco_source_info

        self._source_info = get_fco_source_info()
        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=family, tags=tags)

        self._args = FeatureViewArgs()

        self._args.feature_view_id.CopyFrom(IdHelper.from_string(IdHelper.generate_string_id()))
        self._args.info.CopyFrom(basic_info)
        self._args.feature_view_type = FeatureViewType.FEATURE_VIEW_TYPE_FEATURE_TABLE

        self._args.entities.extend(
            [EntityKeyOverride(entity_id=entity._id(), join_keys=entity._args_join_keys()) for entity in entities]
        )
        if online_serving_index:
            self._args.online_serving_index.extend(online_serving_index)

        self._args.online_enabled = online
        self._args.offline_enabled = offline

        feature_table_args = FeatureTableArgs()
        feature_table_args.output_schema.CopyFrom(SparkSchemaWrapper(schema).to_proto())
        if ttl:
            feature_table_args.serving_ttl.FromTimedelta(pendulum.duration(seconds=strict_pytimeparse(ttl)))
        feature_table_args.offline_config.CopyFrom(offline_config._to_proto())
        self._args.feature_table_args.CopyFrom(feature_table_args)
