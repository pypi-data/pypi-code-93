import httpx
import respx
from decouple import config

from . import utils
import xmltodict

from ..schema.response import BaseResponse



class OnlineAfsprakenMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class OnlineAfsprakenError(Exception):
    pass


class OnlineAfsprakenAPI(metaclass=OnlineAfsprakenMeta):

    BASE_URL = config("ONLINE_AFSRPAKEN_API_URL")
    params = {}

    def __init__(self):
        # if is_test:
        #     self._setup_test_api(self)
        self._setup_api()

    def _setup_api(self):
        self.client = httpx.Client(base_url=self.BASE_URL)

    def set_params(self, method, **kwargs):
        self.params = utils.build_param(method, **kwargs)

    def get_params(self):
        return self.params

    def get(self, method, **kwargs):
        filter_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        self.set_params(method, **filter_kwargs)
        response = self.client.get(url="", params=self.params)

        if response.status_code == 200 and config('SAVE_RESPONSE', default=False, cast=bool):
            from tests.utils import save_response
            save_response(method, response.content)

        if response.status_code == 200:

            json_resp = xmltodict.parse(response.content)

            base_response = BaseResponse.parse_obj(json_resp)

            if base_response.response.status.status == "failed":
                raise OnlineAfsprakenError(base_response.response.status.message)

            return json_resp["Response"]

    def get_base_url(self):
        return self.BASE_URL


client = OnlineAfsprakenAPI()
