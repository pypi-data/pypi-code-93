import uuid
import logging
from ariadne import ScalarType

logger = logging.getLogger(__name__)


uuid_scalar = ScalarType("UUID")


@uuid_scalar.serializer
def serialize_uuid(value):
    if isinstance(value, uuid.UUID):
        return value.hex
    return value


@uuid_scalar.value_parser
def parse_uuid_value(value):
    if isinstance(value, uuid.UUID):
        return value
    result = uuid.UUID(value)
    logger.debug("GQL: parse_uuid_value: %s, %s", value, result)
    return result
