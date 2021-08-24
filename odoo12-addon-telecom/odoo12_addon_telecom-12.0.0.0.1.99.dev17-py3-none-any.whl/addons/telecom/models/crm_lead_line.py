from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class CRMLeadLine(models.Model):
    _inherit = 'crm.lead.line'

    broadband_isp_info = fields.Many2one(
       'broadband.isp.info',
       string='Broadband ISP Info'
    )
    mobile_isp_info = fields.Many2one(
       'mobile.isp.info',
       string='Mobile ISP Info'
    )

    is_mobile = fields.Boolean(
       compute='_get_is_mobile',
       store=True
    )
    is_adsl = fields.Boolean(
       compute='_get_is_adsl',
    )
    is_fiber = fields.Boolean(
       compute='_get_is_fiber',
    )

    def action_won(self):
        return
        # Create Partner
        print("Writing the CRMLead with stage 4...")
        partner = self._create_partner()
        # Create SaleOrder
        order = self._create_order(partner)

    def _create_order(self, partner):
        """
        Create a SaleOrder with CRMLead info.
        Create also the SaleOrderLines with the product and the services info.
        """
        # TODO: Check if order already exists
        product_id = self.product_id.id
        order_vals = {
            # TODO: Complete all SaleOrder data from the CRMLead and CRMLeadLine
            "product_id": product_id
        }
        self.env["sale.order"].create({
            # TODO: Complete all SaleOrder data from the CRMLead and CRMLeadLine
            "name": "{} - {}".format(partner.name, self.product_id.showed_name),
            "partner_id": partner.id,
            "opportunity_id": self.lead_id.id,
            "is_telecom": True,
            "order_line": [(0, 0, order_vals)]
        })
        print("Opportunity created...")

    def _create_partner(self):
        """
        Create a partner with CRMLead info if it does not exist.
        """
        if self.lead_id.partner_id:
            return self.lead_id.partner_id
        if not self.lead_id.vat:
            raise ValidationError()

        partner = self.env["res.partner"].search([
            ("vat", "=", self.lead_id.vat)
        ], limit=1)

        if not partner:
            partner = self.env["res.partner"].create({
                # TODO: Complete all Partner data from the CRMLead
                "name": self.lead_id.name,
                "vat": self.lead_id.vat,
                "type": None,
                "email": self.lead_id.email_from,
                "phone": self.lead_id.phone,
                "street": self.lead_id.street,
                "bank_ids": [(0, 0,
                    {
                        "acc_number": self.lead_id.iban
                    })
                ]
            })
            print("Partner created")

        # Assign partner to CRMLead
        self.lead_id.write({"partner_id": partner.id})
        print("Partner assigned to the CRMLead")

        return partner

    @api.depends('product_id')
    def _get_is_mobile(self):
        mobile = self.env.ref('telecom.mobile_service')
        for record in self:
            record.is_mobile = (
                mobile.id == record.product_id.product_tmpl_id.categ_id.id
            )

    @api.depends('product_id')
    def _get_is_adsl(self):
        adsl = self.env.ref('telecom.broadband_adsl_service')
        for record in self:
            record.is_adsl = (
                adsl.id == record.product_id.product_tmpl_id.categ_id.id
            )

    @api.depends('product_id')
    def _get_is_fiber(self):
        fiber = self.env.ref('telecom.broadband_fiber_service')
        for record in self:
            record.is_fiber = (
                fiber.id == record.product_id.product_tmpl_id.categ_id.id
            )
