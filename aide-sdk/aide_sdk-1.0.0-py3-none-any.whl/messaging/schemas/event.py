from marshmallow import Schema, fields
from marshmallow_polyfield import PolyField
from aide_sdk.messaging.schemas.execution import ExecutionSchema
from aide_sdk.messaging.schemas.origin import choose_origin_class_deserialisation, \
    choose_origin_class_serialisation
from aide_sdk.messaging.schemas.resource import ResourceSchema


class EventSchema(Schema):
    correlation_id = fields.Str()
    origin = PolyField(deserialization_schema_selector=choose_origin_class_deserialisation,
                       serialization_schema_selector=choose_origin_class_serialisation)
    resources = fields.List(fields.Nested(ResourceSchema))
    executions = fields.List(fields.Nested(ExecutionSchema))
