# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import abc
import six

from anna.adaptors import ConfigurationAdaptor as Adaptor
from anna.dependencies import Dependency
from anna.exceptions import ConfigurationError
from anna.parameters import ActionParameter, AwareParameter, Parameter, \
    PhysicalQuantityParameterBase, StringParameter
from anna.utils import convert_to_json_serializable_object, to_json_string


class _ConfigMeta(abc.ABCMeta):
    # noinspection PyInitNewSignature
    def __new__(mcs, name, bases, attributes):
        config_path = attributes.get('CONFIG_PATH', None)
        if config_path is None:
            # Only set the config path if the class inherits from Configurable (not if this is
            # the creation of Configurable itself - which only inherits from object).
            if set(sum(map(
                lambda base_: base_.__mro__,
                bases
            ), ())) != {object}:
                inherited_by = map(
                    lambda base_: getattr(base_, 'CONFIG_PATH', None) is not None,
                    bases
                )
                if not any(inherited_by):
                    config_path = Adaptor.join_paths(name, 'Parameters')
                    attributes['CONFIG_PATH'] = config_path
                else:
                    config_path = list(filter(
                        lambda item: item is not None,
                        map(
                            lambda base_: getattr(base_, 'CONFIG_PATH', None),
                            bases
                        )
                    ))[0]
        # Copy inherited parameters and update their config paths.
        for base in bases:
            if hasattr(base, 'get_parameters') and callable(getattr(base, 'get_parameters')):
                for parameter in base.get_parameters():
                    if parameter.field_name not in attributes:
                        attributes[parameter.field_name] = parameter.copy()
                        attributes[parameter.field_name].path = config_path
        return super(_ConfigMeta, mcs).__new__(mcs, name, bases, attributes)

    def __setattr__(cls, key, value):
        if isinstance(value, Parameter):
            if isinstance(value, ActionParameter):
                parameters_by_name = {p.name: p for p in cls.get_parameters()}
                try:
                    value.depends_on = map(
                        lambda d: parameters_by_name[d] if isinstance(d, six.text_type) else d,
                        value.depends_on
                    )
                except KeyError as err:
                    ValueError('Dependency "%s" does not resolve' % six.text_type(err))
            value._field_name = key
            return super(_ConfigMeta, cls).__setattr__(
                key, AwareParameter(value, getattr(cls, 'CONFIG_PATH'))
            )
        else:
            super(_ConfigMeta, cls).__setattr__(key, value)

    def __str__(cls):
        return to_json_string({
            parameter.field_name: parameter.as_json()
            for parameter in cls.get_parameters()
        })

    def get_parameters(cls):
        return filter(
            lambda x: isinstance(x, (AwareParameter, Parameter)),
            map(lambda field_name: getattr(cls, field_name), dir(cls))
        )


