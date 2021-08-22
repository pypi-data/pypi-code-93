from django.contrib.auth import get_user_model

from .shortcuts import get_user_by_token
from .utils import get_credentials

UserModel = get_user_model()

from rest_framework_simplejwt.authentication import JWTAuthentication


class JSONWebTokenBackend:
    def __init__(self):
        self.simple_jwt = JWTAuthentication()

    def authenticate(self, request=None, **kwargs):
        if request is None or getattr(request, "_jwt_token_auth", False):
            return None

        token = get_credentials(request, **kwargs)

        if token is not None:
            # validated token by rest_framework_simplejwt
            # if token is not right it will raise exception
            # and return anomyous user
            try:
                self.simple_jwt.get_validated_token(token)
            except:
                return None

            return get_user_by_token(token, request)

        return None

    def get_user(self, user_id):
        try:
            return UserModel._default_manager.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
