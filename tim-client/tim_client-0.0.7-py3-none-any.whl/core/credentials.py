from typing import Optional


class Credentials:
  __email: Optional[str] = None
  __password: Optional[str] = None
  __token: Optional[str] = None
  __token_expiration: str = ""
  __endpoint: Optional[str] = None

  def __init__(
      self,
      email: str,
      password: str,
      endpoint: str = "https://tim-platform-test.tangent.works/api/v5",
  ):
    self.__email = email
    self.__password = password
    self.__endpoint = endpoint

  @property
  def email(self):
    return self.__email

  @property
  def token(self):
    return self.__token

  @property
  def password(self):
    return self.__password

  @property
  def endpoint(self):
    return self.__endpoint

  @property
  def token_expiration(self):
    return self.__token_expiration

  @token.setter
  def token(self, token: str):
    self.__token = token

  @token_expiration.setter
  def token_expiration(self, token_expiration: str):
    self.__token_expiration = token_expiration