class Configurable(six.with_metaclass(_ConfigMeta, object)):
    """
    Base class for components that can be configured. A component can be be assigned
    parameters either by using :func:`parametrize` or by setting the parameters as
    class attributes directly. Initializing the component with a configuration adaptor
    then loads the specified values as attributes of the instance in order to match
    the parameter declarations.
    The parameter specifications are retrieved from the configuration adaptor based on
    their configuration path which is compound of the component's base configuration path
    and the parameter name. The component's base configuration path can set via the class
    attribute ``CONFIG_PATH``. If it is missing or ``None`` then the following default base
    path is used: ``'<class-name>/Parameters'``.

    Examples
    --------
    Default ``CONFIG_PATH``:

    >>> from anna import parametrize, Integer, String, JSONAdaptor
    >>> @parametrize(
    ... Integer('SomeInteger'),
    ... String('SomeString')
    ... )
    ... class Component(Configurable):
    ...     def __init__(self, configuration):
    ...         super(Component, self).__init__(configuration)
    ...
    >>> config = JSONAdaptor(root={
    ... 'Component/Parameters/SomeInteger': '42',
    ... 'Component/Parameters/SomeString': 'I am a string.',
    ... })
    >>> component = Component(config)
    >>> component._some_integer
    42
    >>> component._some_string
    'I am a string.'

    Specifying ``CONFIG_PATH``:

    >>> from anna import Number, PhysicalQuantity, Vector
    >>> @parametrize(
    ... Vector[Number]('Limits'),
    ... PhysicalQuantity('Height', unit='mm')
    ... )
    ... class Component(Configurable):
    ...     CONFIG_PATH = 'CustomPath'
    ...     def __init__(self, configuration):
    ...             super(Component, self).__init__(configuration)
    ...
    >>> config = JSONAdaptor(root={
    ... 'CustomPath/Limits': '[ 1.0, 2.0, 3.0 ]',
    ... 'CustomPath/Height': {
    ...     'text': '5.0',
    ...     'meta': {'unit': 'm'}
    ... }})
    >>> component = Component(config)
    >>> component._limits
    [ 1.,  2.,  3.]
    >>> component._height
    5000.0
    """

    CONFIG_PATH = None

    def __init__(self, configuration=None):
        """
        If no configuration is provided then all parameters of this component must be either
        optional or have default values. Otherwise initialization will fail as the component
        would remain in an incompletely configured state.

        Parameters
        ----------
        configuration : :class:`ConfigurationAdaptor`, optional

        Raises
        ------
        ConfigurationError
            If no configuration is provided and the component has non-optional, non-default
            parameters.
        """
        super(Configurable, self).__init__()

        parameters = self.get_parameters()
        if configuration is None and any(filter(lambda p: not p.is_expert, parameters)):
            raise ConfigurationError(
                'Component %s did not receive a configuration source however would remain in '
                'an incompletely configured state as it contains parameters without default values'
                % self.__class__.__name__
            )
        for parameter in parameters:
            setattr(self, parameter.field_name, parameter.load_from_configuration(configuration))

    def __str__(self):
        return to_json_string(self.as_json())

    def as_json(self):
        """
        JSON serializable representation of the declared parameters' values.

        Returns
        -------
        json : dict
        """
        return {
            '{0} => {1}'.format(parameter.name, parameter.field_name):
                convert_to_json_serializable_object(getattr(self, parameter.field_name))
            for parameter in self.get_parameters()
        }

    @classmethod
    def get_parameters(cls):
        """
        Retrieve all parameters that have been declared on this component.

        Returns
        -------
        parameters : list
        """
        return list(filter(
            lambda x: isinstance(x, (AwareParameter, Parameter)),
            map(
                lambda field_name: getattr(cls, field_name),
                dir(cls)
            )
        ))


def adopt(*components, **kwargs):
    """
    Use this function to adopt parameters from other components.
    
    .. note::
    This decorator does not adjust the config path of the decorated component. It only uses the
    specified (or derived) config path for creating the adopted parameters. Additional parameters
    that are set on this component will use the native config path.
     
    Parameters
    ----------
    *components
        Subclasses of :class:`Configurable`.
    **kwargs
        Use the key ``config_path`` to specify a new configuration path to be used for the adopted
        parameters. If multiple components are given then the configuration path must be specified
        in order to avoid ambiguities. If a single component is specified its configuration path
        is used as a default.
        
    Returns
    -------
    callable
        Class decorator which adopts the parameters of the specified components.
    """
    if not components:
        raise ValueError('Need at least one component to adopt')
    config_path = kwargs.get('config_path')
    if len(components) > 1 and config_path is None:
        raise ValueError(
            'A configuration path must be specified if multiple components are adopted'
        )
    if config_path is None:
        config_path = components[0].CONFIG_PATH

    def add_parameters(cls):
        for component in components:
            for parameter in component.get_parameters():
                setattr(
                    cls,
                    parameter.field_name,
                    AwareParameter(parameter.parameter, config_path)
                )
        return cls
    return add_parameters


def depends_on(*components):
    """
    Use this function to declare a number of components as dependencies for
    the decorated class. Dependencies will show up in the corresponding GUI form
    of the decorated component however they need to maintain an independent ``CONFIG_PATH``.

    Parameters
    ----------
    *components
        Subclasses of :class:`Configurable`.

    Returns
    -------
    callable
        Class decorator which declares the specified dependencies on the given class.

    Examples
    --------
    >>> from anna import Configurable, depends_on, parametrize, String
    >>> @parametrize(
    ... String('Type')
    ... )
    ... class Motor(Configurable):
    ...     def __init__(self, configuration):
    ...             super(Motor, self).__init__(configuration)
    ...
    >>> @depends_on(Motor)
    ... @parametrize(
    ... String('Model')
    ... )
    ... class Car(Configurable):
    ...     def __init__(self, configuration):
    ...             super(Car, self).__init__(configuration)
    ...
    If ``Car`` is configured via the GUI then ``Motor`` will automatically show up as well.
    """
    def add_dependency(cls):
        for component in components:
            setattr(
                cls,
                '_depends_on_%s' % component.__name__,
                Dependency(component)
            )
        return cls
    return add_dependency


