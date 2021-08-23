from marshmallow import (
    Schema,
    fields,
    validate,
)


class ICDResourceSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer(dump_only=True)
    icd_code = fields.String(validate=not_blank, required=True)
    description = fields.String(validate=not_blank, required=True)
    class_kind = fields.String()
    is_leaf = fields.Boolean()
    updated_at = fields.DateTime()


class ICDQueryParamsSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    id = fields.Integer()
    icd_code = fields.String(validate=not_blank)
    description = fields.String(validate=not_blank)


class ICDPatchSchema(Schema):
    not_blank = validate.Length(min=1, error='Field cannot be blank')

    icd_code = fields.String(validate=not_blank)
    description = fields.String(validate=not_blank)
    class_kind = fields.String()
    is_leaf = fields.Boolean()
