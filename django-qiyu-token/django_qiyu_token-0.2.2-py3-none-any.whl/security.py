import logging
from typing import Optional, List

import jwt
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpRequest
from ninja.security import HttpBearer

from .models import BearerTokenModel, JwtAppModel

__all__ = ["BearerTokenAuth", "JwtTokenAuth"]


class BearerTokenAuth(HttpBearer):
    def authenticate(self, request: HttpRequest, token: str) -> Optional[User]:
        try:
            m = BearerTokenModel.check_token(token)
            return m.user
        except ObjectDoesNotExist:
            return None


class JwtTokenAuth(HttpBearer):
    def __init__(self, jwt_name: str, audience: List[str]):
        super().__init__()
        self._jwt_name = jwt_name
        self._jwt_app: Optional[JwtAppModel] = None
        self._audience = audience

    def authenticate(self, request: HttpRequest, token: str) -> Optional[str]:
        try:
            if self._jwt_app is None:
                # cache the result
                self._jwt_app = JwtAppModel.objects.get(app_name=self._jwt_name)

            payload = jwt.decode(
                token,
                self._jwt_app.app_key,
                algorithms=self._jwt_app.app_type,
                audience=self._audience,
            )
            return payload["sub"]
        except Exception as e:
            logging.info(f"jwt: {token=} auth failed: {e=}")
            return None
