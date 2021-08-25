from typing import *

from urllib.parse import urlparse, quote, unquote

import os


class QxUrl(object):
  def __init__(self, url: Union[str, object] = None, **kw):
    self._protocol = None
    self._username = None
    self._password = None
    self._hostname = None
    self._port = None
    self._path = None
    self._query = None
    self._query_str = None
    self._fragment = None

    self.set_url(url)

  @property
  def protocol(self) -> str:
    return self._protocol

  @protocol.setter
  def protocol(self, protocol: str):
    self._protocol = protocol

  @property
  def username(self) -> str:
    return self._username

  @username.setter
  def username(self, username: str):
    self._username = username

  @property
  def password(self) -> str:
    return self._password

  @password.setter
  def password(self, password: str):
    self._password = password

  @property
  def hostname(self) -> str:
    return self._hostname

  @hostname.setter
  def hostname(self, hostname: str):
    self._hostname = hostname

  @property
  def port(self) -> int:
    return self._port

  @port.setter
  def port(self, port: Union[int, str, None]):
    if isinstance(port, str):
      try:
        port = int(port)
      except ValueError:
        port = None

    self._port = port if isinstance(port, int) and port >= 0 else None

  @property
  def path(self) -> str:
    return self._path

  @path.setter
  def path(self, path: str):
    if not path.startswith('/'):
      path = f'/{path}'
    self._path = path

  @staticmethod
  def parse_query_str(query_str: str) -> dict:
    q = OrderedDict()
    for kv in query_str.split('&'):
      if not len(kv.strip()):
        continue

      kv = kv.split('=', maxsplit=1)

      k = kv[0]
      v = unquote(kv[1]) if len(kv) > 1 else ''

      if k in q:
        if isinstance(q[k], (tuple, list)):
          q[k] = list(q[k]) + [v]
        else:
          q[k] = [q[k], v]
      else:
        q[k] = v
    return q

  @staticmethod
  def mk_query_str(query: dict) -> str:
    items = []
    for k, vl in query.items():
      if not isinstance(vl, (tuple, list)):
        vl = [vl]
      for v in vl:
        items.append(f'{k}={quote(v)}')
    return '&'.join(items)

  @property
  def query(self) -> dict:
    return self._query

  @property
  def query_str(self) -> str:
    return self._query_str

  @query.setter
  def query(self, query: Union[str, dict]):
    if isinstance(query, str):
      query = self.parse_query_str(query)
      query_str = self.mk_query_str(query)
    elif isinstance(query, dict):
      query_str = self.mk_query_str(query)
      query = self.parse_query_str(query_str)
    else:
      query = {}
      query_str = ''
    self._query = query
    self._query_str = query_str

  @property
  def path_with_query(self) -> str:
    if self.query_str:
      ret = f'{self.path}?{self.query_str}'
    else:
      ret = self.path
    return ret

  @property
  def fragment(self) -> str:
    return self._fragment

  @fragment.setter
  def fragment(self, fragment: str):
    self._fragment = fragment

  def set_protocol(self, protocol: str):
    self.protocol = protocol
    return self

  def set_username(self, username: str):
    self.username = username
    return self

  def set_password(self, password: str):
    self.password = password
    return self

  def set_hostname(self, hostname: str):
    self.hostname = hostname
    return self

  def set_port(self, port: Union[int, str, None]):
    self.port = port
    return self

  def set_path(self, path: str):
    self.path = path
    return self

  def join_path(self, *paths):
    self.path = os.path.join('/' if not self.path else self.path, *paths)
    return self

  def set_query(self, query: Union[str, dict]):
    self.query = query
    return self

  def set_param(self, k, v, arr=False):
    v = unquote(v)
    q = self._query
    if arr and k in self._query:
      if isinstance(q[k], (tuple, list)):
        q[k] = list(q[k]) + [v]
      else:
        q[k] = [q[k], v]
    else:
      q[k] = v
    self._query = q
    self._query_str = self.mk_query_str(q)
    return self

  def set_fragment(self, fragment: str):
    self.fragment = fragment
    return self

  def set_url(self, url: str):
    if isinstance(url, str):
      p = urlparse(url)
      self.protocol = p.scheme
      self.username = p.username
      self.password = p.password
      self.hostname = p.hostname
      self.port = p.port
      self.path = p.path
      self.query = p.query
      self.fragment = p.fragment
    elif isinstance(url, QxUrl):
      self._protocol = url._protocol
      self._username = url._username
      self._password = url._password
      self._hostname = url._hostname
      self._port = url._port
      self._path = url._path
      self._query = url._query
      self._query_str = url._query_str
      self._fragment = url._fragment
    return self

  def mk_url(self) -> str:
    s = f'{self.protocol}://'
    if self.username:
      s += quote(self.username)
      if self.password:
        s += f':{quote(self.password)}'
      s += '@'
    s += self.hostname
    if self.port:
      s += f':{self.port}'
    s += quote(self.path)

    if self.query_str:
      s += f'?{self.query_str}'

    if self.fragment:
      s += f'#{quote(self.fragment)}'

    return s

  def __str__(self):
    return self.mk_url()

  def mk_dict(self) -> dict:
    return {
      'protocol': self.protocol,
      'username': self.username,
      'password': self.password,
      'hostname': self.hostname,
      'port': self.port,
      'query': self.query,
      'query_str': self.query_str,
      'fragment': self.fragment,
    }
