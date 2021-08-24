from typing import *

import os
import json
import threading


class QxConf(dict):
  _ns = None
  _parent = None

  def __init__(self, ns: str = None, parent: object = None, *a, **kw):
    super(QxConf, self).__init__(*a, **kw)

    self.ns = ns
    self.parent = parent

  @property
  def ns(self) -> str:
    return self._ns

  @ns.setter
  def ns(self, ns: str):
    self._ns = ns.upper() if isinstance(ns, str) else ''

  @property
  def parent(self):
    return self._parent  # type: QxConf

  @parent.setter
  def parent(self, parent: object = None):
    self._parent = parent if isinstance(parent, QxConf) else None

  def update_from_json(self, json_str: str):
    try:
      self.update(json.loads(json_str))
    except (json.JSONDecodeError, TypeError, ValueError):
      pass
    return self

  def update_from_file(self, path: str, encoding: str = 'utf-8'):
    if os.path.isfile(path):
      with open(path, 'r+', encoding=encoding) as fo:
        self.update_from_json(fo.read())
    return self

  def write_to_file(self, path: str, encoding: str = 'utf-8'):
    d = os.path.dirname(path)
    if not os.path.isdir(d):
      os.makedirs(d)
    with open(path, 'w+', encoding=encoding) as fo:
      fo.write(json.dumps(self, indent=2, ensure_ascii=False))

  def pprint(self):
    print(json.dumps(self, indent=2, ensure_ascii=False))

  @staticmethod
  def mk_env_k(*items):
    return '_'.join([x.strip() for x in items if isinstance(x, str) and x.strip()]).upper()

  def get(self, k, default: Any = None, check: Callable = None) -> Any:
    if isinstance(self.parent, QxConf):
      default = self.parent.get(k, default=default, check=check)

    v = super(QxConf, self).get(k, os.environ.get(self.mk_env_k(self.ns, k), default))

    if callable(check) and not check(v):
      v = default

    if isinstance(v, dict):
      v = QxConf(self.mk_env_k(self.ns, k), v.items())

    return v

  @staticmethod
  def is_true(v: Any) -> bool:
    if isinstance(v, bool):
      ret = v is True
    elif isinstance(v, str):
      ret = v.upper() in ('TRUE', 'T', 'YES', 'Y', 'ON')
    elif isinstance(v, int):
      ret = v == 1
    else:
      ret = False
    return ret

  @staticmethod
  def is_false(v: Any) -> bool:
    if isinstance(v, bool):
      ret = v is False
    elif isinstance(v, str):
      ret = v.upper() in ('FALSE', 'F', 'NO', 'N', 'OFF')
    elif isinstance(v, int):
      ret = v == 0
    else:
      ret = False
    return ret

  @staticmethod
  def is_not_true(v: Any) -> bool:
    return not QxConf.is_true(v)

  @staticmethod
  def is_not_false(v: Any) -> bool:
    return not QxConf.is_false(v)


class QxGlobalConf(QxConf):
  _lock = threading.Lock()
  _inst = None

  def __new__(cls, *a, **kw):
    if not isinstance(cls._inst, cls):
      with cls._lock:
        if not isinstance(cls._inst, cls):
          cls._inst = super().__new__(cls)
    return cls._inst

  def __init__(self):
    super(QxGlobalConf, self).__init__('QX')
    self._root = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'conf')

    self._i18n = QxConf()
    self._i18n.update_from_file(os.path.join(self._root, 'i18n', 'zh-cn.json'))

    self._code = QxConf()

    code = QxConf()
    code.update_from_file(os.path.join(self._root, 'code.json'))
    for k, v in code.items():
      k = int(k)
      v = str(v)
      self._code[k] = v
      self._code[v] = k

  @property
  def i18n(self):
    return self._i18n

  @property
  def code(self):
    return self._code

  @property
  def charset(self):
    return self.get('charset', 'utf-8')

  @property
  def is_debug(self) -> bool:
    return self.is_true(self.get('debug'))
