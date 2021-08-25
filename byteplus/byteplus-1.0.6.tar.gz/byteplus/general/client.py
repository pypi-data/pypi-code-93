from datetime import datetime
from datetime import timedelta
import logging
from optparse import Option
from typing import Optional

from byteplus.common.client import CommonClient
from byteplus.common.protocol import *
from byteplus.core import BizException
from byteplus.core import MAX_WRITE_ITEM_COUNT, MAX_IMPORT_ITEM_COUNT
from byteplus.core import Region
from byteplus.core.context import Param
from byteplus.general.url import _GeneralURL
from byteplus.general.protocol import *

log = logging.getLogger(__name__)

_ERR_MSG_TOO_MANY_ITEMS = "Only can receive max to %d items in one request".format(MAX_IMPORT_ITEM_COUNT)


class Client(CommonClient):

    def __init__(self, param: Param):
        super().__init__(param)
        self._general_url: _GeneralURL = _GeneralURL(self._context)

    def do_refresh(self, host: str):
        self._general_url.refresh(host)

    def write_data(self, data_list: list, topic: str, *opts: Option) -> WriteResponse:
        if len(data_list) > MAX_WRITE_ITEM_COUNT:
            log.warning("[ByteplusSDK][WriteData] item count more than '%d'", MAX_WRITE_ITEM_COUNT)
            if len(data_list) > MAX_IMPORT_ITEM_COUNT:
                raise BizException(_ERR_MSG_TOO_MANY_ITEMS)
        url_format: str = self._general_url.write_data_url_format
        url: str = url_format.replace("#", topic)
        response: WriteResponse = WriteResponse()
        self._http_caller.do_json_request(url, data_list, response, *opts)
        log.debug("[ByteplusSDK][WriteData] rsp:\n %s", response)
        return response

    def import_data(self, data_list: Optional[list], topic: str, *opts: Option) -> OperationResponse:
        if data_list is None:
            data_list = []
        if len(data_list) > MAX_IMPORT_ITEM_COUNT:
            raise BizException(_ERR_MSG_TOO_MANY_ITEMS)
        url_format: str = self._general_url.import_data_url_format
        url: str = url_format.replace("#", topic)
        response: OperationResponse = OperationResponse()
        self._http_caller.do_json_request(url, data_list, response, *opts)
        log.debug("[ByteplusSDK][ImportData] rsp:\n%s", response)
        return response

    def done(self, date_list: Optional[list], topic: str, *opts: Option) -> DoneResponse:
        date_map_list: list = []
        if date_list is None or len(date_list) == 0:
            previous_day = datetime.now() - timedelta(days=1)
            self.append_done_date(date_map_list, previous_day)
        else:
            for date in date_list:
                self.append_done_date(date_map_list, date)
        url_format = self._general_url.done_url_format
        url = url_format.replace("#", topic)
        response = DoneResponse()
        self._http_caller.do_json_request(url, date_map_list, response, *opts)
        log.debug("[ByteplusSDK][Done] rsp:\n%s", response)
        return response

    @staticmethod
    def append_done_date(date_map_list: list, date: datetime):
        formatted_date: str = date.strftime("%Y%m%d")
        date_map: dict = {"partition_date": formatted_date}
        date_map_list.append(date_map)

    def predict(self, request: PredictRequest, scene: str, *opts: Option) -> PredictResponse:
        url_format: str = self._general_url.predict_url_format
        url: str = url_format.replace("#", scene)
        response: PredictResponse = PredictResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][Predict] rsp:\n%s", response)
        return response

    def callback(self, request: CallbackRequest, *opts: Option) -> CallbackResponse:
        url: str = self._general_url.callback_url
        response: CallbackResponse = CallbackResponse()
        self._http_caller.do_pb_request(url, request, response, *opts)
        log.debug("[ByteplusSDK][Callback] rsp:\n%s", response)
        return response


class ClientBuilder(object):
    def __init__(self):
        self._param = Param()

    def tenant(self, tenant: str):
        self._param.tenant = tenant
        return self

    def tenant_id(self, tenant_id: str):
        self._param.tenant_id = tenant_id
        return self

    def token(self, token: str):
        self._param.token = token
        return self

    def schema(self, schema: str):
        self._param.schema = schema
        return self

    def hosts(self, hosts: list):
        self._param.hosts = hosts
        return self

    def headers(self, headers: dict):
        self._param.headers = headers
        return self

    def region(self, region: Region):
        self._param.region = region
        return self

    def build(self) -> Client:
        return Client(self._param)
