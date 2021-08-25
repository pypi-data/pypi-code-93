from stad import sparse


def _hop_k_approximation(distances, path_lengths, k: int = 1):
  """
  Internal function that sparsifies a distance matrix based on the path-lengths
  between nodes in a network. Only distances for paths below `k` steps are
  included.

  Parameters
  ----------
  distances : scipy sparse coo matrix
    The distance matrix to approximate, should have explicit values for all
    edges.
  path_lengths : 1D numpy array
    A condensed shortest-path distance matrix of the network.
  k : int
    The path-length threshold.

  Returns
  -------
    A scipy sparse CSR matrix.
  """
  out = sparse.filter(distances.copy(), path_lengths <= k)
  out = out + out.transpose()
  return out.tocsr()
