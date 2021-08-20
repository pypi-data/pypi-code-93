from marshmallow import (
    Schema,
    fields,
    validate,
)


class RegulatoryApprovalOutboxResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_id = fields.Integer(allow_none=True)
    condition_id = fields.Integer(allow_none=True)
    geography = fields.String(allow_none=True)
    approval_text = fields.String(validate=not_blank)
    stage = fields.Integer(allow_none=True)
    updated_at = fields.DateTime()
