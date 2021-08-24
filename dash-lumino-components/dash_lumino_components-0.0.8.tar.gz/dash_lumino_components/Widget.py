# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Widget(Component):
    """A Widget component.
The base class of the lumino widget hierarchy.  
{@link https://jupyterlab.github.io/lumino/widgets/classes/widget.html}

This class will typically be subclassed in order to create a useful
widget. However, it can be used directly to host externally created
content.
@hideconstructor

@example
//Python:
import dash
import dash_lumino_components as dlc

dock = dlc.DockPanel([
    dlc.Widget(
        "Content",
        id="test-widget",
        title="Title",
        icon="fa fa-folder-open",
        closable=True,
        caption="Hover label of the widget"
    )],
    id="dock-panel")

Keyword arguments:

- children (a list of or a singular dash component, string or number; optional):
    The children of this component @type {Object | Object[]}.

- id (string; required):
    ID of the widget @type {string}.

- caption (string; optional):
    The long title of the widget @type {string}.

- closable (boolean; default True):
    Is the widget closable @type {boolean}.

- deleted (boolean; default False):
    Is the widget deleted. Note: In the future this might dissapear
    and the deleted widgets are automatically removed from the dom.
    @type {boolean}.

- icon (string; optional):
    The icon of the widget (a cass class name) @type {string}.

- title (string; required):
    The title of the widget @type {string}."""
    @_explicitize_args
    def __init__(self, children=None, id=Component.REQUIRED, title=Component.REQUIRED, closable=Component.UNDEFINED, caption=Component.UNDEFINED, deleted=Component.UNDEFINED, icon=Component.UNDEFINED, **kwargs):
        self._prop_names = ['children', 'id', 'caption', 'closable', 'deleted', 'icon', 'title']
        self._type = 'Widget'
        self._namespace = 'dash_lumino_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['children', 'id', 'caption', 'closable', 'deleted', 'icon', 'title']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id', 'title']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Widget, self).__init__(children=children, **args)
