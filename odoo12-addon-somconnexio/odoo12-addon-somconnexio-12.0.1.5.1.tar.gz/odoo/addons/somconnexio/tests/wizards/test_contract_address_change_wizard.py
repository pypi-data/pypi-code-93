from otrs_somconnexio.otrs_models.coverage.adsl import ADSLCoverage
from otrs_somconnexio.otrs_models.coverage.mm_fibre import MMFibreCoverage
from otrs_somconnexio.otrs_models.coverage.vdf_fibre import VdfFibreCoverage

from odoo.tests.common import TransactionCase


class TestContractAddressChangeWizard(TransactionCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        self.vodafone_fiber_contract_service_info = self.env[
            'vodafone.fiber.service.contract.info'
        ].create({
            'phone_number': '654321123',
            'vodafone_id': '123',
            'vodafone_offer_code': '456',
        })
        self.partner = self.browse_ref('base.partner_demo')
        partner_id = self.partner.id
        self.service_partner = self.env['res.partner'].create({
            'parent_id': partner_id,
            'name': 'Partner service OK',
            'type': 'service'
        })
        vals_contract = {
            'name': 'Test Contract Broadband',
            'partner_id': partner_id,
            'service_partner_id': self.service_partner.id,
            'invoice_partner_id': partner_id,
            'service_technology_id': self.ref(
                "somconnexio.service_technology_fiber"
            ),
            'service_supplier_id': self.ref(
                "somconnexio.service_supplier_vodafone"
            ),
            'vodafone_fiber_service_contract_info_id': (
                self.vodafone_fiber_contract_service_info.id
            ),
            'bank_id': self.partner.bank_ids.id
        }
        self.contract = self.env['contract.contract'].create(vals_contract)

    def test_wizard_address_change_ok(self):
        wizard = self.env['contract.address.change.wizard'].with_context(
            active_id=self.partner.id
        ).create({
            'partner_bank_id': self.partner.bank_ids.id,
            'service_street': 'Carrer Nou 123',
            'service_street2': 'Principal A',
            'service_zip_code': '00123',
            'service_city': 'Barcelona',
            'service_state_id': self.ref('base.state_es_b'),
            'service_country_id': self.ref('base.es'),
            'service_supplier_id': self.ref('somconnexio.service_supplier_jazztel'),
            'previous_product_id': self.ref('somconnexio.Fibra600Mb'),
            'product_id': self.ref('somconnexio.Fibra1Gb'),
            'mm_fiber_coverage': MMFibreCoverage.VALUES[2][0],
            'vdf_fiber_coverage': VdfFibreCoverage.VALUES[3][0],
            'adsl_coverage': ADSLCoverage.VALUES[6][0],
            'notes': 'This is a random note'
        })

        crm_lead_action = wizard.button_change()
        crm_lead_line = self.env["crm.lead.line"].browse(crm_lead_action["res_id"])
        crm_lead = crm_lead_line.lead_id

        self.assertEquals(crm_lead_action.get('xml_id'),
                          "somconnexio.view_form_lead_line_broadband")
        self.assertEquals(crm_lead.name, "Change Address process")
        self.assertEquals(crm_lead.partner_id, self.partner)
        self.assertEquals(
            crm_lead.iban,
            self.partner.bank_ids.sanitized_acc_number
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.service_street,
            'Carrer Nou 123'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.service_street2,
            'Principal A'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.service_zip_code,
            '00123'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.service_city,
            'Barcelona'
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.service_state_id,
            self.browse_ref('base.state_es_b')
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.service_country_id,
            self.browse_ref('base.es')
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.service_supplier_id,
            self.browse_ref('somconnexio.service_supplier_jazztel')
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.previous_service,
            'fiber'
        )
        self.assertEquals(
            crm_lead_line.product_id,
            self.browse_ref('somconnexio.Fibra1Gb')
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.adsl_coverage,
            ADSLCoverage.VALUES[6][0]
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.vdf_fiber_coverage,
            VdfFibreCoverage.VALUES[3][0]
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.mm_fiber_coverage,
            MMFibreCoverage.VALUES[2][0]
        )
        self.assertEquals(
            crm_lead.description,
            'This is a random note'
        )
        self.assertTrue(crm_lead_line.broadband_isp_info.change_address)
        self.assertEquals(
            crm_lead_line.broadband_isp_info.previous_owner_first_name,
            self.partner.firstname
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.previous_owner_name,
            self.partner.lastname
        )
        self.assertEquals(
            crm_lead_line.broadband_isp_info.previous_owner_vat_number,
            self.partner.vat
        )

    def test_wizard_address_default_options(self):
        """
        Without executing the wizzard:
        - Check available (previous) BA suppliers and products with a partner that
        has thee different contracts - adsl, fiber, mobile -
        - Check that Spain is the default country
        """

        # Fiber
        fiber_product_contract_line = {
            "name": "Fiber product contract line",
            "product_id": self.browse_ref('somconnexio.Fibra600Mb').id,
            "date_start": '2021-01-01'
        }
        self.contract.write(
            {'contract_line_ids': [(0, 0, fiber_product_contract_line)]}
        )

        # ADSL
        router_product = self.env['product.product'].search(
            [
                ("default_code", "=", "NCDS224WTV"),
            ]
        )
        router_lot = self.env['stock.production.lot'].create({
            'product_id': router_product.id,
            'name': '123',
            'router_mac_address': '12:BB:CC:DD:EE:90'
        })
        adsl_contract_service_info = self.env[
            'adsl.service.contract.info'
        ].create({
            'phone_number': '654987654',
            'administrative_number': '123',
            'router_product_id': router_product.id,
            'router_lot_id': router_lot.id,
            'ppp_user': 'ringo',
            'ppp_password': 'rango',
            'endpoint_user': 'user',
            'endpoint_password': 'password'
        })
        ADSL_product_contract_line = {
            "name": "ADSL product contract line",
            "product_id": self.browse_ref('somconnexio.ADSL20MB1000MinFix').id,
            "date_start": '2021-01-01'
        }
        vals_adsl_contract = {
            'name': 'Test Contract Broadband',
            'partner_id': self.partner.id,
            'service_partner_id': self.service_partner.id,
            'invoice_partner_id': self.partner.id,
            'service_technology_id': self.ref("somconnexio.service_technology_adsl"),
            'service_supplier_id': self.ref("somconnexio.service_supplier_jazztel"),
            'adsl_service_contract_info_id': (adsl_contract_service_info.id),
            'bank_id': self.partner.bank_ids.id,
            'contract_line_ids': [(0, 0, ADSL_product_contract_line)]
        }
        self.contract = self.env['contract.contract'].create(vals_adsl_contract)

        # Mobile
        mobile_contract_service_info = self.env[
            'mobile.service.contract.info'
        ].create({
            'phone_number': '654987654',
            'icc': '123'
        })
        mobile_product_contract_line = {
            "name": "Mobile product contract line",
            "product_id": self.browse_ref('somconnexio.150Min1GB').id,
            "date_start": '2021-01-01'
        }
        vals_mobile_contract = {
            'name': 'Test Contract Mobile',
            'partner_id': self.partner.id,
            'service_partner_id': self.service_partner.id,
            'invoice_partner_id': self.partner.id,
            'service_technology_id': self.ref("somconnexio.service_technology_mobile"),
            'service_supplier_id': self.ref("somconnexio.service_supplier_masmovil"),
            'mobile_contract_service_info_id': mobile_contract_service_info.id,
            'bank_id': self.partner.bank_ids.id,
            'contract_line_ids': [(0, 0, mobile_product_contract_line)]
        }
        self.contract = self.env['contract.contract'].create(vals_mobile_contract)

        wizard = self.env['contract.address.change.wizard'].with_context(
            active_id=self.partner.id
        ).create({
            'partner_bank_id': self.partner.bank_ids.id,
            'service_street': 'Carrer Nou 123',
            'service_street2': 'Principal A',
            'service_zip_code': '00123',
            'service_city': 'Barcelona',
            'service_state_id': self.ref('base.state_es_b'),
            'service_supplier_id': self.ref('somconnexio.service_supplier_jazztel'),
            'previous_product_id': self.ref('somconnexio.ADSL20MB100MinFixMobile'),
            'product_id': self.ref('somconnexio.Fibra1Gb'),
            'mm_fiber_coverage': MMFibreCoverage.VALUES[2][0],
            'vdf_fiber_coverage': VdfFibreCoverage.VALUES[3][0],
            'adsl_coverage': ADSLCoverage.VALUES[6][0]
        })

        self.assertEquals(wizard.service_country_id.id, self.ref('base.es'))

        self.assertEquals(len(wizard.partner_ba_suppliers), 2)
        self.assertEquals(
            wizard.partner_ba_suppliers,
            self.env["service.supplier"].search([
                ('name', 'in', ['Jazztel', 'Vodafone'])
            ])
        )
        self.assertEquals(len(wizard.partner_ba_products), 2)
        self.assertEquals(
            wizard.partner_ba_products,
            self.env["product.product"].search([
                ('default_code', 'in', ['SE_SC_REC_BA_ADSL_1000', 'SE_SC_REC_BA_F_600'])
            ])
        )

    def test_wizard_address_change_terminated_contract(self):
        self.contract.write({"is_terminated": True})

        wizard = self.env['contract.address.change.wizard'].with_context(
            active_id=self.partner.id
        ).create({
            'partner_bank_id': self.partner.bank_ids.id,
            'service_street': 'Carrer Nou 123',
            'service_street2': 'Principal A',
            'service_zip_code': '00123',
            'service_city': 'Barcelona',
            'service_state_id': self.ref('base.state_es_b'),
            'service_country_id': self.ref('base.es'),
            'service_supplier_id': self.ref('somconnexio.service_supplier_jazztel'),
            'previous_product_id': self.ref('somconnexio.Fibra600Mb'),
            'product_id': self.ref('somconnexio.Fibra1Gb'),
            'mm_fiber_coverage': MMFibreCoverage.VALUES[2][0],
            'vdf_fiber_coverage': VdfFibreCoverage.VALUES[3][0],
            'adsl_coverage': ADSLCoverage.VALUES[6][0],
            'notes': 'This is a random note'
        })

        self.assertEquals(len(wizard.partner_ba_products), 0)
