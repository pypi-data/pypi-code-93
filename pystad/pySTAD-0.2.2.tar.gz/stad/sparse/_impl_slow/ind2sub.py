import numpy as np
import math

def ind2sub(k: int, n: int):
  """
  Computes the row and column location in a dense matrix for an index
  in a condensed matrix.
  
  Parameters
  ----------
  k : unsigned int 
    The index value to transform.
  n : unsigned int
    The number of nodes in the distance matrix.
  Returns
  -------
    A tuple with the (row, col) value. (-1 , -1) if the given index does not 
    exist in a condensed matrix of the given size.
  """
  i = calc_row_idx(k, n)
  j = calc_col_idx(k, i, n)
  if i < 0 or j > n or j < 0 or i > n:
    return -1, -1
  return i, j


def calc_row_idx(k: int, n: int):
  v = (1/2.) * (- (-8*k + 4 *n**2 -4*n - 7)**0.5 + 2*n -1) - 1
  if isinstance(v, complex):
    return -1
  
  return int(math.ceil(v))


def elem_in_i_rows(i: int, n: int):
    return i * (n - 1 - i) + (i*(i + 1))//2


def calc_col_idx(k: int, i: int, n: int):
    return n - elem_in_i_rows(i + 1, n) + k
