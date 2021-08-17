from typing import Callable, Deque, Iterable, Iterator, List, Tuple, TypeVar, Union

import operator as op

from collections import deque

from functools import partial
from functools import reduce
from itertools import chain
from itertools import compress
from itertools import count
from itertools import islice
from itertools import product
from itertools import repeat

X = TypeVar("X")
Y = TypeVar("Y")
Z = TypeVar("Z")

Option = Union[Tuple[X], Tuple[()]]
Either = Tuple[Option[X], Option[Y]]

def binary_compose(f: Callable[[Y], Z], g: Callable[[X], Y]) -> Callable[[X], Z]:
  return lambda x: f(g(x))

def curry(f: Callable[..., Y]) -> Callable[..., Y]:
  return lambda *args, **kwargs: partial(f, *args, **kwargs)

lift = curry(map)

def fmap(f: Callable[[X], Y], x: Iterable[X]) -> Tuple[Y, ...]:
  return binary_compose(tuple, lift(f))(x)

def bind(f: Callable[[X], Iterable[Y]], x: Iterable[X]) -> Tuple[Y, ...]:
  ys: Iterable[Iterable[Y]] = map(f, x)
  y: Iterable[Y] = chain.from_iterable(ys)

  return tuple(y)

def wraptry(f: Callable[..., Y], *args: object, **kwargs: object) -> Callable[..., Option[Y]]:
  def g(*args_: object, **kwargs_: object) -> Option[Y]:
    try:
      return (f(*args, *args_, **{**kwargs, **kwargs_}),)
    except:
      return ()

  return g

def wrapexcept(f: Callable[..., Y], *args: object, **kwargs: object) -> Callable[..., Either[Exception, Y]]:
  def g(*args_: object, **kwargs_: object) -> Either[Exception, Y]:
    try:
      y = f(*args, *args_, **{**kwargs, **kwargs_})
      return (), (y,)
    except Exception as e:
      return (e,), ()

  return g

@curry
def maptry(f: Callable[[X], Y], xs: Iterable[X]) -> Iterable[Y]:
  ys: Iterable[Option[Y]] = map(wraptry(f), xs)
  return chain.from_iterable(ys)

wrapnext: Callable[[Iterator[X]], Option[X]] = wraptry(next)

def wrapeek(xs: Iterable[X]) -> Tuple[Option[X], Iterable[X]]:
  xs = iter(xs)
  x = wrapnext(xs)

  return x, chain(x, xs)

@curry
def iterfind(ps: Iterable[Callable[[X], bool]], xs: Iterable[X]) -> Iterable[Option[X]]:
  xs = iter(xs)
  buffer = []

  for p in ps:
    x = find(p)(buffer)

    if not x:
      x, buffer = find_and_collect(p, xs, buffer)

    yield x

@curry
def find(p: Callable[[X], bool], xs: Iterable[X]) -> Option[X]:
  xs = filter(p, xs)
  return wrapnext(xs)

def find_and_collect(
  p: Callable[[X], bool],
  xs: Iterator[X],
  buffer: List[X]
  ) -> Tuple[Option[X], List[X]]:

  x = wrapnext(xs)

  while x:
    buffer.extend(x)

    if p(*x):
      return x, buffer

    x = wrapnext(xs)

  return (), buffer

@curry
def findindex(p: Callable[[X], bool], xs: Iterable[X]) -> Option[int]:
  return wrapnext(where(p)(xs))

def first(xy: Tuple[X, Y]) -> X:
  return xy[0]

def second(xy: Tuple[X, Y]) -> Y:
  return xy[1]

def slide(
  n: int = 2,
  step: int = 1,
  exact: bool = False
  ) -> Callable[[Iterable[X]], Iterable[Tuple[X, ...]]]:

  p = (lambda w: len(w) == n) if exact else (lambda w: len(w) > 0)

  def g(xs: Iterable[X]) -> Iterable[Tuple[X, ...]]:
    xs = iter(xs)

    window = islice(xs, n)
    window = tuple(window)

    while p(window):
      yield window

      window = chain(window[step:], islice(xs, step))
      window = tuple(window)

  return g

def take(n: int) -> Callable[[Iterable[X]], Iterable[X]]:
  return lambda xs: islice(xs, n)

def drop(n: int) -> Callable[[Iterable[X]], Iterable[X]]:
  return lambda xs: islice(xs, n, None)

