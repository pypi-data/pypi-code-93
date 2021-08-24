import numpy as np
from scipy.optimize import dual_annealing

from ._SweepBase import _SweepBase
from stad import masks, objective, sparse


class OptimizerFunction(_SweepBase):
  """
  A helper class used to configure how STAD optimizes the network.

  This class optimizes the STAD network using a configurable optimizer function
  It also keeps track of the objective traces, using the _SweepBase class.
  """
  start: float = 0.01
  stop: float = 0.3
  function: callable = dual_annealing
  kwargs: dict = None

  optimizer_output = None

  def __init__(self, function: callable = dual_annealing, n_steps: int = 100,
               start: float = 0.01, stop: float = 0.3, **kwargs):
    """
    Initializes the optimizer class.

    Parameters
    ----------
    function : callable
        An optimisation algorithm. It should minimise the objective function
        and have the form:
        f(to_call_fun, to_call_fun_args, bounds, max_iterations, **kwargs)
    start : float
        The normalized distance (0 = min, 1 = max) to use as lower bound.
    stop : float
        The normalized distance (0 = min, 1 = max) to use as upper bound.
    kwargs :
        optional keyword arguments to pass to the optimizer function.
    """
    # Do not let _Sweepbase allocate the traces
    super().__init__(0)

    assert start < stop, "The starting value has to be lower than the stop " \
                         "value"
    self.n_steps = n_steps
    self.start = np.max([start, 0])
    self.stop = np.min([stop, 1])
    self.kwargs = kwargs
    self.function = function

  def __call__(self, sparse_distances, mst_mask, lens_mask, edge_penalty,
               use_ratio, num_threads):
    """ This function is used internally to optimize the STAD network.
    It runs the optimization algorithms and computes the objective traces.

    Returns the optimal network
    """
    self.mst_mask = mst_mask
    self.lens_mask = lens_mask
    self.edge_penalty = edge_penalty
    self.use_ratio = use_ratio

    # The optimisation function
    self.optimiser_output = self.function(# The evaluation function
      self.run_iteration, # Fixed parameters for evaluate_correlation_at
      args = (sparse_distances, num_threads),
      # Bounds provided by explore params
      bounds = [(self.start, self.stop)], maxiter = self.n_steps,
      # Additional arguments
      **self.kwargs)

    self.finalize()
    best_edge_mask = masks.distances(sparse_distances.data, self.best_distance)
    self.network_mask = self.create_network_mask(best_edge_mask)
    return sparse.filter(sparse_distances, self.network_mask)

  def evaluate_network_append(self, sparse_distances, edge_mask, num_threads):
    """ Compute the objective for the given network. """

    # Determine edges of the network
    network_mask = self.create_network_mask(edge_mask)

    # Compute network distances
    sparse_network = sparse.filter(sparse_distances.copy(), network_mask)
    network_distances = objective.network_distances(sparse_network,
      num_threads = num_threads)

    # Compute the objective and traces
    o, c, p, r, e = objective.objective(sparse_distances, network_distances,
                                        network_mask, self.mst_mask,
                                        self.lens_mask, self.edge_penalty,
                                        self.use_ratio)
    self.objective_trace = np.append(self.objective_trace, o)
    self.correlation_trace = np.append(self.correlation_trace, c)
    self.penalty_trace = np.append(self.penalty_trace, p)
    self.ratio_trace = np.append(self.ratio_trace, r)
    self.added_edges_trace = np.append(self.added_edges_trace, e)

    return network_mask

  def run_iteration(self, distance, sparse_distances, num_threads):
    edge_mask = masks.distances(sparse_distances.data, distance)
    self.distance_trace = np.append(self.distance_trace, distance)
    self.evaluate_network_append(sparse_distances, edge_mask, num_threads)

    return -self.objective_trace[len(self.objective_trace) - 1]
