import requests
from requests_toolbelt.utils import dump
import keyring
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
from urllib.parse import parse_qs
from webbrowser import open_new
import certifi

from enum import Enum


class HTTPServerHandler(BaseHTTPRequestHandler):

    def __init__(self, request, address, server):
        super().__init__(request, address, server)

    def do_GET(self):
        if self.path.startswith('/auth?access_token='):
            self.server.access_token = parse_qs(self.path[6:])["access_token"][0]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(
                "<html><head></head><h1>You may now close this window."
                + "</h1></html>", "utf-8"))
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes("<html><head><script>window.location.href = '/auth?access_token=' + window.location.href.split('#')[1].split('&').filter(function(c) { return c.startsWith('access_token=')})[0].substring(13);</script></head><h1>You may now close this window."
                               + "</h1></html>", "utf-8"))
        return


class AuthMode(str, Enum):
    CLIENT_CERT = 'CLIENT_CERT'
    CLIENT_KEY = 'CLIENT_KEY'
    AUTH_URL = 'AUTH_URL'
    BASIC = 'BASIC'
    NONE = 'NONE'


class AuthCfg:

    def __init__(self,
                 auth_mode='NONE',
                 auth_url=os.getenv('AUTH_URL'),
                 callback_url=os.getenv('CALLBACK_URL', 'http://localhost:8080'),
                 client_id=os.getenv('CLIENT_ID'),
                 client_key=os.getenv('CLIENT_KEY'),
                 client_secret=os.getenv('CLIENT_SECRET'),
                 token_url=os.getenv('TOKEN_URL'),
                 client_cert=os.getenv('CLIENT_CERT'),
                 client_cert_key=os.getenv('CLIENT_CERT_KEY'),
                 ca_bundle=os.getenv('CA_BUNDLE', certifi.where()),
                 basic_username=os.getenv('BASIC_USERNAME'),
                 basic_password=os.getenv('BASIC_PASSWORD'),
                 basic_use_digest=os.getenv('BASIC_USE_DIGEST', False),
                 debug=os.getenv('DEBUG', False),
                 timeout=os.getenv('TIMEOUT', 10),
                 name=None,
                 url=None):

        '''
        :param api_base_url:
        :param auth_url:
        :param callback_url:
        :param client_id:
        :param client_key:
        :param client_secret:
        :param token_url:
        :param client_cert:
        :param client_cert_key:
        :param ca_bundle:
        :param basic_username:
        :param basic_password:
        :param basic_use_digest:
        :param debug:
        :param timeout:
        '''

        self.auth_mode = auth_mode
        self.auth_url = auth_url
        self.callback_url = callback_url
        self.client_id = client_id
        self.client_key = client_key
        self.client_secret = client_secret
        self.token_url = token_url
        self.basic_username = basic_username
        self.basic_password = basic_password
        self.basic_use_digest = basic_use_digest
        self.client_cert = client_cert
        self.client_cert_key = client_cert_key
        self.ca_bundle = ca_bundle
        self.debug = debug
        self.timeout = timeout

    def get_client_id(self):
        return self.client_id

    def get_client_key(self):
        return self.client_key

    def get_client_secret(self):
        return self.client_secret

    def get_callback_url(self):
        return self.callback_url

    def get_auth_url(self):
        return self.auth_url

    def get_token_url(self):
        return self.token_url

    def get_debug(self):
        return self.debug

    def get_client_cert(self):
        return self.client_cert

    def get_client_cert_key(self):
        return self.client_cert_key

    def get_ca_bundle(self):
        return self.ca_bundle

    def get_timeout(self):
        return self.timeout

    def get_basic_username(self):
        return self.basic_username

    def get_basic_password(self):
        return self.basic_password

    def get_basic_use_digest(self):
        return self.basic_use_digest

    def to_dict(self):
        return {
            'auth_url': self.get_auth_url(),
            'callback_url': self.get_callback_url(),
            'client_id': self.get_client_id(),
            'client_key': self.get_client_key(),
            'client_secret': self.get_client_secret(),
            'token_url': self.get_token_url(),
            'basic_username': self.get_basic_username(),
            'basic_password': self.get_basic_password(),
            'basic_use_digest': self.get_basic_use_digest(),
            'client_cert': self.get_client_cert(),
            'client_cert_key': self.get_client_cert_key(),
            'ca_bundle': self.get_ca_bundle(),
            'debug': self.get_debug(),
            'timeout': self.get_timeout()
        }


