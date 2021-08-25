import numpy as np
from scipy.special import binom


def _triu_rows(num_points: int):
  length = int(binom(num_points - 1 + 1, 2))
  result = np.zeros(length, dtype=int)
  
  idx = 0
  value = 0
  repeat = 0
  for value in range(num_points - 1):
    for repeat in range(num_points - 1 - value, 0, -1):
      result[idx] = value
      idx += 1
  return result
