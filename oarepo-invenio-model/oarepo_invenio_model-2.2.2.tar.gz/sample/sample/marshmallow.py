from marshmallow import fields, validate

from oarepo_invenio_model.marshmallow import InvenioRecordMetadataSchemaV1Mixin


class SampleSchemaV1(InvenioRecordMetadataSchemaV1Mixin):
    title = fields.String(validate=validate.Length(min=5), required=True)
