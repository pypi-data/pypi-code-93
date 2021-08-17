# deprecate
from typing import Callable, Dict, Optional, Tuple, TypeVar, Union

import sys
import json

from io import IOBase
from io import StringIO

from nonion.tools import Option
from nonion.tools import wraptry

X = TypeVar("X")

BufferLoader = Callable[[IOBase, Tuple[object, ...], Dict[str, object]], X]
Loader = Callable[[Optional[str], Tuple[object, ...], Dict[str, object]], Option[X]]

FROM_STDIN = None

def load(path: Optional[str] = FROM_STDIN) -> IOBase:
  if path is FROM_STDIN:
    return StringIO(sys.stdin.read())

  buffer: Option[IOBase] = wrapopen(path) or (StringIO(),)
  buffer, *_ = buffer

  return buffer

wrapopen: Callable[[str], Option[IOBase]] = wraptry(open)

def as_loader(f: BufferLoader[X]) -> Loader[X]:
  def wrapped(path: Optional[str] = FROM_STDIN, *args: object, **kwargs: object) -> Option[X]:
    g = lambda x: f(x, *args, **kwargs)

    with load(path) as buffer:
      return wraptry(g)(buffer)

  return wrapped

load_json: Loader[Union[Dict[str, object], Tuple[object, ...]]] = as_loader(json.load)
