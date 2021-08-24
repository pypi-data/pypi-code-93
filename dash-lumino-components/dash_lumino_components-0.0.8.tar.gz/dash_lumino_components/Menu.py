# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Menu(Component):
    """A Menu component.
A widget which displays items as a canonical menu.  
{@link https://jupyterlab.github.io/lumino/widgets/classes/menu.html}
@hideconstructor

@example
//Python:
import dash
import dash_lumino_components as dlc


menu = dlc.Menu([
    dlc.Command(id="com:openwidget", label="Open", icon="fa fa-plus"),
    dlc.Separator(),
    dlc.Menu([
        dlc.Command(id="com:closeall", label="Close All", icon="fa fa-minus"),
        dlc.Command(id="com:closeone",
                    label="Close One", icon="fa fa-minus"),
    ], id="extraMenu", title="Extra")
], id="openMenu", title="Widgets")

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    An array of the menu items (dlc.Command | dlc.Menu |
    dlc.Separator) @type {Array<Command, Menu, Separator>}.

- id (string; required):
    The ID used to identify this component in Dash callbacks. @type
    {string}.

- iconClass (string; optional):
    The icon class of the menu @type {string}.

- title (string; optional):
    The title of the menu @type {string}."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.REQUIRED, title=Component.UNDEFINED, iconClass=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'iconClass', 'title']
        self._type = 'Menu'
        self._namespace = 'dash_lumino_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'iconClass', 'title']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Menu, self).__init__(children=children, **args)
