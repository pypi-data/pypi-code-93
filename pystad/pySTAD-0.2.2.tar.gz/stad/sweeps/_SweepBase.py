import numpy as np

from stad import objective, sparse


class _SweepBase:
  """ The sweeper base-class.

  This class contains the objective-traces, so we can evaluate the sweep's
  performance, and not just the best found network. In addition, this class
  implements the functionality of evaluating the objective for a given network.

  Parameters
  ----------
  n_steps :
    The number of steps of the sweep.


  Functions
  ---------
  evaluate_network :
    Evaluates the objective of a given network and stores the result at the
    current index in the traces.
  create_network_mask :
    Combines the mst_mask, lens_mask, mask of edges to include to create a
    mask for the edges in the network.

  Attributes
  ----------
  network_mask : 1d numpy array
    The final mask for the full condensed distance matrix indicating which edges are
    included in the network.
  mst_mask : 1d numpy array
    A mask for the full condensed distance matrix indicating which edges are
    included in the minimum spanning tree.
  lens_mask : 1d numpy array
    A mask for the full condensed distance matrix indicating which edges are
    allowed through the lens.

  edge_penalty : float
    A factor applied to the fraction `n_edges_added_to_mst / n_edges_possible`.
    The result is subtracted from the objective. The objective is the
    correlation of the network distances with the data distances by default.
  use_ratio : bool
    A flag specifying whether to use STAD-R, which multiplies the correlation
    with `sum(1 - edge_distance) / 1 + sum(edge_distance)` before applying the
    edge penalty.

  objective_trace : 1d numpy array
    The objective values found in the sweep.
  correlation_trace : 1d numpy array
    The correlation values found in the sweep.
  penalty_trace : 1d numpy array
    The penalty values found in the sweep.
  ratio_trace : 1d numpy array
    The ratio values found in the sweep.
  distance_trace : 1d numpy array
    The distance thresholds applied in the sweep.
  added_edges_trace : 1d numpy array
    The number of added edges applied in the sweep.

  best_trace_idx :
    The index of the network with the highest observed objective in the sweep.
    This network is returned by STAD.
  best_objective :
    The objective of the final network.
  best_correlation :
    The correlation of the final network.
  best_penalty :
    The penalty applied to the objective of the final network.
  best_ratio :
    The ratio value applied to the objective of the final network.
    Nan if use_ratio is False.
  best_distance :
    The distance-threshold used to construct the final network.
  best_added_edges :
    The number of edges added to the mst in the final network.
  """
  n_steps: int = 1

  mst_mask: np.array = np.empty(0, dtype = bool)
  lens_mask: np.array = np.empty(0, dtype = bool)
  network_mask: np.array = np.empty(0, dtype = bool)

  edge_penalty: float = 0
  use_ratio: bool = False

  objective_trace: np.array = np.empty(0, dtype = float)
  correlation_trace: np.array = np.empty(0, dtype = float)
  penalty_trace: np.array = np.empty(0, dtype = float)
  ratio_trace: np.array = np.empty(0, dtype = float)
  distance_trace: np.array = np.empty(0, dtype = float)
  added_edges_trace: np.array = np.empty(0, dtype = int)

  best_trace_idx: int = np.nan
  best_objective: float = np.nan
  best_correlation: float = np.nan
  best_penalty: float = np.nan
  best_ratio: float = np.nan
  best_distance: float = np.nan
  best_added_edges: int = np.nan

  def __init__(self, n_steps: int = 1):
    self.n_steps = n_steps
    self.objective_trace = np.empty(n_steps, dtype = float)
    self.correlation_trace = np.empty(n_steps, dtype = float)
    self.penalty_trace = np.empty(n_steps, dtype = float)
    self.ratio_trace = np.empty(n_steps, dtype = float)
    self.distance_trace = np.empty(n_steps, dtype = float)
    self.added_edges_trace = np.empty(n_steps, dtype = int)

  def evaluate_network(self, idx, sparse_distances, edge_mask, num_threads):
    """ Compute the objective for the given network. """

    # Determine edges of the network
    network_mask = self.create_network_mask(edge_mask)

    # Compute network distances
    sparse_network = sparse.filter(sparse_distances.copy(), network_mask)
    network_distances = objective.network_distances(sparse_network, num_threads = num_threads)

    # Compute the objective and traces
    (self.objective_trace[idx], self.correlation_trace[idx],
     self.penalty_trace[idx], self.ratio_trace[idx],
     self.added_edges_trace[idx]) = objective.objective(sparse_distances,
                                                        network_distances,
                                                        network_mask,
                                                        self.mst_mask,
                                                        self.lens_mask,
                                                        self.edge_penalty,
                                                        self.use_ratio)

    return network_mask

  def create_network_mask(self, edge_mask: np.ndarray):
    """
    Combines masks to create the complete network.
    lens_mask and mst_mask have to be assigned before this function can
    be used. This is done in __call__ of the sweeper classes!
    """
    return (edge_mask & self.lens_mask) | self.mst_mask

  def finalize(self):
    self.best_trace_idx = np.argmax(self.objective_trace)
    self.best_objective = self.objective_trace[self.best_trace_idx]
    self.best_correlation = self.correlation_trace[self.best_trace_idx]
    self.best_penalty = self.penalty_trace[self.best_trace_idx]
    self.best_ratio = self.ratio_trace[self.best_trace_idx]
    self.best_distance = self.distance_trace[self.best_trace_idx]
    self.best_added_edges = self.added_edges_trace[self.best_trace_idx]
