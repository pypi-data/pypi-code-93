# -*- coding: utf-8 -*-

from __future__ import unicode_literals

"""
This module provides classes which can be used to declare parameters of various
types on components.
"""

import abc
import numbers
import os
import re
import six

import numpy

import anna.datatypes as datatypes
from anna.exceptions import IncompleteConfigurationError, InvalidPathError, \
    RepresentationError, InvalidUnitError, UnknownUnitError, ValueError_, ParameterError, SpecificationError
from anna.input import Unit, Value
from anna.utils import convert_camel_case_to_snake_case, safe_math_eval, supply_with_constants, \
    to_json_string, use_docs_from


@six.python_2_unicode_compatible
class AwareParameter(object):
    """
    Parameter wrapper that is aware of the wrapped parameter's location within
    the configuration source.
    """

    def __init__(self, parameter, path):
        self._parameter = parameter
        self._path = path

    def __getattr__(self, item):
        try:
            return getattr(self._parameter, item)
        except AttributeError:
            raise AttributeError('Parameter "%s" has no attribute "%s"' % (self, item))

    def __repr__(self):
        return '{0}({1}, {2})'.format(
            self.__class__.__name__,
            '%r' % self._parameter,
            '%r' % self._path
        )

    def __str__(self):
        """
        JSON decodable string representation of the parameter.

        Returns
        -------
        unicode
        """
        return to_json_string(self.as_json())

    def as_json(self):
        """
        JSON compatible representation of the parameter.

        Returns
        -------
        dict
        """
        return dict(parameter=self._parameter.as_json(), path=self._path)

    def copy(self):
        """
        Create a deep copy of this parameter.

        Returns
        -------
        copy : AwareParameter
        """
        return self.__class__(self._parameter, self._path)

    @property
    def parameter(self):
        """
        The wrapped parameter.

        Returns
        -------
        parameter : :class:`Parameter` derived class
        """
        return self._parameter

    @property
    def path(self):
        """
        The path at which the wrapped parameter is to be found within a configuration source.

        Returns
        -------
        path : unicode
        """
        return self._path

    @path.setter
    def path(self, value):
        """
        Set the path where the wrapped parameter is to be found within a configuration source.

        Parameters
        ----------
        value : unicode
        """
        self._path = value

    def load_from_configuration(self, configuration):
        """
        Load the wrapped parameter's value from the specified configuration source and
        convert it to its corresponding native representation (data type).

        Parameters
        ----------
        configuration : :class:`ConfigurationAdaptor` derived class
            The configuration adaptor representing the configuration source.

        Returns
        -------
        native_representation
            The wrapped parameter's native representation which is derived from
            the text/meta representation that is provided by the configuration source.
        """
        try:
            return self._parameter.load_from_configuration(configuration, self._path)
        except ParameterError as err:
            raise type(err)(err.reason, self)

    def load_from_representation(self, *args, **kwargs):
        """
        Proxy for the wrapped parameter's ``load_from_representation`` method which catches any
        ``ParameterError``s and re-raises them with the ``AwareParameter`` instance as argument
        (in order to provide information about the parameter's path).
        
        See Also
        --------
        :method:`Parameter.load_from_representation`
        """
        try:
            return self._parameter.load_from_representation(*args, **kwargs)
        except ParameterError as err:
            raise type(err)(err.reason, self)

    def convert_representation(self, *args, **kwargs):
        """
        Proxy for the wrapped parameter's ``convert_representation`` method which catches any
        ``ParameterError``s and re-raises them with the ``AwareParameter`` instance as argument
        (in order to provide information about the parameter's path).
        
        See Also
        --------
        :method:`Parameter.convert_representation`
        """
        try:
            return self._parameter.convert_representation(*args, **kwargs)
        except ParameterError as err:
            raise type(err)(err.reason, self)

    def validate_representation(self, *args, **kwargs):
        """
        Proxy for the wrapped parameter's ``validate_representation`` method which catches any
        ``ParameterError``s and re-raises them with the ``AwareParameter`` instance as argument
        (in order to provide information about the parameter's path).
        
        See Also
        --------
        :method:`Parameter.validate_representation` 
        """
        try:
            return self._parameter.validate_representation(*args, **kwargs)
        except ParameterError as err:
            raise type(err)(err.reason, self)

    def validate_specification(self, *args, **kwargs):
        """
        Proxy for the wrapped parameter's ``validate_specification`` method which catches any
        ``ParameterError``s and re-raises them with the ``AwareParameter`` instance as argument
        (in order to provide information about the parameter's path).

        See Also
        --------
        :method:`Parameter.validate_specification` 
        """
        try:
            return self._parameter.validate_specification(*args, **kwargs)
        except ParameterError as err:
            raise type(err)(err.reason, self)


