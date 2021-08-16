#
# Copyright (c) 2020, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the same license as the current project.
#
import json
import jwt
import logging
import requests
from dateutil.parser import parse as parse_datetime
from gettext import gettext as _
from time import time

from astersay.backends.base import BaseToken, BaseTokenManager
from astersay.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class YandexToken(BaseToken):
    min_length = 128


class YandexTokenManager(BaseTokenManager):
    token_class = YandexToken

    def __init__(self, private_filename, token_filename, key_id,
                 service_account_id, **kwargs):
        self.private_filename = private_filename
        self.token_filename = token_filename
        self.key_id = key_id
        self.service_account_id = service_account_id

        return BaseTokenManager.__init__(self, logger)

    def from_response(cls, jsondata):
        key = jsondata['iamToken']
        expiration = parse_datetime(jsondata['expiresAt']).timestamp()
        return YandexToken(key, expiration)

    def generate_token(self):
        """
        Запрашивает новый IAM-токен у Яндекса.
        """

        # Этот временный токен нужен только на несколько минут, чтобы
        # запросить настоящий токен.
        jwt_token = self.make_json_web_token()

        logger.info(_('Запрашивается новый IAM-токен.'))
        response = requests.post(
            "https://iam.api.cloud.yandex.net/iam/v1/tokens",
            headers={"Content-Type": "application/json"},
            data=json.dumps({'jwt': jwt_token})
        )

        if response.status_code != 200:
            logger.error(_(
                'Ошибка запроса на обновление IAM-токена. '
                'Запрос вернул код, отличный от 200. %s'),
                response.content.decode('utf-8'))
            raise ConnectionError(
                _('Запрос вернул код %s.') % response.status_code)

        token = self.from_response(response.json())
        logger.debug(_('Новый IAM-токен успешно создан: %s'), token)
        return token

    def make_json_web_token(self, lifetime=600):
        """
        Создаёт новый JWT с помощью которого будет периодически запрашиваться
        новый IAM-токен. Время жизни этого токена по умолчанию - 10 минут.
        """
        if not self.service_account_id:
            raise ImproperlyConfigured(
                _('Для Яндекс не установлен service_account_id.'))
        if not self.key_id:
            raise ImproperlyConfigured(
                _('Для Яндекс не установлен key_id.'))

        with open(self.private_filename, 'r') as private:
            private_key = private.read()

        now = int(time())
        payload = {
            'aud': 'https://iam.api.cloud.yandex.net/iam/v1/tokens',
            'iss': self.service_account_id,
            'iat': now,
            'exp': now + lifetime
        }
        token = jwt.encode(
            payload,
            private_key,
            algorithm='PS256',
            headers={
                'kid': self.key_id,
            },
        )
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        logger.info(_('Создан новый JWT-токен: %s...%s'), token[:8], token[-8:])
        return token
