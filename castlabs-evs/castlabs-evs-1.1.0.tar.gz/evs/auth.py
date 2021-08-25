# Copyright 2020, castLabs GmbH

from . import __version__
from .core.error import NonInteractiveError

from sys import stdin
from os import environ, path, makedirs
import errno
from getpass import getpass
import json

import boto3

################################################################################

DEFAULT_CONFIG_FILE = '~/.config/evs/config.json'
DEFAULT_CLIENT_ID = '4mdbpdvnjc0tq0lvi96aqvictb'
DEFAULT_CLIENT_REGION = 'us-east-1'

################################################################################

class Auth(object):
  def __init__(self, no_refresh=False, no_ask=True, config_file=None, client_id=None, region=None):
    self._version = __version__
    self._config_file = path.expanduser(config_file or environ.get('EVS_CONFIG_FILE', DEFAULT_CONFIG_FILE))
    self._config_dir = path.dirname(self._config_file)
    self._client_id = client_id or environ.get('EVS_CLIENT_ID', DEFAULT_CLIENT_ID)
    self._client_region = region or environ.get('EVS_CLIENT_REGION', DEFAULT_CLIENT_REGION)
    self._auth_account_name = None
    self._auth_passwd = None
    self._auth_access_token = None
    self._auth_refresh_token = None
    self._auth_id_token = None
    self.__refreshed_auth = False
    self.__no_ask = no_ask or not stdin.isatty()
    self._load_config()

  def _on_load_config(self, j):
    a = j.get('Auth', {})
    account_name = a.get('AccountName')
    if self._auth_account_name and account_name != self._auth_account_name:
      return
    self._auth_account_name = account_name
    self._auth_access_token = self._auth_access_token or a.get('AccessToken')
    self._auth_refresh_token = self._auth_refresh_token or a.get('RefreshToken')
    self._auth_id_token = self._auth_id_token or a.get('IdToken')

  def _load_config(self):
    try:
      with open(self._config_file) as fh:
        self.__config = json.load(fh)
        self._on_load_config(self.__config)
    except:
      self.__config = {}

  def _on_store_config(self, j={}):
    j['Auth'] = {
      'AccountName': self._auth_account_name,
      'AccessToken': self._auth_access_token,
      'RefreshToken': self._auth_refresh_token,
      'IdToken': self._auth_id_token,
    }
    return j

  def _store_config(self):
    if not self._config_file:
      return False
    try:
      try:
        makedirs(self._config_dir)
      except OSError as e:
        if errno.EEXIST != e.errno or not path.isdir(self._config_dir):
          return False
      with open(self._config_file, 'w') as fh:
        json.dump(self._on_store_config(self.__config), fh, indent=2)
      return True
    except Exception as e:
      return False

  def _auth_client(self):
    if not hasattr(self, '_Auth__auth_client'):
      for k in environ.keys():
        if k.startswith('AWS_'):
          del environ[k]
      session = boto3.Session(region_name=self._client_region)
      self.__auth_client = session.client('cognito-idp')
    return self.__auth_client

  def _ask(self, title, default=None, min=None, max=None, secret=False, confirm=False):
    if self.__no_ask:
      if confirm:
        raise NonInteractiveError('\'{}\' attribute requires user confirmation'.format(title))
      if default is None:
        raise NonInteractiveError('\'{}\' attribute has no default value'.format(title))
      return default
    default = default or ''
    prompt = '>> {} [{}]: '.format(title, '*' * len(default) if secret else default)
    fn = getpass if secret else input
    while True:
      v = fn(prompt) or default
      if min is not None and len(v) < min:
        print(' - \'{}\' needs to be at least {} characters long'.format(title, min))
        continue
      if max is not None and len(v) > max:
        print(' - \'{}\' needs to be at most {} characters long'.format(title, max))
        continue
      return v

  def _refresh_auth(self, account_name=None, passwd=None):
    if account_name and account_name != self._auth_account_name:
      self._clear_auth()
    if self.__refreshed_auth:
      return False
    self.__refreshed_auth = True
    self._auth_access_token = None
    try:
      client = self._auth_client()
      if self._auth_refresh_token:
        try:
          r = client.initiate_auth(
            ClientId=self._client_id,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={'REFRESH_TOKEN': self._auth_refresh_token}
          )
          j = r['AuthenticationResult']
          self._auth_access_token = j['AccessToken']
          self._auth_id_token = j['IdToken']
        except Exception as e:
          self._auth_refresh_token = self._auth_id_token = None
      if not self._auth_access_token:
        try:
          self._auth_account_name = account_name or self._ask('Account Name', default=self._auth_account_name, min=1)
          self._auth_passwd = passwd or self._ask('Password', default=self._auth_passwd, min=1, secret=True)
          r = client.initiate_auth(
            ClientId=self._client_id,
            AuthFlow='USER_PASSWORD_AUTH',
            AuthParameters={'USERNAME': self._auth_account_name, 'PASSWORD': self._auth_passwd}
          )
          j = r['AuthenticationResult']
          self._auth_access_token = j['AccessToken']
          self._auth_refresh_token = j['RefreshToken']
          self._auth_id_token = j['IdToken']
        except Exception as e:
          self._auth_access_token = self._auth_refresh_token = self._auth_id_token = None
          raise
      return True
    finally:
      self._store_config()

  def _clear_auth(self):
    self._auth_access_token = None
    self._auth_refresh_token = None
    self._auth_id_token = None
    self.__refreshed_auth = False

  def _check_auth(self, account_name=None, passwd=None):
    account_name = account_name or self._auth_account_name
    if account_name != self._auth_account_name or not self._auth_access_token:
      self._clear_auth()
      return self._refresh_auth(account_name, passwd)
    return False

################################################################################
