import logging
try:
    import pyquerystring
except (ImportError, IOError) as err:
    _logger = logging.getLogger(__name__)
    _logger.debug(err)

from odoo import http
from odoo.http import Root
from odoo.http import request
from odoo.addons.base_rest.http import HttpRestRequest
from odoo.addons.somconnexio.services import contract_contract_service
from odoo.addons.base_rest.controllers.main import RestController
import json
_logger = logging.getLogger(__name__)
emc_process_method = RestController._process_method


def _process_method(self, service_name, method_name, *args, **kwargs):
    _logger.debug("args: {}, kwargs: {}".format(args, kwargs))
    return emc_process_method(
        self, service_name, method_name, *args, **kwargs
    )


RestController._process_method = _process_method


class UserPublicController(http.Controller):

    @http.route(['/public-api/contract'], auth='public',
                methods=['POST'], csrf=False)
    def create_contract(self, **kwargs):
        service = contract_contract_service.ContractService(request.env)
        data = request.params
        response = service.create(**data)
        return request.make_json_response(response)

    @http.route(['/public-api/contract-count'], auth='public',
                methods=['GET'], csrf=False)
    def count_contract(self):
        service = contract_contract_service.ContractService(request.env)
        response = service.count()
        return request.make_json_response(response)


ori_get_request = Root.get_request


def get_request(self, httprequest):
    if httprequest.path.startswith('/public-api/contract'):
        return HttpRestRequest(httprequest)
    return ori_get_request(self, httprequest)


Root.get_request = get_request


# Workaround to fix Open Cell bug in JSON Request with 'body=' prefix
def patched_httprestrequest_init(self, httprequest):
    super(HttpRestRequest, self).__init__(httprequest)
    if self.httprequest.mimetype == "application/json":
        _logger.info("Enter patched constructor")
        data = self.httprequest.get_data().decode(self.httprequest.charset)
        if data[0:5] == "body=":
            data = data.replace("body=", "")
        self.params = json.loads(data)
    else:
        # We reparse the query_string in order to handle data structure
        # more information on https://github.com/aventurella/pyquerystring
        self.params = pyquerystring.parse(
            self.httprequest.query_string.decode("utf-8")
        )
    self._determine_context_lang()


HttpRestRequest.__init__ = patched_httprestrequest_init
