# Copyright 2020, castLabs GmbH

from .auth import Auth

################################################################################

class Account(Auth):
  def __init__(self, no_ask=True, **_):
    self._account_name = None
    self._first_name = None
    self._last_name = None
    self._email = None
    self._organization = None
    super().__init__(no_ask=no_ask)

  def _on_load_config(self, j):
    super()._on_load_config(j)
    i = j.get('Account', {})
    account_name = i.get('AccountName')
    if self._account_name and account_name != self._account_name:
      return
    self._account_name = account_name
    self._first_name = self._first_name or i.get('FirstName')
    self._last_name = self._last_name or i.get('LastName')
    self._email = self._email or i.get('Email')
    self._organization = self._organization or i.get('Organization')

  def _on_store_config(self, j={}):
    j['Account'] = {
      'FirstName': self._first_name,
      'LastName': self._last_name,
      'Email': self._email,
      'Organization': self._organization,
      'AccountName': self._account_name,
    }
    return super()._on_store_config(j)

  def _refresh_account(self, account_name=None, passwd=None):
    client = self._auth_client()
    while True:
      try:
        r = client.get_user(
          AccessToken=self._auth_access_token,
        )
        r = { i['Name']: i['Value'] for i in r['UserAttributes'] }
        self._email = r.get('email')
        self._first_name = r.get('given_name', self._first_name)
        self._last_name = r.get('family_name', self._first_name)
        self._organization = r.get('custom:organization', self._organization)
        self._account_name = self._auth_account_name
        self._store_config()
        break
      except client.exceptions.NotAuthorizedException as e:
        if not self._refresh_auth():
          raise

  def signup(self, account_name=None, passwd=None, email=None, first_name=None, last_name=None, organization=None, no_confirm=False, **_):
    print('Signing up for castLabs EVS')
    print(' - A valid e-mail address is required for account verification')
    self._email = email or self._ask('E-mail Address', default=self._email, min=5, confirm=True)
    self._first_name = first_name or self._ask('First Name', default=self._first_name, min=1, confirm=True)
    self._last_name = last_name or self._ask('Last Name', default=self._last_name, min=1, confirm=True)
    self._organization = organization or self._ask('Organization', default=self._organization, confirm=True)
    self._account_name = account_name or self._ask('Account Name', default=self._account_name or self._auth_account_name, min=1, confirm=True)
    if not passwd:
      while True:
        passwd = self._ask('Password', min=8, secret=True)
        if passwd == self._ask('Verify Password', min=8, secret=True):
          break
        print(' - Passwords do not match')
    self._store_config()
    r = self._auth_client().sign_up(
      ClientId=self._client_id,
      Username=self._account_name,
      Password=passwd,
      UserAttributes=[
        {'Name': 'email', 'Value': self._email},
        {'Name': 'given_name', 'Value': self._first_name},
        {'Name': 'family_name', 'Value': self._last_name},
        {'Name': 'custom:organization', 'Value': self._organization},
      ]
    )
    if not r['UserConfirmed'] and not no_confirm:
      self.confirm_signup(self._account_name, passwd)

  def resend(self, account_name=None, passwd=None, no_confirm=False, **_):
    print('Resending EVS account confirmation code')
    account_name = account_name or self._ask('Account Name', default=self._account_name or self._auth_account_name, min=1, confirm=True)
    r = self._auth_client().resend_confirmation_code(
      ClientId=self._client_id,
      Username=self._account_name
    )
    if not no_confirm:
      self.confirm_signup(self._account_name, passwd)

  def confirm_signup(self, account_name=None, passwd=None, code=None, **_):
    print('Confirming EVS account')
    print(' - A confirmation code has been sent to your e-mail address')
    account_name = account_name or self._ask('Account Name', default=self._account_name or self._auth_account_name, min=1, confirm=True)
    code = code or self._ask('Confirmation Code', min=6)
    r = self._auth_client().confirm_sign_up(
      ClientId=self._client_id,
      Username=account_name,
      ConfirmationCode=code,
    )
    self.reauth(account_name, passwd)

  def update(self, account_name=None, passwd=None, first_name=None, last_name=None, organization=None):
    print('Updating EVS account details')
    account_name = account_name or self._ask('Account Name', default=self._auth_account_name or self._account_name, min=1, confirm=True)
    if self._check_auth(account_name, passwd):
      self._refresh_account(account_name, passwd)
    self._first_name = first_name or self._ask('First Name', default=self._first_name, min=1, confirm=True)
    self._last_name = last_name or self._ask('Last Name', default=self._last_name, min=1, confirm=True)
    self._organization = organization or self._ask('Organization', default=self._organization, confirm=True)
    self._store_config()
    client = self._auth_client()
    while True:
      try:
        r = client.update_user_attributes(
          AccessToken=self._auth_access_token,
          UserAttributes=[
            {'Name': 'given_name', 'Value': self._first_name},
            {'Name': 'family_name', 'Value': self._last_name},
            {'Name': 'custom:organization', 'Value': self._organization},
          ]
        )
        break
      except client.exceptions.NotAuthorizedException as e:
        if not self._refresh_auth():
          raise

  def reset(self, account_name=None, passwd=None, no_confirm=False, **_):
    print('Requesting EVS account password reset')
    print(' - A confirmation code will be sent to your e-mail address')
    account_name = account_name or self._ask('Account Name', default=self._auth_account_name or self._account_name, min=1, confirm=True)
    r = self._auth_client().forgot_password(
      ClientId=self._client_id,
      Username=account_name,
    )
    if not no_confirm:
      self.confirm_reset(account_name, passwd)

  def confirm_reset(self, account_name=None, passwd=None, code=None, **_):
    print('Confirming EVS account password reset')
    print(' - A confirmation code has been sent to your e-mail address')
    account_name = account_name or self._ask('Account Name', default=self._auth_account_name or self._account_name, min=1, confirm=True)
    if not passwd:
      while True:
        passwd = self._ask('New Password', min=8, secret=True)
        if passwd == self._ask('Verify Password', min=8, secret=True):
          break
        print(' - Passwords do not match')
    code = code or self._ask('Confirmation Code', min=6)
    r = self._auth_client().confirm_forgot_password(
      ClientId=self._client_id,
      Username=account_name,
      Password=passwd,
      ConfirmationCode=code,
    )
    self.reauth(account_name, passwd)

  def refresh(self, account_name=None, passwd=None, **_):
    print("Refreshing authorization token(s)")
    if self._refresh_auth(account_name, passwd):
      self._refresh_account(account_name, passwd)

  def deauth(self, **_):
    print("Discarding authorization token(s)")
    self._clear_auth()
    self._store_config()

  def reauth(self, account_name=None, passwd=None, **_):
    self.deauth()
    self.refresh(account_name, passwd)

  def delete(self, account_name=None, passwd=None, **_):
    print('Deleting EVS account')
    print(' - Account deletion requires user confirmation')
    account_name = self._ask('Confirm Account Name', default=account_name or self._auth_account_name or self._account_name, min=1, confirm=True)
    if self._check_auth(account_name, passwd):
      self._refresh_account(account_name, passwd)
    client = self._auth_client()
    while True:
      try:
        r = client.delete_user(
          AccessToken=self._auth_access_token
        )
        break
      except client.exceptions.NotAuthorizedException as e:
        if not self._refresh_auth():
          raise

################################################################################

if __name__ == '__main__':
  from .cli.account import main
  main()

################################################################################
