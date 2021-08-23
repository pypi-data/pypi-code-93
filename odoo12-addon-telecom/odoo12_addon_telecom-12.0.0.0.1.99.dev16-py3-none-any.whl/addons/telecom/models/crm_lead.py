# -*- coding: utf-8 -*-

from odoo import models, fields, api

class CRMLead(models.Model):
    """
    El CRMLead se usa como primer elemento en el que guardamos la info de la solicitud.

    En la info de la solicitud puede venir solo los datos de la solicitud y un DNI o los datos de la solicitud + los datos para generar el partner.

    En la validación, antes de generar el partner, revisamos si este existe buscando por VAT.
    """
    _inherit = 'crm.lead'

    def _language_selection(self):
        return [
            ('es', 'ES')
        ]

    is_telecom = fields.Boolean(string="Is Telecom lead?")

    birth_date = fields.Char(string="Birth Date")
    vat = fields.Char(string="VAT")
    iban = fields.Char(string="IBAN")
    language = fields.Selection(
        selection='_language_selection',
        string="Language"
    )
    policy_accepted = fields.Boolean(string="Policy accepted")

    product_id = fields.Many2one(
        "product.product",
        computed='_compute_product',
        string="Product"
    )

    def _compute_product(self):
        for crm in self:
            if crm.lead_line_ids:
                crm.product_id = crm.lead_line_ids[0].product_id
