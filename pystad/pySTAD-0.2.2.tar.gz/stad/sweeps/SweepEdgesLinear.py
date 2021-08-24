import numpy as np

from ._SweepBase import _SweepBase
from stad import masks, sparse


class SweepEdgesLinear(_SweepBase):
  """
  A helper class used to configure how STAD optimizes the network.

  This class computes a STAD network using a linear sweep between fixed numbers
  of edges. All x shortest edges for the number of edges that maximises
  the objective are included in the network. It also keeps track of the
  objective traces, using the _SweepBase class.
  """
  start: float = 0.01
  stop: float = 0.3
  n_steps: int = 10

  def __init__(self, start: float = 0.01, stop: float = 0.3, n_steps: int = 10):
    """ Initialize the sweeper class

    Parameters
    ----------
    start: float
        The minimum number of added edges as a factor of the total number of
        possible edges.
    stop: float
        The maximum number of added edges as a factor of the total number of
        possible edges.
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
    It applies the edge threshold and computes the objective traces.

    Returns the optimal network
    """
    self.mst_mask = mst_mask
    self.lens_mask = lens_mask
    self.edge_penalty = edge_penalty
    self.use_ratio = use_ratio

    n_edges = len(sparse_distances.data)
    evaluation_points = np.linspace(self.start * (n_edges - 1),
                                    self.stop * (n_edges - 1), self.n_steps)
    evaluation_points = np.unique(evaluation_points.round()).astype('int')

    for idx in range(len(evaluation_points)):
      edge_threshold = evaluation_points[idx]
      edge_mask, distance = masks.edges(sparse_distances.data, edge_threshold)
      self.distance_trace[idx] = distance
      self.evaluate_network(idx, sparse_distances, edge_mask, num_threads)

    self.finalize()
    best_edge_mask = masks.distances(sparse_distances.data, self.best_distance)
    self.network_mask = self.create_network_mask(best_edge_mask)
    return sparse.filter(sparse_distances, self.network_mask)
