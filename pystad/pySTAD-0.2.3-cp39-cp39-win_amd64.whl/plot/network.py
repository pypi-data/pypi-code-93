import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from stad import _validation


def network(network, layout: str = 'spring', ax = None, positions = None,
            edge_color: str = 'lightgrey', edge_alpha: float = 1, **kwargs):
  """ Draws the objective using NetworkX

  Parameters
  ----------
  network : Scipy sparse matrix
    The output of STAD.
  layout : string
    The layout to use for drawing:
    ::
        >>> "kk": nx.kamada_kawai_layout,
        >>> "spring": nx.spring_layout,
        >>> "circ": nx.circular_layout,
        >>> "spect": nx.spectral_layout
  positions : np.array or networkx layout dictionary
    Positions to use for drawing, overrides layout. Should be either a
    networkx layout dictionary or a 2d numpy array.
  edge_color : string
    Color to dray edges in.
  edge_alpha : float
    Transparancy of edges
  ax : matplotlib Axes object
    The matplotlib axes to draw to. If None, a new one is created
  kwargs : dictionary
    Keyword arguments for networkx.draw_networkx_nodes()

  Returns
  -------
  - the matplotlib Figure object that was drawn to
  - the networkx nodes object
  - the networkx edges object
  - the networkx graph object
  - the networkx layout dictionary
  """
  network = _validation.network(network)
  if ax is None:
    fig = plt.figure()
    ax = plt.gca()
  else:
    plt.sca(ax)
    fig = plt.gcf()

  layouts = {
    "kk": nx.kamada_kawai_layout, "spring": nx.spring_layout,
    "circ": nx.circular_layout, "spect": nx.spectral_layout
  }

  # Determine node size, from:
  # https://github.com/scikit-tda/kepler-mapper/blob/master/kmapper/drawing.py
  bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
  width, height = bbox.width, bbox.height
  area = width * height * fig.dpi
  n_nodes = network.shape[0]

  # size of node should be related to area and number of nodes -- heuristic
  node_size = np.pi * area / n_nodes
  node_r = np.sqrt(node_size / np.pi)
  node_edge = node_r / 3

  g = nx.Graph(network)
  if not (positions is None):
    if isinstance(positions, dict):
      pos = positions
    else:
      pos = dict()
      for idx in range(positions.shape[0]):
        pos[idx] = np.array([positions[idx, 0], positions[idx, 1]])
  else:
    pos = layouts[layout](g)

  edges = nx.draw_networkx_edges(g, pos = pos, ax = ax, edge_color = edge_color,
                                 alpha = edge_alpha)

  nodes = nx.draw_networkx_nodes(g, node_size = node_size, pos = pos, ax = ax,
                                 **kwargs)
  edges.set_linewidth(node_edge)
  nodes.set_edgecolor("w")
  nodes.set_linewidth(node_edge)
  ax.axis("off")

  return fig, nodes, edges, g, pos
