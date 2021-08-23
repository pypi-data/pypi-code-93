import json
import logging
from typing import Any

import backoff
import httpx
import requests
from requests import Response
from requests.adapters import HTTPAdapter
from requests.exceptions import RetryError, ConnectionError
from urllib3.util.retry import Retry


class PRTGHTTPApi(object):
    """Represents the PRTG HTTP API.

    Attributes:
        probe_config (dict): The probe config as dict.
        server_uri (str): The URI of the PRTG Server.
        auth (frozenset): The authentication part.
        session (requests.Session): A ``requests`` session object.
        retry_strategy (urllib3.util.retry.Retry): Retry strategy for sync HTTP requests.
        adapter (requests.adapters.HTTPAdapter): The ``requests`` HTTP adapter.
        PROTOCOL_VERSION (int): Version of the communication protocol.

    """

    PROTOCOL_VERSION = 1

    def __init__(self, probe_config: dict, backoff_factor: float):
        """Constructor for the PRTGHTTPApi object

        Args:
            probe_config (dict): The probe config as dict.
            backoff_factor (float): The backoff factor for the retry strategy.

        """
        self.probe_config = probe_config
        self.server_uri = f'https://{self.probe_config["prtg_server_ip_dns"]}:{self.probe_config["prtg_server_port"]}'
        self.auth = frozenset(
            [
                ("gid", self.probe_config["probe_gid"]),
                ("key", self.probe_config["probe_access_key_hashed"]),
                ("protocol", self.PROTOCOL_VERSION),
            ]
        )
        self.session = requests.Session()
        self.retry_strategy = Retry(
            total=5,
            backoff_factor=backoff_factor,
            status_forcelist=[400, 429, 500, 502, 503, 504],
            method_whitelist=["POST"],
        )
        self.adapter = HTTPAdapter(max_retries=self.retry_strategy)
        if probe_config["disable_ssl_verification"]:
            logging.info("Disabling verification of PRTG certificate")

    def _send_api_request(self, api_url: str = None, post_data: dict = None, url_params: dict = None) -> Response:
        """Send an API request to the PRTG Core.

        Args:
            api_url (str): The API URL.
            post_data (:obj: `dict', optional): The POST data to include in the request.
            url_params (:obj: 'dict', optional): The URL parameters for the request.

        Returns:
            requests.Response: Response object for the request.

        Raises:
            RetryError: Raised when max connection retries are exceeded.
            ConnectionError: Raised when no connection is possible.

        """
        self.session.mount("https://", self.adapter)
        try:
            result = self.session.post(
                url=api_url,
                data=post_data,
                params=url_params,
                verify=not self.probe_config["disable_ssl_verification"],
            )
            if result.status_code == 401:
                logging.error("Cannot connect to the PRTG server, have you approved your probe?")
            return result
        except RetryError:
            logging.exception("Max connection retries exceeded, backing off!")
            raise
        except ConnectionError:
            logging.exception("Cannot connect to server, please check your config")
            raise

    @backoff.on_exception(
        backoff.expo,
        (httpx.TimeoutException, httpx.NetworkError, httpx.HTTPStatusError),
        max_tries=20,
        logger=logging.getLogger(),
    )
    async def _send_api_request_async(
        self, api_url: str = None, post_data: Any = None, url_params: dict = None
    ) -> Response:
        """Send an async API request to the PRTG Core.

        Args:
            api_url (str, optional): The API URL.
            post_data (:obj: `Any', optional): The POST data to include in the request.
            url_params (:obj: 'dict', optional): The URL parameters for the request.

        Returns:
            httpx._models.Response: ``httpx`` response.

        Raises:
            httpx.HTTPStatusError: Raised for status code in list.
        """
        verify_ssl = True
        if self.probe_config["disable_ssl_verification"]:
            verify_ssl = False
        async with httpx.AsyncClient(verify=verify_ssl) as client:
            request = client.build_request(method="POST", url=api_url, data=post_data, params=url_params)
            response = await client.send(request=request, timeout=10)
            if response.status_code in [400, 429, 500, 502, 503, 504]:
                raise httpx.HTTPStatusError(message="Request failed.", request=request, response=response)
            return response

    def send_announce(self, sensor_definitions: list) -> Response:
        """Send a request to the PRTG Core to announce the pyprobe.

        Args:
            sensor_definitions (:obj: `list` of :obj:`dict`): List of sensor definitions.

        Returns:
            requests.Response: The repsonse object for the announce request.

        """
        announce_url = f"{self.server_uri}/probe/announce"
        announce_params = dict(self.auth)
        announce_params["probe_base_interval"] = self.probe_config["probe_base_interval"]
        announce_params["sensors"] = json.dumps(sensor_definitions)
        announce_params["name"] = self.probe_config["probe_name"]
        logging.info(f"Sending Announce request to PRTG Core at {self.server_uri}")
        logging.debug(f"Payload for Announce request to {announce_url} is: {str(announce_params)}")
        return self._send_api_request(api_url=announce_url, post_data=announce_params)

    async def get_tasks(self) -> Response:
        """Send an async request to the PRTG Core to retrieve tasks.

        Returns:
            httpx._models.Response: ``httpx`` response.
        """
        tasks_url = f"{self.server_uri}/probe/tasks"
        logging.info(f"Sending Task request to PRTG Core at {self.server_uri}")
        logging.debug(f"Payload for Task request to {tasks_url} is: {str(dict(self.auth))}")
        return await self._send_api_request_async(api_url=tasks_url, post_data=dict(self.auth))

    async def send_data(self, sensor_response_data: list) -> Response:
        """Send an async request to the PRTG Core to submit sensor data.

        Args:
            sensor_response_data (:obj:`list` of :obj:`dict`):

        Returns:
            httpx._models.Response: ``httpx`` response.

        """
        data_url = f"{self.server_uri}/probe/data"
        logging.info(f"Sending Data Request to PRTG Core at {self.server_uri}")
        logging.debug(
            f"Payload for Data request to {data_url} with URL parameters {str(dict(self.auth))} is: "
            f"{str(sensor_response_data)}"
        )
        return await self._send_api_request_async(
            api_url=data_url,
            post_data=json.dumps(sensor_response_data),
            url_params=dict(self.auth),
        )
