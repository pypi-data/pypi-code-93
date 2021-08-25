import logging
from abc import abstractmethod

from byteplus.common.protocol import *
from byteplus.common.url import CommonURL
from byteplus.core import Option
from byteplus.core.context import Param, Context
from byteplus.core.host_availabler import HostAvailabler
from byteplus.core.http_caller import HttpCaller
from byteplus.core.url_center import URLCenter

log = logging.getLogger(__name__)


class CommonClient(URLCenter):
    def __init__(self, param: Param):
        context: Context = Context(param)
        self._context = context
        self._common_url: CommonURL = CommonURL(context)
        self._http_caller: HttpCaller = HttpCaller(context)
        self._host_availabler = HostAvailabler(self, context)

    def refresh(self, host: str):
        self._common_url.refresh(host)
        self.do_refresh(host)

    @abstractmethod
    def do_refresh(self, host: str):
        pass

    def release(self):
        self._host_availabler.shutdown()

    def get_operation(self, request: GetOperationRequest, *opts: Option) -> OperationResponse:
        url: str = self._common_url.get_operation_url
        response: OperationResponse = OperationResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][GetOperations] rsp:\n%s", response)
        return response

    def list_operations(self, request: ListOperationsRequest, *opts: Option) -> ListOperationsResponse:
        url: str = self._common_url.list_operations_url
        response: ListOperationsResponse = ListOperationsResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][ListOperations] rsp:\n%s", response)
        return response
