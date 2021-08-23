from odoo import models, fields


class BaseServiceContractInfo(models.AbstractModel):
    _name = 'base.service.contract.info'
    _rec_name = 'phone_number'
    phone_number = fields.Char("Phone number", required=True)
