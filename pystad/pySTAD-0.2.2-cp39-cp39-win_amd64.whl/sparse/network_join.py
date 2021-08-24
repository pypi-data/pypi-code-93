import numpy as np

def network_join(sparse_distance_matrix, vertex_values):
  """ Join vertex-data with edges of a network

  Creates two condensed matrices, one for the 'from' vertices and one
  for the 'to' vertices, filled with the vertex values. Analogous to
  performing two (left) joins in a tabular format. This function is f.i.
  used to find edges of which the vertices lie in different lens bins.

  Parameters
  ----------
  sparse_distance_matrix : A Scipy sparse coo-matrix
      A Scipy sparse matrix.
  vertex_values : a 1D numpy array
      An array with a value for every vertex.
  Returns
  -------
  Two 1D numpy arrays containing the vertex_values for the to and from
  vertices of each edge.
  """
  vertex_values = np.asarray(vertex_values)
  sparse_distance_matrix = sparse_distance_matrix.tocoo(copy=False)
  return vertex_values[sparse_distance_matrix.row], \
         vertex_values[sparse_distance_matrix.col]
