from marshmallow import (
    Schema,
    fields,
    validate,
)


class PharmacologicResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    pharma_set_id = fields.String(validate=not_blank, required=True)
    unii_code = fields.String(allow_none=True)
    unii_name = fields.String(allow_none=True)
    nui = fields.String(allow_none=True)
    code_system = fields.String(allow_none=True)
    class_name = fields.String(allow_none=True)
    class_type = fields.String(allow_none=True)
    updated_at = fields.DateTime()


class PharmacologicQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    pharma_set_id = fields.String(validate=not_blank)
    nui = fields.String(validate=not_blank)
    class_name = fields.String(validate=not_blank)


class PharmacologicPatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    pharma_set_id = fields.String(validate=not_blank)
    unii_code = fields.String(allow_none=True)
    unii_name = fields.String(allow_none=True)
    nui = fields.String(allow_none=True)
    code_system = fields.String(allow_none=True)
    class_name = fields.String(allow_none=True)
    class_type = fields.String(allow_none=True)
