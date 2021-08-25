import numpy as np

from ._SweepBase import _SweepBase
from stad import masks, sparse


class ThresholdDistance(_SweepBase):
  """
  A helper class used to configure how STAD optimizes the network.

  This class computes a STAD network using a configurable fixed distance
  threshold. All edges with a distance smaller than the threshold are included
   in the network. It also keeps track of the objective traces, using the
  _SweepBase class.
  """
  distance: float = 0.2

  def __init__(self, distance: float = 0.2):
    """ Initialize the sweeper class

    Parameters
    ----------
    distance: float
        The normalized distance (0 = min, 1 = max) to use as threshold.
    """
    super().__init__(1)
    self.distance = np.min([np.max([distance, 0]), 1])

  def __call__(self, sparse_distances, mst_mask, lens_mask, edge_penalty,
               use_ratio, num_threads):
    """ This function is used internally to optimize the STAD network.
    It applies the distance threshold and computes the objective traces.

    Returns the optimal network
    """
    self.mst_mask = mst_mask
    self.lens_mask = lens_mask
    self.edge_penalty = edge_penalty
    self.use_ratio = use_ratio

    edge_mask = masks.distances(sparse_distances.data, self.distance)
    self.distance_trace[0] = self.distance
    self.network_mask = self.evaluate_network(0, sparse_distances, edge_mask,
                                              num_threads)
    self.finalize()
    return sparse.filter(sparse_distances, self.network_mask)
