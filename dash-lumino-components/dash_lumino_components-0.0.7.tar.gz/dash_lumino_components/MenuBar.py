# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class MenuBar(Component):
    """A MenuBar component.
A widget which displays menus as a canonical menu bar.  
{@link https://jupyterlab.github.io/lumino/widgets/classes/menubar.html}
@hideconstructor

@example
//Python:
import dash
import dash_lumino_components as dlc

menuBar = dlc.MenuBar([
    dlc.Menu([
        dlc.Command(id="com:openwidget", label="Open", icon="fa fa-plus"),
    ], id="exampleMenu", title="Example")
], 'menuBar')

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    An array of the menus (dlc.Menu) @type {Menu[]}.

- id (string; required):
    ID of the widget @type {string}."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.REQUIRED, **kwargs):
        self._prop_names = ['children', 'id']
        self._type = 'MenuBar'
        self._namespace = 'dash_lumino_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(MenuBar, self).__init__(children=children, **args)
