# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Panel(Component):
    """A Panel component.
A simple and convenient panel widget class.  
{@link https://jupyterlab.github.io/lumino/widgets/classes/panel.html}

This class is suitable to directly display a collection of dash widgets.
@hideconstructor

@example
//Python:
import dash_lumino_components as dlc
import dash_html_components as html

panelA = dlc.Panel(
    id="panelA",
    children=html.Div("Content"),
    label="Test",
    icon="fa fa-plus")

panelB = dlc.Panel(
    [
        html.Div("Content")
    ],
    id="panelB",
    label="Test",
    icon="fa fa-plus")

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The widgets @type {Object | Array<Object>}.

- id (string; required):
    ID of the widget @type {string}.

- addToDom (boolean; default False):
    bool if the object has to be added to the dom directly @type
    {boolean}.

- icon (string; optional):
    The icon of the panel (a cass class name) @type {string}.

- label (string; optional):
    The label of the panel @type {string}."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.REQUIRED, label=Component.UNDEFINED, icon=Component.UNDEFINED, addToDom=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'addToDom', 'icon', 'label']
        self._type = 'Panel'
        self._namespace = 'dash_lumino_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'addToDom', 'icon', 'label']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Panel, self).__init__(children=children, **args)
