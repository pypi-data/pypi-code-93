# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class SplitPanel(Component):
    """A SplitPanel component.
A panel which arranges its widgets into resizable sections.   
{@link https://jupyterlab.github.io/lumino/widgets/classes/splitpanel.html}
@hideconstructor

@example
//Python:
import dash
import dash_lumino_components as dlc

splitPanel = dlc.SplitPanel([
    dlc.TabPanel([], id="tab-panel"),
    dlc.DockPanel([], id="dock-panel")
], id="split-panel")

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The widgets @type {Array<DockPanel, TabPanel, BoxPanel, Panel>}.

- id (string; required):
    ID of the widget @type {string}.

- addToDom (boolean; default False):
    bool if the object has to be added to the dom directly @type
    {boolean}.

- alignment (string; default 'start'):
    the content alignment of the layout (\"start\" | \"center\" |
    \"end\" | \"justify\") @type {string}.

- orientation (string; default 'horizontal'):
    a type alias for a split layout orientation (\"horizontal\" |
    \"vertical\") @type {string}.

- spacing (number; default 0):
    The spacing between items in the layout @type {number}."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.REQUIRED, alignment=Component.UNDEFINED, orientation=Component.UNDEFINED, spacing=Component.UNDEFINED, addToDom=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'addToDom', 'alignment', 'orientation', 'spacing']
        self._type = 'SplitPanel'
        self._namespace = 'dash_lumino_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'addToDom', 'alignment', 'orientation', 'spacing']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(SplitPanel, self).__init__(children=children, **args)
