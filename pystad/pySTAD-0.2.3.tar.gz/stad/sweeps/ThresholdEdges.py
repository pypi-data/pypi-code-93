import numpy as np

from ._SweepBase import _SweepBase
from stad import masks, sparse


class ThresholdEdges(_SweepBase):
  """
  A helper class used to configure how STAD optimizes the network.

  This class computes a STAD network using a configurable fixed number of
  edges. The specified number of smallest edges are included in the network.
  It also keeps track of the objective traces, using the _SweepBase class.
  """

  edge_factor: float = 0.1

  def __init__(self, edge_factor: float = 0.1):
    """ Initialize the sweeper class

    Parameters
    ----------
    edge_factor: float
        The number of edges to include as a factor of the total number of
        possible edges. The resulting network may contain more
        edges if there exist multiple edges with the same distance.
    """
    super().__init__(1)
    self.edge_factor = np.min([np.max([edge_factor, 0]), 1])

  def __call__(self, sparse_distances, mst_mask, lens_mask, edge_penalty,
               use_ratio, num_threads):
    """ This function is used internally to optimize the STAD network.
    It applies the edge threshold and computes the objective traces.

    Returns the optimal network
    """
    self.mst_mask = mst_mask
    self.lens_mask = lens_mask
    self.edge_penalty = edge_penalty
    self.use_ratio = use_ratio

    n_edges = len(sparse_distances.data)
    edge_mask, distance = masks.edges(sparse_distances.data, int(
      np.ceil(self.edge_factor * (n_edges - 1))))
    self.distance_trace[0] = distance
    self.network_mask = self.evaluate_network(0, sparse_distances, edge_mask,
                                              num_threads)
    self.finalize()
    return sparse.filter(sparse_distances, self.network_mask)