@six.python_2_unicode_compatible
class Parameter(six.with_metaclass(abc.ABCMeta, object)):
    """
    (Abstract) Base class for parameter classes.
    """

    def __init__(self, name, **kwargs):
        """
        Parameters
        ----------
        name : unicode
            The parameter's name.
        **kwargs
            Additional parameter attributes.
        """
        self._name = name
        self._specifications = kwargs.copy()
        self._field_name = None
        self._restrictions = []

    def __repr__(self):
        attr_str = ', '.join(['{0}={1}'.format(k, v) for k, v in self._specifications.items()])
        if attr_str:
            attr_str = ', ' + attr_str
        return '{0}({1}{2})'.format(self.__class__.__name__, self._name, attr_str)

    def __str__(self):
        """
        JSON decodable string representation of the parameter.

        Returns
        -------
        unicode
        """
        return to_json_string(self.as_json())

    def as_json(self):
        """
        JSON compatible representation of the parameter.

        Returns
        -------
        dict
        """
        return {
            'type': self.__class__.__name__,
            'name': self._name,
            'optional': self.is_optional,
        }

    @property
    def default(self):
        """
        The default value of the parameter if any. If no default is available and
        the parameter is marked optional then``None`` is returned.
        Otherwise an ``AttributeError`` is raised.

        Returns
        -------
        default
            The default value if any otherwise ``None`` if the parameter is optional.

        Raises
        ------
        AttributeError
            If the parameter has no default value and is not optional.

        Examples
        --------
        >>> from anna import Integer
        >>> p = Integer('IDefaultTo42', default=42)
        >>> print(p.default)
        42
        >>> print(p.load_from_configuration(None, None))
        42
        >>> p = Integer('IAmOptional', optional=True)
        >>> print(p.default)
        None
        """
        try:
            return self._specifications['default']
        except KeyError:
            if self.is_optional:
                return None
            else:
                raise AttributeError('Parameter "%s" has no default' % self)

    @property
    def field_name(self):
        """
        By default the field name of the parameter is computed from its name via
        CamelCase to _snake_case_with_leading_underscore conversion. This behaviour
        can be overridden by setting a field name manually:
        ``some_parameter.field_name = 'custom_field_name'``.

        .. note::
        The field name may also be adjusted by the framework if the parameter was specified
        as a keyword argument in :func:`parametrize`. In this case the field name equals
        the given keyword.

        Returns
        -------
        field_name : unicode

        Examples
        --------
        >>> from anna import String
        >>> p = String('ThisIsSnakeCaseReally')
        >>> print(p.field_name)
        _this_is_snake_case_really
        >>> p.field_name = 'not_quite'
        >>> print(p.field_name)
        not_quite
        """
        return self._field_name or self.convert_parameter_name_to_field_name(self.name)

    @field_name.setter
    def field_name(self, value):
        self._field_name = value

    @property
    def for_example(self):
        """
        Obtain an example value for this parameter.
        
        .. note::
           This is not the same as default! An example value solely aims to give an example for a
           meaningful value however this is not a preferred value that was chosen by the developer.
        
        Returns
        -------
        for_example
            An example value or ``None`` if no example value is available.
        """
        return self._specifications.get('for_example')

    @property
    def info(self):
        """
        Additional information about the parameter. Such information can be specified
        upon initialization using the keyword argument ``info``.

        Returns
        -------
        info : unicode or None
            If no information is available ``None`` is returned.

        Examples
        --------
        >>> from anna import String
        >>> p = String('IAmInformative', info='Some useful information about this parameter')
        >>> print(p.info)
        Some useful information about this parameter
        """
        return self._specifications.get('info')

    @property
    def is_expert(self):
        """
        Expert parameters are parameters which have default values and thus don't
        necessarily have to be specified in a configuration source. Such a parameter's
        value is usually not an obvious choice and for that reason a default value is
        provided by the developer.

        Returns
        -------
        is_expert : bool
            ``True`` if the parameter has a default value ``False`` otherwise.

        Examples
        --------
        >>> p1 = IntegerParameter('IAmNotAnExpert')
        >>> p1.is_expert
        False
        >>> p2 = IntegerParameter('IAmAnExpert', default=42)
        >>> p2.is_expert
        True
        """
        return 'default' in self._specifications

    @property
    def is_optional(self):
        """
        Optional parameters don't need to be specified in a configuration source and
        if they are missing ``None`` is used as a value instead. A parameter can be
        declared optional by using the keyword argument ``optional=True``.

        Returns
        -------
        is_optional : bool
            ``True`` if the parameter is optional ``False`` otherwise.

        Examples
        --------
        >>> p1 = IntegerParameter('IAmRequired')
        >>> p1.is_optional
        False
        >>> p2 = IntegerParameter('IAmOptional', optional=True)
        >>> p2.is_optional
        True
        """
        return bool(self._specifications.get('optional'))

    @property
    def name(self):
        """
        The name of the parameter.

        Returns
        -------
        name : unicode
        """
        return self._name

    def load_from_configuration(self, configuration, path):
        """
        Load the parameter's value from the specified configuration source and
        convert it to its corresponding native representation (data type).

        Parameters
        ----------
        configuration : :class:`ConfigurationAdaptor`
            The configuration adaptor representing the configuration source.
        path : unicode
            The path which localizes the parameter within the configuration source.

        Returns
        -------
        native_representation
            The parameter's native representation which is derived from
            the text/meta representation that is provided by the configuration source.

        See Also
        --------
        :method:`~Parameter.load_from_representation` : Load a parameter from
        a text/meta representation.
        """
        full_path = configuration.join_paths(path, self.name)
        if configuration is None:
            try:
                return self.default
            except AttributeError:
                raise IncompleteConfigurationError(self, full_path)
        try:
            text = configuration.get_text(full_path)
            meta = configuration.get_meta(full_path)
        except InvalidPathError:
            try:
                return self.default
            except AttributeError:
                if self.is_optional:
                    return None
                else:
                    raise IncompleteConfigurationError(self, full_path)
        return self.load_from_representation(text, meta)

    def load_from_representation(self, text, meta):
        """
        Load the parameter's value from the specified text/meta representation and
        convert it to its corresponding native representation (data type). This method
        also applies any conversions that are necessary in order to match
        the parameter's declaration.

        Parameters
        ----------
        text : unicode
            The parameter's value as text.
        meta : dict
            Meta data on the given value.

        Returns
        -------
        native_representation
            The parameter's value in native representation which is computed from
            the specified text/meta representation.

        Raises
        ------
        ParameterError
            If the given representation could not be converted to the parameter's
            native representation. The error message contains the cause as well as
            information on this parameter.
        """
        try:
            self.validate_representation(text, meta)
            self.validate_specification(text, meta)
        except ParameterError as err:
            raise type(err)(err.reason, self)
        return self._match_declaration(self.convert_representation(text, meta))

    def restrict(self, condition):
        """
        Restrict the possible values for this parameters with a condition.
        
        Parameters
        ----------
        condition : callable
            This function is passed the value of the parameter *after* it has been loaded. It must
            return True if the value satisfies the condition and False if it doens't.
            
        Returns
        -------
        self
            The instance.
        """
        self._restrictions.append(condition)
        return self

    def validate_specification(self, text, meta):
        """
        Checks if the given specification is valid. In contrast to
        :method:`~Parameter.validate_specification` this method checks for parameter instance
        specific attributes such as any given restrictions or unit conversion errors.
        
        .. note::
           Before calling this method the representation should have been verified via
           :method:`~Parameter.validate_representation`. Otherwise error messages might
           not be as helpful.
        
        Parameters
        ----------
        text : unicode
            The parameter's value as text.
        meta : None or dict
            Meta data on the given value.

        Returns
        -------
        None
            If the specification is valid.

        Raises
        ------
        SpecificationError
            If the given specification is invalid.
            
        See Also
        --------
        :method:`~Parameter.validate_representation`
        """
        value = self._match_declaration(self.convert_representation(text, meta))
        if not all(map(lambda condition: condition(value), self._restrictions)):
            raise ValueError_(six.text_type(value), self)
        return None

    @classmethod
    def convert_representation(cls, text, meta):
        """
        Check if the given text/meta representation is valid and convert it to
        the parameter's value in native representation by calling the parameter's
        class specific :method:`~Parameter._convert_representation` method.

        Parameters
        ----------
        text : unicode
            The parameter's value as text.
        meta : None or dict
            Meta data on the given value.

        Raises
        ------
        RepresentationError
            If the given representation doesn't match the parameter's format.
        """
        cls.validate_representation(text, meta)
        return cls._convert_representation(text, meta)

    @classmethod
    def validate_representation(cls, text, meta):
        """
        Validate if the given text/meta representation matches the parameter's format.

        .. note::
        By default this method only checks the types of `text` and `meta` and
        also if `text` is not empty.
        This method should be overridden in subclasses as appropriate.

        Parameters
        ----------
        text : unicode
            The parameter's value as text.
        meta : None or dict
            Meta data on the given value.

        Returns
        -------
        None
            If the representation is valid.

        Raises
        ------
        TypeError
            If `text` or `meta` has the wrong type.
        RepresentationError
            If `text` is an empty string.
        """
        if text is not None and not isinstance(text, six.text_type):
            raise TypeError(
                'Text must be represented by a unicode (got %s instead)'
                % type(text)
            )
        if meta is not None and not isinstance(meta, dict):
            raise TypeError(
                'Meta data must be represented by a dict (got %s instead)'
                % type(meta)
            )
        if not text:
            raise RepresentationError('Is empty')

    @classmethod
    def _convert_representation(cls, text, meta):
        """
        Convert the given representation to the parameter's native representation.

        .. note::
        By default this method just returns `text`. This method gets invoked by
        :method:`~Parameter.convert_representation`. Thus it should be overridden
        in subclasses as appropriate.

        .. warning::
        This method doesn't perform validity checks on the given representation.
        Unexpected results may occur if the text/meta representation is invalid.
        Validate the representation first using
        :method:`~Parameter.validate_representation` or use
        :method:`~Parameter.load_from_representation` which performs the validity
        check before converting.

        Parameters
        ----------
        text : unicode
            The parameter's value as text.
        meta : None or dict
            Meta data on the given value.

        Returns
        -------
        text : unicode
            `text`, unmodified
        """
        return text

    def _match_declaration(self, value):
        """
        Convert the specified value given in native representation so that after conversion
        it matches the parameter's declaration.

        .. note::
        By default this method is a no-op. It gets invoked by
        :method:`~Parameter.load_from_representation` and thus
        it should be overridden in subclasses as appropriate.

        Parameters
        ----------
        value
            The parameter's specified value in native representation.

        Return
        ------
        value
            `value`, unmodified
        """
        return value

    @staticmethod
    def convert_parameter_name_to_field_name(name):
        # Replace whitespace before lowercase letters or digits with an underscore.
        name = re.sub(r'\s+([a-z0-9])', r'_\1', name)
        # Remove whitespace before uppercase letters. The underscore will be inserted by
        # `convert_camel_case_to_snake_case`.
        name = re.sub(r'\s+([A-Z])', r'\1', name)
        # Replace hyphens with an underscore.
        name = name.replace('-', '_')
        # Prepend an underscore and convert.
        return '_%s' % convert_camel_case_to_snake_case(name)


class BoolParameter(Parameter):
    """
    This parameter type represents a bool. Its text representation must be
    either ``'true'`` or ``'false'``.
    """

    true = 'true'
    false = 'false'

    def __init__(self, name, **kwargs):
        super(BoolParameter, self).__init__(name, **kwargs)

    @classmethod
    def convert_representation(cls, text, meta=None):
        """
        Convert the text/meta representation to the native representation (bool).

        Parameters
        ----------
        text : unicode
        meta : dict, optional

        Returns
        -------
        value : bool
            True if the text matches ``BoolParameter.true`` False otherwise.

        Examples
        --------
        >>> BoolParameter.convert_representation('true')
        True
        >>> BoolParameter.convert_representation('false')
        False
        """
        return super(BoolParameter, cls).convert_representation(text, meta)

    @classmethod
    def validate_representation(cls, text, meta=None):
        """
        Validate the given representation. ``text`` must be either ``'true'`` or ``'false'``.

        Parameters
        ----------
        text : unicode
        meta : dict, optional

        Returns
        -------
        None
            If the representation is valid.

        Raises
        ------
        RepresentationError

        Examples
        --------
        >>> BoolParameter.validate_representation('true')  # => None
        >>> BoolParameter.validate_representation('false')  # => None
        >>> BoolParameter.validate_representation('whatever')
        [...]
        RepresentationError: Must be either "true" or "false"
        """
        super(BoolParameter, cls).validate_representation(text, meta)
        if re.match(r'^(%s|%s)$' % (cls.true, cls.false), text) is None:
            raise RepresentationError(
                'Must be either "%s" or "%s" (got "%s")'
                % (cls.true, cls.false, text)
            )

    @classmethod
    def _convert_representation(cls, text, meta=None):
        """
        Convert the text/meta representation to the native representation (bool)
        without performing validity checks.

        See Also
        --------
        :method:`~BoolParameter.convert_representation`: For arguments and examples.
        """
        return text == cls.true


