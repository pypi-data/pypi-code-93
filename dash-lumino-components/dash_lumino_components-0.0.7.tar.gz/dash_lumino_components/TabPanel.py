# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class TabPanel(Component):
    """A TabPanel component.
A widget which combines a TabBar and a StackedPanel.  
{@link https://jupyterlab.github.io/lumino/widgets/classes/tabpanel.html}

This is a simple panel which handles the common case of a tab bar placed
next to a content area. The selected tab controls the widget which is
shown in the content area.
For use cases which require more control than is provided by this panel,
the TabBar widget may be used independently.
@hideconstructor

@example
//Python:
import dash
import dash_lumino_components as dlc
import dash_html_components as html
import dash_bootstrap_components as dbc

tabPanel = dlc.TabPanel(
    [
        dlc.Panel(
            html.Div([
                dbc.Button("Open Plot",
                           id="button2",
                           style={"width": "100%"})
            ]),
            id="tab-panel-A"
            label="Plots",
            icon="fa fa-bar-chart")
    ],
    id='tab-panel-left')

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The widgets @type {Panel[]}.

- id (string; required):
    ID of the widget @type {string}.

- addToDom (boolean; default False):
    bool if the object has to be added to the dom directly @type
    {boolean}.

- allowDeselect (boolean; default False):
    bool if all tabs can be deselected @type {boolean}.

- currentIndex (number; default -1):
    Get the index of the currently selected tab. It will be -1 if no
    tab is selected. @type {number}.

- tabPlacement (string; default 'top'):
    the placement of the tab bar relative to the content. (\"left\" |
    \"right\" | \"top\" | \"bottom\") @type {string}.

- tabsMovable (boolean; default False):
    whether the tabs are movable by the user @type {boolean}.

- width (number; default 250):
    the default width or height of the tab panel content @type
    {number}."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.REQUIRED, tabPlacement=Component.UNDEFINED, tabsMovable=Component.UNDEFINED, allowDeselect=Component.UNDEFINED, width=Component.UNDEFINED, addToDom=Component.UNDEFINED, currentIndex=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'addToDom', 'allowDeselect', 'currentIndex', 'tabPlacement', 'tabsMovable', 'width']
        self._type = 'TabPanel'
        self._namespace = 'dash_lumino_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'addToDom', 'allowDeselect', 'currentIndex', 'tabPlacement', 'tabsMovable', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(TabPanel, self).__init__(children=children, **args)
