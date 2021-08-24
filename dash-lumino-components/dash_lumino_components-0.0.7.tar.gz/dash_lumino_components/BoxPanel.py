# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class BoxPanel(Component):
    """A BoxPanel component.
A panel which arranges its widgets in a single row or column.  
{@link https://jupyterlab.github.io/lumino/widgets/classes/boxpanel.html}
@hideconstructor

@example
//Python:
import dash
import dash_lumino_components as dlc

boxPanel = dlc.BoxPanel([
  dlc.SplitPanel([], id="split-panel")
], id="box-panel")

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The widgets @type {Array<Panel, SplitPanel, DockPanel>}.

- id (string; required):
    ID of the widget @type {string}.

- addToDom (boolean; default False):
    bool if the object has to be added to the dom directly @type
    {boolean}.

- alignment (string; default 'start'):
    the content alignment of the layout (\"start\" | \"center\" |
    \"end\" | \"justify\") @type {string}.

- direction (string; default 'left-to-right'):
    a type alias for a box layout direction (\"left-to-right\" |
    \"right-to-left\" | \"top-to-bottom\" | \"bottom-to-top\") @type
    {string}.

- spacing (number; default 0):
    The spacing between items in the layout @type {number}."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.REQUIRED, alignment=Component.UNDEFINED, direction=Component.UNDEFINED, spacing=Component.UNDEFINED, addToDom=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'addToDom', 'alignment', 'direction', 'spacing']
        self._type = 'BoxPanel'
        self._namespace = 'dash_lumino_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'addToDom', 'alignment', 'direction', 'spacing']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(BoxPanel, self).__init__(children=children, **args)
