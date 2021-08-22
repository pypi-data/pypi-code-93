from typing import Optional

from classiq.authentication import password_manager as pm, auth0


class TokenManager:
    def __init__(self):
        self._access_token = None
        self._refresh_token = None
        self._password_manager: pm.PasswordManager = pm.PasswordManager()

    @property
    def access_token(self) -> str:
        if self._access_token:
            return self._access_token

        if access_token := self._password_manager.access_token:
            self._access_token = access_token
            return access_token

        self._access_token = self._refresh_access_token(
            refresh_token=self._refresh_token
        )
        self._password_manager.access_token = self._access_token
        return self._access_token

    def update_expired_access_token(self) -> None:
        refresh_token = self._refresh_token
        if refresh_token is None:
            refresh_token = self._password_manager.refresh_token

        self._access_token = self._refresh_access_token(refresh_token=refresh_token)
        self._password_manager.access_token = self._access_token

    @classmethod
    def _refresh_access_token(cls, refresh_token: str) -> str:
        data = auth0.Auth0.refresh_access_token(refresh_token)

        return data["access_token"]

    def save_tokens(self, access_token: str, refresh_token: Optional[str]) -> None:
        self._access_token = access_token
        self._password_manager.access_token = access_token
        self._refresh_token = refresh_token
        self._password_manager.refresh_token = refresh_token

    def is_refresh_token_available(self) -> bool:
        if self._refresh_token is not None:
            return True

        self._refresh_token = self._password_manager.refresh_token
        return self._refresh_token is not None