class IntegerParameter(Parameter):
    """
    This parameter type represents an integer. Its text representation may contain
    integer numbers, multiplication operators (``*``), addition operators (``+``),
    inverting operators with respect to addition (``-``), exponentiation operators
    (``**``) as well as parentheses (``()``). The common calculation rules apply.

    .. note::
    Division (``/``) is not allowed due to possible misunderstandings due to
    integer division. Decimal points (and floating point numbers in general)
    are not allowed due to possible misunderstandings from conversion to integer.

    .. note::
    The conversion from text to ``int`` uses Python's :func:`eval` function internally.

    See Also
    --------
    :method:`~IntegerParameter.convert_representation`: For more examples on text representations.
    :method:`~IntegerParameter.validate_representation`: For more examples on text representations.
    """
    def __init__(self, name, **kwargs):
        super(IntegerParameter, self).__init__(name, **kwargs)

    def __ge__(self, other):
        """
        Restrict the possible values of this parameter.
         
        .. note::
        This is equivalent to ``.restrict(lambda x: x >= other)``.
        
        Parameters
        ----------
        other : :class:`numbers.Integral`
        
        Returns
        -------
        self
            The instance. 
        """
        if not isinstance(other, numbers.Integral):
            raise TypeError('Can only compare to integral values')
        return self.restrict(lambda x: x >= other)

    def __gt__(self, other):
        """
        Restrict the possible values of this parameter.
         
        .. note::
        This is equivalent to ``.restrict(lambda x: x > other)``.
        
        Parameters
        ----------
        other : :class:`numbers.Integral`
        
        Returns
        -------
        self
            The instance. 
        """
        if not isinstance(other, numbers.Integral):
            raise TypeError('Can only compare to integral values')
        return self.restrict(lambda x: x > other)

    def __le__(self, other):
        """
        Restrict the possible values of this parameter.
         
        .. note::
        This is equivalent to ``.restrict(lambda x: x <= other)``.
        
        Parameters
        ----------
        other : :class:`numbers.Integral`
        
        Returns
        -------
        self
            The instance.
        """
        if not isinstance(other, numbers.Integral):
            raise TypeError('Can only compare to integral values')
        return self.restrict(lambda x: x <= other)

    def __lt__(self, other):
        """
        Restrict the possible values of this parameter.
         
        .. note::
        This is equivalent to ``.restrict(lambda x: x < other)``.
        
        Parameters
        ----------
        other : :class:`numbers.Integral`
        
        Returns
        -------
        self
            The instance. 
        """
        if not isinstance(other, numbers.Integral):
            raise TypeError('Can only compare to integral values')
        return self.restrict(lambda x: x < other)

    @classmethod
    def convert_representation(cls, text, meta=None):
        """
        Convert the text/meta representation to the native representation (``int``).

        Parameters
        ----------
        text : unicode
        meta : dict, optional

        Returns
        -------
        value : int

        Examples
        --------
        >>> IntegerParameter.convert_representation('2')
        2
        >>> IntegerParameter.convert_representation('2 + 5')
        7
        >>> IntegerParameter.convert_representation('2 + 5*3')
        17
        >>> IntegerParameter.convert_representation('2**3 + 5*3')
        23
        >>> IntegerParameter.convert_representation('2 ** (3 + 5) *3')
        768
        """
        return super(IntegerParameter, cls).convert_representation(text, meta)

    @classmethod
    def validate_representation(cls, text, meta=None):
        """
        Validate the given representation. See the class doc string for more information
        about the format.

        Parameters
        ----------
        text : unicode
        meta : dict, optional

        Returns
        -------
        None
            If the representation is valid.

        Raises
        ------
        RepresentationError

        Examples
        --------
        >>> IntegerParameter.validate_representation('1**2 + 3*4 - (5 + 3)')
        >>> IntegerParameter.validate_representation('1/2')
        [...]
        RepresentationError: Division is not supported for IntegerParameters in order to
        prevent misunderstandings arising from integer division
        >>> IntegerParameter.validate_representation('1.1 * 5')
        [...]
        RepresentationError: Floating point numbers are not allowed for integer values
        """
        super(IntegerParameter, cls).validate_representation(text, meta)
        if '/' in text:
            raise RepresentationError(
                'Division is not supported for IntegerParameters in order to '
                'prevent misunderstandings arising from integer division'
            )
        if '.' in text:
            raise RepresentationError(
                'Floating point numbers are not allowed for integer values'
            )

        if re.match(r'^[0-9\s+*\-()]+$', text) is None:
            raise RepresentationError('"%s" is not a valid integer' % text)

        try:
            IntegerParameter._convert_representation(text)
        except (SyntaxError, ValueError):
            raise RepresentationError('"%s" is not a valid integer' % text)

    @classmethod
    def _convert_representation(cls, text, meta=None):
        """
        Convert the text/meta representation to the native representation
        without performing validity checks.

        See Also
        --------
        :method:`~IntegerParameter.convert_representation`: For arguments, return values and
        examples.
        """
        return datatypes.convert_to(datatypes.integer)(
            safe_math_eval(text, RepresentationError)
        )


class StringParameter(Parameter):
    """
    This parameter type represents a string. The text representation can be anything.
    """

    def __init__(self, name, **kwargs):
        super(StringParameter, self).__init__(name, **kwargs)

    @classmethod
    def convert_representation(cls, text, meta=None):
        """
        Convert the text/meta representation to the native representation (unicode).

        Parameters
        ----------
        text : unicode
        meta : dict, optional

        Returns
        -------
        value : unicode
        """
        return super(StringParameter, cls).convert_representation(text, meta)

    @classmethod
    def validate_representation(cls, text, meta=None):
        """
        Validate the given representation. Any string is valid.

        Parameters
        ----------
        text : unicode
        meta : dict, optional
        """
        super(StringParameter, cls).validate_representation(text, meta)


class FilepathParameter(Parameter):
    """
    This parameter type represents a file path. If the ``exists`` parameter is set to True, the text representation
    must point to an existing file.
    """

    def __init__(self, name, exists=False, **kwargs):
        super(FilepathParameter, self).__init__(name, **kwargs)
        self._exists = exists

    def validate_specification(self, text, meta):
        if self._exists and not os.path.exists(text):
            raise SpecificationError('File path %s does not exist' % text)

    @classmethod
    def convert_representation(cls, text, meta=None):
        """
        Convert the text/meta representation to the native representation (unicode).

        Parameters
        ----------
        text : unicode
        meta : dict, optional

        Returns
        -------
        value : unicode
        """
        return super(FilepathParameter, cls).convert_representation(text, meta)

    @classmethod
    def validate_representation(cls, text, meta=None):
        """
        Validate the given representation. Any string is valid.

        Parameters
        ----------
        text : unicode
        meta : dict, optional
        """
        super(FilepathParameter, cls).validate_representation(text, meta)


class NumberParameter(Parameter):
    """
    This parameter type represents a (floating point) number. The text representation
    may contain floating point numbers as well as all kind of common arithmetic operations.
    It may also contain references to :module:`numpy` via ``"numpy"`` or the shortcut
    ``"np"`` (e.g. ``"np.exp(np.pi)"``).
    """

    def __init__(self, name, **kwargs):
        super(NumberParameter, self).__init__(name, **kwargs)

    def __ge__(self, other):
        """
        Restrict the possible values of this parameter.

        .. note::
        This is equivalent to ``.restrict(lambda x: x >= other)``.

        Parameters
        ----------
        other : :class:`numbers.Number`

        Returns
        -------
        self
            The instance. 
        """
        if not isinstance(other, numbers.Number):
            raise TypeError('Can only compare to numbers')
        return self.restrict(lambda x: x >= other)

    def __gt__(self, other):
        """
        Restrict the possible values of this parameter.

        .. note::
        This is equivalent to ``.restrict(lambda x: x > other)``.

        Parameters
        ----------
        other : :class:`numbers.Number`

        Returns
        -------
        self
            The instance. 
        """
        if not isinstance(other, numbers.Number):
            raise TypeError('Can only compare to numbers')
        return self.restrict(lambda x: x > other)

    def __le__(self, other):
        """
        Restrict the possible values of this parameter.

        .. note::
        This is equivalent to ``.restrict(lambda x: x <= other)``.

        Parameters
        ----------
        other : :class:`numbers.Number`

        Returns
        -------
        self
            The instance.
        """
        if not isinstance(other, numbers.Number):
            raise TypeError('Can only compare to numbers')
        return self.restrict(lambda x: x <= other)

    def __lt__(self, other):
        """
        Restrict the possible values of this parameter.

        .. note::
        This is equivalent to ``.restrict(lambda x: x < other)``.

        Parameters
        ----------
        other : :class:`numbers.Number`

        Returns
        -------
        self
            The instance. 
        """
        if not isinstance(other, numbers.Number):
            raise TypeError('Can only compare to numbers')
        return self.restrict(lambda x: x < other)

    @classmethod
    def convert_representation(cls, text, meta=None):
        """
        Convert the given representation to the native representation (``float``).

        Parameters
        ----------
        text : unicode
        meta : dict, optional

        Returns
        -------
        value : float

        Raises
        ------
        RepresentationError
            If the conversion to float fails.

        Examples
        --------
        >>> NumberParameter.convert_representation('1 * 2 + 3')
        5.0
        >>> NumberParameter.convert_representation('2 * np.pi')
        6.2831853071795862
        >>> NumberParameter.convert_representation('np.sin(np.pi / 2)')
        1.0
        """
        return super(NumberParameter, cls).convert_representation(text, meta)

    @classmethod
    def validate_representation(cls, text, meta=None):
        """
        Validate the given representation. See the class doc string for more information
        about the format.

        Parameters
        ----------
        text : unicode
        meta : dict, optional

        Returns
        -------
        None
            If the representation is valid.

        Raises
        ------
        RepresentationError
            If the conversion to float fails.

        See Also
        --------
        :method:`~NumberParameter.convert_representation` : For examples on valid text
        representations.
        """
        super(NumberParameter, cls).validate_representation(text, meta)
        try:
            NumberParameter._convert_representation(text)
        except (NameError, SyntaxError, ValueError):
            raise RepresentationError('"%s" is not a valid number' % text)

    @classmethod
    def _convert_representation(cls, text, meta=None):
        """
        Convert the text/meta representation to the native representation
        without performing validity checks.

        See Also
        --------
        :method:`~NumberParameter.convert_representation`: For arguments, return values and
        examples.
        """
        text = text.replace('numpy', 'np')
        return datatypes.convert_to(datatypes.number)(
            safe_math_eval(text, RepresentationError, {'np': numpy})
        )


