import numpy as np
from scipy.sparse import issparse

from ._assert import _assert
from stad import sparse
from stad import sweeps


def network(network):
  """ Validates that the given network meets our requirements.

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
  Returns
  -------
  A scipy sparse coo matrix representing the network.
  """
  if type(network) == tuple and issparse(network[0]):
    network = network[0]
  if issparse(network):
    _assert(network.shape[0] == network.shape[1], "Network is not square")
    _assert(network.shape[0] > 1, "Network should contain at least 2 points")
    network = network.tocoo(copy = True)
    network.data = network.data.astype('float')
  else:
    network = np.asarray(network)
    network = network.astype('float')
    if len(network.shape) == 1:
      s = network.shape
      d = int(np.ceil(np.sqrt(s[0] * 2)))
      _assert(d * (d - 1) == s[0] * 2,
              "Incompatible vector length, it must be a binomial coefficient "
              "n  choose 2 for some integer n >= 2.")
      _assert(len(network) > 1,
              "Incompatible length, should contain at least two nodes")
      network = sparse.from_condensed(network)
      network.eliminate_zeros()
    elif len(network.shape) == 2:
      _assert(network.shape[0] == network.shape[1],
              "Network matrix is not square")
      _assert(np.allclose(network, network.T),
              "Network should be undirected (symmetrical matrix)")
      _assert(network.shape[0] > 1, "Network should contain at least 2 points")
      network = sparse.triu(network)
      network = sparse.filter(network, network.data > 0)
    else:
      raise ValueError('Unsupported distance input')

  _assert(network.shape[0] > 0, "Network matrix is empty")
  _assert(not np.isnan(network.data).any(), "Network matrix contains nans")
  _assert(not np.isinf(network.data).any(),
          "Network matrix contains infinite values")
  _assert((network.data >= 0).all(),
          "Network matrix contains negative distances")

  return network
