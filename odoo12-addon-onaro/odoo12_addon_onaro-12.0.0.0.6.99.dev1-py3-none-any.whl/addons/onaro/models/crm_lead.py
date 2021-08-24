from odoo import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    def _get_default_user_id(self):
        return self.env['res.users'].search([
            ('login', '=', "bulegoa@onaro.eus")
        ])

    def _language_selection(self):
        return [
            ('eu_ES', 'EU'), ('es', 'ES')
        ]
    
    # TODO: Move to module telecom invoice address??
    invoice_address = fields.Char(string="Invoice Address")
    portability_number = fields.Char(string="Portability Number")
    user_id = fields.Many2one(default=_get_default_user_id)
