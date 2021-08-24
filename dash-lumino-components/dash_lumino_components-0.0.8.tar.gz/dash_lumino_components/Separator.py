# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Separator(Component):
    """A Separator component.
A dummy widget to create a seperation in menus.  
This is actually not a component of lumino.
@hideconstructor

@example
//Python:
import dash
import dash_lumino_components as dlc

menu = dlc.Menu([
    dlc.Command(id="com:openwidget", label="Open", icon="fa fa-plus"),
    dlc.Separator(),
    dlc.Command(id="com:closeall", label="Close All", icon="fa fa-minus")
], id="openMenu", title="File")

Keyword arguments:

- id (string; optional):
    The id of the separator @type {string}."""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id']
        self._type = 'Separator'
        self._namespace = 'dash_lumino_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Separator, self).__init__(**args)
