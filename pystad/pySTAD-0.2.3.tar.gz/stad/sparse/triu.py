import numpy as np

from scipy.spatial.distance import squareform
from .from_condensed import from_condensed


def triu(dense_matrix: np.array):
  """ Extract upper triangle of a square matrix

  Unlike scipy.sparse.triu, zero values are stored explicitly.

  Parameters
  ----------
  dense_matrix : 2D numpy array
      A square distance matrix.

  Returns
  -------
  A coo matrix containing the upper triangle (k=1) of the distance matrix.
  """
  condensed_distance = squareform(dense_matrix)
  return from_condensed(condensed_distance)
