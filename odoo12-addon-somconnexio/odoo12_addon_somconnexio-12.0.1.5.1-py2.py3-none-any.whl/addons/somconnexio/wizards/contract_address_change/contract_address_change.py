from otrs_somconnexio.otrs_models.coverage.adsl import ADSLCoverage
from otrs_somconnexio.otrs_models.coverage.mm_fibre import MMFibreCoverage
from otrs_somconnexio.otrs_models.coverage.vdf_fibre import VdfFibreCoverage

from odoo import api, fields, models


class ContractAddressChangeWizard(models.TransientModel):
    _name = 'contract.address.change.wizard'
    partner_id = fields.Many2one('res.partner')

    partner_bank_id = fields.Many2one(
        'res.partner.bank',
        string='Partner Bank',
        required=True
    )
    service_street = fields.Char(
        string='Service Street',
        required=True
    )
    service_street2 = fields.Char(string='Service Street 2')
    service_zip_code = fields.Char(
        string='Service ZIP',
        required=True
    )
    service_city = fields.Char(
        string='Service City',
        required=True
    )
    service_state_id = fields.Many2one(
        'res.country.state',
        string='Service State',
        required=True
    )
    service_country_id = fields.Many2one(
        'res.country',
        string='Service Country',
        required=True
    )
    partner_ba_contracts = fields.Many2many(
        'contract.contract',
        compute='_compute_partner_ba_contracts',
    )
    partner_ba_products = fields.Many2many(
        'product.product',
        compute='_compute_partner_ba_products',
    )
    previous_product_id = fields.Many2one(
        'product.product',
        'Previous Product',
        required=True,
    )
    partner_ba_suppliers = fields.Many2many(
        'service.supplier',
        compute='_compute_partner_ba_suppliers',
    )
    service_supplier_id = fields.Many2one(
        'service.supplier',
        'Service Supplier',
        required=True,
    )
    product_id = fields.Many2one(
        'product.product',
        string='Requested product',
        required=True,
    )
    new_product_category_id = fields.Many2one(
        'product.category',
        related='product_id.product_tmpl_id.categ_id',
    )
    mm_fiber_coverage = fields.Selection(
        MMFibreCoverage.VALUES,
        'MM Fiber Coverage',
    )
    vdf_fiber_coverage = fields.Selection(
        VdfFibreCoverage.VALUES,
        'Vdf Fiber Coverage',
    )
    adsl_coverage = fields.Selection(
        ADSLCoverage.VALUES,
        'ADSL Coverage',
    )
    notes = fields.Text(
        string='Notes',
    )

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)
        defaults['partner_id'] = self.env.context['active_id']
        defaults['service_country_id'] = self.env["res.country"].search([("code", "=", "ES")]).id  # noqa
        return defaults

    @api.depends("partner_id")
    def _compute_partner_ba_contracts(self):
        partner_id = self.env.context['active_id']
        mobile_service_technology_id = self.env.ref(
            "somconnexio.service_technology_mobile")

        ba_contracts = self.env["contract.contract"].search([
            ("partner_id", "=", partner_id),
            ("service_technology_id", "!=", mobile_service_technology_id.id),
            ("is_terminated", "=", False),
        ])
        self.partner_ba_contracts = [(6, 0, [contract.id for contract in ba_contracts])]

    @api.depends("partner_ba_contracts")
    def _compute_partner_ba_products(self):
        ba_products = [contract.current_tariff_product.id for contract in self.partner_ba_contracts]  # noqa
        self.partner_ba_products = [(6, 0, ba_products)]

    @api.depends("partner_ba_contracts")
    def _compute_partner_ba_suppliers(self):
        ba_suppliers = [contract.service_supplier_id.id for contract in self.partner_ba_contracts]  # noqa
        self.partner_ba_suppliers = [(6, 0, ba_suppliers)]

    def _previous_service(self):
        service_technology = {
            self.env.ref('somconnexio.broadband_adsl_service').id: "adsl",
            self.env.ref('somconnexio.broadband_fiber_service').id: "fiber"
        }
        return service_technology.get(
            self.previous_product_id.product_tmpl_id.categ_id.id
        )

    @api.multi
    def button_change(self):
        self.ensure_one()
        broadband_isp_info = self.env["broadband.isp.info"].create(
            {
                "service_street": self.service_street,
                "service_street2": self.service_street2,
                "service_zip_code": self.service_zip_code,
                "service_city": self.service_city,
                "service_state_id": self.service_state_id.id,
                "service_country_id": self.service_country_id.id,
                "type": "new",
                "previous_service": self._previous_service(),
                "service_supplier_id": self.service_supplier_id.id,
                "change_address": True,
                "mm_fiber_coverage": self.mm_fiber_coverage or "NoRevisat",
                "vdf_fiber_coverage": self.vdf_fiber_coverage or "NoRevisat",
                "adsl_coverage": self.adsl_coverage or "NoServei",
                "previous_owner_vat_number": self.partner_id.vat,
                "previous_owner_first_name": self.partner_id.firstname,
                "previous_owner_name": self.partner_id.lastname,
            }
        )
        line_params = {
            "name": self.product_id.name,
            "product_id": self.product_id.id,
            "product_tmpl_id": self.product_id.product_tmpl_id.id,
            "category_id": self.product_id.product_tmpl_id.categ_id.id,
            "broadband_isp_info": broadband_isp_info.id,
        }
        crm_lead_line = self.env["crm.lead.line"].create(line_params)

        self.env['crm.lead'].create({
            "name": "Change Address process",
            "description": self.notes,
            "partner_id": self.partner_id.id,
            "iban": self.partner_bank_id.sanitized_acc_number,
            "lead_line_ids": [(6, 0, [crm_lead_line.id])]
        })

        action = self.env.ref("somconnexio.action_crm_lead_line_broadband").read()[0]

        action.update({
            "target": "current",
            "xml_id": "somconnexio.view_form_lead_line_broadband",
            "views": [[
                self.env.ref("somconnexio.view_form_lead_line_broadband").id, "form"
            ]],
            "res_id": crm_lead_line.id,
        })

        return action