@six.python_2_unicode_compatible
class PhysicalQuantityParameterBase(Parameter):
    """
    (Abstract) Base class for parameter types which are associated with a (physical) unit.
    A unit may consist of alpha-numerical characters as well as "*", "/" and "^"
    (to indicate exponentiation).
    """

    def __init__(self, name, unit=None, dimension=None, **kwargs):
        """
        Initialize the parameter with a unit.

        .. note::
        Either a unit or a dimension need to be specified. If both are specified
        the unit has precedence.

        Parameters
        ----------
        name : unicode
        unit : unicode, optional
        dimension : unicode, optional
            The parameter's unit will be derived as the default unit for the given dimension.

        Raises
        ------
        ValueError
            If neither a `unit` nor a `dimension` are specified.
        """
        if unit is None:
            if dimension is None:
                raise ValueError(
                    'Unit-associated parameters must declare either a unit or a dimension'
                )
            else:
                try:
                    unit = Unit.default(dimension)
                except Unit.UnknownUnitError as err:
                    raise UnknownUnitError(six.text_type(err), self)
        super(PhysicalQuantityParameterBase, self).__init__(name, unit=unit, **kwargs)

    def as_json(self):
        """
        JSON compatible representation of the parameter.

        Returns
        -------
        dict
        """
        return dict(
            super(PhysicalQuantityParameterBase, self).as_json(),
            unit=six.text_type(self.unit)
        )

    def __str__(self):
        """
        JSON decodable string representation of the parameter.

        Returns
        -------
        unicode
        """
        return to_json_string(self.as_json())

    @property
    def unit(self):
        return self._specifications['unit']

    @unit.setter
    def unit(self, value):
        self._specifications['unit'] = value

    @use_docs_from(Parameter)
    def validate_specification(self, text, meta):
        super(PhysicalQuantityParameterBase, self).validate_specification(text, meta)
        try:
            Unit(meta['unit']).conversion_factor(self.unit)
        except (Unit.ConversionError, Unit.UnknownUnitError) as err:
            raise InvalidUnitError(six.text_type(err), self)

    @classmethod
    @use_docs_from(Parameter)
    def convert_representation(cls, text, meta):
        return super(PhysicalQuantityParameterBase, cls).convert_representation(text, meta)

    @classmethod
    def format_unit(cls, unit_or_meta):
        """
        Format the unit string by removing all whitespaces.

        Parameters
        ----------
        unit_or_meta : unicode or dict
            If provided as a dict it must contain the unit at key ``"unit"``.

        Returns
        -------
        formatted_unit : unicode
            The unit string without whitespaces.
        """
        if isinstance(unit_or_meta, dict):
            try:
                unit = unit_or_meta['unit']
            except KeyError:
                raise RepresentationError(
                    'Physical quantity parameters must declare a unit'
                )
        else:
            unit = unit_or_meta
        return unit.replace(' ', '')

    @classmethod
    def validate_representation(cls, text, meta):
        """
        Validate the given representation. See the class doc string for more information
        about the format.

        Parameters
        ----------
        text : unicode
        meta : dict

        Returns
        -------
        None
            If the representation is valid.

        Raises
        ------
        RepresentationError
            If the unit is not represented by a valid string.
        InvalidUnitError
            If the given unit is unknown.
        """
        super(PhysicalQuantityParameterBase, cls).validate_representation(text, meta)
        if not isinstance(meta, dict):
            raise TypeError(
                'Meta data must be represented by a dict (got %s instead)'
                % type(meta)
            )
        if 'unit' not in meta:
            raise RepresentationError('Does not declare a unit')
        unit = cls.format_unit(meta)
        if not unit:
            raise RepresentationError('Does not declare a unit')
        try:
            Unit.validate(unit)
        except Unit.UnknownUnitError:
            raise InvalidUnitError(unit)


class PhysicalQuantityParameter(PhysicalQuantityParameterBase, NumberParameter):
    """
    This parameter type represents a physical quantity (magnitude + unit).
    The text representation may contain all elements of a :class:`NumberParameter`.
    In addition it may also refer to constants that are contained in either
    :mod:`scipy.constants` or ``scipy.constants.physical_constants`` using the format
    ``'%\(key\)(e|f|s)'``, where ``key`` can bei either an attribute name of
    ``scipy.constants`` or a key in ``scipy.constants.physical_constants``.
    The placeholder format string will be replaced by the corresponding constant
    (precision loss is accounted for).

    A PhysicalQuantityParameter must always be associated with a unit (if it is
    dimensionless use "1" instead). When the parameter is loaded from a specifications
    the unit conversion will be applied too.

    See Also
    --------
    :method:`~PhysicalQuantityParameter.convert_representation`: For more examples on
    text representations.
    :method:`~PhysicalQuantityParameter.validate_representation`: For more examples on
    text representations.
    """
    def __init__(self, name, unit=None, dimension=None, **kwargs):
        """
        See :method:`PhysicalQuantityParameterBase.__init__` for parameter descriptions.
        """
        super(PhysicalQuantityParameter, self).__init__(
            name, unit=unit, dimension=dimension, **kwargs
        )

    def __ge__(self, other):
        """
        Restrict the possible values of this parameter.

        .. note::
        This is equivalent to ``.restrict(lambda x: x >= other)``.

        Parameters
        ----------
        other : :class:`numbers.Number`

        Returns
        -------
        self
            The instance. 
        """
        if not isinstance(other, numbers.Number):
            raise TypeError('Can only compare to numbers')
        return self.restrict(lambda x: x >= other)

    def __gt__(self, other):
        """
        Restrict the possible values of this parameter.

        .. note::
        This is equivalent to ``.restrict(lambda x: x > other)``.

        Parameters
        ----------
        other : :class:`numbers.Number`

        Returns
        -------
        self
            The instance. 
        """
        if not isinstance(other, numbers.Number):
            raise TypeError('Can only compare to numbers')
        return self.restrict(lambda x: x > other)

    def __le__(self, other):
        """
        Restrict the possible values of this parameter.

        .. note::
        This is equivalent to ``.restrict(lambda x: x <= other)``.

        Parameters
        ----------
        other : :class:`numbers.Number`

        Returns
        -------
        self
            The instance.
        """
        if not isinstance(other, numbers.Number):
            raise TypeError('Can only compare to numbers')
        return self.restrict(lambda x: x <= other)

    def __lt__(self, other):
        """
        Restrict the possible values of this parameter.

        .. note::
        This is equivalent to ``.restrict(lambda x: x < other)``.

        Parameters
        ----------
        other : :class:`numbers.Number`

        Returns
        -------
        self
            The instance. 
        """
        if not isinstance(other, numbers.Number):
            raise TypeError('Can only compare to numbers')
        return self.restrict(lambda x: x < other)

    # noinspection PyMethodOverriding
    @classmethod
    def convert_representation(cls, text, meta):
        """
        Convert the text/meta representation to the native representation (:class:`Value`).

        Parameters
        ----------
        text : unicode
        meta : dict
            Must contain a unit at key ``'unit'``.

        Returns
        -------
        value : :class:`Value`

        Examples
        --------
        >>> print(PhysicalQuantityParameter.convert_representation('1 * 2 + 3', {'unit': '1'}))
        5.0 [1]
        >>> print(PhysicalQuantityParameter.convert_representation('np.pi', {'unit': '1'}))
        3.14159265359 [1]
        >>> print(PhysicalQuantityParameter.convert_representation('%(pi)s', {'unit': '1'}))
        3.14159265359 [1]
        >>> print(PhysicalQuantityParameter.convert_representation(
        ... '%(electron mass energy equivalent in MeV)f*1.0e6 * %(elementary charge)f'
        ... '/ %(speed of light in vacuum)f**2',
        ... {'unit': 'kg'}))
        9.10938355699e-31 [kg]
        >>> print(PhysicalQuantityParameter.convert_representation(
        ... '%(electron mass)f',
        ... {'unit': 'kg'}))
        9.10938356e-31 [kg]
        """
        return super(PhysicalQuantityParameter, cls).convert_representation(text, meta)

    # noinspection PyMethodOverriding
    @classmethod
    def validate_representation(cls, text, meta):
        """
        Validate the given representation. See the class doc string for more information
        about the format.

        Parameters
        ----------
        text : unicode
        meta : dict
            Must contain a unit at key ``'unit'``.

        Returns
        -------
        None
            If the representation is valid.

        Raises
        ------
        RepresentationError
            If one of the constant keys cannot be resolved or if the conversion to float fails.
        """
        if re.match(r'^[.\-+*/0-9a-zA-Z%\s(){},_]+$', text) is None:
            raise RepresentationError('"%s" is not a valid number' % text)
        try:
            text = supply_with_constants(text)
        except ValueError:
            raise RepresentationError('"%s" contains invalid keys for constants')
        super(PhysicalQuantityParameter, cls).validate_representation(text, meta)

    # noinspection PyMethodOverriding
    @classmethod
    def _convert_representation(cls, text, meta):
        """
        Convert the text/meta representation to the native representation
        without performing validity checks.

        See Also
        --------
        :method:`~PhysicalQuantityParameter.convert_representation`: For arguments, return values
        and examples.
        """
        try:
            return Value(
                super(PhysicalQuantityParameter, cls)._convert_representation(
                    supply_with_constants(text), meta
                ),
                Unit(cls.format_unit(meta))
            )
        except Unit.UnknownUnitError as err:
            raise InvalidUnitError('Unknown unit: %s' % six.text_type(err))

    def _match_declaration(self, value):
        """
        Convert the given value to the parameter's unit (which was declared upon initialization).

        Parameters
        ----------
        value : :class:`Value`

        Returns
        -------
        magnitude : float
            The magnitude of the value after conversion to the declared unit;
            the unit is dropped and should be respected implicitly.

        Raises
        ------
        InvalidUnitError
            If the conversion to the declared unit fails.
        """
        try:
            return value.convert_to(self.unit).magnitude
        except Unit.ConversionError as err:
            raise InvalidUnitError(six.text_type(err))


