import numpy as np


def _k_min(distances: np.array, k: int):
  """ Finds k-closest neighbours

  For each node, returns the distance of the k-closest neighbours.

  Parameters
  ----------
  distances : dense square 2D numpy array
      The distance matrix to evaluate.
  k : int
      number of distances to return.
      The 1st closest neighbour is every node itself.

  Returns
  -------
  - N by k numpy array
  """
  return np.take_along_axis(
    distances,
    np.argpartition(distances, k-1, axis = 1)[:, :k],
    axis = 1
  )
