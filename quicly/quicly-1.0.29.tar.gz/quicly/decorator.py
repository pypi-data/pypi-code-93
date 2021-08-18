from typing import *

import copy


class QxDecoratorHook(object):
  def __init__(self):
    self._al = []
    self._kw = {}
    self._func_check = None
    self._func_target = None

  @property
  def al(self) -> List:
    return self._al

  @property
  def kw(self) -> Dict:
    return self._kw

  def set_func_check(self, func: Callable):
    self._func_check = func

  def set_func_target(self, func: Callable):
    self._func_target = func

  def _check(self, target: Any) -> bool:
    raise NotImplementedError()

  def _target(self, target: Any) -> Any:
    raise NotImplementedError()

  def check(self, target: Any) -> bool:
    if callable(self._func_check):
      return self._func_check(self, target)
    return self._check(target)

  def set_args(self, *al, **kw):
    self._al = copy.copy(al)
    self._kw = copy.copy(kw)

  def arg(self, k: Union[int, str, List[Union[int, str]]], default: Optional[Any] = None) -> Any:
    ret = default
    if isinstance(k, int):
      if len(self.al) > k:
        ret = self.al[k]
    elif isinstance(k, str):
      if k in self.kw:
        ret = self.kw[k]
    elif isinstance(k, list):
      for kk in k:
        if isinstance(kk, int):
          if len(self.al) > kk:
            ret = self.al[kk]
            break
        elif isinstance(kk, str):
          if kk in self.kw:
            ret = self.kw[kk]
            break
    return ret

  def target(self, target: Any) -> Any:
    if callable(self._func_target):
      return self._func_target(self, target)
    return self._target(target)


class QxDecoratorDefaultHook(QxDecoratorHook):
  def _check(self, target: Any) -> bool:
    return True

  def _target(self, target: Any) -> Any:
    return target


def QxDecorator(hook_cls: Optional[Type[QxDecoratorHook]] = None, func_check: Optional[Callable] = None, func_target: Optional[Callable] = None):
  if isinstance(hook_cls, QxDecoratorHook):
    hook_cls = hook_cls.__class__
  elif callable(hook_cls):
    hook_cls = hook_cls

  if not (isinstance(hook_cls, type) and issubclass(hook_cls, QxDecoratorHook)) or hook_cls == QxDecoratorHook:
    hook_cls = QxDecoratorDefaultHook

  def __init__(*al, **kw):
    hook = hook_cls()
    hook.set_func_check(func_check)
    hook.set_func_target(func_target)

    def __target__(target):
      return hook.target(target)

    if len(al) == 1 and hook.check(al[0]) and len(kw) == 0:
      return __target__(al[0])

    hook.set_args(*al, **kw)

    return __target__

  return __init__