@six.python_2_unicode_compatible
class ActionParameter(object):
    """
    This parameter type wraps another parameter and allows for specification of
    an action that will be applied to the wrapped parameter's value after it is loaded.
    That is in addition to any automatic conversion which are applied to the value
    this class allows a custom action to be applied in addition.
    If for example the wrapped parameter represented a file path then
    the action could load data from the file pointed to by the parameter's value.

    This parameter type also allows to declare dependencies on other parameters
    (either of the same parametrized class or another parametrized class).
    Those parameter must be referred to by their *name* (not their field name!) or
    by an instance reference. The specifications of dependencies must reside in
    the same configuration object that is used to load this parameter and they must be
    localizable by their own paths. All loaded values of parameters that have been declared
    as dependencies will be passed as additional arguments to the specified action.

    Examples
    --------
    >>> from anna import Configurable, parametrize, ActionParameter, Integer, String, JSONAdaptor
    >>>
    >>> @parametrize(squared_number=ActionParameter(Integer('SquareMe'),
    ...                                             action=lambda x: x**2))
    >>> class Component(Configurable):
    ...     CONFIG_PATH = ''
    ...     def __init__(self, configuration):
    ...         super(Component, self).__init__(configuration)

    >>> component = Component(JSONAdaptor(root={
    ...     'SquareMe': '5'
    >>> }))
    >>> print(component.squared_number)
    25

    >>> @parametrize(
    ... Integer('MagicNumber'),
    ... ActionParameter(String('Statement'),
    ...                 action=lambda s, n: '%d %s' % (n, s),
    ...                 depends_on=('MagicNumber',)))
    ... class Component(Configurable):
    ...     CONFIG_PATH = ''
    ...     def __init__(self, configuration):
    ...         super(Component, self).__init__(configuration)
    ...
    >>> component = Component(JSONAdaptor(root={
    ...     'MagicNumber': '42',
    ...     'Statement':  'is the answer to everything.'
    ... }))
    >>> print(component._statement)
    42 is the answer to everything.
    >>> print(component._magic_number)
    42
    """

    def __init__(self, parameter, action, depends_on=()):
        """
        Initialize the ActionParameter with a parameter instance to be wrapped and
        an action to be applied upon loading. Optionally a list of other
        dependant parameters can be specified. If so their (native) values are passed to
        the specified action as additional arguments in the order they are specified.

        .. note::
        Only :class:`AwareParameter`s and strings may be used to declare dependencies.
        A string can only refer to other parameters of the same parametrized component.
        To refer to parameters of other components use the parameter instance that
        has been set on that component. Parameters that are specified as strings must be
        referred to by their names (not field names!).

        Parameters
        ----------
        parameter : Parameter
            The wrapped parameter.
        action : callable
            Will be applied to the wrapped parameter's loaded value.
        depends_on : tuple or list, optional
            A list of parameters that act as dependencies for this ActionParameter and
            whose loaded value are passed as additional arguments to the specified `action`.
        """
        super(ActionParameter, self).__init__()
        self._parameter = parameter
        self._action = action
        if any(map(lambda p: not isinstance(p, (AwareParameter, six.text_type)), depends_on)):
            raise TypeError(
                'Only AwareParameters may serve as dependencies. Dependencies within '
                'the same component need to be declared via their names as strings.'
            )
        self.depends_on = depends_on

    def __getattr__(self, item):
        return getattr(self._parameter, item)

    def __str__(self):
        """
        JSON decodable string representation of the parameter.

        Returns
        -------
        unicode
        """
        return to_json_string(self.as_json())

    def as_json(self):
        """
        JSON compatible representation of the parameter.

        Returns
        -------
        dict
        """
        return dict(
            self._parameter.as_json(),
            action=self._action.__name__,
            depends_on=tuple(map(lambda p: p.as_json(), self.depends_on))
        )

    # Need to redefine property field_name because the field name might be set by
    # `parametrize` after a (Action)Parameter has been created.
    @property
    @use_docs_from(Parameter)
    def field_name(self):
        return self._parameter.field_name

    @field_name.setter
    @use_docs_from(Parameter)
    def field_name(self, value):
        self._parameter.field_name = value

    @property
    def parameter(self):
        """
        The wrapped parameter

        Returns
        -------
        parameter : :class:`Parameter` derived class
        """
        return self._parameter

    def load_from_configuration(self, configuration, path):
        """
        Load the wrapped parameter's value from the specified configuration source and
        convert it to its corresponding native representation (data type).
        Then apply the custom action to the result.

        Parameters
        ----------
        configuration : :class:`ConfigurationAdaptor`
            The configuration adaptor representing the configuration source.
        path : unicode
            The path which localizes the wrapped parameter within the configuration.

        Returns
        -------
        native_representation
            The result of the custom action which is applied to he parameter's
            native representation which is computed from the text/meta representation
            that is present in the configuration source.
        """
        dependency_values = tuple(map(
            lambda p: p.load_from_configuration(configuration),
            self.depends_on
        ))
        return self._match_declaration(
            self._parameter.load_from_configuration(configuration, path),
            dependency_values
        )

    def load_from_representation(self, text, meta, *args):
        """
        Load the parameter's value from the specified text/meta representation and
        convert it to its native representation. This method also applies any conversions
        that are necessary in order to match the parameter's declaration. Then apply
        the custom action to the result. `args` must contain the text/meta representations
        of all dependencies.

        Parameters
        ----------
        text : unicode
            The parameter's value as text
        meta : None or dict
            Meta data on the given value
        *args : tuple or list
            A tuple or list containing the text/meta representation for every dependency
            that this ActionParameter declared in order to load their values beforehand
            so the results can be passed to the custom `action`.
            The text/meta values for each dependency need to be passed as separate arguments
            and none of them can be omitted.

        Returns
        -------
        native_representation
            The result of the custom action which is applied to the parameter's
            native representation which is computed from the specified
            text/meta representation.

        Raises
        ------
        ValueError
            If the number of additional text/meta arguments (for the dependencies)
            doesn't match the number of dependencies. This methods requires one text and
            one meta argument per dependency, that is the number of additional arguments
            must be 2*<number-of-dependencies>.
        ParameterError
            If the given representation could not be converted to the parameter's
            native representation. The error message contains the cause as well as
            information this parameter.

        Examples
        --------
        >>> from anna import parametrize, Integer
        >>>
        >>> @parametrize(
        ... number=IntegerParameter('AddMe'),
        ... adder=ActionParameter(Integer('MoreToAdd'),
        ...                       action=lambda x, y: x + y,
        ...                       depends_on=('AddMe',)))
        ... class Foo: pass
        ...
        >>> Foo.adder.load_from_representation('5', None, '12', None)
        17
        >>> Foo.adder.load_from_representation('5', None)
        [...]
        ValueError: Requires one text and meta argument per dependency. Got 0 (expected 2)
        """
        if len(args) != 2*len(self.depends_on):
            raise ValueError(
                'Requires one text and meta argument per dependency. Got %d (expected %d)'
                % (len(args), 2*len(self.depends_on))
            )
        dependencies_text_meta = zip(args[::2], args[1::2])
        dependency_values = tuple(map(
            lambda ptm: ptm[0].load_from_representation(*ptm[1]),
            zip(self.depends_on, dependencies_text_meta)
        ))
        return self._match_declaration(
            self._parameter.load_from_representation(text, meta),
            dependency_values
        )

    def _match_declaration(self, value, dependency_values):
        """
        Apply the custom action to the parameter's value.

        Parameters
        ----------
        value
            The parameter's value in native representation.
        dependency_values : tuple or list
            The values of all dependencies in native representation. They are passed as
            additional arguments to the custom action.

        Returns
        -------
        action_value
            The parameter's value converted via the custom action.
        """
        return self._action(value, *dependency_values)

