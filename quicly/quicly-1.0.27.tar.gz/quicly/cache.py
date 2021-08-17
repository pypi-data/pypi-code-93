from typing import *

from collections import OrderedDict


class QxCache(object):
  def __init__(self, size: int = 1024):
    self._size = size
    self._pool = OrderedDict()

  @property
  def size(self) -> int:
    return self._size

  @property
  def pool(self) -> OrderedDict:
    return self._pool

  def _refresh(self, k: str):
    if k in self.pool:
      self.pool.move_to_end(k, last=False)

  def _gc(self):
    if isinstance(self.size, int) and self.size > 0:
      while len(self.pool) > self.size:
        self.pool.popitem(last=True)

  def set(self, k: str, v: Any) -> None:
    self.pool[k] = v
    self._refresh(k)
    self._gc()

  def get(self, k: str, default: Any = None) -> Any:
    self._refresh(k)
    return self.pool.get(k, default)

  def has(self, k: str) -> bool:
    return k in self.pool

  def clear(self) -> None:
    self.pool.clear()

  def __contains__(self, k: str):
    return self.has(k)

  def __setitem__(self, k: str, v: Any):
    self.set(k, v)

  def __getitem__(self, k: str) -> Any:
    return self.get(k)

  def __str__(self):
    return f'{self.__class__.__name__}{str(self.pool)[len(self.pool.__class__.__name__):]}'
