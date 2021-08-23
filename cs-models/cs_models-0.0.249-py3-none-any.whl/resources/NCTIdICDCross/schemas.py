from marshmallow import (
    Schema,
    fields,
)


class NCTIdICDCrossResourceSchema(Schema):
    nct_id = fields.String(allow_none=False)
    icd_code = fields.String(allow_none=False)


class NCTIdICDCrossQueryParamsSchema(Schema):
    nct_id = fields.String(allow_none=False)
    icd_code = fields.String(allow_none=False)


class NCTIdICDCrossPatchSchema(Schema):
    nct_id = fields.String(allow_none=False)
    icd_code = fields.String(allow_none=False)
