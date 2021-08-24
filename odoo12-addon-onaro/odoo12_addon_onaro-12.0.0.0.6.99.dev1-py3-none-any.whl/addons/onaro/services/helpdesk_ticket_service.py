import logging

from odoo import _
from odoo.addons.component.core import Component

from . import schemas

_logger = logging.getLogger(__name__)


class HelpdeskTicketService(Component):
    _inherit = "base.rest.service"
    _name = "helpdesk.ticket.service"
    _usage = "helpdesk-ticket"
    _collection = "onaro.services"
    _description = """
        Create helpdesk tickets
    """

    def create(self, **params):
        params = self._prepare_create(params)
        # tracking_disable=True in context is needed
        # to avoid to send a mail in CRMLead creation
        sr = self.env["helpdesk.ticket"].with_context(
            tracking_disable=True).sudo().create(params)
        return self._to_dict(sr)

    @staticmethod
    def _to_dict(helpdesk_ticket):
        return {
            "id": helpdesk_ticket.id,
        }

    def _validator_create(self):
        return schemas.S_HELPDESK_TICKET_CREATE

    def _validator_return_create(self):
        return schemas.S_HELPDESK_TICKET_RETURN_CREATE

    def _prepare_create(self, params):
        return {
            "name": params.get("name"),
            "description": params.get("description"),
            "channel_id": self.env.ref("helpdesk_mgmt.helpdesk_ticket_channel_web").id,
        }
