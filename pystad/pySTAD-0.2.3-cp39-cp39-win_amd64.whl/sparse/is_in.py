try:
  from ._impl_fast import _is_in
except ImportError:
  from ._impl_slow import _is_in
  from sys import stderr
  print("Falling back to slow stad.sparse implementation", file=stderr)


def is_in(sparse_distances, sparse_network):
  """ Is-in for sparse matrices
  
  The function assumes that all edges of sparse_network occur in
  sparse_distances, and the edges are in the same order.
  
  Parameters
  ----------
  sparse_distances : scipy coo-matrix
      A sparse distance matrix containing the full upper triangle.
  sparse_network : scipy coo-matrix
      A sparse distance matrix containing a subset of the upper triangle.
  Returns
  -------
  A 1D boolean numpy array for sparse_distances, indicating True for the
  edges that occur in sparse_network
  """
  return _is_in(sparse_distances.row, sparse_distances.col,
                sparse_network.row, sparse_network.col)

