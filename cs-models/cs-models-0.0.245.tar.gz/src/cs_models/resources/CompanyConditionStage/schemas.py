from marshmallow import (
    Schema,
    fields,
    validate,
)


class CompanyConditionStageResourceSchema(Schema):
    not_blank = validate.Length(min=1, error="Field cannot be blank")

    id = fields.Integer(dump_only=True)
    company_condition_stage = fields.String(allow_none=False, validate=not_blank)
    stage = fields.String(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)
