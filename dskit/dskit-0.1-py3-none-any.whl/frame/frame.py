from typing import Callable, Dict, Tuple

import warnings

from functools import partial

import numpy as np
import pandas as pd

from nonion import Pipeline
from nonion import as_catch
from nonion import star
from nonion import wraptry

from sklearn.preprocessing import OneHotEncoder

Dummifier = Callable[[pd.DataFrame], pd.DataFrame]
Encoder = Callable[[Tuple[object, ...]], pd.DataFrame]

ENCODER_PARAMETERS = {
  "sparse": False,
  "handle_unknown": "ignore"
}

def dummifier(
  xys: Dict[str, Tuple[object, ...]],
  name: Callable[[str, object], str] = lambda n, x: n + "_" + str(x)
  ) -> Dummifier:

  to_encoder = (
    Pipeline(xys.items())
    / star(lambda x, y: (x, encoder(y, partial(name, x))))
    >> as_catch(lambda _: pd.DataFrame)
  )

  def g(xs: pd.DataFrame) -> pd.DataFrame:
    frame = (
      Pipeline(xs.iteritems())
      / star(lambda n, x: to_encoder(n)(x))
      >> partial(pd.concat, axis=1)
    )
    frame.index = xs.index
    return frame

  return g

def encoder(xs: Tuple[object, ...], name: Callable[[object], str] = str) -> Encoder:
  e = OneHotEncoder(**ENCODER_PARAMETERS)
  e.fit(np.expand_dims(xs, axis=-1))
  encode = wraptry(e.transform)

  columns = tuple(map(name, *e.categories_))

  def g(ys: Tuple[object, ...]) -> pd.DataFrame:
    zs = np.expand_dims(ys, axis=-1)

    with warnings.catch_warnings():
      warnings.simplefilter("ignore")
      frame, *_ = encode(zs) or (np.zeros((len(ys), len(columns))),)

    return pd.DataFrame(frame, columns=columns)

  return g
