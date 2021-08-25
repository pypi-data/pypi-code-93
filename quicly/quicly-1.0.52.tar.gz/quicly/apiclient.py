from typing import *

from quicly import jsonutils as json
from quicly.hashutils import QxHash
from quicly.result import QxResult, QxError, QxFinish
from quicly.urlutils import QxUrl

import os
import requests
import base64


class QxApiClient(object):
  UA_DEFAULT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'

  def __init__(self, url: str, signer: Callable = None, **kw):
    self._url = self._process_url(url)
    self._host = self._process_host(url)
    self._cookies_dir = kw.get('cookies_dir', '/tmp')
    self._session = kw.get('session', requests.Session())
    self._signer = signer

  @staticmethod
  def _process_url(url: str):
    url = url.strip().strip('/').strip()

    url_t = url.lower()
    if not url_t.startswith('http://') and not url_t.startswith('https://'):
      url = f'http://{url}'
    url.rstrip('/')

    return url

  @staticmethod
  def _process_host(url: str):
    return url.split('//', maxsplit=1)[1].split('/', maxsplit=1)[0]

  @staticmethod
  def mk_url(url: str, path: str = None, params: dict = None) -> str:
    return QxUrl().set_url(url).join_path(path).set_query(params).mk_url()

  def _mk_url(self, path: str = None, params: dict = None) -> str:
    return self.mk_url(self._url, path, params)

  @staticmethod
  def mk_headers(headers: Union[dict, str] = None) -> dict:
    headers = headers if isinstance(headers, dict) else dict()

    headers.setdefault('User-Agent', QxApiClient.UA_DEFAULT)

    return headers

  def _mk_headers(self, headers: Union[dict, str] = None) -> dict:
    headers = self.mk_headers(headers)

    headers.setdefault('Host', self._host)
    headers.setdefault('Origin', self._url)

    return headers

  def _mk_cookies_path(self):
    if not os.path.isdir(self._cookies_dir):
      os.makedirs(self._cookies_dir)

    cookies_file_path = os.path.join(self._cookies_dir, f'{self._host}.cookies.json')
    cookies_lock_path = f'{cookies_file_path}.lock'

    return cookies_file_path, cookies_lock_path

  def _mk_cookies_hash(self):
    return QxHash('sha512').hash_s(self._url)

  def _load_cookies(self):
    if not self._cookies_dir:
      return

    self._session.cookies.clear()

    cookies_file_path, cookies_lock_path = self._mk_cookies_path()
    if not os.path.isfile(cookies_file_path) or not os.path.isfile(cookies_lock_path):
      return

    with open(cookies_lock_path, 'r+', encoding='utf-8') as fo:
      if fo.read() != self._mk_cookies_hash():
        return

    with open(cookies_file_path, 'r+', encoding='utf-8') as fo:
      try:
        cookies = json.loads(fo.read())
      except json.JSONDecodeError:
        cookies = None

    if isinstance(cookies, dict):
      for k, v in cookies.items():
        self._session.cookies.set(k, v)

  def _save_cookies(self):
    if not self._cookies_dir:
      return

    cookies_file_path, cookies_lock_path = self._mk_cookies_path()

    with open(cookies_file_path, 'w+', encoding='utf-8') as fo:
      fo.write(json.dumps(self._session.cookies.get_dict(), indent=2, ensure_ascii=False))

    with open(cookies_lock_path, 'w+', encoding='utf-8') as fo:
      fo.write(self._mk_cookies_hash())

  @staticmethod
  def _process_request_data(data: Union[bytes, str, dict, None]):
    return data

  def _request_raw(self, method: str, path: str, **kw):
    method = method.upper()
    assert method in ('GET', 'PUT', 'POST', 'PATCH', 'DELETE')
    url = self._mk_url(path, params=kw.get('params', {}))

    headers = self._mk_headers(kw.get('headers'))

    if callable(self._signer):
      headers = self._signer(method, url, headers)

    kw['headers'] = headers
    kw['data'] = self._process_request_data(kw.get('data'))
    kw.setdefault('verify', False)

    self._load_cookies()

    res = self._session.request(method, url, **kw)

    self._save_cookies()

    return res

  def _get_raw(self, path: str, params: dict = None, **kw):
    return self._request_raw('GET', path, params=params, **kw)

  def _put_raw(self, path: str, params: dict = None, data: Union[AnyStr, dict, None] = None, **kw):
    return self._request_raw('PUT', path, params=params, data=data, **kw)

  def _post_raw(self, path: str, params: dict = None, data: Union[AnyStr, dict, None] = None, **kw):
    return self._request_raw('POST', path, params=params, data=data, **kw)

  def _patch_raw(self, path: str, params: dict = None, data: Union[AnyStr, dict, None] = None, **kw):
    return self._request_raw('PATCH', path, params=params, data=data, **kw)

  def _delete_raw(self, path: str, params: dict = None, **kw):
    return self._request_raw('DELETE', path, params=params, **kw)

  @staticmethod
  def _decode_response_text(text: AnyStr, default: Any = None):
    return text

  def _decode_response(self, res: requests.Response):
    if res.status_code == 200:
      ret = QxFinish(data=self._decode_response_text(res.text))
    else:
      ret = QxError(code=res.status_code, message=self._decode_response_text(res.text, res.text))
    return ret

  def _request(self, method: str, path: str, **kw):
    return self._decode_response(self._request_raw(method, path, **kw))

  def _get(self, path: str, params: dict = None, **kw):
    return self._decode_response(self._get_raw(path, params, **kw))

  def _put(self, path: str, params: dict = None, data: Union[AnyStr, dict, None] = None, **kw):
    return self._decode_response(self._put_raw(path, params, data, **kw))

  def _post(self, path: str, params: dict = None, data: Union[AnyStr, dict, None] = None, **kw):
    return self._decode_response(self._post_raw(path, params, data, **kw))

  def _patch(self, path: str, params: dict = None, data: Union[AnyStr, dict, None] = None, **kw):
    return self._decode_response(self._patch_raw(path, params, data, **kw))

  def _delete(self, path: str, params: dict = None, **kw):
    return self._decode_response(self._delete_raw(path, params, **kw))


