import logging
from odoo.addons.component.core import Component
from . import schemas

_logger = logging.getLogger(__name__)


class CRMLeadService(Component):
    _inherit = "base.rest.service"
    _name = "crm.lead.services"
    _usage = "crm-lead"
    _collection = "onaro.services"
    _description = """
        CRMLead requests
    """

    def create(self, **params):
        params = self._prepare_create(params)
        sr = self.env["crm.lead"].sudo().create(params)
        return self._to_dict(sr)

    def _validator_create(self):
        return schemas.S_CRM_LEAD_CREATE

    def _validator_return_create(self):
        return schemas.S_CRM_LEAD_RETURN_CREATE

    @staticmethod
    def _to_dict(crm_lead):
        return {
            "id": crm_lead.id
        }

    def _prepare_address(self, address):
        if address:
            return "{} {} {} {} {} {}".format(
                address["street"],
                address.get("street2"),
                address["zip_code"],
                address["city"],
                address["state"],
                address["country"]
            )
        else:
            return ""

    def _prepare_create(self, params):
        return {
            "is_telecom": True,
            "name": params.get("partner_name"),
            "partner_name": params.get("partner_name"),
            # TODO: dni is called vat in vertical telecom
            "vat": params.get("dni"),
            "birth_date": params.get("birth_date"),
            "phone": params.get("phone"),
            "email_from": params.get("email_from"),
            # TODO: send street to odoo without concatenate
            "street": self._prepare_address(params.get("street")),
            "invoice_address": self._prepare_address(params.get("invoice_address")),
            "portability_number": params.get("portability_number"),
            "iban": params.get("iban"),
            "language": params.get("language"),
            "policy_accepted": params.get("policy_accepted"),
            "tag_ids": [(6, 0, params.get("tag_ids", []))],
            "description": params.get("description"),
        }
