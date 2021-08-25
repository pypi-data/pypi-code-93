import numpy as np

from stad import _validation


def eccentricity(distances, power: int = np.Inf):
  """ Computes point-could eccentricity

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
  power : int
      The power to use, may also be infinite.

  Returns
  -------
  N by 1 numpy array containing the vertex eccentricity values.
  """
  distances = _validation.distances_dense(distances)
  if power == np.inf:
    return np.max(distances, axis = 0)

  return np.power(
    np.sum(np.power(distances, power), axis = 0) / distances.shape[0],
    1 / power)
