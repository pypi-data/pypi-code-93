import numpy as np

from ._assert import _assert
from .network import network


def export(network_, node_color = None, node_radius = None, node_label = None,
           link_color = None, link_width = None):
  """ Validates the parameters used in export functions.

    Parameters
    ----------
    network_ :
        This parameter can have four types of distance matrices:
            - a dense (weighted) adjacency matrix (symmetrical)
            - a condensed (weighted) adjacency mask (including explicit
              zeros)
            - a scipy sparse (weighted) adjacency matrix (zeros may be
              implicit)
            - a tuple with as first element a scipy sparse (weighted)
              adjacency matrix and as second element an instance of
              stad.sweeps._SweepBase.
        Negative, nan, or infinite values are not allowed.
    node_color: List, numpy array
        A float value for every node to be mapped to the node-colour.
    node_radius: List, numpy array
        A float value for every node to be mapped to the node-radius.
    node_label: List, numpy array
        A value convertable to string for every node, to be used as label on
        node hover.
    link_color: List, numpy array
        A float for every edge in the objective, to be mapped to the
        edge-colour.
    link_width: List, numpy array
        A float for every edge in the objective, to be mapped to the edge-width.

    Returns
    -------
    Returns the network as sparse distance matrix and other input arguments as
    numpy arrays.
    """

  if node_radius is None:
    node_radius = [1]
  else:
    node_radius = np.asarray(node_radius).astype('float')
  if link_width is None:
    link_width = [0.2]
  else:
    link_width = np.asarray(link_width).astype('float')
  if link_color is None:
    link_color = [0.5]
  else:
    link_color = np.asarray(link_color).astype('float')
  if node_color is None:
    node_color = [0.5]
  else:
    node_color = np.asarray(node_color).astype('float')
  if node_label is not None:
    node_label = np.asarray(node_label)

  sparse_network = network(network_)
  _assert(len(node_color) == 1 or len(node_color) == sparse_network.shape[0],
          "Invalid node_color length")
  _assert(len(node_radius) == 1 or len(node_radius) == sparse_network.shape[0],
          "Invalid node_radius length")
  _assert(len(link_color) == 1 or len(link_color) == len(sparse_network.row),
          "Invalid link_color length")
  _assert(len(link_width) == 1 or len(link_width) == len(sparse_network.row),
          "Invalid link_width length")
  _assert(node_label is None or len(node_label) == sparse_network.shape[0],
          "Invalid node_label length")

  return (sparse_network, node_color, node_radius,
          node_label, link_color, link_width)
