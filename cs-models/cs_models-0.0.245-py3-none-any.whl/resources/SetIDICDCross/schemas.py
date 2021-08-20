from marshmallow import (
    Schema,
    fields,
)


class SetIDICDCrossResourceSchema(Schema):
    set_id = fields.String(allow_none=False)
    icd_code = fields.String(allow_none=False)


class SetIDICDCrossQueryParamsSchema(Schema):
    set_id = fields.String(allow_none=False)
    icd_code = fields.String(allow_none=False)


class SetIDICDCrossPatchSchema(Schema):
    set_id = fields.String(allow_none=False)
    icd_code = fields.String(allow_none=False)