Parameter.register(ActionParameter)


@six.python_2_unicode_compatible
class ChoiceParameter(object):
    """
    This parameter type allows for specifying possible choices for a parameter's value.
    """

    def __init__(self, parameter):
        """
        Parameters
        ----------
        parameter : :class:`Parameter` derived class
        """
        self._parameter = parameter
        self._options = set()
        if parameter.is_expert:
            self._options.add(parameter.default)

    def __getattr__(self, item):
        return getattr(self._parameter, item)

    def __str__(self):
        return to_json_string(self.as_json())

    def as_json(self):
        return dict(
            self._parameter.as_json(),
            options=self.options
        )

    def add_option(self, value):
        """
        Add an option for the parameter's value.

        Parameters
        ----------
        value

        Returns
        -------
        self
            The instance.
        """
        self._options.add(value)
        return self

    @property
    def options(self):
        """
        The possible values for the wrapped parameter.

        Returns
        -------
        list
        """
        return list(sorted(self._options))

    # Need to redefine property field_name because the field name might be set by
    # `parametrize` after a (Choice)Parameter has been created.
    @property
    @use_docs_from(Parameter)
    def field_name(self):
        return self._parameter.field_name

    @field_name.setter
    @use_docs_from(Parameter)
    def field_name(self, value):
        self._parameter.field_name = value

    @use_docs_from(Parameter)
    def load_from_configuration(self, configuration, path):
        return self._parameter.load_from_configuration(configuration, path)

    @use_docs_from(Parameter)
    def load_from_representation(self, text, meta):
        return self._parameter.load_from_representation(text, meta)

    def validate_representation(self, text, meta):
        """
        The given representation is valid if it fulfills the following conditions:

        1. The wrapped parameters validates the representation.
        2. Either the given text representation or the corresponding loaded value is part of
           the choices.

        Parameters
        ----------
        text : unicode
            The parameter's value as text.
        meta : None or dict
            Meta data on the given value.

        Returns
        -------
        None
            If the representation is valid.

        Raises
        ------
        RepresentationError
        """
        self._parameter.validate_representation(text, meta)
        if (text not in self._options and
                self._parameter.load_from_representation(text, meta) not in self._options):
            raise RepresentationError('%s is not a valid choice' % text)

Parameter.register(ChoiceParameter)


@six.python_2_unicode_compatible
class ParameterGroup(object):
    """
    A parameter group wraps a number of other parameters without any special restrictions. One
    advantage is that the class namespace is not filled with one attribute per parameter but
    contains only one for the parameter group. When loaded the single parameter values are
    available as a dict where the keys are the parameters' names. Also those parameters will show
    up together in the GUI.
    """

    def __init__(self, group_name, *args, **kwargs):
        """
        Parameters
        ----------
        group_name : unicode
            The name of the arameter group.
        *args
            A number of parameters which participate in this group.
        """
        self._name = group_name
        self._parameters = list(args)
        self._info = kwargs.get('info', None)
        self._field_name = None

    def __iter__(self):
        return iter(self._parameters)

    def __str__(self):
        return to_json_string(self.as_json())

    def as_json(self):
        return {
            'name': self._name,
            'type': self.__class__.__name__,
            'parameters': {
                parameter.name: parameter.as_json()
                for parameter in self._parameters
            }
        }

    @property
    @use_docs_from(Parameter)
    def field_name(self):
        return self._field_name or Parameter.convert_parameter_name_to_field_name(self.name)

    @field_name.setter
    @use_docs_from(Parameter)
    def field_name(self, value):
        self._field_name = value

    @property
    def info(self):
        return self._info

    @property
    def name(self):
        return self._name

    @property
    def is_expert(self):
        return all(map(lambda p: p.is_expert, self._parameters))

    @property
    def is_optional(self):
        return all(map(lambda p: p.is_optional, self._parameters))

    @property
    def parameters(self):
        return self._parameters

    def add(self, parameter):
        """
        Add a parameter to this group.
        
        Parameters
        ----------
        parameter : :class:`Parameter` derived class
        """
        self._parameters.append(parameter)

    def load_from_configuration(self, configuration, path):
        """
        Load the values of all group members of the group from the given configuration.

        Parameters
        ----------
        configuration : :class:`ConfigurationAdaptor`
            The configuration adaptor representing the configuration source.
        path : unicode
            The path which localizes the group within the configuration.

        Returns
        -------
        values : dict
            Each key-value pair corresponds to a parameter's name and its value: ``name: value``.

        Raises
        ------
        IncompleteConfigurationError
            If not all members of the group are specified in the configuration source.
        """
        joint_path = configuration.join_paths(path, self._name)
        values = {}
        for parameter in self._parameters:
            values[parameter.name] = parameter.load_from_configuration(configuration, joint_path)
        return values

    def load_from_representation(self, texts, metas):
        """
        Load the group members from the given representations.

        Parameters
        ----------
        texts : dict
            Contains the text representation per parameter name.
        metas : dict
            Contains the parameters' meta data per parameter name. If a parameter doesn't require
            meta data it can be left out.
            
        Returns
        -------
        values : dict
            Each key-value pair corresponds to a parameter's name and its value: ``name: value``.

        Raises
        ------
        RepresentationError
            If one of the parameter text specifications is missing.
        """
        values = {}
        for parameter in self._parameters:
            try:
                values[parameter.name] = parameter.load_from_representation(
                    texts[parameter.name],
                    metas.get(parameter.name)
                )
            except KeyError as err:
                raise RepresentationError(
                    'Parameter %s is missing' % six.text_type(err)
                )
        return values

Parameter.register(ParameterGroup)


@six.python_2_unicode_compatible
class ComplementaryParameterGroup(object):
    """
    A complementary parameter group is a group of N (N >= 2) parameters where each parameter's
    value can be computed from the values of all other parameters in the group. Each parameter
    that is declared as part of complementary group also needs to specify a completion function.
    This function must accept N-1 arguments which are the loaded values of all other parameters of
    the group in the order they were defined. The completion function must return the corresponding
    value of the corresponding parameter. When loaded this group returns a tuple with N elements
    where each element corresponds to the parameter that was declared at the corresponding
    position. A configuration source must specify exactly N-1 parameters that are part of the
    group. The group has a separate name, the path of parameters in the group is computed as
    ``<PathToGroup>/<GroupName>/<ParameterName>``. A configuration source must therefore have the
    following layout::
    
        <GroupName>
            <ParameterName1></ParameterName1>
            <ParameterName2></ParameterName2>
            [...]
            <ParameterNameN-1></ParameterNameN-1>
        </GroupName>
    """
    def __init__(self, group_name, *args, **kwargs):
        """
        Parameters
        ----------
        group_name : unicode
            The name of the complementary parameter group.
        *args
            A number of tuples which represent the parameters that participate in this group.
            The first element is the parameter and the second element is the completion function.
            See the class doc string for more information.
        """
        self._name = group_name
        self._parameters = list(zip(*args))[0]
        self._completion_functions = list(zip(*args))[1]
        self._info = kwargs.get('info', None)
        self._field_name = None

    def __str__(self):
        return to_json_string(self.as_json())

    def as_json(self):
        return {
            'name': self._name,
            'type': self.__class__.__name__,
            'parameters': {
                parameter.name: parameter.as_json()
                for parameter in self._parameters
            }
        }

    @property
    @use_docs_from(Parameter)
    def field_name(self):
        return self._field_name or Parameter.convert_parameter_name_to_field_name(self.name)

    @field_name.setter
    @use_docs_from(Parameter)
    def field_name(self, value):
        self._field_name = value

    @property
    def info(self):
        return self._info

    @property
    def name(self):
        return self._name

    @property
    def is_expert(self):
        return False

    @property
    def is_optional(self):
        return False

    def load_from_configuration(self, configuration, path):
        """
        Load the values of all specified members of the group (need to be exactly N-1 for N group
        members) and compute the value of the remaining one using the corresponding completion
        function.

        Parameters
        ----------
        configuration : :class:`ConfigurationAdaptor`
            The configuration adaptor representing the configuration source.
        path : unicode
            The path which localizes the group within the configuration.

        Returns
        -------
        tuple : size N
            Each element of the tuple represents the value of the parameter which was declared at
            the corresponding position.

        Raises
        ------
        IncompleteConfigurationError
            If the group is missing in the configuration.
        RepresentationError
            If not exactly N-1 members are specified.
        """
        joint_path = configuration.join_paths(path, self._name)
        values = []
        for parameter, completion_function in zip(self._parameters, self._completion_functions):
            try:
                values.append(parameter.load_from_configuration(configuration, joint_path))
            except IncompleteConfigurationError:
                values.append(None)
        specifications = list(filter(lambda x: x is not None, values))
        if not specifications:
            raise IncompleteConfigurationError(self, path)
        if len(specifications) != len(self._parameters)-1:
            raise RepresentationError(
                'Requires exactly %d members to be specified (found %d instead)'
                % (len(self._parameters)-1, len(specifications))
            )
        index = values.index(None)
        values[index] = self._completion_functions[index](*specifications)
        return tuple(values)

    def load_from_representation(self, texts, metas):
        """
        Loads the group from the given representations. The representations must contain exactly
        N-1 elements if the group has N members.
        
        Parameters
        ----------
        texts : dict
            Contains the text representation per parameter name.
        metas : dict
            Contains the parameters' meta data per parameter name.

        Raises
        ------
        RepresentationError
            If one of the given representations is invalid or if the number of given
            representations is not exactly N-1.
        """
        if len(texts) != len(self._parameters)-1:
            raise RepresentationError(
                'Requires exactly %d members to be specified (got %d instead)'
                % (len(self._parameters) - 1, len(texts))
            )
        if len(texts) != len(metas):
            raise RepresentationError(
                'Got %d text representations and %d meta data'
                % (len(texts), len(metas))
            )
        missing_parameter_index = None
        specifications = []
        for index, parameter in enumerate(self._parameters):
            try:
                specifications.append(parameter.load_from_representation(
                    texts[parameter.name],
                    metas[parameter.name]
                ))
            except KeyError:
                missing_parameter_index = index
        assert missing_parameter_index is not None, 'No parameter is missing'
        completion_function = self._completion_functions[missing_parameter_index]
        missing_value = completion_function(*specifications)
        specifications.insert(missing_parameter_index, missing_value)
        return tuple(specifications)

