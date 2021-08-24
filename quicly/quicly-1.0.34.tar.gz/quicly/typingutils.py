from typing import *

from quicly.cache import QxCache

import threading


QX_FUNCTION_TYPE = type(lambda: None)


class QxTyping(object):
  def check_typing(self, v: Any) -> bool:
    raise NotImplementedError()

  def assert_typing(self, v: Any) -> NoReturn:
    assert self.check_typing(v)


class QxCustomTyping(QxTyping):
  def __init__(self, t: Type):
    self.t = t

  def check_typing(self, v: Any) -> bool:
    ret = False

    if self.t is None and v is None:
      ret = True
    elif isinstance(self.t, type) and isinstance(v, self.t):
      ret = True
    elif isinstance(self.t, QxTyping):
      ret = self.t.check_typing(v)

    return ret


class _QxCoreTyping(QxTyping):
  _lock = threading.Lock()
  _inst = None

  @classmethod
  def __new__(cls, *a, **kw):
    if not isinstance(cls._inst, cls):
      with cls._lock:
        if not isinstance(cls._inst, cls):
          cls._inst = super().__new__(cls)
    return cls._inst

  def check_typing(self, v: Any) -> bool:
    raise NotImplementedError()


class QxAnyTyping(_QxCoreTyping):
  def check_typing(self, v: Any) -> bool:
    return True


class QxNoneTyping(_QxCoreTyping):
  def check_typing(self, v: Any) -> bool:
    return v is None


class QxBoolTyping(_QxCoreTyping):
  def check_typing(self, v: Any) -> bool:
    return isinstance(v, bool)


class QxIntTyping(_QxCoreTyping):
  def check_typing(self, v: Any) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


class QxFloatTyping(_QxCoreTyping):
  def check_typing(self, v: Any) -> bool:
    return isinstance(v, float)


class QxStrTyping(_QxCoreTyping):
  def check_typing(self, v: Any) -> bool:
    return isinstance(v, str)


class QxListTyping(QxTyping):
  def __init__(self, e: Optional[QxTyping] = None):
    self.e = e

  def check_typing(self, v: Any) -> bool:
    if isinstance(v, (tuple, list, set)):
      ret = True
      if isinstance(self.e, QxTyping):
        for i in v:
          if not self.e.check_typing(i):
            ret = False
            break
    else:
      ret = False
    return ret


class QxDictTyping(QxTyping):
  def __init__(self, k: Optional[QxTyping] = None, v: Optional[QxTyping] = None):
    self.k = k
    self.v = v

  def check_typing(self, v: Any) -> bool:
    if isinstance(v, dict):
      ret = True
      if isinstance(self.k, QxTyping) or isinstance(self.v, QxTyping):
        if isinstance(self.k, QxTyping):
          fk = lambda x: self.k.check_typing(x)
        else:
          fk = lambda x: True

        if isinstance(self.v, QxTyping):
          fv = lambda x: self.v.check_typing(x)
        else:
          fv = lambda x: True

        for ik, iv in v.items():
          if not (fk(ik) and fv(iv)):
            ret = False
            break
    else:
      ret = False
    return ret


class QxFunctionTyping(QxTyping):
  def __init__(self):
    super(QxFunctionTyping, self).__init__()

  def check_typing(self, v: Any) -> bool:
    return isinstance(v, QX_FUNCTION_TYPE)


class QxOptionalTyping(QxTyping):
  def __init__(self, e: QxTyping):
    self.e = e

  def check_typing(self, v: Any) -> bool:
    ret = False

    if v is None:
      ret = True
    elif isinstance(self.e, type) and isinstance(v, self.e):
      ret = True

    return ret


class QxUnionTyping(QxTyping):
  def __init__(self, el: List[QxTyping]):
    self.el = el

  def match(self, v: Any) -> QxTyping:
    ret = None

    for e in self.el:
      if e.check_typing(v):
        ret = e
        break

    return ret

  def check_typing(self, v: Any) -> bool:
    return isinstance(self.match(v), QxTyping)


class QxTypingCache(QxCache):
  _lock = threading.Lock()
  _inst = None

  @classmethod
  def __new__(cls, *a, **kw):
    if not isinstance(cls._inst, cls):
      with cls._lock:
        if not isinstance(cls._inst, cls):
          cls._inst = super().__new__(cls)
    return cls._inst

  def __init__(self):
    super(QxTypingCache, self).__init__(size=128)


class QxTypingUtils(object):
  @staticmethod
  def is_alias_typing(t: Any) -> bool:
    return str(t).startswith('typing.') or t.__class__.__name__ == 'TypeVar'

  @staticmethod
  def is_basic_typing(t: Any) -> bool:
    return t is None or isinstance(t, type)

  @staticmethod
  def parse_typing(t: Any) -> QxTyping:
    cache = QxTypingCache()

    ret = QxAnyTyping()

    if isinstance(t, QxTyping):
      ret = t
    elif QxTypingUtils.is_alias_typing(t):
      fullname = str(t)
      if fullname.startswith('typing.'):
        name = fullname[7:].split('[', maxsplit=1)[0]
      else:
        name = t.__class__.__name__

      origin = getattr(t, '__origin__', None)
      args = getattr(t, '__args__', ())

      args_i = lambda i: QxTypingUtils.parse_typing(args[i]) if isinstance(args, (tuple, list)) and len(args) >= i + 1 else None
      args_t = lambda: [QxTypingUtils.parse_typing(arg) for arg in args] if isinstance(args, (tuple, list)) else []

      ret = cache.get(fullname)
      if not isinstance(ret, QxTyping):
        if name == 'Optional':
          ret = QxOptionalTyping(e=args_i(0))
        elif name == 'Union':
          ret = QxUnionTyping(el=args_t())
        elif name in ('List', 'Tuple'):
          ret = QxListTyping(e=args_i(0))
        elif name == 'Dict':
          ret = QxDictTyping(k=args_i(0), v=args_i(1))
        elif name == 'Text':
          ret = QxStrTyping()
        elif name == 'TypeVar':
          ret = QxAnyTyping()
        elif name in ('Callable', 'Function'):
          ret = QxFunctionTyping()
        else:
          ret = QxTypingUtils.parse_typing(origin)
        cache.set(fullname, ret)

    elif QxTypingUtils.is_basic_typing(t):
      if t is None or isinstance(t, type) and isinstance(None, t):
        ret = QxNoneTyping()
      elif t is bool:
        ret = QxBoolTyping()
      elif t is int:
        ret = QxIntTyping()
      elif t is float:
        ret = QxFloatTyping()
      elif t is str:
        ret = QxStrTyping()
      elif t is list or t is tuple:
        ret = QxListTyping()
      elif t is dict:
        ret = QxDictTyping()

    return ret

  @staticmethod
  def check_typing(v: Any, t: Any) -> bool:
    return QxTypingUtils.parse_typing(t).check_typing(v)

  @staticmethod
  def assert_typing(v: Any, t: Any) -> NoReturn:
    assert QxTypingUtils.parse_typing(t).assert_typing(v)
