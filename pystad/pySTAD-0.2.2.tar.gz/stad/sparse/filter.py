import numpy as np

def filter(sparse_matrix, boolean_mask: np.array):
  """ Applies a boolean masks to a sparse matrix.

  This is an inplace operation. The function does not copy the matrix!

  Parameters
  ----------
  coo_matrix : a scipy sparse coo-matrix
      The matrix to filter from
  boolean_mask : 1d boolean numpy array
      The boolean masks to filter with

  Returns
  -------
  The same coo_matrix, containing only the values for which the masks was
  true.
  """
  sparse_matrix = sparse_matrix.tocoo(copy=False)
  sparse_matrix.row = sparse_matrix.row[boolean_mask]
  sparse_matrix.col = sparse_matrix.col[boolean_mask]
  sparse_matrix.data = sparse_matrix.data[boolean_mask]
  return sparse_matrix
