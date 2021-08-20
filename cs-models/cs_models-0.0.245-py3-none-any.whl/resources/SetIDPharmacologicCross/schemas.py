from marshmallow import (
    Schema,
    fields,
)


class SetIDPharmacologicCrossResourceSchema(Schema):
    spl_set_id = fields.String(allow_none=True)
    pharma_set_id = fields.String(allow_none=True)


class SetIDPharmacologicCrossQueryParamsSchema(Schema):
    spl_set_id = fields.String(allow_none=True)
    pharma_set_id = fields.String(allow_none=True)


class SetIDPharmacologicCrossPatchSchema(Schema):
    spl_set_id = fields.String(allow_none=True)
    pharma_set_id = fields.String(allow_none=True)
