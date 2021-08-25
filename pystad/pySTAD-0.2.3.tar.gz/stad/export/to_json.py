import json

from ._to_dict import _to_dict


def to_json(network, node_color = None, node_radius = None, node_label = None,
            link_color = None, link_width = None):
  """ Exports a STAD network as json:
      "([
          {
              'id': node index,
              'label': a string
              'color_data': a float
              'radius_data': a float
          },...
       ], [
          {
              'source': source node id
              'target': target node id
              'color_data': a float
              'width_data': a float
              'distance': a float
          },...
       ])"

  Parameters
  ----------
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
  output = _to_dict(network, node_color, node_radius, node_label, link_color,
                    link_width)
  return json.dumps(output)
