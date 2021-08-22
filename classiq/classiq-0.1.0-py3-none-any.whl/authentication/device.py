import asyncio
import time
import webbrowser
from typing import Tuple, Optional

from classiq.authentication import auth0


class DeviceRegistrar:
    _TIMEOUT_ERROR = (
        "Device registration timed out. Please re-initiate the flow and "
        "authorize the device within the timeout."
    )
    _TIMEOUT_SEC = 15 * 60

    @staticmethod
    async def register(get_refresh_token: bool = True) -> Tuple[str, str]:
        data = auth0.Auth0.get_device_data(get_refresh_token=get_refresh_token)

        print(f"Your user code: {data['user_code']}")
        webbrowser.open(data["verification_uri_complete"])
        timeout = min(data["expires_in"], DeviceRegistrar._TIMEOUT_SEC)
        return await DeviceRegistrar._poll_tokens(
            device_code=data["device_code"],
            interval=data["interval"],
            timeout=timeout,
            get_refresh_token=get_refresh_token,
        )

    @staticmethod
    async def _poll_tokens(
        device_code: str, interval: int, timeout: int, get_refresh_token: bool = True
    ) -> Tuple[str, Optional[str]]:
        data = dict()
        polling_start = time.time()

        while not (timed_out := time.time() - polling_start > timeout):
            await asyncio.sleep(interval)
            data = auth0.Auth0.poll_tokens(device_code=device_code)

            error_code = data.get("error")
            if error_code is None:
                break

            if error_code == "authorization_pending":
                continue
            if error_code == "slow_down":
                interval *= 2
                continue
            if error_code == "expired_token":
                raise Exception(DeviceRegistrar._TIMEOUT_ERROR)
            if error_code == "access_denied":
                raise Exception("Access denied.")

            raise Exception(
                f"Device registration failed with an unknown error: {error_code}."
            )

        if timed_out:
            raise Exception(DeviceRegistrar._TIMEOUT_ERROR)

        access_token = data.get("access_token")
        # If refresh token was not requested, this would be None
        refresh_token = data.get("refresh_token")

        if access_token is None or (
            get_refresh_token is True and refresh_token is None
        ):
            raise Exception("Token generation failed for unknown reason.")

        return access_token, refresh_token