def cache(f: Callable[..., Y], *args: object, **kwargs: object) -> Callable[..., Y]:
  f = partial(f, *args, **kwargs)

  def cached() -> Iterable[Y]:
    args_, kwargs_ = yield
    y = f(*args_, **kwargs_)

    while True:
      yield y

  cached = cached()
  next(cached)

  def g(*args_: object, **kwargs_: object) -> Y:
    return cached.send((args_, kwargs_))

  return g

def shift(f: Callable[..., Y], *args: object, **kwargs: object) -> Callable[..., Y]:
  return lambda *args_, **kwargs_: f(*args_, *args,  **{**kwargs_, **kwargs})

def key(f: Callable[[X], Z]) -> Callable[[Tuple[X, Y]], Tuple[Z, Y]]:
  g: Callable[[Tuple[X, Y]], Z] = binary_compose(f, first)
  return lambda xy: (g(xy), second(xy))

def value(f: Callable[[Y], Z]) -> Callable[[Tuple[X, Y]], Tuple[X, Z]]:
  g: Callable[[Tuple[X, Y]], Z] = binary_compose(f, second)
  return lambda xy: (first(xy), g(xy))

def flip(f: Callable[[Y, X], Z]) -> Callable[[X, Y], Z]:
  return lambda x, y: f(y, x)

@curry
def foldl(f: Callable[[Y, X], Y], acc: Y, xs: Iterable[X]) -> Y:
  return reduce(f, xs, acc)

@curry
def foldr(f: Callable[[X, Y], Y], acc: Y, xs: Iterable[X]) -> Y:
  return foldl(flip(f), acc)(reversed(tuple(xs)))

@curry
def foldl1(f: Callable[[X, X], X], xs: Iterable[X]) -> X:
  return reduce(f, xs)

@curry
def foldr1(f: Callable[[X, X], X], xs: Iterable[X]) -> X:
  return foldl1(flip(f))(reversed(tuple(xs)))

@curry
def scanl(f: Callable[[Y, X], Y], acc: Y, xs: Iterable[X]) -> Iterable[Y]:
  yield acc

  for x in xs:
    acc = f(acc, x)
    yield acc

@curry
def scanr(f: Callable[[X, Y], Y], acc: Y, xs: Iterable[X]) -> Deque[Y]:
  def g(x: X, acc_: Deque[Y]) -> Deque[Y]:
    acc_.appendleft(f(x, acc_[0]))
    return acc_

  return foldr(g, deque([acc]))(xs)

@curry
def scanl1(f: Callable[[X, X], X], xs: Iterable[X]) -> Iterable[X]:
  xs = iter(xs)
  acc = wrapnext(xs)

  if acc: return scanl(f, *acc)(xs)
  else: return ()

@curry
def scanr1(f: Callable[[X, X], X], xs: Iterable[X]) -> Deque[X]:
  xs = tuple(xs)

  if len(xs) > 0: return scanr(f, xs[-1])(xs[:-1])
  else: return deque()

def zipl(xs: Iterable[X]) -> Callable[[Iterable[Y]], Iterable[Tuple[X, Y]]]:
  return lambda ys: zip(xs, ys)

def zipr(ys: Iterable[Y]) -> Callable[[Iterable[X]], Iterable[Tuple[X, Y]]]:
  return lambda xs: zip(xs, ys)

def flattenl(xyz: Tuple[Tuple[X, Y], Z]) -> Tuple[X, Y, Z]:
  (*xy,), *z = xyz
  return (*xy, *z)

def flattenr(xyz: Tuple[X, Tuple[Y, Z]]) -> Tuple[X, Y, Z]:
  *x, (*yz,) = xyz
  return (*x, *yz)

def zipmapl(f: Callable[[X], Y]) -> Callable[[Iterable[X]], Iterable[Tuple[Y, X]]]:
  return lambda xs: map(lambda x: (f(x), x), xs)

def zipmapr(f: Callable[[X], Y]) -> Callable[[Iterable[X]], Iterable[Tuple[X, Y]]]:
  return lambda xs: map(lambda x: (x, f(x)), xs)

def call(fx: Tuple[Callable[..., Y], Tuple[object, ...]]) -> Y:
  f, *x = fx
  return f(*x)

