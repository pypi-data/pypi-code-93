import networkx as nx

from stad import _validation


def to_networkx(network, node_color = None, node_radius = None,
                node_label = None, link_color = None, link_width = None):
  """ Exports a STAD network to networkx graph object

  Parameters
  ----------
  file_path : string
      the location to save the gfx file to.
  network :
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
      A float for every edge in the objective, to be mapped to the edge-colour.
  link_width: List, numpy array
      A float for every edge in the objective, to be mapped to the edge-width.
  """
  (sparse_network, node_color, node_radius, node_label, link_color,
   link_width) = _validation.export(network, node_color, node_radius,
                                    node_label, link_color, link_width)
  max_distance = sparse_network.data.max()
  g = nx.Graph()

  for i in range(sparse_network.shape[0]):
    g.add_node(i,
               label = str(node_label[i]) if node_label is not None else str(i),
               color_data = node_color[i] if len(node_color) > 1 else node_color[0],
               radius_data = node_radius[i] if len(node_radius) > 1 else node_radius[0])
  for i in range(len(sparse_network.data)):
    g.add_edge(int(sparse_network.row[i]), int(sparse_network.col[i]),
               distance = float(sparse_network.data[i] / max_distance),
               color_data = link_color[i] if len(link_color) > 1 else link_color[0],
               width_data = link_width[i] if len(link_width) > 1 else link_width[0])

  return g
