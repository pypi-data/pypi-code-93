import numpy as np

from ._k_min import _k_min
from stad import _validation


def distance_to_measure(distances, k: int = 5):
  """ Computes the 2-norm of the vector containing the k-th closest distances.

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
  k : int
      The number of neighbours to evaluate.

  Returns
  -------
  N by 1 numpy array containing the vertex distance values.
  """
  distances = _validation.distances_dense(distances)
  return np.sqrt(1 / k * np.sum(np.power(_k_min(distances, k), 2), axis = 1))
