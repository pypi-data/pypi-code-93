import logging
from typing import Dict

import httpx

from .exceptions import ApiClientException


def compute_function_endpoint(two_dotted_function_name: str):
    uri_chunks = two_dotted_function_name.split(".")
    if len(uri_chunks) != 3:
        raise ApiClientException(
            f"Function ({two_dotted_function_name}) doesn't match standard Jelastic function (Group.Class.Function)"
        )
    grp = uri_chunks[0]
    cls = uri_chunks[1]
    fnc = uri_chunks[2]
    uri = f"{grp}/{cls}/REST/{fnc}".lower()

    return uri


class ApiClient:
    def __init__(self, api_url: str, api_token: str):
        """
        Get all needed data to connect to a Jelastic API
        """
        self.api_url = api_url
        self.api_data = {"session": api_token}
        self.logger = logging.getLogger(self.__class__.__name__)
        # the jelastic api is _synchronous_ => no timeouts
        self.client = httpx.Client(timeout=None)

    def _apicall(self, uri: str, method: str, data: dict = {}) -> Dict:
        """
        Lowest-level API call: that's the method that talks over the network to the Jelastic API
        """
        self.logger.debug(f"_apicall {method.upper()} {uri}, data:{data}")
        data.update(self.api_data)
        r = self.client.request(
            method=method, url=f"{self.api_url.strip('/')}/{uri}", data=data
        )
        if r.status_code != httpx.codes.OK:
            raise ApiClientException(
                f"{method} to {uri} failed with HTTP code {r.status_code}"
            )

        response = r.json()
        if response["result"] != 0:
            raise ApiClientException(
                f"{method} to {uri} returned non-zero result", response
            )
        self.logger.debug(f"response : {response}")
        return response

    def execute(self, function: str, **kwargs) -> Dict:
        """
        Direct API call, converting function paths into URLs; allows:
            api_client.execute('Environment.Control.GetEnvs')
        """
        self.logger.info(f"{function}({kwargs})")
        uri = compute_function_endpoint(function)

        return self._apicall(uri=uri, method="post", data=kwargs)