def parametrize(*parameters, **parameters_with_field_name):
    """
    Use this function to generate a decorator which declares the specified parameters
    on a component. It takes a list of parameters as arguments and optionally a list of
    keyword arguments which lets you specify custom field names (keys are field names,
    values are parameters).
    When declaring the specified parameters by decorating a class, if the class does not
    specify a ``CONFIG_PATH``, the following config path is used as a default:
    ``'<class-name>/Parameters'``.
    Also any by-name dependencies of :class:`ActionParameter`s are resolved properly to
    their :class:`AwareParameter` counterparts.

    Parameters
    ----------
    *parameters
        A number of parameters (subclasses of :class:`Parameter`).
    **parameters_with_field_name
        A number of parameters (subclasses of :class:`Parameter`)
        where the corresponding keys are used as custom field names.

    Returns
    -------
    callable
        Class decorator which declares the specified parameters on the given class.

    Raises
    ------
    ValueError
        If two parameter field names clash.
        If an :class:`ActionParameter` declares an invalid dependency.

    Examples
    --------
    >>> from anna import Configurable, parametrize, String
    >>> @parametrize(
    ...     String('Brand'),
    ...     String('Model')
    ... )
    ... class Car(Configurable):
    ...     def __init__(self, config):
    ...         super(Car, self).__init__(config))
    """
    # Check if parameter names clash.
    all_field_names = (
        set(map(lambda p: p.field_name, parameters))
        | set(parameters_with_field_name)
    )
    if len(all_field_names) < len(parameters) + len(parameters_with_field_name):
        raise ValueError('At least two parameter field names clash')

    all_parameters = list(parameters) + list(parameters_with_field_name.values())

    # Check if all dependencies can be resolved to their targets. A target can be specified
    # either via an AwareParameter instance or via a string that refers to the name of a
    # parameter withing the same component.
    # We also need to replace string indicators with their AwareParameter counterparts.
    parameter_names = map(lambda p: p.name, all_parameters)
    for parameter in all_parameters:
        if isinstance(parameter, ActionParameter):
            for dependency in parameter.depends_on:
                if isinstance(dependency, six.text_type):
                    if dependency == parameter.name:
                        raise ValueError(
                            'Parameters cannot depend on themselves (%s)'
                            % parameter.name
                        )
                    if dependency not in parameter_names:
                        raise ValueError(
                            'Dependency "%s" declared by parameter %s does not resolve'
                            % (dependency, parameter.name)
                        )

    # Update field names of keyword parameters.
    for field_name, parameter in iter(parameters_with_field_name.items()):
        parameter.field_name = field_name

    field_names_and_parameters = [(param.field_name, param) for param in parameters] + \
                                 [(param.field_name, param)
                                  for param in parameters_with_field_name.values()]
    # Reorder parameters so that ones serving as dependencies are processed before
    # those declaring the dependencies, so any string dependencies can be replaced properly
    # by their AwareParameter counterparts later on.
    non_action_pars = list(filter(
        lambda fn_p: not isinstance(fn_p[1], ActionParameter),
        field_names_and_parameters
    ))
    action_pars = list(filter(
        lambda fn_p: isinstance(fn_p[1], ActionParameter),
        field_names_and_parameters
    ))
    field_names_and_parameters = non_action_pars + action_pars

    # noinspection PyShadowingNames
    def add_parameters(cls):
        # If the config path has not been specified use the component's name.
        if not hasattr(cls, 'CONFIG_PATH') or cls.CONFIG_PATH is None:
            config_path = Adaptor.join_paths(cls.__name__, 'Parameters')
        else:
            config_path = cls.CONFIG_PATH
        aware_parameters_by_name = {}
        for field_name, parameter in field_names_and_parameters:
            if isinstance(parameter, ActionParameter):
                parameter.depends_on = tuple(map(
                    lambda d: aware_parameters_by_name[d] if isinstance(d, six.text_type) else d,
                    parameter.depends_on
                ))
            aware_parameter = AwareParameter(parameter, config_path)
            aware_parameters_by_name[parameter.name] = aware_parameter
            setattr(cls, field_name, aware_parameter)
        # Resolve dependencies of ActionParameters.
        for field_name, parameter in action_pars:
            parameter.depends_on = tuple(map(
                lambda d: aware_parameters_by_name[d] if isinstance(d, six.text_type) else d,
                parameter.depends_on
            ))
        return cls
    return add_parameters


