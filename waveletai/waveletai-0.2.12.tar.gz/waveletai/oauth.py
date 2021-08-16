#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2021/3/11 16:34
@Author  : WaveletAI-Product-Team Janus
@license : (C) Copyright 2019-2022, Visionet(Tianjin)Information Technology Co.,Ltd.
@Site    : plus.xiaobodata.com
@File    : oauth.py
@Desc    : 
"""

import threading
import time

import jwt
from bravado.requests_client import Authenticator
from oauthlib.oauth2 import TokenExpiredError, OAuth2Error
from requests.auth import AuthBase
from requests_oauthlib import OAuth2Session

from waveletai.utils import with_api_exceptions_handler

_decoding_options = {
    "verify_signature": False,
    "verify_exp": False,
    "verify_nbf": False,
    "verify_iat": False,
    "verify_aud": False,
    "verify_iss": False
}


class WaveletAIAuth(AuthBase):
    __LOCK = threading.RLock()

    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = session_factory()
        self.token_expires_at = 0

    def __call__(self, r):
        try:
            return self._add_token(r)
        except TokenExpiredError:
            self._refresh_token()
            return self._add_token(r)

    def _add_token(self, r):
        # pylint: disable=protected-access
        r.url, r.headers, r.body = self.session._client.add_token(r.url,
                                                                  http_method=r.method,
                                                                  body=r.body,
                                                                  headers=r.headers)
        return r

    @with_api_exceptions_handler
    def refresh_token_if_needed(self):
        if self.token_expires_at - time.time() < 30:
            self._refresh_token()

    def _refresh_token(self):
        with self.__LOCK:
            try:
                self._refresh_session_token()
            except OAuth2Error:
                # for some reason oauth session is no longer valid. Retry by creating new fresh session
                # we can safely ignore this error, as it will be thrown again if it's persistent
                self.session = self.session_factory()
                self._refresh_session_token()

    def _refresh_session_token(self):
        self.session.refresh_token(self.session.auto_refresh_url, verify=self.session.verify)
        if self.session.token is not None and self.session.token.get('access_token') is not None:
            decoded_json_token = jwt.decode(self.session.token.get('access_token'), options=_decoding_options)
            self.token_expires_at = decoded_json_token.get(u'exp')


class WaveletAIAuthenticator(Authenticator):

    def __init__(self, api_token, backend_client, ssl_verify):
        super(WaveletAIAuthenticator, self).__init__(host='')

        # We need to pass a lambda to be able to re-create fresh session at any time when needed
        def session_factory():
            auth_tokens = backend_client.api.exchangeApiToken(X_Token=api_token).response().result
            decoded_json_token = jwt.decode(auth_tokens.accessToken, options=_decoding_options)
            expires_at = decoded_json_token.get(u'exp')
            client_name = decoded_json_token.get(u'azp')
            refresh_url = u'{realm_url}/protocol/openid-connect/token'.format(realm_url=decoded_json_token.get(u'iss'))
            token = {
                u'access_token': auth_tokens.accessToken,
                u'refresh_token': auth_tokens.refreshToken,
                u'expires_in': expires_at - time.time()
            }

            session = OAuth2Session(
                client_id=client_name,
                token=token,
                auto_refresh_url=refresh_url,
                auto_refresh_kwargs={'client_id': client_name},
                token_updater=_no_token_updater
            )
            session.verify = ssl_verify

            return session

        self.auth = WaveletAIAuth(session_factory)

    def matches(self, url):
        return True

    def apply(self, request):
        self.auth.refresh_token_if_needed()
        request.auth = self.auth
        return request


def _no_token_updater():
    # For unit tests.
    return None
