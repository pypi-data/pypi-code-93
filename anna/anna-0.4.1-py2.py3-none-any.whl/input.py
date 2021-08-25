# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import numbers
import six

from scipy.constants import physical_constants


_ELEMENTARY_CHARGE = physical_constants['elementary charge'][0]
_SPEED_OF_LIGHT = physical_constants['speed of light in vacuum'][0]


def _string_guard(method):
    def wrapper(self_or_cls, other):
        if isinstance(other, six.text_type):
            if isinstance(self_or_cls, type):
                # If wrapping a classmethod.
                other = self_or_cls(other)
            else:
                # If wrapping an instance method.
                other = self_or_cls.__class__(other)
        return method(self_or_cls, other)
    return wrapper


@six.python_2_unicode_compatible
class Unit(object):
    """
    This class represents physical units. Each unit belongs to a dimension
    (base quantity or derived quantity). Conversion between units of the same
    dimension are supported. New dimension and units can be registered by using
    :method:`~Unit.register_dimension` and :method:`~Unit.register_unit`
    respectively. For base quantities base units of the SI system are used.
    The base units in use can be checked via the class attribute
    ``_defaults_per_dimension``. All units that are registered per dimension
    are stored in ``_units_per_dimension``. The corresponding conversion
    factors are stored in ``_conversion_factors``.
    """

    class ConversionError(Exception):
        pass

    class UnknownUnitError(Exception):
        pass

    _defaults_per_dimension = {
        'amount of substance': 'mol',
        'area': 'm^2',
        'dimensionless': '1',
        'electric current': 'A',
        'electric field strength': 'V/m',
        'electrical charge': 'C',
        'electrical potential': 'V',
        'energy': 'eV',
        'frequency': 'Hz',
        'length': 'm',
        'luminous intensity': 'cd',
        'magnetic field strength': 'T',
        'mass': 'kg',
        'plane angle': 'rad',
        'thermodynamic temperature': 'K',
        'time': 's',
        'velocity': 'm/s',
    }

    _units_per_dimension = {
        'amount of substance': ('mol',),
        'area': ('m^2', 'mm^2'),
        'dimensionless': ('1',),
        'electric current': ('A', 'mA', 'uA', 'nA'),
        'electric field strength': ('V/m', 'V/mm', 'kV/m', 'MV/m'),
        'electrical charge': ('elementary charge', 'C'),
        'electrical potential': ('V',),
        'energy': ('eV', 'keV', 'MeV', 'GeV', 'TeV'),
        'frequency': ('Hz', 'kHz', 'MHz', 'GHz', 'THz'),
        'length': ('m', 'cm', 'mm', 'um'),
        'luminous intensity': ('cd',),
        'magnetic field strength': ('T',),
        'mass': ('kg', 'keV/c^2', 'MeV/c^2', 'GeV/c^2', 'u'),
        'plane angle': ('rad',),
        'thermodynamic temperature': ('K',),
        'time': ('s', 'ms', 'us', 'ns'),
        'velocity': ('m/s', 'c'),
    }

    _conversion_factors = {
        ('m', 'cm'): 1.0e2,
        ('m', 'mm'): 1.0e3,
        ('m', 'um'): 1.0e6,

        ('m^2', 'mm^2'): 1.0e6,

        ('s', 'ms'): 1.0e3,
        ('s', 'us'): 1.0e6,
        ('s', 'ns'): 1.0e9,

        ('keV', 'eV'): 1.0e3,
        ('MeV', 'eV'): 1.0e6,
        ('GeV', 'eV'): 1.0e9,
        ('TeV', 'eV'): 1.0e12,

        ('kHz', 'Hz'): 1.0e3,
        ('MHz', 'Hz'): 1.0e6,
        ('GHz', 'Hz'): 1.0e9,
        ('THz', 'Hz'): 1.0e12,

        ('A', 'mA'): 1.0e3,
        ('A', 'uA'): 1.0e6,
        ('A', 'nA'): 1.0e9,

        ('keV/c^2', 'kg'): 1.0e3 * _ELEMENTARY_CHARGE / _SPEED_OF_LIGHT**2,
        ('MeV/c^2', 'kg'): 1.0e6 * _ELEMENTARY_CHARGE / _SPEED_OF_LIGHT**2,
        ('GeV/c^2', 'kg'): 1.0e9 * _ELEMENTARY_CHARGE / _SPEED_OF_LIGHT**2,
        ('u', 'kg'): physical_constants['unified atomic mass unit'][0],

        ('c', 'm/s'): _SPEED_OF_LIGHT,

        ('elementary charge', 'C'): _ELEMENTARY_CHARGE,

        ('V/mm', 'V/m'): 1.0e3,
        ('kV/m', 'V/m'): 1.0e3,
        ('MV/m', 'V/m'): 1.0e6,
    }
    # Update conversion factors for inverse directions.
    _conversion_factors.update(
        {(to_unit, from_unit): 1./factor
         for (from_unit, to_unit), factor in iter(_conversion_factors.items())}
    )

    def __init__(self, unit_or_dimension):
        """
        Parameters
        ----------
        unit_or_dimension : unicode or :class:`Unit`
            If unicode it can denote either a unit or a dimension. If it
            denotes a dimension the default unit for that dimension is used
            instead. If it is another instance of ``Unit`` a copy is created.

        Raises
        ------
        TypeError
            If the type of `unit_or_dimension` doesn't match.
        ValueError
            If the specified unit is unknown.

        Examples
        --------
        >>> meters = Unit('m')
        >>> print(meters)
        [m]

        Create a unit from another unit:

        >>> meters2 = Unit(meters)
        >>> meters2 == meters
        True

        Create units via a dimension:

        >>> print(Unit('length'))
        [m]
        >>> print(Unit('time'))
        [s]

        Specifying an invalid unit:

        >>> Unit('foo')
        [...]
        UnknownUnitError: foo
        """
        if isinstance(unit_or_dimension, six.text_type):
            identifier = unit_or_dimension
        elif isinstance(unit_or_dimension, self.__class__):
            identifier = unit_or_dimension._identifier
        else:
            raise TypeError(
                'Unit must be either of type unicode or %s (got %s instead).'
                % (self.__class__, type(unit_or_dimension))
            )

        if identifier in self._defaults_per_dimension:
            identifier = self._defaults_per_dimension[identifier]

        self.validate(identifier)

        self._identifier = identifier

    @_string_guard
    def __eq__(self, other):
        return self._identifier == other._identifier

    @_string_guard
    def __ne__(self, other):
        return self._identifier != other._identifier

    def __repr__(self):
        return "{0}('{1}')".format(self.__class__.__name__, self._identifier)

    def __str__(self):
        return '[%s]' % self._identifier

    @_string_guard
    def conversion_factor(self, other):
        """
        Retrieve the conversion factor for converting this unit to `other`.

        Parameters
        ----------
        other : unicode or :class:`Unit`
            Convert to the specified unit. If `other` denotes a dimension then
            the corresponding default unit is used instead.

        Returns
        -------
        conversion_factor : float
            Multiplying the magnitude given in this unit with conversion_factor
            yields the magnitude given in `other` unit.

        Examples
        --------
        >>> m = Unit('m')
        >>> m.conversion_factor('cm')
        100.0
        >>> m.conversion_factor(Unit('mm'))
        1000.0
        >>> Unit('mm').conversion_factor('cm')
        0.1
        """
        if self == other:
            return 1.0
        try:
            return self._conversion_factors[(self._identifier,
                                             other._identifier)]
        except KeyError:
            # If units are of the same dimension then convert via the default
            # unit for that dimension.
            if self.dimension(self) == self.dimension(other):
                default_unit = self.default(self)
                return (Unit._conversion_factors[(self._identifier,
                                                  default_unit._identifier)]
                        * Unit._conversion_factors[(default_unit._identifier,
                                                    other._identifier)])
            raise Unit.ConversionError(
                'No conversion factor available for %s -> %s'
                % (self, other)
            )

    @classmethod
    @_string_guard
    def default(cls, dimension_or_unit):
        """
        Retrieve the default unit corresponding to the specified unit or
        dimension.

        Parameters
        ----------
        dimension_or_unit : unicode or :class:`Unit`
            Specifies the dimension of which the default unit is returned.
            If it denotes a unit the corresponding dimension's default unit
            is returned.

        Returns
        -------
        default_unit : :class:`Unit`
            The default unit for the specified dimension.

        Examples
        --------
        >>> print(Unit.default('length'))
        [m]
        >>> print(Unit.default('ms'))
        [s]
        """
        # `dimension_or_unit` is of type Unit due to _string_guard and is
        # guaranteed to be known at this point.
        return cls(
            cls._defaults_per_dimension[cls.dimension(dimension_or_unit)]
        )

    @classmethod
    @_string_guard
    def dimension(cls, unit):
        """
        Retrieve the dimension of the specified unit.

        Parameters
        ----------
        unit : unicode or :class:`Unit`
            If `unit` denotes a dimension instead of a unit then this method
            is a no-op and returns the dimension.

        Returns
        -------
        dimension : unicode
            The dimension of the specified unit.

        Examples
        --------
        >>> Unit.dimension('m')
        'length'
        >>> Unit.dimension(Unit('ms'))
        'time'
        """
        # `unit` is of type Unit due to _string_guard and is guaranteed to be
        # known at this point.
        return tuple(filter(
            lambda d: unit._identifier in cls._units_per_dimension[d],
            cls._units_per_dimension
        ))[0]

    @classmethod
    def register_dimension(cls, name, base_unit):
        """
        Register a new dimension along with its base unit.

        Parameters
        ----------
        name : unicode
            The name of the dimension.
        base_unit : unicode
            The identifier of the dimension's base unit.

        Raises
        ------
        ValueError
            If the given dimension already exists.
        """
        if name in cls._defaults_per_dimension:
            raise ValueError('Dimension %s already exists' % name)
        cls._defaults_per_dimension[name] = base_unit

    @classmethod
    def register_unit(cls, dimension, name, conversion_to_base_unit):
        """
        Register a new unit under the given dimension.

        Parameters
        ----------
        dimension : unicode
            The dimension to which the unit belongs.
        name : unicode
            The identifier of the unit.
        conversion_to_base_unit : float
            The conversion factor for converting the given unit to the
            dimension's base unit.

        Raises
        ------
        ValueError
            If the given dimension does not exist.
        ValueError
            If the given unit already exists for the given dimension.
        """
        try:
            base_unit = cls._defaults_per_dimension[dimension]
        except KeyError:
            raise ValueError('Dimension %s does not exist' % dimension)
        if name in cls._units_per_dimension[dimension]:
            raise ValueError('Unit %s already exists' % name)
        cls._units_per_dimension[dimension] += (name,)
        cls._conversion_factors[
            (name, base_unit)] = conversion_to_base_unit
        cls._conversion_factors[
            (base_unit, name)] = 1. / conversion_to_base_unit

    @classmethod
    def validate(cls, unit):
        """
        Check if the given unit is valid (exists).

        Parameters
        ----------
        unit : unicode
            The unit to be checked.

        Returns
        -------
        None
            If the given unit is valid and exists.

        Raises
        ------
        Unit.UnknownUnitError
        """
        if not any(map(lambda d: unit in cls._units_per_dimension[d],
                       cls._units_per_dimension)):
            raise cls.UnknownUnitError(unit)


