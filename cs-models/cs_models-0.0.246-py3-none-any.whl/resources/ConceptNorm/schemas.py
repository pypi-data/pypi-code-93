from marshmallow import (
    Schema,
    fields,
    validate,
)


class ConceptNormResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    cui = fields.String(validate=not_blank, required=True)
    norm_cui = fields.String(validate=not_blank, required=True)
    norm_cui_name = fields.String(validate=not_blank, required=True)
    updated_at = fields.DateTime()
