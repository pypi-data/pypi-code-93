from typing import *

import importlib
import inspect


class QxInspectUtils(object):
  @staticmethod
  def get_method_class(method: Callable) -> Optional[Type]:
    ret = None

    if method.__class__.__name__ in ('function', 'method') and method.__qualname__ != method.__name__:
      try:
        mod = importlib.import_module(method.__module__)
        cls_name = method.__qualname__[:-len(method.__name__) - 1]
        cls = getattr(mod, cls_name, None)
        if cls is not None and isinstance(cls, type):
          ret = cls
      except ModuleNotFoundError as e:
        import traceback
        traceback.print_exc()
        pass
    return ret

  @staticmethod
  def is_static_method(method: Callable) -> bool:
    args = inspect.getfullargspec(method).args
    return not len(args) or args[0] not in ('cls', 'self')

  @staticmethod
  def is_class_method(method: Callable) -> bool:
    args = inspect.getfullargspec(method).args
    return len(args) and args[0] == 'cls'

  @staticmethod
  def is_inst_method(method: Callable) -> bool:
    args = inspect.getfullargspec(method).args
    return len(args) and args[0] == 'self'
