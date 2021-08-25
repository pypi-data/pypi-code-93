import numpy as np

from .knn_distance import knn_distance
from stad import _validation


def graph_laplacian_alt(distances, eps: float = 0.3, n: int = 1, k: int = 5,
                        weighted_edges: bool = False, sigma_eps: float = 1.0,
                        normalised: bool = True):
  """ Graph laplacian based on knn-graph of the point-cloud.

  Implementation based on Mapper's documentation at:
      http://danifold.net/mapper/filters.html

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
  eps : float
      If k == 1, the distance threshold for constructing the graph
  n : int
      Specifies the n-th eigenvector to return.
  k : int
      Specifies the number of neighbours for the knn-graph construction.
  weighted_edges : bool
      Flag for using edge weights.
  sigma_eps : float
      Determines std of Gaussian smoothing kernel (eps * sigma_eps).
  normalised : bool
      Flag for normalising the laplacian before computing the eigenvectors.

  Returns
  -------
  The n-th eigenvector (may be complex) of the graph laplacian
  """

  # Determine which edges to use for the laplacian
  distances = _validation.distances_dense(distances)
  if k == 1:
    edge_mask = distances < eps
    degrees = np.diag(np.sum(edge_mask, axis = 1))
  else:
    edge_mask = distances < knn_distance(distances, k)[np.newaxis].T
    degrees = np.diag(np.repeat(k, distances.shape[0]))

  # Compute the edge weights
  if weighted_edges:
    weights = np.exp(
      -np.power(distances, 2) / (2 * np.power(eps * sigma_eps, 2)))
    weights[~edge_mask] = 0
  else:
    weights = edge_mask

  # Compute the laplacian
  laplacian = degrees - weights
  if normalised:
    d = np.sqrt(np.diag(degrees)[np.newaxis])
    laplacian = laplacian / d * d.T

  # Return the n-th eigenvector
  [value, vectors] = np.linalg.eig(laplacian)

  order = value.argsort()[::-1]

  return vectors[:, order[n]]
