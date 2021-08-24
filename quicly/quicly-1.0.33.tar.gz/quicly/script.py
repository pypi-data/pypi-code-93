from typing import *

from quicly.value import QxValue

from collections import OrderedDict


class QxScriptContext(object):
  def __init__(self, parent: None):
    assert parent is None or isinstance(parent, QxScriptContext)
    self.parent = parent
    self.vars = OrderedDict()

  def set(self, name: str, value: Any) -> NoReturn:
    self.vars[name] = QxValue(value)

  def has(self, name: str, local: bool = False) -> bool:
    if name in self.vars:
      ret = True
    elif not local and self.parent:
      ret = self.parent.has(name, local)
    else:
      ret = False
    return ret

  def get(self, name: str, default: Any = None, local: bool = False) -> QxValue:
    if name in self.vars:
      ret = self.vars.get(name, default)
    elif not local and self.parent:
      ret = self.parent.get(name, default)
    else:
      ret = default
    return QxValue(ret)

  def delete(self, name: str, local: bool = True) -> bool:
    if name in self.vars:
      del self.vars[name]
      ret = True
    elif not local and self.parent:
      ret = self.parent.delete(name, local)
    else:
      ret = False
    return ret