Parameter.register(ComplementaryParameterGroup)


@six.python_2_unicode_compatible
class SubstitutionParameterGroup(object):
    """
    This parameter type allows for declaring multiple possible options for
    a parameter together with appropriate conversion rules. The configuration source
    then must only specify one of the options in order to load the parameter.

    Each parameter group specifies a primary parameter which determines attributes
    such as the ``field_name`` for example.
    Additional parameter options can be added via :method:`~ParameterGroup.add_option`.
    Options are to be understood as substitutes of the primary parameter and hence
    must be specified together with a conversion rule that converts the option's
    loaded value to the primary parameter's value (as if this value would have been loaded).

    Examples
    --------
    >>> from anna import Configurable, parametrize, Number, JSONAdaptor
    >>> @parametrize(
    ... SubstitutionParameterGroup(Number('StandardDeviation'))
    ... .add_option(Number('Variance'), lambda x: numpy.sqrt(x))
    ... )
    ... class Component(Configurable):
    ...     def __init__(self, configuration):
    ...             super(Component, self).__init__(configuration)
    ...
    >>> config_stddev = JSONAdaptor(root={
    ... 'Component/Parameters/StandardDeviation': '4'
    ... })
    >>> component_stddev = Component(config_stddev)
    >>> component_stddev._standard_deviation
    4.0
    >>> config_variance = JSONAdaptor(root={
    ... 'Component/Parameters/Variance': '16'
    ... })
    >>> component_variance = Component(config_variance)
    >>> component_variance._standard_deviation
    4.0
    """

    def __init__(self, primary_parameter):
        """
        Initialize the parameter group with a primary parameter.

        Parameters
        ----------
        primary_parameter : :class:`Parameter` derived class
            The primary option which also defines attributes such as
            ``info``, ``default``, ``field_name``.
        """
        super(SubstitutionParameterGroup, self).__init__()
        self._options = [ActionParameter(primary_parameter, lambda v: v)]

    def __getattr__(self, item):
        return getattr(self._primary, item)

    def __iter__(self):
        """
        Yield all the options.

        Returns
        -------
        options : iterator
        """
        return iter(self._options)

    def __str__(self):
        """
        JSON decodable string representation of the parameter.

        Returns
        -------
        unicode
        """
        return to_json_string(self.as_json())

    # noinspection PyTypeChecker
    def as_json(self):
        """
        JSON compatible representation of the parameter.

        Returns
        -------
        dict
        """
        return dict(
            primary=self._primary.as_json(),
            options=tuple(map(lambda p: p.as_json(), self._options[1:])),
            type=self.__class__.__name__
        )

    # Need to redefine property field_name because the field name might be set
    # by `parametrize` after a Parameter(Group) has been created.
    @property
    @use_docs_from(Parameter)
    def field_name(self):
        return self._primary.field_name

    @field_name.setter
    @use_docs_from(Parameter)
    def field_name(self, value):
        self._primary.field_name = value

    @property
    def options(self):
        return self._options

    def add_option(self, parameter, conversion):
        """
        Add a parameter option to the group. This requires also a conversion function
        which converts the option's loaded value to the value of the primary parameter
        (as if this value would have been loaded). The conversion function is applied to
        the option's value after it has been loaded from the configuration source.

        Parameters
        ----------
        parameter : :class:`Parameter` derived class
        conversion : callable
            Function which convert's `parameter`s value to the primary parameter's value.

        Returns
        -------
        self
            The instance.

        Examples
        --------
        >>> standard_deviation = SubstitutionParameterGroup(NumberParameter('StandardDeviation'))
        >>> standard_deviation.add_option(NumberParameter('Variance'), lambda x: numpy.sqrt(x))
        """
        self._options.append(ActionParameter(parameter, conversion))
        return self

    def load_from_configuration(self, configuration, path):
        """
        Load the value from the first option which is found in the given configuration source
        (starting with the primary option, continuing in the order in which options have been
        added). If no option is present an exception is raised.

        Parameters
        ----------
        configuration : :class:`ConfigurationAdaptor`
            The configuration adaptor representing the configuration source.
        path : unicode
            The path which localizes one of the options within the configuration.

        Returns
        -------
        native_representation
            The value of the first option which is found in the configuration source,
            converted via the corresponding conversion function.

        Raises
        ------
        IncompleteConfigurationError
            If no option is found in the configuration source.
        """
        for option in self._options:
            try:
                return option.load_from_configuration(configuration, path)
            except IncompleteConfigurationError:
                pass
        raise IncompleteConfigurationError(self, path)

    def load_from_representation(self, text, meta, *args):
        """
        Loading from representation is not supported as it would be ambiguous to
        which option the given representation refers to.

        Raises
        ------
        NotImplementedError
            This method is not implemented.
        """
        raise NotImplementedError(
            'Loading from representation is not supported for SubstituteParameterGroups '
            'as it is not clear which option the given representation refers to'
        )

    @property
    def _primary(self):
        """
        The primary option of this group.

        Returns
        -------
        primary_option : :class:`ActionParameter`
            The primary option with which the group has been initialized.
            The corresponding action is a no-op.
        """
        return self._options[0]

Parameter.register(SubstitutionParameterGroup)


