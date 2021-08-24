import numpy as np
from scipy.sparse import issparse
from scipy.special import binom

from ._assert import _assert
from stad import sparse


def distances(distances):
  """ Validates the given distance matrix.

  Parameters
  ----------
  distances : 1D or 2D numpy array or scipy sparse matrix
      This parameter can be three types of distance matrices:
          - a dense distance matrix (0 values on diagonals, symmetrical)
          - a condensed distance matrix (as given by
            scipy.spatial.distance.pdist)
          - a scipy sparse distance matrix (including explicit zeros)
      Missing or infinite values are not allowed. In addition, the distance
      matrix should contain at least two unique values.

  Returns
  -------
  The distance matrix as a scipy sparse coo matrix
  """

  # transform distances to a sparse coo matrix
  if issparse(distances):
    _assert(distances.shape[0] == distances.shape[1],
            "Distance matrix is not square")
    _assert(distances.shape[0] > 1,
            "Distance matrix should contain at least 2 points")

    distances = distances.tocoo(copy = True)
    distances.data = distances.data.astype('float')
    _assert(len(distances.data) == binom(distances.shape[0], 2),
            "Distance matrix should include an explicit value for each edge "
            "in the data")
  else:
    distances = np.asarray(distances)
    distances = distances.astype('float')
    if len(distances.shape) == 1:
      s = distances.shape
      d = int(np.ceil(np.sqrt(s[0] * 2)))
      _assert(d * (d - 1) == s[0] * 2,
              "Incompatible length of distances, it must be a binomial "
              "coefficient n choose 2 for some integer n >= 2.")
      _assert(len(distances) > 1,
              "Incompatible length of distances, should contain at least two "
              "nodes")

      distances = sparse.from_condensed(distances)
    elif len(distances.shape) == 2:
      _assert(distances.shape[0] == distances.shape[1],
              "Distance matrix is not square")
      _assert((np.diagonal(distances) == 0).all(),
              "Diagonal entries are not zero")
      _assert(np.allclose(distances, distances.T),
              "Distance matrix is not symmetrical")
      _assert(distances.shape[0] > 1,
              "Distance matrix should contain at least 2 nodes")
      distances = sparse.triu(distances)
    else:
      raise ValueError('Unsupported distance input')

  _assert(distances.shape[0] > 0, "Distance matrix is empty")
  _assert(not np.isnan(distances.data).any(), "Distance matrix contains nans")
  _assert(not np.isinf(distances.data).any(),
          "Distance matrix contains infinite values")
  _assert((distances.data >= 0).all(),
          "Distance matrix contains negative distances")
  _assert(distances.shape[0] <= 2 or len(np.unique(distances.data)) > 1,
          "All distances have the same value")

  return distances
