from typing import *

from quicly.value import QxValue
from quicly.limits import *


class QxAttr(object):
  def __init__(self):
    super(QxAttr, self).__init__()

  def check(self, v: Any) -> bool:
    raise NotImplementedError()

  def value(self, v: Any, default: Any = None) -> Any:
    raise NotImplementedError()


class QxAny(QxAttr):
  def check(self, v: Any) -> bool:
    return True

  def value(self, v: Any, default: Any = None) -> Any:
    return v


class QxOptional(QxAttr):
  def __init__(self, element: QxAttr, default: Any = None):
    super(QxOptional, self).__init__()
    assert isinstance(element, QxAttr)
    self._element = element
    self._default = default

  @property
  def element(self) -> QxAttr:
    return self._element

  @property
  def default(self) -> Any:
    return self._default

  def check(self, v: Any) -> bool:
    v = QxValue.create(v)
    return v.is_none() or self.element.check(v)

  def value(self, v: Any, default: Any = None) -> Any:
    return self.element.value(v, default=default)


class QxUnion(QxAttr):
  def __init__(self, elements: List[QxAttr]):
    super(QxUnion, self).__init__()
    self._elements = elements

  @property
  def elements(self) -> List[QxAttr]:
    return self._elements

  def match(self, v: Any) -> QxAttr:
    ret = None

    for elem in self.elements:
      if elem.check(v):
        ret = elem
        break

    return ret

  def check(self, v: Any) -> bool:
    elem = self.match(v)

    return isinstance(elem, QxAttr)

  def value(self, v: Any, default: Any = None) -> Any:
    elem = self.match(v)

    if isinstance(elem, QxAttr):
      ret = elem.value(v, default)
    else:
      ret = default

    return ret


class QxBool(QxAttr):
  def check(self, v: Any) -> bool:
    return QxValue.create(v).is_bool()

  def value(self, v: Any, default: Optional[bool] = None) -> bool:
    return QxValue.create(v).to_bool(default=default)


class QxInt(QxAttr):
  LIMITS_MAX = sys.maxsize
  LIMITS_MIN = -LIMITS_MAX - 1

  def __init__(self, limits: Optional[Tuple[Optional[int], Optional[int]]] = None):
    super(QxInt, self).__init__()
    limits = list(limits) if isinstance(limits, (tuple, list)) and len(limits) == 2 else [self.LIMITS_MIN, self.LIMITS_MAX]
    limits[0] = max(limits[0], self.LIMITS_MIN) if isinstance(limits[0], int) else self.LIMITS_MIN
    limits[1] = min(limits[1], self.LIMITS_MAX) if isinstance(limits[1], int) else self.LIMITS_MAX
    self._limits = (limits[0], limits[1])

  @property
  def limits(self) -> Tuple[int, int]:
    return self._limits

  @property
  def limits_min(self) -> int:
    return self._limits[0]

  @property
  def limits_max(self) -> int:
    return self._limits[1]

  def check(self, v: Any) -> bool:
    v = QxValue.create(v)
    return v.is_int() and self.limits_min <= v.int_value <= self.limits_max

  def value(self, v: Any, default: Optional[int] = None) -> int:
    return QxValue.create(v).to_int(default=default)


class QxInt32(QxInt):
  LIMITS_MAX = INT32_MAX
  LIMITS_MIN = INT32_MIN


class QxInt64(QxInt):
  LIMITS_MAX = INT64_MAX
  LIMITS_MIN = INT64_MIN


class QxUint32(QxInt):
  LIMITS_MAX = UINT32_MAX
  LIMITS_MIN = UINT32_MIN


class QxUint64(QxInt):
  LIMITS_MAX = UINT64_MAX
  LIMITS_MIN = UINT64_MIN


class QxFloat(QxAttr):
  LIMITS_MAX = float('inf')
  LIMITS_MIN = float('-inf')
  EPSILON = FLOAT64_EPSILON

  def __init__(self, limits: Optional[Tuple[Optional[float], Optional[float]]] = None):
    super(QxFloat, self).__init__()
    limits = list(limits) if isinstance(limits, (tuple, list)) and len(limits) == 2 else [self.LIMITS_MIN, self.LIMITS_MAX]
    limits[0] = max(limits[0], self.LIMITS_MIN - self.EPSILON) if isinstance(limits[0], float) else self.LIMITS_MIN
    limits[1] = min(limits[1], self.LIMITS_MAX + self.EPSILON) if isinstance(limits[1], float) else self.LIMITS_MAX
    self._limits = (limits[0], limits[1])

  @property
  def limits(self) -> Tuple[float, float]:
    return self._limits

  @property
  def limits_min(self) -> float:
    return self._limits[0]

  @property
  def limits_max(self) -> float:
    return self._limits[1]

  def check(self, v: Any) -> bool:
    v = QxValue.create(v)
    return v.is_float() and self.limits_min - self.EPSILON <= v.int_value <= self.limits_max + self.EPSILON

  def value(self, v: Any, default: Optional[float] = None) -> float:
    return QxValue.create(v).to_float(default=default)


class QxFloat32(QxFloat):
  LIMITS_MAX = FLOAT32_MAX
  LIMITS_MIN = FLOAT32_MIN
  EPSILON = FLOAT32_EPSILON


class QxFloat64(QxFloat):
  LIMITS_MAX = FLOAT64_MAX
  LIMITS_MIN = FLOAT64_MIN
  EPSILON = FLOAT64_EPSILON


class QxStr(QxAttr):
  def check(self, v: Any) -> bool:
    return QxValue.create(v).is_str()

  def value(self, v: Any, default: Optional[str] = None) -> str:
    return QxValue.create(v).to_str(default=default)


class QxList(QxAttr):
  def __init__(self, element: Optional[QxAttr] = None):
    super(QxList, self).__init__()
    self._element = element if isinstance(element, QxAttr) else None

  @property
  def element(self) -> QxAttr:
    return self._element

  def check(self, v: Any) -> bool:
    v = QxValue.create(v)

    if v.is_list():
      ret = True
      if isinstance(self.element, QxAttr):
        for i in v.list_value:
          if not self.element.check(i):
            ret = False
            break
    else:
      ret = False

    return ret

  def value(self, v: Any, default: Optional[List[Any]] = None) -> List[Any]:
    return QxValue.create(v).to_list(default=default)


class QxDict(QxAttr):
  def __init__(self, element: Optional[QxAttr] = None):
    super(QxDict, self).__init__()
    self._element = element if isinstance(element, QxAttr) else None

  @property
  def element(self):
    return self._element

  def check(self, v: Any) -> bool:
    v = QxValue.create(v)

    if v.is_dict():
      ret = True
      if isinstance(self.element, QxAttr):
        for kk, vv in v.dict_value.items():
          if not self.element.check(vv):
            ret = False
            break
    else:
      ret = False

    return ret

  def value(self, v: Any, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return QxValue.create(v).to_dict(default)
