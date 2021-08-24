import numpy as np
from scipy.special import binom


def _triu_cols(num_points: int):
  length = int(binom(num_points, 2))
  result = np.zeros(length, dtype=int)
  idx = 0
  start = 0
  for start in range(1, num_points):
    for value in range(start, num_points):
      result[idx] = value
      idx += 1
  return result