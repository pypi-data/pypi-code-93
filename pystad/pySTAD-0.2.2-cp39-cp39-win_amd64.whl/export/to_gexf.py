import networkx as nx

from .to_networkx import to_networkx


def to_gexf(file_path: str, network, node_color = None, node_radius = None,
            node_label = None, link_color = None, link_width = None):
  """ Exports a STAD network as gexf file

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
  g = to_networkx(network, node_color, node_radius, node_label, link_color,
                  link_width)
  nx.write_gexf(g, file_path)
