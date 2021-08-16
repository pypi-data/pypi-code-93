import jwt
import json
from rest_framework.authentication import BaseAuthentication
from ..utils import Redishelper, AesCipher
from .. import exceptions as exp
from django.conf import settings
from django.contrib.auth import get_user_model


class JwtAuthentication(BaseAuthentication):
    def authenticate(self, request):
        authorization_header = request.headers.get('Authorization', None)
        api_key_header = request.headers.get('API-KEY', None)
        if authorization_header and api_key_header:  # bad request
            raise exp.AuthenticationFailedExp(
                'only Authorization or API-KEY header is accepted')
        if not authorization_header and not api_key_header:  # user is ananymous
            user = get_user_model()()
            user.permcode = 1
            return (user, None)
        if authorization_header and not api_key_header:  # jwt token
            try:
                prefix, access_token = authorization_header.split(' ')
                if prefix != settings.JWT_PREFIX:
                    raise exp.AuthenticationFailedExp('Invalid Token prefix')
                if Redishelper.is_exists(access_token):
                    payload = jwt.decode(
                        access_token, settings.SECRET_KEY, algorithms=['HS256'])
                else:
                    raise exp.AuthenticationFailedExp('access_token revoked')
            except jwt.ExpiredSignatureError:
                raise exp.AuthenticationFailedExp('access_token expired')

            cipher = AesCipher()
            plainuser = json.loads(cipher.decrypt(payload['user']))

            user = get_user_model()()
            user.id = plainuser['id']
            user.is_active = plainuser['is_active']
            user.permcode = plainuser['permcode']
        if not authorization_header and api_key_header:  # api key
            payload = Redishelper.is_exists_hash(api_key_header)
            if payload == {}:
                raise exp.AuthenticationFailedExp('Invalid api key')
            else:
                user = get_user_model()()
                user.id = payload.get('id')
                user.is_active = bool(payload.get('is_active'))
                user.permcode = int(payload.get('permcode'))

        if user is None:
            raise exp.DoesNotExistsExp('User not found')

        if not user.is_active:
            raise exp.UserInactiveExp('user is inactive')
        return (user, None)