@six.python_2_unicode_compatible
class Value(object):
    """
    This class represents physical values (magnitude + unit).

    ..warning::
    Comparing values with different units is not exact due to floating point
    limitations. That is two values which would theoretically compare equal
    don't necessarily do in this case. This is due to the fact that the left
    hand value is converted to the right hand value's unit in order to compare
    the magnitudes afterwards. Example::

        >>> Value(3001, 'mm') == Value(3.001, 'm')
        True
        >>> Value(3002, 'mm') == Value(3.002, 'm')
        False
        >>> Value(3002, 'mm') == Value(3.002 * 1e3, 'mm')
        True

    Consequently the same applies to manually converted values::

        >>> Value(3002, 'mm').convert_to('m') == Value(3.002, 'm')
        False


    Examples
    --------
    >>> print(Value(2, 'm'))
    2.0 [m]
    >>> print(Value(2, 'm').convert_to('mm'))
    2000.0 [mm]
    """

    def __init__(self, magnitude, unit):
        """
        Parameters
        ----------
        magnitude : int or float
            Is converted to float internally.
        unit : unicode or :class:`Unit`
            Specifying a unit or a dimension.
        """
        super(Value, self).__init__()
        self.magnitude = float(magnitude)
        self.unit = Unit(unit)

    def __add__(self, other):
        if not isinstance(other, Value):
            raise TypeError(
                'Cannot add objects of type Value and %s' % type(other)
            )
        if self.unit != other.unit:
            raise Unit.ConversionError(
                'Cannot add units %s and %s without implicit conversion'
                % (self.unit, other.unit)
            )
        return Value(self.magnitude + other.magnitude, self.unit)

    def __div__(self, other):
        if isinstance(other, Value):
            raise NotImplementedError(
                'Division by another unit-associated value is '
                'not implemented yet'
            )
        elif not isinstance(other, numbers.Number):
            raise TypeError(
                'Cannot divide object of type Value by %s '
                '(requires a number instead)'
                % type(other)
            )
        else:
            return Value(self.magnitude/other, self.unit)

    def __eq__(self, other):
        try:
            return self.convert_to(other.unit).magnitude == other.magnitude
        except Unit.ConversionError:
            return False

    def __mul__(self, other):
        if isinstance(other, Value):
            raise NotImplementedError(
                'Multiplication by another unit-associated value is '
                'not implemented yet'
            )
        elif not isinstance(other, numbers.Number):
            raise TypeError(
                'Cannot multiply object of type Value by %s '
                '(requires a number instead)'
                % type(other)
            )
        else:
            return Value(self.magnitude*other, self.unit)

    def __ne__(self, other):
        try:
            return self.convert_to(other.unit).magnitude != other.magnitude
        except Unit.ConversionError:
            return True

    def __repr__(self):
        return '{0}({1}, {2})'.format(
            self.__class__.__name__,
            self.magnitude,
            '%r' % self.unit
        )

    def __str__(self):
        return '%s %s' % (
            self.magnitude,
            self.unit
        )

    def convert_to(self, new_unit):
        """
        Convert this value to another unit.

        Parameters
        ----------
        new_unit : unicode or :class:`Unit`

        Returns
        -------
        converted_value : :class:`Value`
            Multiplying the old value's magnitude with the factor for
            conversion from the old value's unit to the new unit yields
            the new value's magnitude.

        Examples
        --------
        >>> print(Value(1, 'cm').convert_to('m'))
        0.01 [m]
        >>> print(Value(1, 'cm').convert_to('mm'))
        10.0 [mm]
        """
        if new_unit == self.unit:
            return Value(
                self.magnitude,
                self.unit
            )
        else:
            return Value(
                self.magnitude * self.unit.conversion_factor(new_unit),
                new_unit
            )
