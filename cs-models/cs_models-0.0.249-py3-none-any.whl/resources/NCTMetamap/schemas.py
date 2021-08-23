from marshmallow import (
    Schema,
    fields,
    validate,
)


class NCTMetamapResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    nct_id = fields.String(validate=not_blank, required=True)
    cui = fields.String(validate=not_blank, required=True)
    preferred_name = fields.String(validate=not_blank, required=True)
    type = fields.String(required=True)
    score = fields.Integer(allow_none=True)
    note = fields.String(allow_none=True)
    final_mapping = fields.Boolean(required=True)
    updated_at = fields.DateTime()