class QxRestClient(QxApiClient):
  def __init__(self, url: str, **kw):
    super(QxRestClient, self).__init__(url, **kw)

  @staticmethod
  def _decode_response_text(text: AnyStr, default: Any = None):
    try:
      ret = json.loads(text)
    except json.JSONDecodeError:
      ret = default
    return ret

  @staticmethod
  def _mk_page(page: Union[str, dict]) -> dict:
    if isinstance(page, str):
      try:
        page = json.loads(page)
      except json.JSONDecodeError:
        try:
          page = json.loads(base64.b64decode(page))
        except json.JSONDecodeError:
          page = None

    if not isinstance(page, dict):
      page = dict()

    page.setdefault('offset', None)
    page.setdefault('limit', 100)
    page.setdefault('total', None)
    page.setdefault('index', 1)

    return page

  @staticmethod
  def _mk_list_params(page: Union[str, dict], params: dict = None) -> dict:
    ret = dict()

    if isinstance(params, dict):
      ret.update(params)

    if isinstance(page, dict):
      ret.update(page)

    return ret

  def _mk_new_page(self, page: Union[str, dict], data: Any):
    raise NotImplementedError()

  @staticmethod
  def _decode_list_data(data: Any):
    return data

  def _list(self, path: str, page: Union[str, dict] = None, params: str = None, method: str = 'GET', **kw) -> QxResult:
    ret = self._request(method, path, params=self._mk_list_params(page, params), **kw)
    if ret:
      ret = QxFinish((self._decode_list_data(ret.data), self._mk_new_page(page, ret.data)))
    return ret

  @staticmethod
  def _decode_find_data(data: Any):
    return data

  def _find(self, path: str, params: dict = None, method: str = 'GET', **kw) -> QxResult:
    ret = self._request(method, path, params=params, **kw)
    if ret:
      ret = QxFinish(self._decode_find_data(ret.data))
    return ret

  @staticmethod
  def _decode_update_data(data: Any):
    return data

  def _update(self, path: str, params: dict = None, data: dict = None, method: str = 'PUT', **kw) -> QxResult:
    ret = self._request(method, path, params=params, data=data, **kw)
    if ret:
      ret = QxFinish(self._decode_update_data(ret.data))
    return ret

  @staticmethod
  def _decode_delete_data(data: Any):
    return data

  def _delete(self, path: str, params: dict = None, method: str = 'DELETE', **kw) -> QxResult:
    ret = self._request(method, path, params=params, **kw)
    if ret:
      ret = QxFinish(self._decode_delete_data(ret.data))
    return ret

  @staticmethod
  def _decode_create_data(data: Any):
    return data

  def _create(self, path: str, params: dict = None, data: dict = None, method: str = 'POST', **kw) -> QxResult:
    ret = self._request(method, path, params=params, data=data, **kw)
    if ret:
      ret = QxFinish(self._decode_delete_data(ret.data))
    return ret
