"""
request handler with its dependencies to intercept http requests
"""
import enum
import os
import os.path
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin

import requests
from requests import Response

from .._version import __version__ as SAAS_CLIENT_VERSION
from ..auth.model.credentials import CredentialsBase
from ..auth.oauth import OAuthService
from ..config.configuration import Configuration

COOKIE_HEADER = 'Cookie'


class ContentType(enum.Enum):
    """
    Supported Content types
    """

    FORM_URL_ENCODED = 'application/x-www-form-urlencoded'
    MULTIPART_FORM_DATA = 'multipart/form-data'
    APPLICATION_JSON = 'application/json'


class _RequestHandler:
    def __init__(self, credentials: CredentialsBase, configuration: Configuration) -> None:
        super().__init__()
        self.__credentials = credentials
        self.__oauth_service = OAuthService(configuration)
        self.__cookie = self.__oauth_service.login(self.__credentials)
        self.__default_headers = self._get_default_headers()
        self.__configuration = configuration

    def handle_request(
        self,
        url: str,
        data: Union[Dict[str, str], List[Tuple[str, str]]] = None,
        method: str = 'GET',
        content_type: ContentType = None,
    ) -> Response:
        """
        handle request is building and sending requests to the server
        :param url: relative endpoint to invoke
        :type url: str
        :param data: data to be sent to the server
        :type data: Union[Dict[str, str], List[Tuple[str, str]]]
        :param method: HTTP method to invoke
        :type method: str
        :param content_type: ContentType of the request
        :type content_type: ContentType
        :return: Server's response
        :rtype: Response
        """
        data = self.to_tuple_list(data)
        prepared_url = urljoin(f'https://{self.__configuration.hs_domain}', url)
        message = self._create_request_message(prepared_url, data, method, content_type)
        res = self._send_request(message)
        if self._is_session_expired(res):
            self.__cookie = self.__oauth_service.login(self.__credentials)
            self.__default_headers = self._get_default_headers()
            res = self._send_request(message)

        return res

    @staticmethod
    def to_tuple_list(
        data: Union[Dict[str, str], List[Tuple[str, str]], None]
    ) -> List[Tuple[str, str]]:
        """
        Synthesize supported data into List of tuples
        :param data: list, dictionary or None default value
        :type data: Union[Dict[str, str], List[Tuple[str, str]], None]
        :return: data converted into list
        :rtype: List[Tuple[str, str]
        """
        data = data or []
        if isinstance(data, dict):
            data = list(data.items())
        return data

    def _send_request(self, message: Dict[str, Any]) -> Response:
        message['headers'].update(self.__default_headers)
        message['allow_redirects'] = False
        message['timeout'] = 120
        response = requests.request(**message)
        response.close()
        return response

    def _is_session_expired(self, res: Response) -> bool:
        redirect_header = res.headers.get('Location', '')
        return res.status_code == 302 and self.__configuration.auth_server in redirect_header

    def _get_default_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': f'hyperscience-saas-client-python/{SAAS_CLIENT_VERSION}',
            COOKIE_HEADER: self.__cookie,
        }

    def _create_request_message(
        self,
        url: str,
        data: List[Tuple[str, str]],
        method: str,
        content_type: Optional[ContentType],
    ) -> Dict[str, str]:
        switcher = {
            'POST': lambda: self._create_post_message(url, data, method, content_type),
            'GET': lambda: self._create_get_message(url, data, method, content_type),
        }
        create_message = switcher.get(method, lambda: {})
        request_message = create_message()
        if len(request_message) == 0:
            raise ValueError(f'{method} is not a supported operation')
        return request_message

    @staticmethod
    def _create_post_message(
        url: str, data: List[Tuple[str, str]], method: str, content_type: Optional[ContentType]
    ) -> dict:
        if content_type is ContentType.FORM_URL_ENCODED:
            post_message = {
                'url': url,
                'method': method,
                'data': data,
                'headers': {'Content-Type': content_type.value},
            }
        elif content_type is ContentType.MULTIPART_FORM_DATA:
            # we close files opened in hooks handled by requests hooks below
            files = [
                (k, open(v, 'rb')) for (k, v) in data if os.path.isfile(v)  # pylint: disable=R
            ]
            filtered_data = [(k, v) for (k, v) in data if not os.path.isfile(v)]
            post_message = {
                'url': url,
                'method': method,
                'files': files,
                'data': filtered_data,
                'headers': {},
                'hooks': {
                    'response': lambda res, *args, **kwargs: _RequestHandler._close_files(files)
                },
            }
        else:
            raise ValueError(f'{content_type} is not supported!')

        return post_message

    @staticmethod
    def _close_files(files: List[Tuple[str, BinaryIO]]) -> None:
        for _, file in files:
            file.close()

    @staticmethod
    def _create_get_message(
        url: str, data: List[Tuple[str, str]], method: str, content_type: Optional[ContentType]
    ) -> dict:
        headers = {'Content-Type': content_type.value} if content_type else {}
        return {'url': url, 'method': method, 'params': data, 'headers': headers}
