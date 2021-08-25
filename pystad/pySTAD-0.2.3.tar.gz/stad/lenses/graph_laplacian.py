import numpy as np

from stad import _validation


def graph_laplacian(distances, n: int = 1, sigma: float = 0.3):
  """ Graph laplacian based on point-cloud distances.

  Described in section 4.3 from:
      Singh, G., Mémoli, F., & Carlsson, G. (2007). Topological Methods
      for the Analysis of High Dimensional Data Sets and 3D Object
      Recognition. In Eurographics Symposium on Point-Based Graphics.

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
  n : int
      Specifies the n-th eigenvector to return.
  sigma : float
      Stddev of Gaussian smoothing kernel.

  Returns
  -------
  The n-th eigenvector (may be complex) of the graph laplacian.
  """
  distances = _validation.distances_dense(distances)
  weights = np.exp(-np.power(distances, 2) / (2 * np.power(sigma, 2)))
  norm_1 = np.sqrt(np.sum(weights, axis = 0))[np.newaxis].T
  norm_2 = np.sqrt(np.sum(weights, axis = 1))[np.newaxis]
  laplacian = weights / (norm_1 * norm_2)
  [value, vectors] = np.linalg.eig(laplacian)

  order = value.argsort()

  return vectors[:, order[n]]
