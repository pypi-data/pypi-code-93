"""Tornado handlers for logging into the Jupyter Server
with GitHub authentication.
"""

import os
import os.path

from typing import Any, Dict, Optional

import jwt
import datetime

import urllib.parse

from tornado import escape
from tornado.curl_httpclient import CurlAsyncHTTPClient
from tornado.auth import OAuth2Mixin

from jupyter_server.torndsession.session import SessionMixin
from jupyter_server.base.handlers import APIHandler


JWT_SECRET_KEY = "my_secret_key"


class GithubOAuth2Mixin(SessionMixin, OAuth2Mixin):

    _OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    _OAUTH_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
    _OAUTH_USERINFO_URL = "https://api.github.com/user"
    _OAUTH_NO_CALLBACKS = False
    _OAUTH_SETTINGS_KEY = "github_oauth"


    async def get_authenticated_user(
        self, redirect_uri: str, code: str
    ) -> Dict[str, Any]:
        http = self.get_auth_http_client()
        body = urllib.parse.urlencode(
            {
                "redirect_uri": redirect_uri,
                "code": code,
                "client_id": os.getenv('GITHUB_CLIENT_ID'),
                "client_secret": os.getenv('GITHUB_CLIENT_SECRET'),
                "grant_type": "authorization_code",
            }
        )
        response = await http.fetch(
            self._OAUTH_ACCESS_TOKEN_URL,
            method = "POST",
            headers = { "Content-Type": "application/x-www-form-urlencoded" },
            body = body,
        )
        query_qs = urllib.parse.parse_qs(escape.url_unescape(response.body))
        return {
            'access_token': query_qs['access_token'][0], 
            'scope':  query_qs['scope'][0], 
            'token_type':  query_qs['token_type'][0],
        }


class GithubOAuth2Handler(GithubOAuth2Mixin, APIHandler):

    async def get(self):
        if self.get_argument('code', False):
            access = await self.get_authenticated_user(
                redirect_uri = os.getenv('GITHUB_OAUTH_CALLBACK_URL'),
                code = self.get_argument('code')
            )
            user = await self.oauth2_request(
                self._OAUTH_USERINFO_URL,
                access_token = access["access_token"]
            )
            jwt_token = jwt.encode({
                    'iss': '@datalayer-jupyter/id_provider:github',
                    'user':  user['login'],
                    'sub':  user['login'],
                    'azp':  user['login'],
                    'aud': 'jupyter',
                    'name': user['name'],
                    'hireable': user['hireable'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds = 600)
                },
                JWT_SECRET_KEY,
                algorithm = 'HS256',
            )
            user['jwt_token'] = jwt_token
            self.web_session['user'] = user
            self.set_secure_cookie('user', jwt_token)
#            self.redirect(self.config['ServerApp']['default_url'])
            self.redirect(os.getenv('DATALAYER_JUPYTER_HOME', '/'))
        else:
            self.authorize_redirect(
                redirect_uri = os.getenv('GITHUB_OAUTH_CALLBACK_URL'),
                client_id = os.getenv('GITHUB_CLIENT_ID'),
                client_secret = os.getenv('GITHUB_CLIENT_SECRET'),
                scope = ['read:user'],
                response_type = 'code',
                extra_params = { 'approval_prompt': 'auto' }
            )

    async def oauth2_request(
        self,
        url: str,
        access_token: Optional[str] = None,
        post_args: Optional[Dict[str, Any]] = None,
        **args: Any
    ) -> Any:
        all_args = {}
        headers = {}
        if access_token:
            headers['Authorization'] = f'Bearer {access_token}'
        url += "?" + urllib.parse.urlencode(all_args)
        http = CurlAsyncHTTPClient()
        if post_args is not None:
            response = await http.fetch(
                url,
                method = 'POST',
                body = urllib.parse.urlencode(post_args),
                headers=headers
            )
        else:
            response = await http.fetch(url, headers = headers)
        return escape.json_decode(response.body)


class LoginHandler(GithubOAuth2Handler):

    def get_user(self):
        return self.get_session().get("user", None)


    @classmethod
    def get_login_available(cls, settings):
        return True


    @classmethod
    def validate_security(cls, app, ssl_options = None):
        """Check the application's security.

        Show messages, or abort if necessary, based on the security configuration.
        """
        if not app.ip:
            warning = "WARNING: The Jupyter server is listening on all IP addresses"
            if ssl_options is None:
                app.log.warning(warning + " and not using encryption. This "
                    "is not recommended.")
            if not app.password and not app.token:
                app.log.warning(warning + " and not using authentication. "
                    "This is highly insecure and not recommended.")
        else:
            if not app.password and not app.token:
                app.log.warning(
                    "All authentication is disabled."
                    "  Anyone who can connect to this server will be able to run code.")
