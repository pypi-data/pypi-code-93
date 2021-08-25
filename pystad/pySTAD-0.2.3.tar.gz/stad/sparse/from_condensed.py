import numpy as np
from scipy.sparse import coo_matrix

try:
  from ._impl_fast import _triu_rows, _triu_cols
except ImportError:
  from ._impl_slow import _triu_rows, _triu_cols
  from sys import stderr
  print("Falling back to slow stad.sparse implementation", file=stderr)


def from_condensed(condensed_vector: np.array):
  """ Converts a condensed distance matrix to a sparse coo-matrix
  
  Parameters
  ----------
  condensed_vector : 1D numpy array
      a condensed distance matrix
  Returns
  -------
  A scipy sparse coo-matrix.
  """
  s = len(condensed_vector)
  d = int(np.ceil(np.sqrt(s * 2)))
  assert d * (d - 1) == s * 2, \
    "Incompatible length of distances, it must be a binomial coefficient n" \
    " choose 2 for some integer n >= 2."
  
  rows = _triu_rows(d)
  cols = _triu_cols(d)
  return coo_matrix((condensed_vector, (rows, cols)), shape=(d, d))
