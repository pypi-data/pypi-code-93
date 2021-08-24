import numpy as np

from .distances import distances


def edges(condensed_distances: np.ndarray, threshold: int):
  """
  Computes a mask indicating the k shortest edges.

  Parameters
  ----------
  condensed_distances : 1d numpy array
    A condensed distance matrix (values between 0 and 1).
  threshold : int
    The number of edges to include.
  Returns
  -------
    A boolean 1d numpy array indicating the k shortest edges.
  """
  partitioned_distances = np.partition(condensed_distances, threshold)
  threshold_distance = partitioned_distances[threshold]
  return distances(condensed_distances, threshold_distance), threshold_distance
