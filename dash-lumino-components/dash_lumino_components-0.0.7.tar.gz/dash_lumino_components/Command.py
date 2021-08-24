# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Command(Component):
    """A Command component.
A widget which displays items as a canonical menu.
@hideconstructor

@example
//Python:
import dash
import dash_lumino_components as dlc

command_open = dlc.Command(id="com:openwidget", label="Open", icon="fa fa-plus")

Keyword arguments:

- id (string; optional):
    The id of the command @type {string}.

- icon (string; optional):
    The icon of the command (a cass class name) @type {string}.

- label (string; optional):
    The label of the command @type {string}.

- n_called (number; default 0):
    Number of times the command was called @type {number}.

- n_called_timestamp (number; default -1):
    Last time that command was called. @type {number}."""
    @_explicitize_args
    def __init__(self, id=Component.UNDEFINED, label=Component.UNDEFINED, icon=Component.UNDEFINED, n_called=Component.UNDEFINED, n_called_timestamp=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'icon', 'label', 'n_called', 'n_called_timestamp']
        self._type = 'Command'
        self._namespace = 'dash_lumino_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'icon', 'label', 'n_called', 'n_called_timestamp']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in []:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(Command, self).__init__(**args)
