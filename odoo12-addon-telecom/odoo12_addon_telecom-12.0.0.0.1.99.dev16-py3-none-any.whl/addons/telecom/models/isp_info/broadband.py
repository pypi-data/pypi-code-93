from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BroadbandISPInfo(models.Model):
    _inherit = 'base.isp.info'

    _name = 'broadband.isp.info'
    _description = "Broadband ISP Info"

    service_full_street = fields.Char(
        compute='_get_service_full_street',
        store=True
    )
    service_street = fields.Char(string='Service Street')
    service_street2 = fields.Char(string='Service Street 2')
    service_zip_code = fields.Char(string='Service ZIP')
    service_city = fields.Char(string='Service City')
    service_state_id = fields.Many2one(
        'res.country.state',
        string='Service State')
    service_country_id = fields.Many2one(
        'res.country',
        string='Service Country')

    previous_service = fields.Selection(
        selection=[
            ('fiber', 'Fiber'),
            ('adsl', 'ADSL')
        ],
        string='Previous Service')

    keep_phone_number = fields.Boolean(string='Keep Phone Number')

    service_supplier_id = fields.Many2one(
        'service.supplier',
        string='Service Supplier')

    @api.depends('service_street', 'service_street2')
    def _get_service_full_street(self):
        for record in self:
            if record.service_street2:
                record.service_full_street = "{} {}".format(
                    record.service_street,
                    record.service_street2)
            else:
                record.service_full_street = record.service_street

    @api.one
    @api.constrains('type', 'previous_service', 'previous_provider')
    def _check_broadband_portability_info(self):
        if self.type == 'new':
            return True
        if not self.previous_service:
            raise ValidationError(
                _('Previous services is required in a portability')
            )
        if not self.previous_provider.broadband:
            raise ValidationError(
                _('This previous provider does not offer broadband services')
            )
