import numpy as np


def _gauss_similarity(distances: np.array, sigma: float = 0.3):
  """
  Internal function to transform distances into similarity using a Gaussian
  kernel.

  Parameters
  ----------
  distances : 1D numpy array
    The condensed distance matrix to transform.
  sigma : float
  The variance of the Gaussian kernel to apply.

  Returns
  -------
  A numpy array with node similarities.
  """
  return np.exp(-np.multiply(distances, distances) / (2 * sigma * sigma))