class Auth:

    def __init__(self, auth):

        cfg = AuthCfg(**auth)
        self.client_id = cfg.get_client_id()

        # AUTH_URL Method
        self.callback_url = cfg.get_callback_url()
        self.auth_url = cfg.get_auth_url()

        # CLIENT_KEY Method
        self.client_key = cfg.get_client_key()
        self.client_secret = cfg.get_client_secret()
        self.token_url = cfg.get_token_url()

        # CLIENT_CERT Method
        self.client_cert = cfg.get_client_cert()
        self.client_cert_key = cfg.get_client_cert_key()
        self.ca_bundle = cfg.get_ca_bundle()

        # BASIC Method
        self.basic_username = cfg.get_basic_username()
        self.basic_password = cfg.get_basic_password()
        self.basic_use_digest = cfg.get_basic_use_digest()

        self.debug = cfg.get_debug()

    def get_mode(self):
        if self.client_cert and self.client_cert_key:
            return AuthMode.CLIENT_CERT
        elif self.client_key and self.client_secret and self.token_url:
            return AuthMode.CLIENT_KEY
        elif self.auth_url and self.callback_url:
            return AuthMode.AUTH_URL
        else:
            return AuthMode.BASIC

    def login(self):
        self.store_token(self.get_token())

    def logout(self):
        self.store_token(None)

    def store_token(self, token):
        if token:
            last_index = 0
            for chunk in self.chunks(token, 256):
                keyring.set_password(self.client_id, "access_token_{0}".format(chunk[0]), chunk[1])
                last_index = chunk[0]
            keyring.set_password(self.client_id, "access_token_count", str(last_index))
        else:
            count = keyring.get_password(self.client_id, "access_token_count")
            if count:
                for index in range(0, int(count) + 1):
                    keyring.delete_password(self.client_id, "access_token_{0}".format(index))
            keyring.delete_password(self.client_id, "access_token_count")

    def retrieve_token(self, force=False):
        if force:
            access_token = self.login()
        else:
            count = keyring.get_password(self.client_id, "access_token_count")
            access_token = ''
            if count:
                for index in range(0, int(count) + 1):
                    access_token += keyring.get_password(self.client_id, "access_token_{0}".format(index))
            else:
                access_token = self.login()
        return access_token

    @classmethod
    def chunks(cls, s, n):
        for index, start in enumerate(range(0, len(s), n)):
            yield (index, s[start:start + n])

    def get_token(self):
        mode = self.get_mode()
        if mode == AuthMode.CLIENT_KEY:
            return self.get_api_token()
        elif mode == AuthMode.AUTH_URL:
            return self.get_auth_token()
        elif mode == AuthMode.BASIC:
            return self.get_basic_token()
        else:
            if self.debug:
                print('using client certificate auth method')
            return None

    def get_api_token(self):
        resp = requests.post(self.token_url, data={'response_type': 'token',
                                        'grant_type': 'password',
                                        'username': self.client_key,
                                        'password': self.client_secret,
                                        'client_id': self.client_id,
                                        'redirect_uri': self.callback_url}, verify=False)

        if self.debug:
            data = dump.dump_all(resp)
            print(data.decode('utf-8'))

        if resp.status_code == 401:
            print('Error: {}'.format(resp.json()['error_description']))
            return None

        return resp.json()['access_token']

    def get_auth_token(self):
        httpServer = HTTPServer(tuple(self.callback_url.split(':')),
                                lambda req, address, server: HTTPServerHandler(req, address, server))

        open_new(
            self.auth_url + '?client_id=' + self.client_id + '&redirect_uri=' + self.callback_url + '&response_type=token')

        httpServer.handle_request()
        httpServer.handle_request()

        return httpServer.access_token

    def get_basic_token(self):
        if str(self.basic_use_digest).lower() == 'true':
            return HTTPDigestAuth(self.basic_username, self.basic_password)
        else:
            return HTTPBasicAuth(self.basic_username, self.basic_password)

    def add_arguments(self, parser):
        parser.add_argument('op', choices=['login', 'logout', 'status'],
                            help="authenticate", default='status', const='status', nargs='?')

    def run(self, args):
        if args.op == 'login':
            self.login()
        elif args.op == 'logout':
            self.logout()
        else:
            print('Authenticated: {0}'.format(self.retrieve_token() is not None))

    def get_help(self):
        return 'access control'



