from ipywidgets import widgets
from traitlets import Bool, Dict, Float, Integer, List, Tuple, Unicode

from stad import export


# See js/lib/widget.ts for the frontend counterpart to this file.
@widgets.register
class Widget(widgets.DOMWidget):
    """
      A Jupyter Lab Widget to visualize networks.

      The attributes of this class can be changed and observed to respond to,
      or change the visualization.

      Attributes
      ----------
      network : tuple
        The network representation as given by stad.export.to_dict(). Contains
        a list of nodes and a list of edges.
      selectedNodes : list
        A list of node-index values indicating which nodes are selected by the
        user.
      featureMode : bool
        A flag indicating whether the widget should show the network as a
        feature network. This changes the default node size and color values and
        disables selection.
    """
    _view_name = Unicode('StadView').tag(sync=True)
    _model_name = Unicode('StadModel').tag(sync=True)
    _view_module = Unicode('jupyter_stad').tag(sync=True)
    _model_module = Unicode('jupyter_stad').tag(sync=True)
    _view_module_version = Unicode('^0.2.0').tag(sync=True)
    _model_module_version = Unicode('^0.2.0').tag(sync=True)

    network = Tuple(List(Dict(per_key_traits = {  # Nodes
        'id': Integer(),
        'label': Unicode(),
        'color_data': Float(),
        'radius_data': Float(),
    })), List(Dict(per_key_traits = {  # Edges
        'source': Integer(),
        'target': Integer(),
        'color_data': Float(),
        'width_data': Float(),
        'distance': Float()
    })), default_value = ([], [])).tag(sync = True)
    selectedNodes = List(Integer()).tag(sync = True)
    featureMode = Bool(False).tag(sync = True)

    def __init__(self, featureMode = False):
        """
        Initialize the Widget

        Parameters
        ----------
        featureMode : bool
          A flag indicating whether the widget should show the network as a
          feature network. This changes the default node size and color values
          and disables selection.
        """
        super().__init__()
        self.featureMode = featureMode

    def show(self, network, node_color = None, node_radius = None,
             node_label = None, link_color = None, link_width = None):
        """
        Updates the visualization with the given network, without loosing
        the layout of the network.

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
        self.network = export._to_dict(network, node_color, node_radius, 
                                       node_label, link_color, link_width)
