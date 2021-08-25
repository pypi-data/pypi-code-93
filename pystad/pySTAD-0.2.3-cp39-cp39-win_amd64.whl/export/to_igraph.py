import igraph as ig
import numpy as np

from stad import _validation


def to_igraph(network, export_edge_distance: bool = True):
  """ Convert sparse adjacency matrix to igraph

  Converts a sparse matrix to an undirected igraph object, including
  edge-weights.

  Parameters
  ----------
  network :
      This parameter can have four types of distance matrices:
          - a dense (weighted) adjacency matrix (symmetrical)
          - a condensed (weighted) adjacency mask (including explicit
            zeros)
          - a scipy sparse (weighted) adjacency matrix (zeros may be
            implicit)
          - a tuple with as first element a scipy sparse (weighted)
            adjacency matrix and as second element an instance of
            stad.sweeps._SweepBase.
      Negative, nan, or infinite values are not allowed.
  export_edge_distance : bool
      Flag to enable exporting the edge distances.
  Returns
  -------
  An igraph graph object
  """
  sparse_network = _validation.network(network)
  g = ig.Graph()
  g.to_undirected()
  g.add_vertices(np.arange(0, sparse_network.shape[0], dtype = 'int'))
  g.add_edges(list(zip(sparse_network.row, sparse_network.col)))
  if export_edge_distance:
    g.es['distance'] = sparse_network.data
  return g
