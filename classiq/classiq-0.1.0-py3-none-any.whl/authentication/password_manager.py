from typing import Optional

import keyring
from keyring.backends import fail


class PasswordManager:
    _SERVICE_NAME = "cadmiumTokenService"
    _ACCESS_TOKEN_KEY = "cadmiumTokenAccount"
    _REFRESH_TOKEN_KEY = "cadmiumRefreshTokenAccount"

    def __init__(self):
        self._pm_available = is_password_manager_available()

    @property
    def access_token(self) -> Optional[str]:
        return self._get(key=self._ACCESS_TOKEN_KEY)

    @access_token.setter
    def access_token(self, access_token: str) -> None:
        self._set(key=self._ACCESS_TOKEN_KEY, value=access_token)

    @property
    def refresh_token(self) -> Optional[str]:
        return self._get(key=self._REFRESH_TOKEN_KEY)

    @refresh_token.setter
    def refresh_token(self, refresh_token: str) -> None:
        self._set(key=self._REFRESH_TOKEN_KEY, value=refresh_token)

    def _get(self, key: str) -> Optional[str]:
        return (
            keyring.get_password(service_name=self._SERVICE_NAME, username=key)
            if self._pm_available
            else None
        )

    def _set(self, key: str, value: str) -> None:
        if not self._pm_available:
            return

        keyring.set_password(
            service_name=self._SERVICE_NAME,
            username=key,
            password=value,
        )


PASSWORD_MANAGER_AVAILABLE = None


def is_password_manager_available() -> bool:
    global PASSWORD_MANAGER_AVAILABLE
    if PASSWORD_MANAGER_AVAILABLE is None:
        PASSWORD_MANAGER_AVAILABLE = not isinstance(keyring.get_keyring(), fail.Keyring)

    return PASSWORD_MANAGER_AVAILABLE
