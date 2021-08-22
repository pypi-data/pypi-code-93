import http.client
import json
from typing import Dict, Union

from httpx import codes

from classiq_interface.server import authentication


class Auth0:
    _SDK_CLIENT_ID = "f6721qMOVoDAOVkzrv8YaWassRKSFX6Y"

    @staticmethod
    def _make_request(
        url: str,
        payload: str,
        content_type: str,
        allow_error: Union[bool, int] = False,
    ) -> Dict[str, str]:
        connection = http.client.HTTPSConnection(authentication.AUTH0_DOMAIN)

        header = {"content-type": content_type}
        connection.request(method="POST", url=url, body=payload, headers=header)
        res = connection.getresponse()
        code = res.getcode()
        error_code_allowed = allow_error is True or allow_error == code
        data = json.loads(res.read().decode("utf-8"))

        if code == codes.OK or error_code_allowed:
            return data

        raise Exception(
            f"Request to Auth0 failed with error code {code}: {data.get('error')}"
        )

    @staticmethod
    def get_device_data(get_refresh_token: bool = True) -> Dict:
        payload = (
            f"client_id={Auth0._SDK_CLIENT_ID}&"
            f"audience={authentication.API_AUDIENCE}"
        )
        if get_refresh_token:
            payload += "&scope=offline_access"

        return Auth0._make_request(
            url="/oauth/device/code",
            payload=payload,
            content_type="application/x-www-form-urlencoded",
        )

    @staticmethod
    def poll_tokens(device_code: str):
        payload = (
            f"client_id={Auth0._SDK_CLIENT_ID}&"
            f"device_code={device_code}"
            f"&grant_type=urn%3Aietf%3Aparams%3Aoauth%3Agrant-type%3Adevice_code"
        )

        return Auth0._make_request(
            url="/oauth/token",
            payload=payload,
            content_type="application/x-www-form-urlencoded",
            allow_error=codes.FORBIDDEN,
        )

    @staticmethod
    def refresh_access_token(refresh_token: str):
        payload = json.dumps(
            {
                "client_id": Auth0._SDK_CLIENT_ID,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }
        )

        return Auth0._make_request(
            url="/oauth/token", payload=payload, content_type="application/json"
        )
