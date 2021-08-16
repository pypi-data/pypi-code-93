# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class WellLogViewer(Component):
    """A WellLogViewer component.


Keyword arguments:

- id (string; required):
    The ID of this component, used to identify dash components in
    callbacks. The ID needs to be unique across all of the components
    in an app.

- template (dict; optional)

- welllog (list; optional)"""
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, welllog=Component.UNDEFINED, template=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'template', 'welllog']
        self._type = 'WellLogViewer'
        self._namespace = 'webviz_subsurface_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'template', 'welllog']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(WellLogViewer, self).__init__(**args)
