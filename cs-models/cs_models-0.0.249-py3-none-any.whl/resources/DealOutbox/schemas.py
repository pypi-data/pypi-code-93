from marshmallow import (
    Schema,
    fields,
    validate,
)


class DealOutboxResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    announcement_date = fields.DateTime(required=True)
    deal_value = fields.Decimal()
    currency = fields.String(allow_none=True)
    company_sec_id = fields.Integer(allow_none=True)
    company_ous_id = fields.Integer(allow_none=True)
    investors = fields.String(allow_none=True)
    updated_at = fields.DateTime()

