import numpy as np


def _inverse_similarity(distances: np.array):
  """
  Internal function that transforms distances to similarity through:
    1 / distance

  Parameters
  ----------
  distances : 1d or 2d numpy array, or scipy sparse matrix
    The distance matrix to transform.

  Returns
  -------
  A similarity matrix of the same type as the input.
  """
  return 1 / (1 + distances)
