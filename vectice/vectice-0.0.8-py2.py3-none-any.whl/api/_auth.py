import json
import logging
from base64 import b64decode
from datetime import datetime
from typing import Optional

from ._http import Connection
from ._utils import read_env


class Auth(Connection):  # nosec B107
    def __init__(
        self,
        api_endpoint: str = None,
        api_token: str = None,
        _token: Optional[str] = None,
        auto_connect=True,
    ):
        self._logger = logging.getLogger("vectice.auth")
        endpoint, self._API_TOKEN = read_env("VECTICE_API_ENDPOINT", "VECTICE_API_TOKEN")
        if api_endpoint is not None:
            endpoint = api_endpoint
        if api_token is not None:
            self._API_TOKEN = api_token
        if not self._API_TOKEN:
            raise ValueError("VECTICE_API_TOKEN is not provided.")
        super().__init__(api_endpoint=endpoint)
        self._jwt = None
        self._jwt_expiration = None
        if _token:
            self._token = _token
        elif auto_connect:
            self._refresh_token()

    @property
    def _token(self) -> Optional[str]:
        if self._jwt_expiration is None:
            return None
        # Refresh token 1 min before expiration
        if datetime.now().timestamp() >= self._jwt_expiration - 60:
            self._refresh_token()
        return self._jwt

    @_token.setter
    def _token(self, jwt: str) -> None:
        self._jwt = jwt
        self._jwt_expiration = self._get_jwt_expiration(jwt)
        self._request_headers = {"Authorization": "Bearer " + jwt}

    def _refresh_token(self) -> None:
        self._logger.info("Vectice: Refreshing token... ")
        response = self._post("/metadata/authenticate", {"apiKey": self._API_TOKEN})
        self._token = response["token"]
        self._logger.info("Success!")

    @staticmethod
    def _get_jwt_expiration(jwt: str) -> int:
        jwt_payload = jwt.split(".")[1]
        jwt_payload_with_padding = f"{jwt_payload}{'=' * (4 - len(jwt_payload) % 4)}"
        return int(json.loads(b64decode(jwt_payload_with_padding))["exp"])

    def token(self) -> Optional[str]:
        return self._token

    def connect(self) -> None:
        self._refresh_token()
