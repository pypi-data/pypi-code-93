import numpy as np

from ._SweepBase import _SweepBase
from stad import masks, sparse


class SweepDistanceLogarithmic(_SweepBase):
  """
  A helper class used to configure how STAD optimizes the network.

  This class computes a STAD network using a logarithmic sweep between fixed
  distance values. All edges with a distance smaller than the distance that
  maximises the objective are included in the network. It also keeps track of
  the objective traces, using the _SweepBase class.
  """
  start: float = 0.01
  stop: float = 0.3
  n_steps: int = 10

  def __init__(self, start: float = 0.01, stop: float = 0.3, n_steps: int = 10):
    """ Initialize the sweeper class

    Parameters
    ----------
    start: float
        The normalized distance (0 = min, 1 = max) to use as start for the
        sweep.
    end: float
        The normalized distance (0 = min, 1 = max) to use as max for the
        sweep.
    n_steps: int
        The number of iterations to perform in the sweep.
    """
    super().__init__(n_steps)
    assert start < stop, "The starting value has to be lower than the stop " \
                         "value"
    self.start = np.max([start, 0])
    self.stop = np.min([stop, 1])

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

    min_value = 0 if self.start == 0 else np.log10(self.start)
    exponents = np.linspace(min_value, np.log10(self.stop), self.n_steps)
    evaluation_points = np.power(10, exponents)

    for idx in range(len(evaluation_points)):
      distance = evaluation_points[idx]
      self.distance_trace[idx] = distance
      edge_mask = masks.distances(sparse_distances.data, distance)
      self.evaluate_network(idx, sparse_distances, edge_mask, num_threads)

    self.finalize()
    best_edge_mask = masks.distances(sparse_distances.data, self.best_distance)
    self.network_mask = self.create_network_mask(best_edge_mask)
    return sparse.filter(sparse_distances, self.network_mask)
