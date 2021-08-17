import dataclasses
import typing
from dataclasses import dataclass

from momotor.bundles import ConfigBundle, RecipeBundle, ProductBundle
from momotor.bundles.elements.content import NoContent
from momotor.bundles.elements.options import Option, OptionsMixin
from momotor.bundles.elements.steps import Step
from momotor.bundles.utils.domain import unsplit_domain

try:
    from typing import Literal  # 3.8+
except ImportError:
    from typing_extensions import Literal


__all__ = ['OptionDefinition', 'OptionProviders', 'OptionNameDomain', 'to_bool',
           'OptionTypeLiteral', 'OPTION_TYPE_MAP', 'OPTION_TYPE_CAST_MAP']

STR_BOOL = {
    'y': True,
    'yes': True,
    't': True,
    'true': True,
    'on': True,
    '1': True,

    'n': False,
    'no': False,
    'f': False,
    'false': False,
    'off': False,
    '0': False,
}


def to_bool(val: typing.Any) -> bool:
    """Convert a representation of truth to True or False.

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.

    >>> to_bool(True)
    True

    >>> to_bool('y')
    True

    >>> to_bool('yes')
    True

    >>> to_bool('t')
    True

    >>> to_bool('true')
    True

    >>> to_bool('on')
    True

    >>> to_bool('1')
    True

    >>> to_bool(1)
    True

    >>> to_bool(False)
    False

    >>> to_bool('n')
    False

    >>> to_bool('no')
    False

    >>> to_bool('f')
    False

    >>> to_bool('false')
    False

    >>> to_bool('off')
    False

    >>> to_bool('0')
    False

    >>> to_bool(0)
    False

    >>> to_bool(None)
    False

    >>> to_bool('other')
    Traceback (most recent call last):
    ...
    ValueError: invalid truth value 'other'


    """
    if val is None:
        return False
    if isinstance(val, (int, float, bool)):
        return bool(val)

    val = str(val).lower()
    try:
        return STR_BOOL[val]
    except KeyError:
        raise ValueError(f"invalid truth value {val!r}")


OptionTypeLiteral = Literal['str', 'bool', 'int', 'float']

OPTION_TYPE_MAP: typing.Dict[OptionTypeLiteral, typing.Type] = {
    'str': str,
    'bool': bool,
    'int': int,
    'float': float,
}

OPTION_TYPE_CAST_MAP: typing.Dict[OptionTypeLiteral, typing.Callable] = {
    **OPTION_TYPE_MAP,
    'bool': to_bool,
}


@dataclass(frozen=True)
class OptionProviders:
    """ The providers of option values.
    """

    #: The :py:class:`~momotor.bundles.elements.steps.Step`
    step: typing.Optional[Step] = None

    #: The :py:class:`~momotor.bundles.RecipeBundle`
    recipe: typing.Optional[RecipeBundle] = None

    #: The :py:class:`~momotor.bundles.ConfigBundle`
    config: typing.Optional[ConfigBundle] = None

    #: The :py:class:`~momotor.bundles.ProductBundle`
    product: typing.Optional[ProductBundle] = None


VALID_LOCATIONS = frozenset(field.name for field in dataclasses.fields(OptionProviders))


_NO_DEFAULT = object()


