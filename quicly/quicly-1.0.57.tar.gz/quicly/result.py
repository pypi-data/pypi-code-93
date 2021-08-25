from typing import *

from quicly.conf import QxGlobalConf
from quicly import jsonutils as json
from quicly.value import QxValue


class QxResult(Exception):
  CODE_0_OK = 0
  CODE_400_BAD_REQUEST = 400
  CODE_401_UNAUTHORIZED = 401
  CODE_403_FORBIDDEN = 403
  CODE_404_NOT_FOUND = 404
  CODE_405_METHOD_NOT_ALLOWED = 405
  CODE_500_INTERNAL_SERVER_ERROR = 500
  CODE_501_NOT_IMPLEMENTED = 501

  def __init__(self, code: int, reason: str, data: Any, debug: dict):
    super(QxResult, self).__init__()
    self._code = self._process_code(code)
    self._reason = self._process_reason(reason, self._code)
    self._message = self._process_message(self._reason)
    self._data = self._process_data(data)
    self._debug = self._process_debug(debug)

  @classmethod
  def mk_code(cls, reason: Optional[str] = None) -> int:
    conf = QxGlobalConf()
    return conf.code.get(reason, cls.CODE_500_INTERNAL_SERVER_ERROR)

  @classmethod
  def mk_reason(cls, code: Optional[int] = None) -> str:
    conf = QxGlobalConf()
    return conf.code.get(code, conf.code.get(cls.CODE_500_INTERNAL_SERVER_ERROR))

  @classmethod
  def mk_message(cls, reason: Optional[str] = None, code: Optional[int] = None):
    conf = QxGlobalConf()
    reason = reason if isinstance(reason, str) and reason else cls.mk_reason(code)
    return conf.i18n.get(reason, reason)

  @classmethod
  def _process_code(cls, code: Optional[int] = None) -> int:
    return QxValue(code).to_int(cls.CODE_500_INTERNAL_SERVER_ERROR)

  @classmethod
  def _process_reason(cls, reason: Optional[str] = None, code: Optional[int] = None) -> str:
    if isinstance(reason, str) and reason:
      ret = reason
    else:
      ret = cls.mk_reason(code)
    return ret

  @classmethod
  def _process_message(cls, reason: Optional[str] = None, code: Optional[int] = None) -> str:
    return cls.mk_message(reason, code)

  @staticmethod
  def _process_data(data: Any) -> Any:
    return data

  @staticmethod
  def _process_debug(debug: dict) -> dict:
    return debug

  @property
  def code(self) -> int:
    return self._code

  @property
  def reason(self) -> str:
    return self._reason

  @property
  def message(self) -> str:
    return self._message

  @property
  def data(self) -> Any:
    return self._data

  @property
  def debug(self) -> Union[dict, None]:
    return self._debug

  def __bool__(self):
    return self._code == 0

  def to_dict(self):
    ret = {
      'code': self._code,
      'reason': self._reason,
      'message': self._message,
      'data': self._data,
    }
    if QxGlobalConf().is_debug:
      ret['debug'] = self._debug
    return ret

  def __str__(self):
    return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

  def __call__(self):
    raise self


class QxError(QxResult):
  def __init__(self, code: int = None, reason: str = None, data: Any = None, debug: dict = None):
    super(QxError, self).__init__(
      code=code if code != self.CODE_0_OK else self.CODE_500_INTERNAL_SERVER_ERROR,
      reason=reason,
      data=data,
      debug=debug,
    )


class QxFinish(QxResult):
  def __init__(self, data: Any = None, reason: str = None, debug: dict = None):
    super(QxFinish, self).__init__(
      code=0,
      reason=reason,
      data=data,
      debug=debug,
    )

################################################################################


class QxHttpResult(QxFinish):
  def __init__(self, status_code: int = 200, content: Union[str, bytes, dict] = '', headers: Optional[dict] = None, cookies: Optional[dict] = None):
    super(QxHttpResult, self).__init__(data={
      'status_code': status_code,
      'content': content,
      'headers': headers if isinstance(headers, dict) else dict(),
      'cookies': cookies if isinstance(cookies, dict) else dict(),
    })

  @property
  def code(self):
    return self.data['status_code']

  @property
  def content(self):
    return self.data['content']

  @property
  def headers(self):
    return self.data['headers']

  @property
  def cookies(self):
    return self.data['cookies']

  def set_header(self, name: str, value: str):
    self.data['headers'][name] = value
    return self

  def set_cookie(self, name: str, value: Optional[str]):
    self.data['cookies'][name] = value
    return self


class QxStatic(QxHttpResult):
  def __init__(self, path: str):
    super(QxStatic, self).__init__(content=path)


class QxRedirect(QxHttpResult):
  def __init__(self, url):
    super(QxRedirect, self).__init__(
      status_code=302,
      headers={
        'Location': url,
      }
    )


class QxHtml(QxHttpResult):
  def __init__(self, html, content_type: str = 'text/html', status_code: int = 200):
    super(QxHtml, self).__init__(
      status_code=status_code,
      content=html,
      headers={
        'Content-Type': content_type,
      },
    )


class QxTemplate(QxHttpResult):
  def __init__(self, name: str, args: Any = None, status_code: int = 200):
    super(QxTemplate, self).__init__(
      status_code=status_code,
      content={
        'name': name,
        'args': args,
      },
    )
