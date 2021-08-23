import json

from .common_service import BaseOnaroRestCaseAdmin


class HelpdeskTicketServiceRestCase(BaseOnaroRestCaseAdmin):

    def test_route_right_create(self):
        url = "/api/helpdesk-ticket"
        data = {
            "name": "Aida Sanahuja",
            "description": "Hello onaro",
        }

        response = self.http_post(url, data=data)

        self.assertEquals(response.status_code, 200)

        content = json.loads(response.content.decode("utf-8"))
        self.assertIn("id", content)

        helpdesk_ticket = self.env["helpdesk.ticket"].browse(content["id"])
        self.assertEquals(helpdesk_ticket.name, data["name"])
        self.assertEquals(helpdesk_ticket.description, '<p>Hello onaro</p>')
