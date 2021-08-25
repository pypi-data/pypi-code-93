from scipy.sparse.csgraph import minimum_spanning_tree

from stad import sparse


def mst(sparse_distances, lens_mask):
  """
  Compute the minimum spanning tree.

  Parameters
  ----------
  sparse_distances : scipy sparse coo matrix
    The full sparse distance matrix to compute the MST on
  lens_mask : boolean 1d numpy array
    A mask for the full condensed distance matrix indicating which edges are
    allowed through the lens.
  Returns
  -------
    A boolean 1d numpy array indicating the edges of the MST.
  """

  # Increasing the distance (past the maximum after normalization)
  # ensures that they will not be added to the MST
  sparse_distances.data[~lens_mask] += 1
  res = minimum_spanning_tree(sparse_distances)
  # avoid propagating the distance increase to the caller.
  # may not be necessary as these distances are not used
  # to compute the correlation and are not included
  # in the network...
  sparse_distances.data[~lens_mask] -= 1
  return sparse.is_in(sparse_distances, res.tocoo())
