from invenio_records.api import Record
from oarepo_validate import MarshmallowValidatedRecordMixin, SchemaKeepingRecordMixin

from .constants import SAMPLE_ALLOWED_SCHEMAS, SAMPLE_PREFERRED_SCHEMA
from .marshmallow import SampleSchemaV1


class SampleRecord(SchemaKeepingRecordMixin,
                   MarshmallowValidatedRecordMixin,
                   Record):
    ALLOWED_SCHEMAS = SAMPLE_ALLOWED_SCHEMAS
    PREFERRED_SCHEMA = SAMPLE_PREFERRED_SCHEMA
    MARSHMALLOW_SCHEMA = SampleSchemaV1

    def validate(self, **kwargs):
        return super().validate(**kwargs)