@dataclass(frozen=True)
class OptionDefinition:
    """ Definition of an option.

    Options are provided by steps, recipes, configs and products. When resolving the option to a value, these
    are inspected based on the :py:attr:`.location` attribute. Depending on the other settings like
    :py:attr:`.multiple` and :py:attr:`required` one or more option values are returned when resolving the option.
    """

    #: Name of the option. Required
    name: str

    #: Expected type of the option. Optional. If not set, the type as given by the <option> node is used
    #: as-is. Allowed values: ``str``, ``bool``, ``int`` and ``float``
    type: typing.Optional[OptionTypeLiteral] = None

    #: Documentation of the option
    doc: typing.Optional[str] = None

    #: This option is required. If the option is not defined by any of the providers, :py:meth:`.resolve` will throw a
    #: :py:exc:`ValueError` exception: Default: ``False``
    required: bool = False

    #: This option can be provided multiple times. If `True`, :py:meth:`.resolve` will return a FilterableTuple of
    #: matched options. If `False`, :py:meth:`.resolve` will return a single value, or throw a :py:exc:`ValueError`
    #: if multiple options match. Default: ``False``
    multiple: bool = False

    #: When :py:attr:`.multiple` is True, :py:meth:`.resolve` will match the first provider in :py:attr:`.location`
    #: that defines an option with the correct :py:attr:`.name` and :py:attr:`.domain`.
    #: Set :py:attr:`.all` to True to resolve all matching options of all providers listed in :py:attr:`location`.
    #: Has no effect when :py:attr:`.multiple` is False.
    all: bool = False

    #: The names and order of the providers :py:meth:`.resolve` looks for the options. Can be provided as a
    #: comma separated string, or as a sequence of strings. Default: `step, config, recipe`.
    #: When accessing, will always be a sequence
    location: typing.Union[str, typing.Sequence[str], None] = None

    #: The domain of the option:
    #: Momotor defines the following values for :py:attr:`.domain`:
    #:
    #: * **checklet**: (Default) These options are used by checklets.
    #: * **broker**: These options are used by the Momotor broker eg. for task scheduling purposes.
    #: * **x-...**: "Experimental", or private use domains
    #:
    #: Domain names starting with **x-** can be used for private use cases. All other domain names are reserved for
    #: use by Momotor in the future.
    #:
    #: Cannot have a subdomain.
    domain: typing.Optional[str] = None

    #: The default value if the option is not provided by any provider.
    default: typing.Any = _NO_DEFAULT

    #: If `False` this OptionDefinition will be disabled (ie. ignored as if it was not listed)
    enable: bool = True

    # Cast a value into the correct type for this option
    _cast: typing.Callable[[typing.Any], typing.Any] = dataclasses.field(init=False)

    def __post_init__(self):
        assert self.type is None or self.type in OPTION_TYPE_CAST_MAP
        assert self.domain is None or '#' not in self.domain

        # Turn `location` into a tuple
        location = self.location
        if location is None:
            location_seq = None
        elif isinstance(location, str):
            location_seq = tuple(loc.strip() for loc in location.split(','))
        else:
            location_seq = tuple(location)

        assert location_seq is None or set(location_seq) <= VALID_LOCATIONS

        object.__setattr__(self, 'location', location_seq)

        # Create self._cast helper
        cast = OPTION_TYPE_CAST_MAP.get(self.type, lambda value: value)
        object.__setattr__(self, '_cast', cast)

        # Cast default value to correct type
        if self.default is not _NO_DEFAULT:
            object.__setattr__(self, 'default', cast(self.default))

    def resolve(self, providers: OptionProviders,
                subdomains: typing.Dict[str, typing.Union[typing.Optional[str],
                                                          typing.Sequence[typing.Optional[str]]]] = None) -> typing.Any:
        """ Resolve the value of this option by inspecting the options of the providers.

        Sub-domains to look for can be specified for each provider.
        Options including a specified sub-domain take priority over options without the sub-domain.

        :param providers: The providers
        :param subdomains: For each provider, a sequence of subdomains to take into account when looking for
               options. Merged with :py:attr:`.domain`. Missing values and empty sequences are interpreted
               as containing ``None``.
        :return: The resolved option value. A tuple of values if :py:attr:`.multiple` is True.
        """
        assert self.enable

        def _get_loc_domain() -> typing.Generator[typing.Tuple[OptionsMixin, str], None, None]:
            # Collect pairs of (provider, domain). In order to guarantee priority for the most-specified domains, we
            # do two loops here, one for domains with subdomains, one for domains without.
            if subdomains:
                for loc in self.location:
                    prov = getattr(providers, loc)
                    if prov is not None and loc in subdomains:
                        loc_subdomains = subdomains.get(loc)

                        if not isinstance(loc_subdomains, (list, tuple)):
                            loc_subdomains = [loc_subdomains]

                        for loc_subdomain in loc_subdomains:
                            if loc_subdomain:
                                yield prov, unsplit_domain(self.domain, loc_subdomain)

            if self.location:
                for loc in self.location:
                    prov = getattr(providers, loc)
                    if prov is not None:
                        loc_subdomains = subdomains.get(loc, None) if subdomains else None
                        if not isinstance(loc_subdomains, (list, tuple)):
                            loc_subdomains = [loc_subdomains]

                        if not loc_subdomains or None in loc_subdomains or '' in loc_subdomains:
                            yield prov, self.domain

        matched = []
        for provider, domain in _get_loc_domain():
            try:
                options = provider.get_options(self.name, domain=domain)
            except KeyError:
                pass
            else:
                for option in options:
                    try:
                        matched.append(self._cast(option.value))
                    except NoContent:
                        pass

                if not self.all:
                    break

        if not matched:
            if self.required:
                raise ValueError("Required option missing")
            if self.default is not _NO_DEFAULT:
                matched.append(self.default)
            elif not self.multiple:
                matched.append(None)

        return tuple(matched) if self.multiple else matched[0]


@dataclass(frozen=True)
class OptionNameDomain:
    name: str
    domain: str = Option.DEFAULT_DOMAIN

    def __str__(self):
        if self.domain == Option.DEFAULT_DOMAIN:
            return self.name
        else:
            return f'{self.name}@{self.domain}'
