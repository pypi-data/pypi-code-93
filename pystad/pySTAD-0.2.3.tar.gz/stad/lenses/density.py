import numpy as np

from ._gauss_similarity import _gauss_similarity
from stad import _validation


def density(distances, sigma: float = 0.3):
  """ Computes point-cloud density

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
  sigma : float
      stddev of Gaussian smoothing kernel.

  Returns
  -------
  N by 1 numpy array containing the vertex density values.
  """

  distances = _validation.distances_dense(distances)
  return np.sum(_gauss_similarity(distances, sigma), axis = 0)
