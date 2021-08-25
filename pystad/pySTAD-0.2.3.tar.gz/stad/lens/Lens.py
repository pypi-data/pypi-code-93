import numpy as np
import pandas as pd

from stad import sparse


class Lens:
  """
  A helper class to configure how STAD applies a lens or filter.

  By default, the lens is disabled. To use a lens, initialize this class
  using a value for each node and a number of bins (larger than zero).

  After running STAD, this class contains the classification of edges,
  indicating whether an edge is within, between adjacent, or between non-
  adjacent bins of the lens. It also contains the value-ranges for each
  lens-bin.

  Parameters
  ----------
  values :
    A numpy array containing a filter-value for each node in the data.
  is_circular :
    A flag indicating whether the filter-dimension is circular.
  n_bins :
    The number of bins to segment the filter dimension in.

  Attributes
  ----------
  bins :
    A list (n-bins + 1) specifying boundaries of the filter segments.
  inner_edges :
    A mask indicating which edges connect nodes within a filter segment.
  adjacent_edges :
    A mask indicating which edges connect nodes in adjacent filter segments.
  non_adjacent_edges :
    A mask indicating which edges connect nodes in non-adjacent filter segments.
  """
  values: np.array = None
  is_circular: bool = False
  n_bins: int = 0

  bins: np.array = None
  inner_edges: np.array = None
  adjacent_edges: np.array = None
  non_adjacent_edges: np.array = None

  def __init__(self, values: np.array = None, n_bins: int = 0,
               circular: bool = False):
    """
    Constructs a Lens object

    Parameters
    ---------
    values : 1D np.array
      A numpy array containing a value for each node in the data.
    n_bins : int
      The number of bins to segment the filter dimension in. This determines the
      strength of the lens on the network output. The lens is disabled for 0
      bins, and does not change the resulting network for less than 3 bins.
    circular : bool
      A flag to determine whether the filter-dimension is interpreted as
      circular. For example, weekdays are circular, the min and max value are
      as close to each other as the other values.
    """
    self.values = values
    if values is not None:
      self.n_bins = n_bins
    self.circular = circular

  def __call__(self, sparse_distances):
    """
    Used internally to find the non-adjacent edges, which are suppressed in the
    output.
    """

    # Check if the lens is enabled
    if self.n_bins == 0:
      return np.ones(sparse_distances.data.shape, dtype = bool)

    binned_lens = self._discretize_lens_dimension()
    self._classify_edges(sparse_distances, binned_lens)

    return ~self.non_adjacent_edges

  def _discretize_lens_dimension(self):
    """
    Used internally to discretize the filter-dimension into a specified
    number of segments / bins.
    """
    binned_lens, self.bins = pd.cut(pd.Series(self.values), bins = self.n_bins,
                                    labels = np.arange(self.n_bins),
                                    retbins = True)

    # Remove empty bins s.t. adjacent edges can cross them
    binned_lens = binned_lens.cat.remove_unused_categories()
    binned_lens.cat.categories = np.arange(0, len(binned_lens.cat.categories))
    return binned_lens

  def _classify_edges(self, sparse_distances, binned_lens):
    """
    Used internally to classify edges as: within bin, to adjacent bin,
    to non-adjacent bin.
    """
    (condensed_from, condensed_to) = sparse.network_join(sparse_distances,
                                                         binned_lens.values.astype(int))

    self.inner_edges = condensed_from == condensed_to
    self.adjacent_edges = ((condensed_from + 1) == condensed_to) | (
          condensed_from == (condensed_to + 1))
    if self.is_circular:
      min_bin = 0
      max_bin = max(binned_lens.cat.categories)
      self.adjacent_edges |= (
           (condensed_from == min_bin) & (condensed_to == max_bin) | (
            condensed_from == max_bin) & (condensed_to == min_bin))

    self.non_adjacent_edges = ~(self.inner_edges | self.adjacent_edges)