class _DocumentParametersWrapper(object):
    """
    Decorator for documenting parameters. Applying ``@document_parameters`` uses
    the default values for options. Custom values for options can be specified using
    the syntax ``@document_parameters[{document_optionals: False}]``. The options
    need to be given as a dict. The following options are available:

    * ``"max_width"``: Determines the maximum text width (text will wrapped around after
      reaching this character limit); default is ``120``
    * ``"document_optionals"``: Determines whether optional parameters should be documented;
      default is ``True``
    """

    def __init__(self):
        super(_DocumentParametersWrapper, self).__init__()

    def __call__(self, cls):
        return self._document_parameters()(cls)

    def __getitem__(self, options):
        return self._document_parameters(**options)

    @staticmethod
    def _document_parameters(max_width=120, document_optionals=True):
        def decorator(cls):
            if not issubclass(cls, Configurable):
                raise TypeError('Can only document parameters of subclasses of Configurable')
            aware_parameters = cls.get_parameters()
            if not aware_parameters:
                return

            def wrap(text, indent):
                return _DocumentParametersWrapper._wrap(text, max_width, indent=indent)

            path = aware_parameters[0].path
            doc = cls.__doc__
            if doc is None:
                doc = '\n'
            else:
                doc += '\n\n'
            doc += wrap('Declared parameters', indent=4) + '\n'
            doc += wrap('-------------------', indent=4) + '\n'
            doc += wrap('(configuration path: {0})'.format(path), indent=4) + '\n\n'
            required_parameters = filter(
                lambda p: not p.is_expert and not p.is_optional,
                aware_parameters
            )
            optional_parameters = filter(
                lambda p: p.is_expert or p.is_optional,
                aware_parameters
            )
            doc = _DocumentParametersWrapper._add_required_parameters(
                doc, required_parameters, max_width
            )
            if document_optionals:
                doc += '\n'
                doc = _DocumentParametersWrapper._add_optional_parameters(
                    doc, optional_parameters, max_width
                )
            cls.__doc__ = doc
            return cls
        return decorator

    @staticmethod
    def _add_required_parameters(doc, aware_parameters, max_width):
        if not aware_parameters:
            return doc

        def wrap(text, indent):
            return _DocumentParametersWrapper._wrap(text, max_width, indent=indent)

        doc += wrap('Required', indent=4) + '\n'
        doc += wrap('~~~~~~~~', indent=4) + '\n'

        for aware_parameter in sorted(aware_parameters, key=lambda p: p.name):
            parameter = aware_parameter.parameter
            if isinstance(parameter, ActionParameter):
                parameter = parameter.parameter
            doc += wrap(
                '{0} : {1}'.format(
                    parameter.name,
                    parameter.__class__.__name__.replace('Parameter', '')
                ),
                indent=4
            ) + '\n'
            if isinstance(parameter, PhysicalQuantityParameterBase):
                doc += wrap('unit: {0}'.format(parameter.unit), indent=8) + '\n'
            if parameter.info is not None:
                doc += wrap(parameter.info, indent=8) + '\n'
        return doc

    @staticmethod
    def _add_optional_parameters(doc, aware_parameters, max_width):
        if not aware_parameters:
            return doc

        def wrap(text, indent):
            return _DocumentParametersWrapper._wrap(text, max_width, indent=indent)

        doc += wrap('Optional', indent=4) + '\n'
        doc += wrap('~~~~~~~~', indent=4) + '\n'

        for aware_parameter in sorted(aware_parameters, key=lambda p: p.name):
            parameter = aware_parameter.parameter
            if isinstance(parameter, ActionParameter):
                parameter = parameter.parameter
            if isinstance(parameter, StringParameter):
                default_value = '"{0}"'.format(parameter.default)
            else:
                default_value = '{0}'.format(parameter.default)
            doc += wrap(
                '{0} : {1}'.format(parameter.name,
                                   parameter.__class__.__name__.replace('Parameter', '')),
                indent=4
            ) + '\n'
            doc += wrap('defaults to: {0}'.format(default_value), indent=8) + '\n'
            if parameter.info is not None:
                doc += wrap(parameter.info, indent=8) + '\n'
        return doc

    @staticmethod
    def _wrap(text, max_width, indent=0):
        import textwrap
        if isinstance(indent, int):
            indent_str = indent * ' '
        elif isinstance(indent, six.text_type):
            indent_str = indent
        else:
            raise TypeError('indent must be either int or unicode')
        return textwrap.fill(text, width=max_width, initial_indent=indent_str,
                             subsequent_indent=indent_str)

document_parameters = _DocumentParametersWrapper()
