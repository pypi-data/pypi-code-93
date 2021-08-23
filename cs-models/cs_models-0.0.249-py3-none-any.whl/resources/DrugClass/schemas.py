from marshmallow import (
    Schema,
    fields,
    validate,
)


class DrugClassResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    disease_id = fields.String(validate=not_blank, required=True)
    disease_name = fields.String(validate=not_blank, required=True)
    moa = fields.String(allow_none=True)
    moa_id = fields.String(validate=not_blank, required=True)
    epc = fields.String(allow_none=True)
    epc_id = fields.String(validate=not_blank, required=True)
    struct = fields.String(allow_none=True)
    struct_id = fields.String(allow_none=True)
    pe = fields.String(allow_none=True)
    pe_id = fields.String(allow_none=True)
    updated_at = fields.DateTime()
