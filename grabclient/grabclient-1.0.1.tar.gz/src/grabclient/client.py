import base64
import hashlib
import hmac
import json
import os

from collections import namedtuple
from datetime import datetime
from enum import Enum
from http import HTTPStatus
from logging import getLogger
from typing import Tuple, Union, TypeVar, Type

import requests

from grabclient.exceptions import APINotContactable, APIResponseNotJson, APIErrorResponse
from grabclient.helper import snake_to_camel
from grabclient.requests import DeliveryQuoteRequest, DeliveryRequest
from grabclient.responses import DeliveryQuoteResponse, DeliveryResponse
from urllib.parse import urlparse
import re
from grabclient.constant import REDIS_KEY_ACCESS_TOKEN
import redis

__all__ = ['GrabClient', ]

T = TypeVar('T')

_log = getLogger()

class GrabClient:

    def __init__(self,
                 credentials: Tuple[str, str],
                 grab_base_url: str,
                 grab_oauth_url: str,
                 redis_url: str,
                 sandbox_mode=False,
                 redis_password=None):
        self.credentials = credentials
        self.sandbox_mode = sandbox_mode
        # self.base_url = os.getenv("GRAB_SANDBOX_URL") if sandbox_mode else os.getenv("GRAB_URL")
        self.base_url = grab_base_url
        # self.oauth_url = os.getenv("GRAB_OAUTH_URL")
        self.oauth_url = grab_oauth_url
        self.redis_url = redis_url
        self.redis_password = redis_password
        self.redis_connection = None
        self.init_redis_connection()

    def init_redis_connection(self):
        url_parsed = urlparse(self.redis_url)

        redis_port = int(url_parsed.port)
        redis_host = url_parsed.hostname
        redis_db = int(re.sub(r'\W+', '', url_parsed.path))
        self.redis_connection = redis.Redis(host=redis_host, port=redis_port, db=redis_db,
                                            password=self.redis_password)

    @property
    def verify_ssl(self):
        """
        :return:
        """
        return not self.sandbox_mode

    def check_rate(self, req: DeliveryQuoteRequest) -> DeliveryQuoteResponse:
        """POST /deliveries/quotes"""
        return self._http_post_json('deliveries/quotes', req, DeliveryQuoteResponse)

    def book_delivery(self, req: DeliveryRequest) -> DeliveryResponse:
        """Booking API: POST /deliveries"""
        return self._http_post_json('deliveries', req, DeliveryResponse)

    def track_delivery(self):
        """Tracking API: GET /deliveries/{deliveryID}/tracking tyg"""
        pass

    def cancel_delivery(self, delivery_id: str):
        """Cancel API: /deliveries/{deliveryID}"""
        return self._http_delete_json(f'deliveries/{delivery_id}')

    def info_delivery(self, delivery_id: str) -> DeliveryResponse:
        """GET deliveries/{DeliveryID}"""
        return self._http_get_json(f'deliveries/{delivery_id}', DeliveryResponse)

    def _headers(self):
        return {
            'Date': datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        }

    def _http_get_json(self, url_path: str, response_class: Type[T]) -> T:
        """
        :param url_path:
        :param response_class:
        :return:
        """
        headers = self._headers()
        headers['Content-Type'] = ""
        headers['Authorization'] = self.get_access_token()
        try:
            url = f"{self.base_url}{url_path}"
            http_response = requests.get(
                url,
                headers=headers,
                timeout=5
            )
            _log.info(f'{datetime.now().isoformat()}: GRAB {url} {http_response.status_code} {http_response.text}')
            if http_response.status_code is not HTTPStatus.OK:
                raise APIErrorResponse.from_api_json(http_response=http_response)
            return response_class.from_api_json(http_response.json())
        except requests.RequestException as e:
            raise APINotContactable from e
        except ValueError as e:
            raise APIResponseNotJson from e

    def _http_post_json(self, url_path: str, payload: Union[dict, namedtuple], response_class: Type[T]) -> T:
        """

        :param url_path:
        :param payload:
        :param response_class:
        :return:
        """
        headers = self._headers()
        headers['Content-Type'] = 'application/json'
        data = self._serialize_request(payload)
        headers['Authorization'] = self.get_access_token()
        try:
            url = f"{self.base_url}{url_path}"
            http_response = requests.post(
                url,
                headers=headers,
                data=data,
                timeout=5
            )
            _log.info(f'{datetime.now().isoformat()}: GRAB {url} {http_response.status_code} {http_response.text}')
            if http_response.status_code != HTTPStatus.OK:
                raise APIErrorResponse.from_api_json(http_response=http_response)
            return response_class.from_api_json(http_response.json())
        except requests.RequestException as e:
            raise APINotContactable from e
        except ValueError as e:
            raise APIResponseNotJson from e

    def _http_delete_json(self, url_path: str):
        """
        :param url_path:
        :param response_class:
        :return:
        """
        headers = self._headers()
        headers['Content-Type'] = ""
        headers['Authorization'] = self.calculate_hash('', url_path, headers, 'DELETE')
        try:
            url = f"{self.base_url}{url_path}"
            http_response = requests.delete(
                url,
                headers=headers,
                timeout=5
            )
            _log.info(f'{datetime.now().isoformat()}: GRAB {url} {http_response.status_code} {http_response.text}')
            if http_response.status_code is not HTTPStatus.NO_CONTENT:
                raise APIErrorResponse.from_api_json(http_response=http_response)
            return http_response
        except requests.RequestException as e:
            raise APINotContactable from e
        except ValueError as e:
            raise APIResponseNotJson from e

    def _marshal_request(self, payload) -> dict:
        """
        :param payload:
        :return:
        """
        marshalled = {}
        # 1. Skip all non-public attributes (starts with sunder or dunder)
        # 2. special case to ignore 'index' and 'count' attributes for namedtuples
        if isinstance(payload, dict):
            fields = payload.keys()
        else:
            if len(getattr(payload, '__slots__')) > 0:
                fields = getattr(payload, '__slots__')
            else:
                fields = getattr(payload, '_fields')
        for attr_name in fields:
            attr_val = getattr(payload, attr_name)
            cameled_attr_name = snake_to_camel(attr_name)
            if isinstance(attr_val, datetime):
                marshalled[cameled_attr_name] = int(attr_val.timestamp())
            elif isinstance(attr_val, Enum):
                marshalled[cameled_attr_name] = attr_val.value
            elif isinstance(attr_val, (int, str, bool, float)):
                marshalled[cameled_attr_name] = attr_val
            elif isinstance(attr_val, list):
                marshalled[cameled_attr_name] = [self._marshal_request(element) for element in attr_val]
            else:
                marshalled[cameled_attr_name] = self._marshal_request(attr_val)
        return marshalled

    def _serialize_request(self, payload) -> str:
        """
        :param payload:
        :return:
        """
        return json.dumps(self._marshal_request(payload))

    def get_cache_access_token(self):
        access_token = self.redis_connection.get(REDIS_KEY_ACCESS_TOKEN)
        return access_token

    def get_access_token(self):
        if self.get_cache_access_token():
            return self.get_cache_access_token()
        else:
            http_response = requests.post(os.getenv("GRAB_OAUTH_URL"), data={
                "client_id": self.credentials[0],
                "client_secret": self.credentials[1],
                "grant_type": "client_credentials",
                "scope": "grab_express.partner_deliveries"
            })
            json_response = http_response.json()
            self.redis_connection.set(REDIS_KEY_ACCESS_TOKEN,
                                      json_response["token_type"]+" "+json_response["access_token"],
                                      ex=json_response["expires_in"])
            return json_response["token_type"]+" "+json_response["access_token"]

    def calculate_hash(self, data: str, url: str, headers: dict, method: str):
        """
        :param data:
        :param url:
        :param headers:
        :param method:
        :return:
        """
        client_id, secret = self.credentials

        h = hashlib.sha256()

        h.update(data.encode('utf-8'))
        content_digest = base64.b64encode(h.digest()).decode()
        string_to_sign = method + '\n' + headers['Content-Type'] + '\n' + headers[
            'Date'] + '\n' + url + '\n' + content_digest + '\n'

        hmac_signature = hmac.new(secret.encode(), string_to_sign.encode(), hashlib.sha256).digest()
        hmac_signature_encoded: object = base64.b64encode(hmac_signature)

        return f'{client_id}:{hmac_signature_encoded.decode()}'
