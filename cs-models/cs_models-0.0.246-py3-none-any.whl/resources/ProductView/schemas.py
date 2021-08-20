from marshmallow import (
    Schema,
    fields,
    validate,
)


class ProductViewResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    intervention_name = fields.String(validate=not_blank, required=True)
    intervention_type = fields.String(allow_none=True)
    synonyms = fields.String()
    condition_id = fields.Integer(allow_none=True)
    disease_name = fields.String(allow_none=True)
    approved_condition = fields.Boolean()
    pharm_actions = fields.String()
    company_sec_id = fields.Integer(allow_none=True)
    company_ous_id = fields.Integer(allow_none=True)
    isonmarket = fields.Boolean(required=True)
    updated_at = fields.DateTime()
