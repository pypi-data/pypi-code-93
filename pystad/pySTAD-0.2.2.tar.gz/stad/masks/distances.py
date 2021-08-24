import numpy as np


def distances(condensed_distances: np.ndarray, threshold: float):
  """
  Computes a mask indicating all edges with a distance below the given
  threshold.

  Parameters
  ----------
  condensed_distances : 1d numpy array
    A condensed distance matrix (values between 0 and 1).
  threshold : float
    The distance threshold to apply.
  Returns
  -------
    A boolean 1d numpy array indicating the edges with a distance below the
    threshold.
  """
  res = condensed_distances < threshold
  return res
