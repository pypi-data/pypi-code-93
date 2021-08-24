import numpy as np

from ._hop_k_approximation import _hop_k_approximation
from stad import _validation, objective, sparse


def boundary_coefficient(network, distances = None):
  """ Computes boundary coefficient of a network

      The boundary coefficient uses distances between data-points to estimate
      whether a point is close to the boundary of the point-cloud. It is based
      on the average angle of paths through a node, from starting and ending
      in neighbouring nodes. If this angle is small, the node is close to the
      boundary. If the angle is large, the node is toward the 'core' of the
      point-cloud, as paths go from one side to another side of the 'shape'.

      Low values indicate nodes close to the 'core' of the point-cloud. High
      values indicate nodes close to the boundary.

      The algorithm is adapted from:
          Vandaele, R., Saeys, Y., & De Bie, T. (2020). Mining topological
          structure in graphs through forest representations. Journal of
          Machine Learning Research, 21, 1–68.

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
      distances : optional 1D or 2D numpy array or scipy sparse matrix
          This parameter can be three types of distance matrices:
              - a dense distance matrix (0 values on diagonals, symmetrical)
              - a condensed distance matrix (as given by
                scipy.spatial.distance.pdist)
              - a scipy sparse distance matrix (including explicit zeros)
          Negative, nan, or infinite values are not allowed. Should contain
          all node-pair distances and match shape with the network.

          Vandaele et al. recommend to use the network's weighted node
          distances, as they always satisfy the triangle inequality.

          When not provided, the network's unweighted shortest-path lengths
          are used as distance. For STAD, these distances have a high
          correlation with the underlying point-cloud distances.

      Returns
      -------
      N by 1 numpy array containing the vertex boundary coefficient values.
  """
  sparse_network = _validation.network(network)

  # Compute unweighted shortest path lengths
  sparse_adjacency = sparse_network.copy()
  sparse_adjacency.data = np.ones(len(sparse_adjacency.data), dtype = bool)
  path_lengths = objective.network_distances(sparse_adjacency)

  # Use given distances or unweighted shortest paths
  if distances is not None:
    distances = _validation.distances(distances)
    assert distances.shape == sparse_network.shape, "Network and distance " \
                                                    "matrix do not have the " \
                                                    "same shape."
  else:
    distances = sparse.from_condensed(path_lengths)

  # Compute approximations
  hop1 = _hop_k_approximation(distances, path_lengths, 1)
  hop2 = _hop_k_approximation(distances, path_lengths, 2)
  hop1_inv = hop1.copy()
  hop1_inv.data = 1 / hop1.data

  # Compute vertex degrees
  vertex_degrees = sparse_adjacency.sum(
    axis = 1) + sparse_adjacency.transpose().sum(axis = 1)

  # Compute boundary coefficient
  v1 = np.multiply(hop1.sum(axis = 1), hop1_inv.sum(axis = 1))
  #     computes diagonal of outer matrix product
  v2 = hop1_inv.multiply((hop2.power(2) * hop1_inv).transpose()).sum(axis = 1)
  bc = np.divide((v1 - v2 / 2), np.power(vertex_degrees, 2))
  return np.asarray(bc).flatten()
