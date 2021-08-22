import ssl
from typing import Optional, Dict, Union

import httpx
import websockets.client
from classiq_interface.server import authentication

from classiq import config
from classiq.authentication import token_manager


class Client:
    def __init__(self, conf: config.Configuration):
        self._config = conf
        self._token_manager = token_manager.TokenManager()
        self._ssl_context = ssl.create_default_context()

    async def call_api(
        self, http_method: str, url: str, body: Optional[Dict] = None
    ) -> Union[Dict, str]:
        _LONG_TIMEOUT = 100  # TODO: solve more generally
        async with httpx.AsyncClient(
            base_url=self._config.host, timeout=_LONG_TIMEOUT
        ) as async_client:
            headers = self._get_authorization_header()
            response = await async_client.request(
                method=http_method, url=url, json=body, headers=headers
            )

        if response.is_error:
            expired = (
                response.status_code == httpx.codes.UNAUTHORIZED
                and response.json()["detail"] == authentication.EXPIRED_TOKEN_ERROR
            )

            if expired:
                raise ExpiredTokenError("Expired token.")

            raise Exception(
                f"Call to API failed with code {response.status_code}: "
                f"{response.json()['detail']}"
            )

        return response.json()

    def _get_authorization_header(self) -> Dict:
        return {"Authorization": f"Bearer {self._token_manager.access_token}"}

    def _get_authorization_query_string(self) -> str:
        return f"?token={self._token_manager.access_token}"

    def save_tokens(self, access_token: str, refresh_token: Optional[str]) -> None:
        self._token_manager.save_tokens(access_token, refresh_token)

    def is_refresh_token_available(self) -> bool:
        return self._token_manager.is_refresh_token_available()

    def update_expired_access_token(self) -> None:
        self._token_manager.update_expired_access_token()

    def establish_websocket_connection(self, path: str) -> websockets.client.connect:
        _MAX_PAYLOAD_SIZE = 2 ** 23  # = 8MiB ~= 8MB

        return websockets.client.connect(
            uri=f"{self._config.ws_uri}{path}{self._get_authorization_query_string()}",
            ssl=self._ssl_context if self._config.ws_uri.scheme == "wss" else None,
            max_size=_MAX_PAYLOAD_SIZE,
        )


class ExpiredTokenError(Exception):
    pass


DEFAULT_CLIENT = None


def client():
    global DEFAULT_CLIENT
    if DEFAULT_CLIENT is None:
        DEFAULT_CLIENT = Client(conf=config.init())

    return DEFAULT_CLIENT


def configure(conf: config.Configuration) -> None:
    global DEFAULT_CLIENT
    assert DEFAULT_CLIENT is None, "Can not configure client after first usage."

    DEFAULT_CLIENT = Client(conf=conf)