def as_match(xys: Iterable[Tuple[X, Y]]) -> Callable[[X], Option[Y]]:
  x_to_y = dict(xys)

  def lookup(x: X) -> Option[Y]:
    return (x_to_y[x],) if x in x_to_y else ()

  return lookup

def match(*fs: Callable[[X], Option[Y]]) -> Callable[[X], Option[Y]]:
  def g(x: X) -> Option[Y]:
    mys = map(lambda f: f(x), fs)
    filtered_ys = filter(lambda y: y, mys)
    ys = map(first, filtered_ys)

    return wrapnext(ys)

  return g

def catch(*fs: Callable[[X], Option[Y]], default: Callable[[X], Y]) -> Callable[[X], Y]:
  f = match(*fs)

  def g(x: X) -> Y:
    y, *_ = f(x) or (default(x),)
    return y

  return g

def stripby(f: Callable[[X, X], bool]) -> Callable[[Iterable[X]], Iterable[X]]:
  return binary_compose(lift(first), groupby(f))

def groupby(f: Callable[[X, X], bool]) -> Callable[[Iterable[X]], Iterable[Tuple[X, ...]]]:
  h: Callable[[X], Callable[[X], bool]] = curry(f)

  def g(xs: Iterable[X]) -> Iterable[Tuple[X, ...]]:
    xs = iter(xs)
    mp = wrapnext(xs)

    while mp:
      p, *_ = mp

      group, xs = span(h(p))(xs)
      yield mp + group

      mp = wrapnext(xs)

  return g

@curry
def span(p: Callable[[X], bool], xs: Iterable[X]) -> Tuple[Tuple[X, ...], Iterable[X]]:
  xs = iter(xs)
  x = wrapnext(xs)

  matched = []

  while x:
    if p(*x):
      matched.extend(x)
      x = wrapnext(xs)
    else:
      break

  return tuple(matched), chain(x, xs)

strip: Callable[[Iterable[X]], Iterable[X]] = stripby(op.eq)
group: Callable[[Iterable[X]], Iterable[Tuple[X, ...]]] = groupby(op.eq)

def on(f: Callable[[Y, Y], Z], g: Callable[[X], Y]) -> Callable[[X, X], Z]:
  return lambda p, n: f(g(p), g(n))

@curry
def partition(p: Callable[[X], bool], xs: Iterable[X]) -> Tuple[Tuple[X, ...], Tuple[X, ...]]:
  ts, fs = [], []

  for x in xs:
    if p(x): ts.append(x)
    else: fs.append(x)

  return tuple(ts), tuple(fs)

def powerset(xs: Tuple[X, ...]) -> Iterable[Iterable[X]]:
  ys = map(lambda _: range(2), range(len(xs)))
  return map(partial(compress, xs), product(*ys))

def between(low: float, high: float) -> Callable[[float], bool]:
  return lambda x: low <= x and x <= high

def in_(xs: Tuple[X, ...]) -> Callable[[X], bool]:
  return lambda x: x in xs

length: Callable[[Iterable[X]], int] = foldl(lambda acc, _: acc + 1, 0)

def not_(p: Callable[..., bool], *args: object, **kwargs: object) -> Callable[..., bool]:
  return lambda *args_, **kwargs_: not p(*args, *args_, **{**kwargs, **kwargs_})

def zipflatl(f: Callable[[X], Option[Y]]) -> Callable[[Iterable[X]], Iterable[Tuple[Y, X]]]:
  def g(xs: Iterable[X]) -> Iterable[Tuple[Y, X]]:
    ys = zipmapl(f)(xs)
    zs = filter(first, ys)

    return map(key(first), zs)

  return g

def zipflatr(f: Callable[[X], Option[Y]]) -> Callable[[Iterable[X]], Iterable[Tuple[X, Y]]]:
  def g(xs: Iterable[X]) -> Iterable[Tuple[X, Y]]:
    ys = zipmapr(f)(xs)
    zs = filter(second, ys)

    return map(value(first), zs)

  return g

@curry
def as_catch(default: Callable[[X], Y], xys: Iterable[Tuple[X, Y]]) -> Callable[[X], Y]:
  return catch(as_match(xys), default=default)

@curry
def as_either(y: Callable[[], Y], x: Option[X]) -> Either[Y, X]:
  if x: return (), x
  else: return (y(),), ()

@curry
def left(f: Callable[[X], Z], xy: Either[X, Y]) -> Either[Z, Y]:
  x, y = xy
  return fmap(f, x), y