@six.python_2_unicode_compatible
class _VectorParameterTemplate(object):
    """
    This parameter type represents a vector (array) of multiple parameters of the same type.
    The text representation must be of the format ``[e1  e2  ...]`` (elements separated by
    two or more spaces) or ``[e1, e2, ...]`` (elements separated by commas). Both representations
    include enclosing square brackets. The format for each single vector element is the one of
    the wrapped parameter's type.
    """

    _element_type = None
    _container_type = list
    vector_format_illustration = '[e1  e2  ...] or [e1, e2, ...]'

    def __init__(self, name, *args, **kwargs):
        super(_VectorParameterTemplate, self).__init__()

        self._info = kwargs.pop('info', None)
        self._default = kwargs.pop('default', None)
        self._optional = kwargs.pop('optional', None)
        self._for_example = kwargs.pop('for_example', None)

        self._parameter = self._element_type(name, *args, **kwargs)
        if self._element_type is None:
            raise TypeError(
                'Element type must not be a subclass of Parameter (got %s instead)'
                % type(self._element_type)
            )

    def __getattr__(self, item):
        return getattr(self._parameter, item)

    def __str__(self):
        """
        JSON decodable string representation of the parameter.

        Returns
        -------
        unicode
        """
        return to_json_string(self.as_json())

    def as_json(self):
        """
        JSON compatible representation of the parameter.

        Returns
        -------
        dict
        """
        return dict(
            parameter=self._parameter.as_json(),
            container_type=self._container_type.__name__,
            type=self.__class__.__name__
        )

    @property
    def default(self):
        return self._default

    # Need to redefine property field_name because the field name might be set
    # by `parametrize` after a (Vector)Parameter has been created.
    @property
    @use_docs_from(Parameter)
    def field_name(self):
        return self._parameter.field_name

    @field_name.setter
    @use_docs_from(Parameter)
    def field_name(self, value):
        self._parameter.field_name = value

    @property
    def for_example(self):
        """
        Obtain an example value for this parameter.
        
        .. note::
           This is not the same as default! An example value solely aims to give an example for a
           meaningful value however this is not a preferred value that was chosen by the developer.
        
        Returns
        -------
        for_example
            An example value or ``None`` if no example value is available. 
        """
        return self._for_example

    @property
    def info(self):
        return self._info

    @property
    def is_expert(self):
        return self._default is not None

    @property
    def is_optional(self):
        return self._optional is not None

    @use_docs_from(Parameter)
    def load_from_configuration(self, configuration, path):
        if configuration is None:
            if self.default is not None:
                return self.default
            else:
                raise IncompleteConfigurationError(self, path)
        full_path = configuration.join_paths(path, self._parameter.name)
        try:
            text = configuration.get_text(full_path)
            meta = configuration.get_meta(full_path)
        except InvalidPathError:
            if self.default is not None:
                return self.default
            else:
                if self.is_optional:
                    return None
                else:
                    raise IncompleteConfigurationError(self, full_path)
        return self.load_from_representation(text, meta)

    def load_from_representation(self, text, meta):
        """
        Convert the given text/meta representation to the parameter's container type hosting the
        vector elements in their native representation. The container type can be configured via
        :method:`~_VectorParameterTemplate.use_container`.

        Parameters
        ----------
        text : unicode
        meta : dict

        Returns
        -------
        elements
            The chosen container type hosting the vector elements in their native
            representation.
        """
        try:
            self.validate_representation(text, meta)
        except ParameterError as err:
            raise type(err)(err.reason, self)
        # Apply an extra `list` here because on Python3 if `self._container_type` is
        # `numpy.array` then it will store the `map` object as `dtype=object` instead of
        # iterating over the map's elements.
        return self._container_type(list(map(
            lambda x: self._parameter.load_from_representation(x, meta),
            self._extract_elements(text)
        )))

    def use_container(self, container_type):
        """
        Customize the container type for this vector parameter instance.

        Parameters
        ----------
        container_type
            Subclass of Iterable, this type is used to store the vector elements.

        Returns
        -------
        self
            The instance.
        """
        self._container_type = container_type
        return self

    def validate_specification(self, text, meta):
        """
        Validate the given specification for each vector element.
        
        .. note::
           Before calling this method the representation should have been verified via
           :method:`~_VectorParameterTemplate.validate_representation`. Otherwise error messages
           might not be as helpful.
        
        Parameters
        ----------
        text : unicode
        meta : dict

        Returns
        -------
        None
            If the specification is valid for each vector element.

        Raises
        ------
        SpecificationError
            If at least one of the vector elements doesn't meet the declaration. 
            
        See Also
        --------
        :method:`~_VectorParameterTemplate.validate_representation`
        """
        for element in self._extract_elements(text):
            self._parameter.validate_specification(element, meta)
        return None

    @classmethod
    def validate_representation(cls, text, meta):
        """
        Validate the given representation. See the class doc string for more information
        about the format.

        Parameters
        ----------
        text : unicode
        meta : dict

        Returns
        -------
        None
            If the representation is valid.

        Raises
        ------
        RepresentationError
            If text doesn't match the vector format or if the conversion to for one of
            the elements failed.
        """
        Parameter.validate_representation(text, meta)

        if not (text.startswith('[') and text.endswith(']')):
            raise RepresentationError(
                'Does not have vector format %s'
                % cls.vector_format_illustration
            )

        elements = cls._extract_elements(text)
        for element in elements:
            cls._element_type.validate_representation(element, meta)

    @classmethod
    def _extract_elements(cls, vector_string):
        """
        Extract the single vector elements from the string representing the vector.
        Vector elements must be separated either by two or more whitespaces or by a comma.

        Parameters
        ----------
        vector_string : unicode

        Returns
        -------
        elements : tuple[unicode]
        """
        return tuple(filter(
            None,
            map(
                six.text_type.strip,
                vector_string[1:-1].replace(',', '  ').split('  ')
            )
        ))

Parameter.register(_VectorParameterTemplate)


class _VectorParameterGenerator(object):
    __doc__ = """
    {0}
    A vector parameter of a specific type can be generated as follows::

        >>> IntegerVector = Vector[Integer]

    A vector parameter needs a `name` argument upon instantiation, all additional arguments and/or
    keyword arguments are passed to the `__init__` method of the wrapped parameter's type. The
    vector parameter effectively acts as a proxy for the wrapped parameter, that is defining a
    default value or marking the parameter optional for example can be achieved as normal by using
    the corresponding keyword arguments.
    """.format(_VectorParameterTemplate.__doc__)

    def __init__(self, template_class):
        super(_VectorParameterGenerator, self).__init__()
        self._template_class = template_class

    def __getitem__(self, item):
        if not issubclass(item, Parameter):
            raise TypeError(
                'A VectorParameter must be specified with a subclass of Parameter '
                'as element type'
            )
        element_type = item
        body = vars(self._template_class).copy()
        body.pop('__dict__', None)
        body.pop('__weakref__', None)
        body['_element_type'] = element_type
        return type(
            str('{0}{1}'.format(
                element_type.__name__.replace('Parameter', ''),
                self._template_class.__name__.replace('ParameterTemplate', '').replace('_', '')
            )),
            (self._template_class,),
            body
        )

VectorParameter = _VectorParameterGenerator(_VectorParameterTemplate)


class _TupleParameterTemplate(_VectorParameterTemplate):
    """
    Base class for vector parameters with a fixed number of elements.
    """

    NUMBER_OF_ELEMENTS = None
    _container_type = tuple

    def __init__(self, name, *args, **kwargs):
        super(_TupleParameterTemplate, self).__init__(name, *args, **kwargs)
        if self.NUMBER_OF_ELEMENTS is None:
            raise TypeError(
                'A TupleParameter must specify its number of elements'
            )

    @classmethod
    def validate_representation(cls, text, meta):
        """
        See :method:`VectorParameter.validate_representation`.

        Raises
        ------
        RepresentationError
             If the number of vector elements doesn't match the number of elements
             defined by the class.
        """
        super(_TupleParameterTemplate, cls).validate_representation(text, meta)

        if len(cls._extract_elements(text)) != cls.NUMBER_OF_ELEMENTS:
            raise RepresentationError(
                'Requires a tuple with exactly %d elements (got %d instead)'
                % (cls.NUMBER_OF_ELEMENTS, len(cls._extract_elements(text)))
            )


class _TupleParameterGenerator(_VectorParameterGenerator):
    """
    A TupleParameter is a VectorParameter with a fixed number of elements. Tuple parameters can be
    created as follows::

        >>> from anna import Tuple, Integer
        >>> IntegerTuple = Tuple[3, Integer]

    This creates a tuple parameter which hosts exactly three elements.

    See Also
    --------
    :class:`_VectorParameterGenerator` : For the vector parameter format.
    """
    def __init__(self, template_class):
        super(_TupleParameterGenerator, self).__init__(template_class)

    def __getitem__(self, item):
        if isinstance(item, tuple) and len(item) == 2:
            number_of_elements = item[0]
            remainder = item[1]
        else:
            raise TypeError(
                'A TupleParameter must be specified either with a number of elements and '
                'a subclass of Parameter as element type'
            )
        parameter_type = super(_TupleParameterGenerator, self).__getitem__(remainder)
        parameter_type.NUMBER_OF_ELEMENTS = number_of_elements
        return parameter_type

TupleParameter = _TupleParameterGenerator(_TupleParameterTemplate)


class _NTupleParameterGenerator(_TupleParameterGenerator):
    """
    This classes are shortcuts for creating tuples of fixed length for common values for
    the length. 2- and 3-tuples are available (Duplet and Triplet respectively). They can be
    created as follows (the two given methods are equivalent)::

        >>> from anna import Duplet, Tuple, Integer
        >>> IntegerDuplet = Duplet[Integer]
        >>> AnotherIntegerDuplet = Tuple[2, Integer]

    See Also
    --------
    :class:`_VectorParameterGenerator` : For the vector parameter format.
    """
    def __init__(self, template_class):
        super(_NTupleParameterGenerator, self).__init__(template_class)

    def __getitem__(self, item):
        if not isinstance(item, type):
            raise TypeError(
                'A fixed length TupleParameter must be specified with a subclass of '
                'Parameter as element type'
            )
        return super(_NTupleParameterGenerator, self).__getitem__(
            (getattr(self._template_class, 'NUMBER_OF_ELEMENTS', None), item)
        )


class _DupletParameterTemplate(_TupleParameterTemplate):
    NUMBER_OF_ELEMENTS = 2

DupletParameter = _NTupleParameterGenerator(_DupletParameterTemplate)


class _TripletParameterTemplate(_TupleParameterTemplate):
    NUMBER_OF_ELEMENTS = 3

TripletParameter = _NTupleParameterGenerator(_TripletParameterTemplate)


def get_proxied_parameter(parameter):
    def deduce(par, from_type):
        if isinstance(par, from_type):
            return par.parameter
        return par
    return deduce(
        deduce(parameter, AwareParameter),
        ActionParameter
    )
