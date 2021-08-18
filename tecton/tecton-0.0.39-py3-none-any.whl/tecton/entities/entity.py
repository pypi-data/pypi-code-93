from typing import Dict
from typing import List
from typing import Union

from tecton._internals import errors
from tecton._internals import utils
from tecton.basic_info import prepare_basic_info
from tecton.entities.entity_args import prepare_args
from tecton_proto.args.entity_pb2 import EntityArgs
from tecton_proto.args.repo_metadata_pb2 import SourceInfo
from tecton_proto.common.id_pb2 import Id
from tecton_spark import errors
from tecton_spark.logger import get_logger

logger = get_logger("Entity")


class Entity:
    """
    Declare an Entity, used to organize and join features.

    An Entity is a class that represents an Entity that is being modelled in Tecton.
    Entities are used to index and organize features - a :class:`FeatureView`
    contains at least one Entity.

    Entities contain metadata about *join keys*, which represent the columns
    that are used to join features together.
    """

    _args: EntityArgs
    _source_info: SourceInfo

    def __init__(
        self,
        *,
        name: str,
        description: str = "",
        family: str = "",
        tags: Dict[str, str] = None,
        owner: str = "",
        default_join_keys: Union[str, List[str]] = None,
        join_keys: Union[str, List[str]] = None,
    ):
        """
        Declare a new Entity.

        :param name: Unique name for the new entity.
        :param description: Short description of the new entity.
        :param family: (Optional) Family of this Entity, used to group Tecton Primitives.
        :param tags: (Optional) Tags associated with this Tecton Primitive (key-value pairs of arbitrary metadata).
        :param owner: Owner name (typically the email of the primary maintainer).
        :param default_join_keys: Deprecated. Use ``join_keys``. Names of columns that uniquely identify the entity in FeatureView's SQL statement
            for which features should be aggregated.
        :param join_keys: Names of columns that uniquely identify the entity in FeatureView's SQL statement
            for which features should be aggregated.
        :param owner: Owner name

        :raises TectonValidationError: if the input parameters are invalid.
        """
        from tecton.cli.common import get_fco_source_info

        if default_join_keys is None and join_keys is None:
            raise errors.TectonValidationError("You must specify `join_keys` to create an Entity object.")

        basic_info = prepare_basic_info(name=name, description=description, owner=owner, family=family, tags=tags)

        resolved_join_keys = join_keys if join_keys is not None else default_join_keys
        if isinstance(resolved_join_keys, str):
            resolved_join_keys = [resolved_join_keys]

        args = prepare_args(join_keys=resolved_join_keys, basic_info=basic_info)

        self._source_info = get_fco_source_info()
        self._args = args

    @property
    def name(self) -> str:
        """
        Name of the entity.
        """
        return self._args.info.name

    def with_join_keys(self, join_keys: Union[str, List[str]]) -> "OverriddenEntity":
        """
        Returns a new OverriddenEntity object with updated join keys. The current entity class is not modified.

        :param join_keys: Names of columns that uniquely identify the entity in FeatureView's transformation
            for which features should be aggregated. Existing `join_keys` will be fully ignored.

        :raises TectonValidationError: if the input parameters are invalid.
        """
        if not isinstance(join_keys, list):
            join_keys = [join_keys]

        utils.validate_join_keys(join_keys)
        if len(join_keys) != len(self._args_join_keys()):
            raise errors.ENTITY_INVALID_JOIN_KEYS_OVERRIDE(self.name)

        return OverriddenEntity(self, join_keys)

    def _id(self) -> Id:
        return self._args.entity_id

    def _args_join_keys(self):
        return self._args.join_keys


class OverriddenEntity:
    """
    Represents a pre-registered Tecton Entity object with overriden fields (join_keys).

    `OverriddenEntity` instance is not persisted in the Database.
    """

    def __init__(self, entity: Entity, new_join_keys: List[str]):
        """Instantiates a new OverriddenEntity object."""
        self._entity = entity
        self._overridden_join_keys = new_join_keys

    @property
    def name(self) -> str:
        return self._entity.name

    def _id(self) -> Id:
        return self._entity._id()

    def _args_join_keys(self):
        return self._overridden_join_keys