@curry
def right(f: Callable[[Y], Z], xy: Either[X, Y]) -> Either[X, Z]:
  x, y = xy
  return x, fmap(f, y)

@curry
def fleft(f: Callable[[Z], X], xzy: Either[X, Either[Z, Y]]) -> Either[X, Y]:
  x, zy = xzy

  if x:
    return x, ()
  else:
    (z, y), *_ = zy
    return fmap(f, z), y

def tee(f: Callable[..., None], *args: object, **kwargs: object) -> Callable[..., X]:
  def g(x: X, *args_: object, **kwargs_: object) -> object:
    f(*args, x, *args_, **{**kwargs, **kwargs_})
    return x

  return g

@curry
def splitat(i: int, xs: Iterable[X]) -> Tuple[Tuple[X, ...], Iterable[X]]:
  xs = iter(xs)
  return tuple(islice(xs, i)), xs

def reverse(xs: Iterable[X]) -> Deque[X]:
  def g(acc: Deque[X], x: X) -> Deque[X]:
    acc.appendleft(x)
    return acc

  return foldl(g, deque())(xs)

@curry
def replicate(n: int, x: X) -> Iterable[X]:
  return take(n)(repeat(x))

@curry
def search(p: Callable[[X], bool], ys: Iterable[Y], xs: Iterable[X]) -> Iterable[Y]:
  filtered = filter(binary_compose(p, second), zip(ys, xs))
  return map(first, filtered)

@curry
def where(p: Callable[[X], bool], xs: Iterable[X]) -> Iterable[int]:
  return search(p, count())(xs)

def fail(
  m: Callable[[Exception], Y],
  *args: object,
  **kwargs: object
  ) -> Callable[[Callable[..., Y]], Callable[..., Y]]:

  def g(f: Callable[..., Y], *args_: object, **kwargs_: object) -> Callable[..., Y]:
    def h(*args__: object, **kwargs__: object) -> Y:
      try:
        return f(*args, *args_, *args__, **{**kwargs, **kwargs_, **kwargs__})
      except Exception as e:
        return m(e)

    return h

  return g

def pickby(
  f: Callable[[X], Y],
  agg: Callable[[Tuple[Y, ...]], Y],
  compare: Callable[[Y, Y], bool] = op.eq
  ) -> Callable[[Iterable[X]], Iterable[X]]:

  @fail(lambda _: ())
  def g(xs: Iterable[X]) -> Iterable[X]:
    xs = tuple(xs)
    ys = tuple(map(f, xs))
    y = agg(ys)

    p = binary_compose(lambda z: compare(y, z), second)
    return map(first, filter(p, zip(xs, ys)))

  return g

def pick(
  agg: Callable[[Tuple[X, ...]], X],
  compare: Callable[[X, X], bool] = op.eq
  ) -> Callable[[Iterable[X]], Iterable[X]]:

  return pickby(lambda x: x, agg, compare)

def merge(
  xs: Iterable[X],
  ys: Iterable[X],
  compare: Callable[[X, X], bool] = op.le
  ) -> Iterable[X]:

  xs = iter(xs)
  ys = iter(ys)

  mx = wrapnext(xs)
  my = wrapnext(ys)

  while mx and my:
    (x, *_), (y, *_) = mx, my

    if compare(x, y):
      yield x
      mx = wrapnext(xs)
    else:
      yield y
      my = wrapnext(ys)

  while mx:
    x, *_ = mx
    yield x
    mx = wrapnext(xs)

  while my:
    y, *_ = my
    yield y
    my = wrapnext(ys)

def padl(n: int, x: X, exact: bool = False) -> Callable[[Iterable[X]], Iterable[X]]:
  if exact:
    g = lambda xs: chain(replicate(n)(x), xs)
  else:
    def g(xs: Iterable[X]) -> Iterable[X]:
      ys = tuple(xs)
      return chain(replicate(n - len(ys))(x), ys)

  return g

def padr(n: int, x: X, exact: bool = False) -> Callable[[Iterable[X]], Iterable[X]]:
  if exact:
    g = lambda xs: chain(xs, replicate(n)(x))
  else:
    def g(xs: Iterable[X]) -> Iterable[X]:
      ys = tuple(xs)
      return chain(ys, replicate(n - len(ys))(x))

  return g
