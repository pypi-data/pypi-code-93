import numpy as np


def objective(sparse_distances, network_distances, network_mask, mst_mask,
              lens_mask, edge_penalty, use_ratio):
  """
  Computes the objective of a network.

  Parameters
  ----------
  sparse_distances : scipy sparse coo matrix
    The distances of the data.
  network_distances : 1d numpy array
    Condensed distance matrix of shortest paths in the network.
  network_mask : 1d numpy array
    A mask for the full condensed distance matrix indicating which edges are
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
  Returns
  -------
    A tuple containing the objective, correlation, penalty, ratio, and number of
    added edges.
  """
  added_edges = (network_mask & ~mst_mask).sum()
  if (network_distances == 1).all():
    correlation = np.nan
    penalty = np.nan
  else:
    correlation = np.corrcoef(network_distances[lens_mask],
                              sparse_distances.data[lens_mask])[0, 1]
    penalty = edge_penalty * float(added_edges) / float(len(network_mask))

  # compute ratio and final objective
  if use_ratio:
    masked_distances = sparse_distances.data[network_mask]
    ratio = np.sum(1 - masked_distances) / (1 + np.sum(masked_distances))
    objective = ratio * correlation - penalty
  else:
    ratio = np.nan
    objective = correlation - penalty

  return objective, correlation, penalty, ratio, added_edges
