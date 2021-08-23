
from tornado.auth import OAuth2Mixin
from panel.auth import OAuthIDTokenLoginHandler
from panel.config import config


class OidcAuth0Handler(OAuthIDTokenLoginHandler, OAuth2Mixin):

    _SCOPE = ['openid', 'email', 'profile']

    _USER_KEY = 'email'

    _EXTRA_TOKEN_PARAMS = {
        'grant_type':    'authorization_code',
        'response_type': 'code,token,id_token'
    }
    
    _EXTRA_AUTHORIZE_PARAMS = {
        'grant_type': 'authorization_code'
    }

    _OAUTH_ACCESS_TOKEN_URL_ = 'https://{0}.auth0.com/oauth/token'
    _OAUTH_AUTHORIZE_URL_ = 'https://{0}.auth0.com/authorize'
    _OAUTH_USER_URL_ = 'https://{0}.auth0.com/userinfo?access_token='

    @property
    def _OAUTH_ACCESS_TOKEN_URL(self):
        url = config.oauth_extra_params.get('subdomain', 'example')
        return self._OAUTH_ACCESS_TOKEN_URL_.format(url)

    @property
    def _OAUTH_AUTHORIZE_URL(self):
        url = config.oauth_extra_params.get('subdomain', 'example')
        return self._OAUTH_AUTHORIZE_URL_.format(url)

    @property
    def _OAUTH_USER_URL(self):
        url = config.oauth_extra_params.get('subdomain', 'example')
        return self._OAUTH_USER_URL_.format(url)
