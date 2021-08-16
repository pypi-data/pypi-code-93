#
#  Copyright (c) 2021. Egor Demushin.
#  All rights reserved.
#  This file is distributed under the same license as the current project.
#
# import json
import jwt
import logging
from base64 import b64decode
from gettext import gettext as _
from time import time

from astersay.backends.base import BaseToken, BaseTokenManager
from astersay.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class TinkoffToken(BaseToken):
    min_length = 32


class TinkoffTokenManager(BaseTokenManager):
    token_class = TinkoffToken

    def __init__(self, private_filename, token_filename, api_key,
                 service_account_id, sub, lifetime=600, **kwargs):
        self.private_filename = private_filename
        self.token_filename = token_filename
        self.api_key = api_key
        self.service_account_id = service_account_id
        self.sub = sub
        self.lifetime = lifetime

        return BaseTokenManager.__init__(self, logger)

    def generate_token(self):
        """
        Запрашивает новый токен у Тинькова.
        """
        if not self.service_account_id:
            raise ImproperlyConfigured(
                _('Для Тинькова не установлен service_account_id.'))
        if not self.api_key:
            raise ImproperlyConfigured(
                _('Для Тинькова не установлен api_key.'))

        with open(self.private_filename, 'r') as private:
            private_key = private.read()
        if not private_key:
            raise ImproperlyConfigured(
                _('Для Тинькова не установлен private_key.'))

        now = int(time())
        payload = {
            "aud": 'tinkoff.cloud.tts tinkoff.cloud.stt',
            "iss": self.service_account_id,
            "iat": now,
            'exp': now + self.lifetime
        }
        token = jwt.encode(
            payload,
            b64decode(private_key),
            algorithm='HS256',
            headers={
                'alg': 'HS256',
                'typ': 'JWT',
                'kid': self.api_key,
            }
        )
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        token = TinkoffToken(token, payload['exp'])
        self.token = token

        logger.debug(_('Новый токен успешно создан: %s'), token)
        return token
