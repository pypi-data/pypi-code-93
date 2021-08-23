# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class DeckGLMap(Component):
    """A DeckGLMap component.


Keyword arguments:

- id (string; required):
    The ID of this component, used to identify dash components in
    callbacks. The ID needs to be unique across all of the components
    in an app.

- coords (dict; default {    visible: True,    multiPicking: True,    pickDepth: 10,}):
    Parameters for the coordinates component.

    `coords` is a dict with keys:

    - multiPicking (boolean; optional)

    - pickDepth (number; optional)

    - visible (boolean; optional)

- deckglSpecBase (dict; optional):
    JSON object describing the map structure to which deckglSpecPatch
    will be applied in order to form the final map specification. More
    detailes about the specification format can be found here:
    https://deck.gl/docs/api-reference/json/conversion-reference.

- deckglSpecPatch (list of dicts; optional):
    A JSON patch (http://jsonpatch.com/) applied to deckglSpecBase.
    This split (base + patch) allows doing partial updates to the map
    while keeping the map state in the Dash store, as well as making
    it easier for the Dash component user to figure out what changed
    in the map spec when recieving a callback on the python side.

- resources (dict; optional):
    Resource dictionary made available in the DeckGL specification as
    an enum. The values can be accessed like this:
    `\"@@#resources.resourceId\"`, where `resourceId` is the key in
    the `resources` dict. For more information, see the DeckGL
    documentation on enums in the json spec:
    https://deck.gl/docs/api-reference/json/conversion-reference#enumerations-and-using-the--prefix."""
    @_explicitize_args
    def __init__(self, id=Component.REQUIRED, resources=Component.UNDEFINED, deckglSpecBase=Component.UNDEFINED, deckglSpecPatch=Component.UNDEFINED, coords=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'coords', 'deckglSpecBase', 'deckglSpecPatch', 'resources']
        self._type = 'DeckGLMap'
        self._namespace = 'webviz_subsurface_components'
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'coords', 'deckglSpecBase', 'deckglSpecPatch', 'resources']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs
        args = {k: _locals[k] for k in _explicit_args if k != 'children'}
        for k in ['id']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')
        super(DeckGLMap, self).__init__(**args)
