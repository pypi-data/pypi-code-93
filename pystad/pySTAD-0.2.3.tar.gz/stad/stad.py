from . import _validation, masks, sparse
from .lens import Lens
from .sweeps import SweepEdgesLogarithmic


def stad(distances, lens: callable = None,
         sweep: callable = None, edge_penalty = 0,
         use_ratio = False, num_threads = -1):
  """ Compute a STAD network representation of a dataset.

  Parameters
  ----------
  distances : 1D or 2D numpy array or scipy sparse matrix
      This parameter can be three types of distance matrices:
          - a dense distance matrix (0 values on diagonals, symmetrical)
          - a condensed distance matrix (as given by
            scipy.spatial.distance.pdist)
          - a scipy sparse distance matrix (including explicit zeros)
      Missing or infinite values are not allowed. In addition, the distance
      matrix should contain at least two unique values.
  lens : stad.lens.Lens
      A callable Lens object. Used to apply a filter or lens to the dataset.
  sweep : stad.sweeps.*
      A callable Sweep object. Configures and performs the network optimization.
  edge_penalty : float
      A factor to penalize the number of edges in the objective function.
  use_ratio : bool
      Flag to indicate whether the STAD-R variant is used. Changes the objective
      function to prioritize smaller networks.
  num_threads : int
      The number of threads to use when computing geodesic network distances.
      A value lower than 0 indicates to a thread on all cores.
  """
  if lens is None:
    lens = Lens()
  if sweep is None:
    sweep = SweepEdgesLogarithmic()

  distances = _validation.distances(distances)
  distances.data /= distances.data.max()

  lens_mask = lens(distances)
  mst_mask = masks.mst(distances, lens_mask)

  # Check for the case of 1 or 2 nodes
  if sum(mst_mask) >= len(distances.data):
    return sparse.filter(distances, mst_mask)

  return sweep(distances, mst_mask, lens_mask, edge_penalty, use_ratio,
               num_threads), sweep
