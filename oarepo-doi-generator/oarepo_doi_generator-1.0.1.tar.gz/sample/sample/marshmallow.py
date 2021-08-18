from marshmallow import EXCLUDE, Schema, fields, validate
from marshmallow.fields import List
from marshmallow_utils.fields import SanitizedUnicode
from oarepo_invenio_model.marshmallow import InvenioRecordMetadataSchemaV1Mixin


class IdentifierSchema(Schema):
    """Identifier schema."""

    class Meta:
        """Meta attributes for the schema."""

        unknown = EXCLUDE

    material = fields.Str()
    scheme = fields.Str()
    value = fields.Str()
    status = fields.Str()

class PersonOrOrganizationSchema(Schema):
    """Person or Organization schema."""

    type = SanitizedUnicode()
    name = SanitizedUnicode()
class ContributorSchema(Schema):
    """Contributor schema."""
    person_or_org = fields.Nested(PersonOrOrganizationSchema)

class SampleSchemaV1(InvenioRecordMetadataSchemaV1Mixin):
    title = fields.String(validate=validate.Length(min=2), required=True)
    creators = List(fields.Nested(ContributorSchema))
    publication_year = fields.String()
    document_type = fields.String()
    _primary_community = fields.String()
    identifiers = fields.List(fields.Nested(IdentifierSchema))

